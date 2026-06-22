Fully working code
from pyspark.sql import Sparksession from pyspark.sql.functions import
from pyspark.sql.window import window
spark
- Sparksession.builder.getorcreate ()
# *
1. Load ENTITY data
df entity cv = spark-read. format ("delta"). load( "abfss://c360-prod-cust360-entity@sasdlclgpii0lpudabdpp07.dfs.core.windows.net/" .filter(
(col ("business dt") - "2026-06-03") (col ("entity nm")-isNotNull()) c (trim(col ("entity nm")) !="") ).orderBy("entity nm", "entity id") \
R
print ("Entity table loaded")
+2. Load GLEIF data +-
elz table name = "qfc.gleif ent hm" bus _date= "2026-06-03"
elz_entity = el2_table_namereplace ("", '-").replace(".", " "_") elz_data_path net/(bus_date)"
elz_data = spark.read.parquet (elz_data_path)
view name = elz table_name.split(".') [1] + "_' + bus_date[5:].replace ('-', '') elz data.createOrReplaceTempview(view name)
print (f"view ' [view_name)" created")
df_gleif - spark.table (view_name) \ -filter (col("entity entityexpirationdate") == "ACTIVE") \ .select ("entity legalname", "lei")
print ("GLEIF table loaded")
#

#3. Normalization

*

noisewwodd - r")bbltdlimited/incipvt|11c|corp|company/the)\b"

df entity_cv - df_entitycc.wwthColumn(

"entitynmnorm",

regexp_replace(
regexp_replace(
regexp_replace(lower(trim(col("entity_nm"))), "["a=20-9]",,""),
noise_words
.
)
I

df_gleif dfgleif.withColumn(
"entity_legalname

regexpreplace(
regexp_replace
regexp_replace(lower(trim(col("entity_legaIname"))), "["a-20-9]",,")
noisewords, ..
),

)

#44. Alias
df_entity_cv - df_entity_
df _gleif - df_gleif.alias cv.alias ("e")
("g")
#
t5. Blocking
df

candidates = df_entity cv-join(
broadcast (df_gleif),
substring (col("e.entity_nm_norm"), 1, 5) " s
substring (col ("gentity legalname orm") 1
"inner"

#6. Select relevant columns

df_candidates = df candidates.select (
col("e-entity_id"),
col("e.entity_nm"),
col("e-entity_ nm_norm"),
col ("g.entity_legalname"),
col ("g.entity_ legalname_norm"),
col ("g.lei")

f7. Filtering

df_candidates = df candidates fi1t..
(soundex (col ("entity nm_norm")) -- soundex (col ("entity_legalname_norm")))

(

abs (length (col ("entity_nm_norm")) - length(col ("entity_legalname_norm"))) <=
0.25 * greatest (length (col ("entity nm_norm")), length (col ("entity_legalname_norm")))
#8. scoring
df scored - df_candidates.withcolumn ( "edit
distance",
levenshtein(col ("entity_nm_norm"), col ("entity_legalname_norm"))
).withcolumn(
"ma _len""
greatest (length (col ("entity_nm_norm")), length (col ("entity_legalname_norm")))
).withcolumn(
"match_percentage", 0r when (col ("max_ len") J (1 - ol("edit_distance") / col("max_len")) * 100 ).otherwise(0)
D
$ 9. Best Match per Entity
window spec = WWindow-partitionBy ("entity_id").orderBy (desc ("match_percentage"))
I
df_best df_ scored.withcolumn(
"rank"
row_number (.over (window_spec) ).filter(col("rank") =- 1)
t 10. Match Classification
df_final = df_ best.withColumn (
"match status", when (col ("match_percentage") >= 95, "Exact Match") .when (col ("match_percentage") >= 85, "strong Match") otherwise ("Weak Match")
t10. Match classification
df_final - df_ best.withcolumn ( "match_status", when (col ("match_percentage") >= 95, "Exact Match") .when (col ("match_percentage") >= 85, "Strong Match") .otherwise ("weak Match")
+
t11. Final Output
df_output = df final.select ( 'entity_ nm" "entity_legalname" "match_percentage", "match_status"
I
df output.show(30000, False)
