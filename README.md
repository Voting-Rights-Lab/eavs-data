# EAVS Data Pipeline

Annual pipeline for loading Election Administration and Voting Survey (EAVS) data into BigQuery.

## What This Does

1. Uploads EAVS CSV files to Google Cloud Storage
2. Creates BigQuery external tables pointing to the files  
3. **Automatically updates union views with new year data**
4. Refreshes materialized tables for dashboard performance
5. Everything works - dashboards update automatically!

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud SDK installed and configured
- Access to the EAVS BigQuery project (eavs-392800)
- Service account or user credentials with appropriate permissions

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd eavs-data

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Authenticate with Google Cloud
gcloud auth application-default login
gcloud config set project eavs-392800
```

## Usage

### Quick Start - Loading a New Year

To load a new year of EAVS data (e.g., 2024):

```bash
# Run the complete loading process
python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
```

This will:
1. Create GCS bucket if needed (eavs-data-files)
2. Upload CSV files to GCS
3. Create BigQuery dataset (eavs_2024)
4. Create external tables pointing to GCS files
5. Generate SQL for updating union views
6. Validate the data

### That's It!

The script automatically:
- Updates all union views with the new year
- No manual SQL copying needed
- Views are ready immediately for dashboards

If you need to refresh materialized tables separately:
```bash
python scripts/load_eavs_year.py 2024 /any/path --refresh-tables
```

## Configuration

The pipeline is configured via `config/field_mappings.yaml`. This file contains:

- **Global settings**: Project ID, dataset names, GCS bucket
- **Section definitions**: Which data sections exist for each year
- **Field mappings**: How raw field names map to standardized column names

### Adding a New Year

1. Download the EAVS data files to a local directory
2. Update `config/field_mappings.yaml`:
   - Add the year to the `sections` configuration
   - Add field mappings for any changed column names
3. Run the pipeline for the new year

### Field Mapping Structure

```yaml
registration_mappings:
  2024:
    state: state  # source_field: target_field
    county: county
    state_abbr: state_name_abbreviation
    total_reg: a1a_total_reg
    # ... more mappings
```

## Data Flow

```
Local CSV Files
    ↓
Google Cloud Storage
    ↓
BigQuery External Tables (eavs_2024.*)
    ↓
Union Views (eavs_analytics.*_union)
    ↓
Materialized Tables (eavs_analytics.stg_*)
    ↓
Analytics Marts & Dashboards
```

## Project Structure

```
eavs-data/
├── scripts/
│   └── load_eavs_year.py      # Main pipeline script
├── config/
│   └── field_mappings.yaml    # Field mappings for all years
├── sql/
│   └── view_updates/          # Generated SQL for view updates
├── docs/
│   └── ANNUAL_CHECKLIST.md    # Step-by-step checklist
├── requirements.txt
└── README.md
```

## Troubleshooting

### Common Issues

1. **Authentication errors**: Ensure you're authenticated with the correct Google account
   ```bash
   gcloud auth list  # Check active account
   gcloud auth login fryda.guedes@contractor.votingrightslab.org
   ```

2. **Missing GCS bucket**: Create the bucket if it doesn't exist
   ```bash
   gsutil mb -p eavs-392800 gs://eavs-data/
   ```

3. **Permission errors**: Ensure your account has the necessary BigQuery and Storage permissions

### Logs

Check the `logs/` directory for detailed pipeline execution logs:
```bash
tail -f logs/eavs_pipeline_*.log
```

## Manual Steps

After running the pipeline, you may need to:

1. **Update union view SQL manually**: The pipeline generates the SQL but doesn't automatically update the view definition. Copy the generated SQL and update the view in BigQuery UI.

2. **Create performance tables**: In BigQuery UI, create tables from views for better performance:
   ```sql
   CREATE OR REPLACE TABLE `eavs_analytics.mart_eavs_analytics_county_rollup` AS
   SELECT * FROM `eavs_analytics.eavs_analytics_county_rollup`;
   ```

3. **Update Looker Studio dashboards**: Refresh data sources if needed

## Contributing

When adding new features:
1. Update field mappings in `config/field_mappings.yaml`
2. Test with a small subset of data first
3. Document any manual steps required
4. Update this README with new functionality