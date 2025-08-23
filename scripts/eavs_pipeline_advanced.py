#!/usr/bin/env python3
"""
EAVS Data Pipeline
Automated ETL pipeline for loading EAVS data into BigQuery
"""

import os
import sys
import yaml
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/eavs_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EAVSPipeline:
    """Main pipeline class for EAVS data processing"""
    
    def __init__(self, config_path: str, year: str):
        """Initialize pipeline with configuration and year"""
        self.year = year
        self.config = self._load_config(config_path)
        self.project_id = self.config['global']['project_id']
        self.analytics_dataset = self.config['global']['analytics_dataset']
        self.gcs_bucket = self.config['global']['gcs_bucket']
        
        # Initialize clients
        self.bq_client = bigquery.Client(project=self.project_id)
        self.storage_client = storage.Client(project=self.project_id)
        
        # Dataset names
        self.year_dataset = f"eavs_{year}"
        
        logger.info(f"Initialized pipeline for year {year}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load YAML configuration file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    
    def run_full_pipeline(self, data_dir: str):
        """Run the complete ETL pipeline"""
        logger.info(f"Starting full pipeline for year {self.year}")
        
        # Step 1: Upload files to GCS
        gcs_paths = self.upload_to_gcs(data_dir)
        
        # Step 2: Create BigQuery dataset
        self.create_bq_dataset()
        
        # Step 3: Create external tables
        self.create_external_tables(gcs_paths)
        
        # Step 4: Update union views
        self.update_union_views()
        
        # Step 5: Refresh materialized tables
        self.refresh_materialized_tables()
        
        # Step 6: Validate data
        self.validate_data()
        
        logger.info(f"Pipeline completed successfully for year {self.year}")
    
    def upload_to_gcs(self, data_dir: str) -> Dict[str, str]:
        """Upload CSV files to Google Cloud Storage"""
        logger.info(f"Uploading files from {data_dir} to GCS")
        
        bucket = self.storage_client.bucket(self.gcs_bucket)
        gcs_paths = {}
        
        # Define file mappings
        file_mappings = {
            'a_reg': 'Section A_ Registration/EAVS_county_24_A_REG.csv',
            'b_uocava': 'Section B_ UOCAVA/EAVS_county_24_B_UOCAVA.csv',
            'c_mail': 'Section C_ Mail/EAVS_county_24_C_MAIL.csv',
            'f1_participation': 'Section F1_ Participation and Method/EAVS_county_24_F1_PARTICIPATION.csv'
        }
        
        for section, local_path in file_mappings.items():
            if section in self.config['sections'].get(self.year, []):
                full_path = Path(data_dir) / local_path
                if full_path.exists():
                    # Upload to GCS
                    blob_name = f"{self.year}/{section}.csv"
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(str(full_path))
                    
                    gcs_path = f"gs://{self.gcs_bucket}/{blob_name}"
                    gcs_paths[section] = gcs_path
                    logger.info(f"Uploaded {local_path} to {gcs_path}")
                else:
                    logger.warning(f"File not found: {full_path}")
        
        return gcs_paths
    
    def create_bq_dataset(self):
        """Create BigQuery dataset for the year"""
        dataset_id = f"{self.project_id}.{self.year_dataset}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        dataset.description = f"{self.year} EAVS County-level data"
        
        try:
            dataset = self.bq_client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Created dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            raise
    
    def create_external_tables(self, gcs_paths: Dict[str, str]):
        """Create external tables pointing to GCS files"""
        logger.info("Creating external tables")
        
        for section, gcs_path in gcs_paths.items():
            table_name = f"eavs_county_{self.year[-2:]}_{section}"
            table_id = f"{self.project_id}.{self.year_dataset}.{table_name}"
            
            # Configure external table
            external_config = bigquery.ExternalConfig("CSV")
            external_config.source_uris = [gcs_path]
            external_config.autodetect = True
            external_config.options.skip_leading_rows = 1
            external_config.options.allow_quoted_newlines = True
            external_config.options.allow_jagged_rows = False
            
            table = bigquery.Table(table_id)
            table.external_data_configuration = external_config
            
            try:
                table = self.bq_client.create_table(table, exists_ok=True)
                logger.info(f"Created external table {table_id}")
            except Exception as e:
                logger.error(f"Error creating external table {table_id}: {e}")
                raise
    
    def update_union_views(self):
        """Update union views to include new year data"""
        logger.info("Updating union views")
        
        # For now, focus on registration view
        if 'registration_mappings' in self.config:
            self._update_registration_view()
        
        # Add other views as needed
        # self._update_uocava_view()
        # self._update_mail_view()
        # self._update_participation_view()
    
    def _update_registration_view(self):
        """Update the registration union view"""
        view_id = f"{self.project_id}.{self.analytics_dataset}.eavs_county_reg_union"
        
        # Generate SQL for the new year
        year_mappings = self.config['registration_mappings'].get(self.year, {})
        if not year_mappings:
            logger.warning(f"No registration mappings found for year {self.year}")
            return
        
        # Build the CTE for this year
        field_selections = []
        for standard_field in self.config['registration_mappings']['standard_fields']:
            if standard_field == 'election_year':
                field_selections.append(f"'{self.year}' AS election_year")
            else:
                source_field = year_mappings.get(standard_field)
                if source_field and source_field != 'null':
                    field_selections.append(f"{source_field} AS {standard_field}")
                else:
                    field_selections.append(f"NULL AS {standard_field}")
        
        year_cte = f"""
  registration_{self.year} AS (
  SELECT
    {',\n    '.join(field_selections)}
  FROM
    `{self.year_dataset}.eavs_county_{self.year[-2:]}_a_reg`)"""
        
        logger.info(f"Generated CTE for year {self.year}")
        
        # Note: In production, you would need to fetch the existing view definition,
        # parse it, add the new CTE, and recreate the view
        # For now, we'll log the SQL that needs to be added
        logger.info(f"Add this CTE to the union view:\n{year_cte}")
        
        # Also add to the UNION ALL section
        union_addition = f"""
UNION ALL
SELECT
  *
FROM
  registration_{self.year}"""
        
        logger.info(f"Add this to the UNION ALL section:\n{union_addition}")
    
    def refresh_materialized_tables(self):
        """Refresh materialized tables from views"""
        logger.info("Refreshing materialized tables")
        
        tables_to_refresh = [
            'stg_eavs_county_reg_union',
            'stg_eavs_county_mail_union',
            'stg_eavs_county_part_union',
            'stg_eavs_county_uocava_union'
        ]
        
        for table_name in tables_to_refresh:
            view_name = table_name.replace('stg_', '')
            
            query = f"""
            CREATE OR REPLACE TABLE `{self.project_id}.{self.analytics_dataset}.{table_name}` AS
            SELECT * FROM `{self.project_id}.{self.analytics_dataset}.{view_name}`
            """
            
            try:
                query_job = self.bq_client.query(query)
                query_job.result()  # Wait for completion
                logger.info(f"Refreshed materialized table {table_name}")
            except Exception as e:
                logger.warning(f"Could not refresh {table_name}: {e}")
    
    def validate_data(self):
        """Run data validation checks"""
        logger.info("Running data validation")
        
        # Check row counts
        sections = self.config['sections'].get(self.year, [])
        for section in sections:
            table_name = f"eavs_county_{self.year[-2:]}_{section}"
            table_id = f"{self.project_id}.{self.year_dataset}.{table_name}"
            
            query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
            
            try:
                result = self.bq_client.query(query).result()
                for row in result:
                    logger.info(f"Table {table_name} has {row.row_count} rows")
                    if row.row_count == 0:
                        logger.warning(f"Table {table_name} is empty!")
            except Exception as e:
                logger.error(f"Error validating {table_name}: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='EAVS Data Pipeline')
    parser.add_argument('--year', required=True, help='Election year (e.g., 2024)')
    parser.add_argument('--data-dir', required=True, help='Directory containing EAVS data files')
    parser.add_argument('--config', default='config/field_mappings.yaml', help='Path to configuration file')
    parser.add_argument('--step', choices=['upload', 'tables', 'views', 'materialize', 'validate', 'all'],
                       default='all', help='Which pipeline step to run')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    # Initialize and run pipeline
    pipeline = EAVSPipeline(args.config, args.year)
    
    if args.step == 'all':
        pipeline.run_full_pipeline(args.data_dir)
    elif args.step == 'upload':
        pipeline.upload_to_gcs(args.data_dir)
    elif args.step == 'tables':
        # Would need to get gcs_paths from somewhere
        logger.info("Run 'upload' step first to get GCS paths")
    elif args.step == 'views':
        pipeline.update_union_views()
    elif args.step == 'materialize':
        pipeline.refresh_materialized_tables()
    elif args.step == 'validate':
        pipeline.validate_data()


if __name__ == '__main__':
    main()