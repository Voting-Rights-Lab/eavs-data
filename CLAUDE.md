# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The EAVS Data Transformation project processes Election Administration and Voting Survey (EAVS) data from raw county-level CSV files into structured BigQuery tables and views for reporting and analysis.

## Architecture

### Data Pipeline
- **Input**: Annual EAVS data files in CSV format organized by sections (Registration, UOCAVA, Mail, Participation, etc.)
- **Processing**: Python ETL scripts for data cleaning, transformation, and validation
- **Storage**: Google BigQuery (project: eavs-392800)
- **Output**: Standardized views for reporting and Looker Studio dashboards

### Key Data Sections
- **Section A**: Registration - Voter registration statistics
- **Section B**: UOCAVA - Military and overseas voting data
- **Section C**: Mail - Absentee/mail ballot data
- **Section F1**: Participation - Voter turnout and participation methods
- **Supplemental**: CVAP data and FIPS code mappings

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### BigQuery Authentication
```bash
# Set project
gcloud config set project eavs-392800

# Authenticate
gcloud auth application-default login

# List datasets
bq ls
```

## Important Technical Details

### Data Processing Constraints
1. **File Naming**: EAVS files follow pattern `EAVS_county_{year}_{section}.csv`
2. **Geographic Keys**: All data includes FIPS codes for county-level joining
3. **Year Variations**: Different years may have different sections available
4. **Data Quality**: Handle missing values and validate against codebooks

### BigQuery Conventions
1. **Dataset Naming**: Use year-based datasets (e.g., `eavs_2024`)
2. **Table Naming**: Preserve section structure (e.g., `section_a_registration`)
3. **View Naming**: Create unified views across years for reporting
4. **Schema Evolution**: Document schema changes between years

## Common Tasks

### When adding a new year of data:
1. Download raw data files from Google Drive to local directory
2. Compare structure with previous years
3. Update field mappings configuration if needed
4. Run ETL pipeline to load into BigQuery
5. Create/update reporting views
6. Validate data against previous years

### When modifying transformations:
1. Always preserve raw data tables
2. Version transformation logic in views
3. Document any business logic changes
4. Test with sample data before full runs
5. Update data quality checks

## File Structure

```
eavs-data/
├── data/               # Local data files (NOT in git)
│   ├── 2022/          # Previous year example
│   ├── 2024/          # Current year to process
│   └── processed/     # Transformed data
├── etl/               # ETL pipeline scripts
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── sql/               # BigQuery SQL scripts
│   ├── tables/        # Table creation scripts
│   └── views/         # View definitions
├── config/            # Configuration files
│   └── field_mappings.yaml
├── docs/              # Documentation
├── logs/              # Processing logs (NOT in git)
├── CLAUDE.md          # This file
├── TODO.md            # Task tracking
└── README.md          # Project documentation
```

## Git and Security Best Practices

### What IS committed:
- Source code and pipeline scripts
- Configuration templates
- Documentation
- SQL scripts and view definitions
- Requirements files

### What is NOT committed:
- Raw data files (CSV, Excel, etc.)
- Processed data files
- BigQuery credentials
- Environment variables (.env)
- Log files
- Virtual environments

### Important Reminders:
- Never commit sensitive data or credentials
- Always use virtual environments for Python development
- Test transformations on sample data first
- Document any changes to business logic
- Maintain data lineage documentation

## Data Sources

- **Google Drive**: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs
- **BigQuery Project**: eavs-392800
- **Google Account**: fryda.guedes@contractor.votingrightslab.org

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.