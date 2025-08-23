# EAVS Data Pipeline

Annual ETL pipeline for processing Election Administration and Voting Survey (EAVS) data into BigQuery.

## Quick Start

1. **Authenticate**:
   ```bash
   gcloud auth login fryda.guedes@contractor.votingrightslab.org
   gcloud config set project eavs-392800
   ```

2. **Load new year** (replace 2024 with target year):
   ```bash
   python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
   ```

3. **Update union views manually** in BigQuery Console using generated SQL

4. **Refresh materialized tables**:
   ```bash
   python scripts/load_eavs_year.py 2024 /any/path --refresh-tables
   ```

## Setup

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What It Does

Processes yearly EAVS election data (typically 3000+ counties) from CSV files into BigQuery for analytics dashboards.

**Data Flow**: CSV files → GCS → BigQuery tables → Union views → Dashboard feeds

## Configuration

Field mappings are in `config/field_mappings.yaml` - column names change between years so mappings must be updated annually.

## Key Files

- `scripts/load_eavs_year.py` - Main ETL pipeline
- `config/field_mappings.yaml` - Year-specific field mappings  
- `docs/ANNUAL_CHECKLIST.md` - Detailed step-by-step guide
- `CLAUDE.md` - Complete technical context for AI collaboration

## Important Notes

- **Field mappings change yearly** - always verify CSV column names before processing
- **Union views require manual updates** - the script generates SQL but cannot update views
- **Test with sample data first** - validate mappings before full load
- See `docs/ANNUAL_CHECKLIST.md` for complete workflow

## Project Info

- **BigQuery Project**: eavs-392800
- **Data Source**: Google Drive (see CLAUDE.md for link)
- **Account**: fryda.guedes@contractor.votingrightslab.org