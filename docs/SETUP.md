# EAVS Data Pipeline - Local Setup Guide

## Quick Setup

### 1. Authenticate with Google Cloud

```bash
# Activate the eavs-data configuration
gcloud config configurations activate eavs-data

# Verify settings (should show eavs-data as active)
gcloud config list

# If eavs-data config doesn't exist, create it:
# gcloud config configurations create eavs-data
# gcloud config set account fryda.guedes@contractor.votingrightslab.org
# gcloud config set project eavs-392800
```

### 2. Verify BigQuery Access

```bash
# Test access to analytics dataset
bq ls eavs_analytics

# Test a query
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`eavs_analytics.stg_eavs_county_reg_union\` WHERE election_year = '2024'"
```

## Configuration Files

### `.bigqueryrc` (Home Directory)

Location: `~/.bigqueryrc`

```ini
# BigQuery CLI Configuration for EAVS project
# credential_file removed to use gcloud auth instead
project_id = eavs-392800
```

**Important**: Do NOT include a `credential_file` line. This allows proper account switching via `gcloud config set account`.

### `.env` (Project Directory)

Location: `/Users/frydaguedes/Projects/eavs-data/.env` (not committed to git)

```bash
# EAVS Data Pipeline Environment Configuration
EAVS_PROJECT_ID=eavs-392800
EAVS_GCS_BUCKET=eavs-data-files
EAVS_ANALYTICS_DATASET=eavs_analytics
EAVS_ACCOUNT=fryda.guedes@contractor.votingrightslab.org
```

## Troubleshooting

### "Permission denied" errors

Make sure you're using the correct account:
```bash
gcloud auth list  # Should show fryda.guedes@contractor.votingrightslab.org as ACTIVE
```

If using wrong account:
```bash
gcloud config set account fryda.guedes@contractor.votingrightslab.org
```

### "Project not found" errors

Check your `.bigqueryrc` file:
```bash
cat ~/.bigqueryrc
# Should show: project_id = eavs-392800
```

If wrong, edit it or run:
```bash
gcloud config set project eavs-392800
```

### BigQuery using wrong credentials

Your `~/.bigqueryrc` may have a `credential_file` line pointing to old credentials.

**Fix**:
```bash
# Backup old config
cp ~/.bigqueryrc ~/.bigqueryrc.backup

# Edit ~/.bigqueryrc and remove the credential_file line
# Keep only: project_id = eavs-392800
```

## Python Dependencies

```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Verification Checklist

- [ ] `gcloud config list` shows correct account and project
- [ ] `bq ls eavs_analytics` returns list of tables/views
- [ ] `python scripts/load_eavs_year.py --help` runs without errors
- [ ] `.env` file exists with correct project settings
- [ ] `~/.bigqueryrc` has correct project_id (no credential_file line)

## Quick Commands

```bash
# Check current config
gcloud config list
bq show --format=prettyjson eavs_analytics

# List datasets
bq ls

# List tables in a dataset
bq ls eavs_2024

# Query data
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`eavs_2024.eavs_county_24_a_reg\`"

# Upload to GCS
gsutil cp file.csv gs://eavs-data-files/2024/
```

## Helpful Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# EAVS project shortcuts
alias eavs-auth='gcloud config set account fryda.guedes@contractor.votingrightslab.org && gcloud config set project eavs-392800'
alias eavs-cd='cd /Users/frydaguedes/Projects/eavs-data'
alias eavs-venv='source /Users/frydaguedes/Projects/eavs-data/venv/bin/activate'
```

Then you can just run:
```bash
eavs-auth  # Set correct account/project
eavs-cd    # Go to project directory
eavs-venv  # Activate virtual environment
```
