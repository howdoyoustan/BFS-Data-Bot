"""
BAWR-186 / BAWR-187 : GLEIF -> Entity LEI mapping job.

Builds the GLIEF_TO_ENTITY_MAPPING table by fuzzy-matching active AC360
entity names against active GLEIF legal names and recording the similarity
percentage for every candidate match.

Design notes
------------
* Uses ONLY native Spark SQL functions (regexp_replace, soundex, levenshtein,
  row_number, ...). No Python UDFs and no third-party libraries, so the whole
  pipeline stays distributed and scalable.
* Stores ALL candidate matches with their percentage (per BAWR-186). A
  downstream FDW.out job selects the single highest match per entity; a helper
  (`select_best_match`) is provided here for that selection plus the
  "one LEI -> one SSN" constraint.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BUSINESS_DT = "2026-06-03"  # monthly run date; drives source partitions + output column

# GLEIF (ELZ) source. Path is templated by business date.
GLEIF_ELZ_TABLE = "qfc.gleif_ent_c"
GLEIF_ELZ_PATH_TEMPLATE = (
    "abfss://elz@<storage-account>.dfs.core.windows.net/qfc/gleif_ent_c/{date}/"
)

# Output target.
MAPPING_TABLE = "cust360.glief_to_entity_mapping"

# Legal-suffix / noise words removed before comparison so that
# "ABC Inc" and "ABC Incorporated LLC" normalize to the same core token.
NOISE_WORDS = (
    r"\b(?:ltd|limited|inc|incorporated|pvt|private|llc|llp|lp|plc|corp|"
    r"corporation|company|co|the|and|of)\b"
)

# Blocking / filtering knobs.
BLOCK_PREFIX_LEN = 4          # candidate join key = first N chars of normalized name
LENGTH_RATIO_TOLERANCE = 0.25  # allowed length diff as a fraction of the longer name
MIN_MATCH_PERCENTAGE = 50.0   # candidates below this are not stored

# Match classification thresholds.
EXACT_THRESHOLD = 95.0
STRONG_THRESHOLD = 85.0


# --------------------------------------------------------------------------- #
# Spark session
# --------------------------------------------------------------------------- #
def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("glief_to_entity_mapping")
        .getOrCreate()
    )


# --------------------------------------------------------------------------- #
# Sources
# --------------------------------------------------------------------------- #
def load_entities(spark: SparkSession) -> DataFrame:
    """Active AC360 entities (BAWR-187).

    Returns: entity_id, entity_nm, ssn_tin_nbr
    """
    df = spark.sql(
        """
        SELECT DISTINCT
               en.entity_id,
               en.entity_nm,
               en.ssn_tin_nbr
        FROM   cust360.entity_cv en
        JOIN   cust360.entity_hierarchy_cv eh
               ON en.entity_id = eh.entity_id
        WHERE  eh.hierarchy_active_flg = 'Y'
          AND  en.entity_active_flg   = 'Y'
        """
    )
    return df.filter(
        F.col("entity_nm").isNotNull() & (F.trim(F.col("entity_nm")) != F.lit(""))
    )


def load_gleif(spark: SparkSession, business_dt: str) -> DataFrame:
    """Active GLEIF entities from ELZ (BAWR-175 / BAWR-186 step 2).

    Returns: entity_legalname, lei
    """
    path = GLEIF_ELZ_PATH_TEMPLATE.format(date=business_dt)
    raw = spark.read.parquet(path)

    return (
        raw.filter(F.col("entity_entityexpirationdate") == F.lit("ACTIVE"))
        .select("entity_legalname", "lei")
        .filter(
            F.col("entity_legalname").isNotNull()
            & (F.trim(F.col("entity_legalname")) != F.lit(""))
            & F.col("lei").isNotNull()
        )
        .dropDuplicates(["lei"])  # one row per LEI
    )


# --------------------------------------------------------------------------- #
# Normalization (native functions only)
# --------------------------------------------------------------------------- #
def normalize_name(name_col: "F.Column") -> "F.Column":
    """lower -> strip punctuation (keep spaces) -> drop legal suffixes ->
    collapse whitespace. Spaces are preserved until after noise-word removal
    so the \\b word boundaries can match."""
    lowered = F.lower(F.trim(name_col))
    no_punct = F.regexp_replace(lowered, r"[^a-z0-9 ]", " ")
    no_noise = F.regexp_replace(no_punct, NOISE_WORDS, " ")
    collapsed = F.regexp_replace(no_noise, r"\s+", " ")
    return F.trim(collapsed)


def add_normalized_columns(entities: DataFrame, gleif: DataFrame):
    entities_n = entities.withColumn(
        "entity_nm_norm", normalize_name(F.col("entity_nm"))
    ).withColumn(
        "block_key", F.substring(F.regexp_replace(F.col("entity_nm_norm"), " ", ""), 1, BLOCK_PREFIX_LEN)
    )

    gleif_n = gleif.withColumn(
        "gleif_name_norm", normalize_name(F.col("entity_legalname"))
    ).withColumn(
        "block_key", F.substring(F.regexp_replace(F.col("gleif_name_norm"), " ", ""), 1, BLOCK_PREFIX_LEN)
    )
    return entities_n, gleif_n


# --------------------------------------------------------------------------- #
# Candidate generation, filtering and scoring
# --------------------------------------------------------------------------- #
def generate_candidates(entities_n: DataFrame, gleif_n: DataFrame) -> DataFrame:
    """Block on prefix key, broadcast the (smaller) GLEIF side, then prune with
    soundex + length-ratio before the more expensive levenshtein scoring."""
    e = entities_n.alias("e")
    g = gleif_n.alias("g")

    candidates = e.join(F.broadcast(g), on="block_key", how="inner").select(
        F.col("e.entity_id").alias("entity_id"),
        F.col("e.entity_nm").alias("entity_nm"),
        F.col("e.ssn_tin_nbr").alias("ssn_tin_nbr"),
        F.col("e.entity_nm_norm").alias("entity_nm_norm"),
        F.col("g.entity_legalname").alias("gleif_name"),
        F.col("g.gleif_name_norm").alias("gleif_name_norm"),
        F.col("g.lei").alias("lei"),
    )

    len_e = F.length("entity_nm_norm")
    len_g = F.length("gleif_name_norm")
    return candidates.filter(
        (F.soundex("entity_nm_norm") == F.soundex("gleif_name_norm"))
        & (
            F.abs(len_e - len_g)
            <= F.lit(LENGTH_RATIO_TOLERANCE) * F.greatest(len_e, len_g)
        )
    )


def score_candidates(candidates: DataFrame) -> DataFrame:
    """Similarity % from normalized Levenshtein edit distance."""
    max_len = F.greatest(F.length("entity_nm_norm"), F.length("gleif_name_norm"))
    edit_distance = F.levenshtein(F.col("entity_nm_norm"), F.col("gleif_name_norm"))

    scored = (
        candidates.withColumn("edit_distance", edit_distance)
        .withColumn("max_len", max_len)
        .withColumn(
            "percentage",
            F.when(
                F.col("max_len") > 0,
                F.round((1 - F.col("edit_distance") / F.col("max_len")) * 100, 2),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "match_status",
            F.when(F.col("percentage") >= EXACT_THRESHOLD, F.lit("Exact Match"))
            .when(F.col("percentage") >= STRONG_THRESHOLD, F.lit("Strong Match"))
            .otherwise(F.lit("Weak Match")),
        )
    )
    return scored.filter(F.col("percentage") >= MIN_MATCH_PERCENTAGE)


def build_mapping(scored: DataFrame, business_dt: str) -> DataFrame:
    """All candidate matches, shaped to the GLIEF_TO_ENTITY_MAPPING table."""
    return scored.select(
        F.col("entity_id"),
        F.col("entity_nm"),
        F.col("ssn_tin_nbr"),
        F.col("gleif_name").alias("gleif_name"),
        F.col("lei"),
        F.col("percentage"),
        F.col("match_status"),
        F.lit(business_dt).cast("date").alias("business_dt"),
    )


# --------------------------------------------------------------------------- #
# Best-match selection (used by the downstream FDW.out job)
# --------------------------------------------------------------------------- #
def select_best_match(mapping: DataFrame) -> DataFrame:
    """Pick the single best LEI per entity, then enforce 'one LEI -> one SSN'
    by keeping, for each LEI, only the SSN with the highest percentage."""
    per_entity = Window.partitionBy("entity_id").orderBy(
        F.desc("percentage"), F.asc("lei")
    )
    best_per_entity = (
        mapping.withColumn("rn", F.row_number().over(per_entity))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )

    per_lei = Window.partitionBy("lei").orderBy(
        F.desc("percentage"), F.asc("ssn_tin_nbr")
    )
    return (
        best_per_entity.withColumn("rn", F.row_number().over(per_lei))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )


# --------------------------------------------------------------------------- #
# Sink
# --------------------------------------------------------------------------- #
def write_mapping(mapping: DataFrame, table: str, business_dt: str) -> None:
    """Idempotent monthly load: overwrite only the current business_dt partition."""
    (
        mapping.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"business_dt = '{business_dt}'")
        .partitionBy("business_dt")
        .saveAsTable(table)
    )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(business_dt: str = BUSINESS_DT) -> None:
    spark = build_spark()

    entities = load_entities(spark)
    gleif = load_gleif(spark, business_dt)

    entities_n, gleif_n = add_normalized_columns(entities, gleif)
    candidates = generate_candidates(entities_n, gleif_n)
    scored = score_candidates(candidates)
    mapping = build_mapping(scored, business_dt)

    write_mapping(mapping, MAPPING_TABLE, business_dt)
    print(f"Wrote {mapping.count()} candidate mappings for business_dt={business_dt}")


if __name__ == "__main__":
    main()
