# EAVS Configuration Fixed ✅

## What Was Fixed (Dec 12, 2024)

### Problem
- `gcloud` config was pointing to wrong account (fguedes@bluestate.co)
- `~/.bigqueryrc` had hardcoded credential file to wrong account
- BigQuery commands were using wrong project (data-exchange-1, a-team-test-project)

### Solution
1. Updated `~/.bigqueryrc` to remove credential_file and set project_id = eavs-392800
2. Set gcloud config: `gcloud config set account fryda.guedes@contractor.votingrightslab.org`
3. Set gcloud project: `gcloud config set project eavs-392800`
4. Created `.env` file in project directory with correct settings

### Verification
```bash
# All of these now work correctly:
bq ls eavs_analytics
gcloud config list
python scripts/load_eavs_year.py --help
```

## Configuration Name

✅ Now using properly named configuration: **eavs-data**

To activate:
```bash
gcloud config configurations activate eavs-data
```

## Future Setup

If you need to set this up again (new machine, different profile, etc.):

```bash
cd /Users/frydaguedes/Projects/eavs-data

# Simply activate the eavs-data configuration
gcloud config configurations activate eavs-data
```

Then verify:
```bash
bq ls eavs_analytics
gcloud config list  # Should show "Your active configuration is: [eavs-data]"
```

## Quick Switch Between Projects

```bash
gcloud config configurations activate eavs-data     # For EAVS work
gcloud config configurations activate guttmacher    # For Guttmacher work
```

See [docs/SETUP.md](docs/SETUP.md) for complete setup guide.
