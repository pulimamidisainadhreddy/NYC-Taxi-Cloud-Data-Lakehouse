from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("s3-test")
    .master("local[1]")
    .config(
        "spark.hadoop.fs.s3a.impl",
        "org.apache.hadoop.fs.s3a.S3AFileSystem",
    )
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "com.amazonaws.auth.profile.ProfileCredentialsProvider",
    )
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        "s3.eu-central-1.amazonaws.com",
    )
    .getOrCreate()
)

path = (
    "s3a://nyc-taxi-lakehouse-722769296222/"
    "bronze/yellow_taxi/2025/01/"
    "yellow_tripdata_2025-01.parquet"
)

df = spark.read.parquet(path)

print("S3 TEST SUCCESS")
print(f"Records: {df.count()}")

spark.stop()
