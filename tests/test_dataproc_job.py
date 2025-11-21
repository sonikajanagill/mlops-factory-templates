import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src/dataproc to path so we can import the job
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/dataproc')))

from feature_engineering_job import run_job

def test_feature_engineering_transforms():
    """Test feature engineering transformations"""
    # Mock Spark session
    with patch('feature_engineering_job.SparkSession') as mock_spark:
        # Mock DataFrame
        mock_df = Mock()
        mock_spark.builder.appName.return_value.getOrCreate.return_value.read.csv.return_value = mock_df
        
        # Mock transformations
        mock_df.dropna.return_value = mock_df
        mock_df.withColumn.return_value = mock_df
        
        # Run job (we expect it to call write.save)
        run_job("gs://input", "project.dataset.table")
        
        # Verify write was called
        mock_df.write.format.assert_called_with("bigquery")
        mock_df.write.format.return_value.option.assert_called_with("table", "project.dataset.table")
        mock_df.write.format.return_value.option.return_value.mode.assert_called_with("overwrite")
        mock_df.write.format.return_value.option.return_value.mode.return_value.save.assert_called()

def test_bigquery_write_config():
    """Test BigQuery write configuration"""
    with patch('feature_engineering_job.SparkSession') as mock_spark:
        mock_df = Mock()
        mock_spark.builder.appName.return_value.getOrCreate.return_value.read.csv.return_value = mock_df
        mock_df.dropna.return_value = mock_df
        mock_df.withColumn.return_value = mock_df

        run_job("gs://bucket/raw/data.csv", "project.dataset.table")

        # Verify temporary bucket config
        mock_spark.builder.appName.return_value.getOrCreate.return_value.conf.set.assert_called_with("temporaryGcsBucket", "bucket")
