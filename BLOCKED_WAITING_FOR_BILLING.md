# ⏸️ BLOCKED: Waiting for Billing Restoration

## Current Status
**Project billing lapsed** - payment card not working. Waiting for organization to renew billing on `eavs-392800` project.

## What's Blocked
- ❌ Loading 2024 policy data to BigQuery
- ❌ Creating new tables or external tables
- ❌ Migrating Google Sheets to native BigQuery tables
- ❌ Running any data loading operations

## What Still Works
- ✅ Querying existing data
- ✅ Creating/updating views
- ✅ Dashboards showing 2016-2022 data (until Google Sheets get deleted!)

## Ready to Execute Immediately When Billing Restored

### Priority 1: Add 2024 Policy Data (5 minutes)
```bash
cd /Users/frydaguedes/Projects/eavs-data
./scripts/add_policy_2024_when_billing_works.sh
```

This will:
1. Load policy_24.csv to BigQuery table
2. Update policy union view
3. Refresh staging tables
4. Rebuild mart tables
5. Verify in dashboards

**File ready**: `data/backups/google_sheets/policy_2024_backup.csv`

### Priority 2: Secure Historical Data (30 minutes)
```bash
# Migrate all Google Sheets to native BigQuery tables
python scripts/migrate_sheets_to_bigquery.py
```

This protects against accidental deletion of 2016-2022 EAVS data and policy data.

## Manual Steps Required First

**Someone at the organization needs to:**

1. **Go to**: https://console.cloud.google.com/billing
2. **Select project**: `eavs-392800`
3. **Update payment method** or **link valid billing account**
4. **Verify billing is active**

## How to Check if Billing is Restored

Try this command - if it works without error, billing is back:
```bash
bq query --project_id=eavs-392800 --use_legacy_sql=false --dry_run \
  "CREATE TABLE test_billing (test STRING)"
```

**Success response**: `Query successfully validated...`
**Still blocked**: `Billing has not been enabled...`

## Who to Contact

Reach out to whoever manages:
- Google Cloud billing for your organization
- Project `eavs-392800` ownership
- Payment methods for cloud services

## Timeline Estimate

Once billing is restored:
- **Policy 2024 integration**: 5 minutes (automated script)
- **Google Sheets migration**: 30 minutes (automated script)
- **Testing and verification**: 15 minutes

**Total**: ~1 hour to complete everything safely.

## What to Do While Waiting

### Immediate Actions (No Billing Needed):
1. ✅ Policy 2024 CSV backed up in repo
2. 🔲 Download Google Sheets backups (when your zip completes)
3. 🔲 Add warnings to Google Sheets: "DO NOT DELETE"
4. 🔲 Restrict edit permissions on Sheets
5. 🔲 Identify who can restore billing

### Documentation Completed:
- ✅ Google Sheets inventory created
- ✅ Migration plan documented
- ✅ Automated scripts ready to run
- ✅ Backup procedures documented

## Files Ready to Execute

**Scripts (ready to run):**
- `scripts/add_policy_2024_when_billing_works.sh` - Adds 2024 policy data
- `scripts/migrate_sheets_to_bigquery.py` - Migrates to native tables
- `scripts/export_google_sheets_backups.sh` - Exports backups

**Data (staged and ready):**
- `data/backups/google_sheets/policy_2024_backup.csv` - 2024 policy data
- `data/backups/google_sheets/` - Directory for all backups

**Documentation:**
- `GOOGLE_SHEETS_INVENTORY.md` - All Sheets URLs
- `MIGRATION_PLAN.md` - Complete migration guide
- `BLOCKED_WAITING_FOR_BILLING.md` - This file

## When You Get the Green Light

1. **Ping me** (or whoever is helping)
2. **Run the scripts** in order
3. **Verify dashboards** show 2024 data
4. **Celebrate** 🎉

The moment billing works, we're ready to execute in minutes!
