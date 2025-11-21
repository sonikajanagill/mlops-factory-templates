"""
Feature Engineering Job (PySpark)

This job reads the Palmer Penguins dataset, performs basic cleaning and feature engineering,
and writes the result to BigQuery.

Usage:
    python feature_engineering_job.py --input_path gs://... --output_table project.dataset.table
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg

def run_job(input_path, output_table):
    spark = SparkSession.builder \
        .appName("PenguinFeatureEngineering") \
        .getOrCreate()

    # 1. Read Data
    # Assuming CSV format for simplicity, in prod could be Parquet/Avro
    df = spark.read.csv(input_path, header=True, inferSchema=True)

    # 2. Data Cleaning
    # Drop rows with missing values
    df_clean = df.dropna()

    # 3. Feature Engineering
    # Example: Create a new feature 'body_mass_kg' from 'body_mass_g'
    df_transformed = df_clean.withColumn("body_mass_kg", col("body_mass_g") / 1000)

    # Example: One-hot encoding for 'sex' (manual for simplicity, use MLlib in prod)
    df_transformed = df_transformed.withColumn(
        "is_male", when(col("sex") == "MALE", 1).otherwise(0)
    )

    # 4. Write to BigQuery
    # Use the temporary bucket for BQ export
    # Note: The bucket name should be passed or configured
    spark.conf.set("temporaryGcsBucket", input_path.split("/")[2]) 

    df_transformed.write \
        .format("bigquery") \
        .option("table", output_table) \
        .mode("overwrite") \
        .save()

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help="GCS path to input CSV")
    parser.add_argument("--output_table", required=True, help="BigQuery output table (project.dataset.table)")
    args = parser.parse_args()

    run_job(args.input_path, args.output_table)
