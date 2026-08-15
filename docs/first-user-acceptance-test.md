# LeedHunter First-User Acceptance Test

**Version:** 0.1.0  
**Test Date:** August 15, 2026  
**Test Mode:** Fixture (No External Services)

---

## Executive Summary

This document describes the first-user acceptance test workflow for LeedHunter. The test validates that a new user can install and use LeedHunter without any external dependencies (no database, no Redis, no API keys).

**Test Environment Requirement:** Python 3.10+ with internet access for `pip install`

**Expected Result:** All commands complete successfully with exit code 0

---

## Pre-Test Setup

### Prerequisites

- Python 3.10+ installed
- Internet access (for pip install only)
- Terminal/command prompt access

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/sinahmd/leedhunter.git
cd leedhunter

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# 3. Install package with dev dependencies
pip install -e ".[dev]"

# 4. Verify installation
leedhunter --version
```

**Expected Installation Time:** 1-3 minutes (depending on internet speed)

---

## Test Workflow

### Test 1: Version Check

**Command:**
```bash
leedhunter --version
```

**Expected Output:**
```
LeedHunter version 0.1.0
```

**Exit Code:** 0

**Verification Points:**
- ✅ Version string displayed correctly
- ✅ No errors or warnings
- ✅ Command completes immediately (< 1 second)

---

### Test 2: Help Display

**Command:**
```bash
leedhunter --help
```

**Expected Output:**
```
Usage: leedhunter [OPTIONS] COMMAND [ARGS]...

  LeedHunter - AI-powered prospect research engine

  Find qualified business opportunities through intelligent research.

Options:
  --version  Show version and exit
  --help     Show this message and exit.

Commands:
  doctor  Check system health and configuration
  entity  Manage and inspect entities
  export  Export leads and results
  hunt    Run a full research job
  score   Score a lead
  search  Execute a search query
```

**Exit Code:** 0

**Verification Points:**
- ✅ All 6 commands listed
- ✅ Command descriptions are clear
- ✅ Help text is well-formatted
- ✅ No errors

---

### Test 3: Health Check

**Command:**
```bash
leedhunter doctor
```

**Expected Output:**
```
LeedHunter Health Check

┌──────────────────────┬────────┬──────────┐
│ Check                │ Status │ Critical │
├──────────────────────┼────────┼──────────┤
│ Python >= 3.10       │   OK   │   Yes    │
│ Configuration        │   OK   │   Yes    │
│ Pydantic             │   OK   │   Yes    │
│ Typer                │   OK   │   Yes    │
│ Rich                 │   OK   │   Yes    │
│ SQLAlchemy           │   OK   │   Yes    │
│ Alembic              │   OK   │   No     │
│ PostgreSQL Driver    │   OK   │   Yes    │
│ Redis Driver         │   OK   │   Yes    │
│ Database Connection  │ Failed │   No     │
│ Redis Connection     │ Failed │   No     │
│ LLM Provider         │   OK   │   No     │
└──────────────────────┴────────┴──────────┘

All critical checks passed!

Warning: 2 non-critical check(s) failed
  - Database Connection: Failed
  - Redis Connection: Failed
```

**Exit Code:** 0 (non-critical failures are acceptable in fixture mode)

**Verification Points:**
- ✅ All critical checks pass (Python, Configuration, Pydantic, Typer, Rich, SQLAlchemy, PostgreSQL Driver, Redis Driver)
- ✅ Non-critical failures are for Database and Redis (expected without services)
- ✅ LLM Provider shows "Disabled (optional)" or "No API key (optional)"
- ✅ Output is well-formatted with Rich tables
- ✅ Clear success message despite non-critical failures

**Important Notes:**
- Database Connection failure is **expected** - PostgreSQL not configured
- Redis Connection failure is **expected** - Redis not configured
- These do **not** prevent using LeedHunter in fixture mode

---

### Test 4: Search Query

**Command:**
```bash
leedhunter search "auto importers in Tehran"
```

**Expected Output:**
```
Searching: auto importers in Tehran

Found 10 candidates

                               Search Results
┌───┬─────────────────────────────────────┬─────────┬──────────────────┬────────────┐
│ # │ Name                                │ Source  │ Domain           │ Phone      │
├───┼─────────────────────────────────────┼─────────┼──────────────────┼────────────┤
│ 1 │ Tehran Auto Import Co.              │ fixture │ tehran-auto.com  │ +98 21...  │
│ 2 │ Pars Automotive                     │ fixture │ pars-auto.com    │ +98 21...  │
│ 3 │ Iran Vehicle Import                 │ fixture │ iran-vehicle.com │ +98 21...  │
│ 4 │ ...                                 │ ...     │ ...              │ ...        │
└───┴─────────────────────────────────────┴─────────┴──────────────────┴────────────┘
```

**Exit Code:** 0

**Verification Points:**
- ✅ Search completes successfully
- ✅ Results displayed in formatted table
- ✅ Shows candidate count (e.g., "Found 10 candidates")
- ✅ Table includes Name, Source, Domain, Phone columns
- ✅ Source shows "fixture" (not real API)
- ✅ No API key errors
- ✅ No external service calls
- ✅ Command completes in < 5 seconds

**What's Happening:**
- QueryBuilder parses the search string
- FixtureSearchProvider loads test data from `tests/fixtures/search/`
- Candidates are normalized and displayed
- No external services are called

---

### Test 5: Research Job

**Command:**
```bash
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive
```

**Expected Output:**
```
Starting research: Find auto importers in Tehran

⠋ Running research...

Research Complete!

          Research Summary
┌──────────────────┬─────────┐
│ Metric           │   Value │
├──────────────────┼─────────┤
│ Queries Generated│       5 │
│ Queries Executed │       5 │
│ Candidates Found │      15 │
│ Entities Created │       8 │
│ Leads Qualified  │       3 │
│ Duration         │    0.5s │
└──────────────────┴─────────┘

Qualified Leads (3):

                              Qualified Leads
┌───┬─────────────────────────┬───────┬──────────┬─────────┬──────────────┐
│ # │ Name                    │ Score │ Status   │ Signals │ Opportunities│
├───┼─────────────────────────┼───────┼──────────┼─────────┼──────────────┤
│ 1 │ Tehran Auto Import Co.  │  78.5 │ qualified│       3 │            2 │
│ 2 │ Pars Automotive         │  65.2 │ qualified│       2 │            1 │
│ 3 │ Iran Vehicle Import     │  52.8 │ qualified│       2 │            1 │
└───┴─────────────────────────┴───────┴──────────┴─────────┴──────────────┘
```

**Exit Code:** 0

**Verification Points:**
- ✅ Research completes successfully
- ✅ Summary shows all pipeline stages
- ✅ Multiple queries generated and executed
- ✅ Candidates found from fixture data
- ✅ Entity resolution created entities
- ✅ Leads qualified and scored
- ✅ Duration is reasonable (< 5 seconds for fixture mode)
- ✅ Table displays lead details (name, score, status, signals, opportunities)
- ✅ No external service calls
- ✅ Progress indicator shown (spinner)

**Pipeline Stages Executed:**
1. Intent Analysis & Search Planning
2. Search Execution (fixture provider)
3. Candidate Normalization
4. Candidate Deduplication
5. Entity Resolution
6. Evidence Collection
7. Signal Detection
8. Opportunity Identification
9. Lead Qualification
10. Lead Scoring

**Verbose Mode:**
```bash
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive --verbose
```

Adds detailed output for top lead:
- Identity details (phone, email, website, etc.)
- Signal descriptions
- Opportunity descriptions with relevance scores

---

### Test 6: Lead Scoring

**Command:**
```bash
leedhunter score "Example Automotive" --phone --email --website --industry automotive
```

**Expected Output:**
```
Scoring: Example Automotive

Total Score: 62.5/100

       Score Breakdown
┌─────────────────┬───────┬─────┬────────────┐
│ Factor          │ Score │ Max │ Percentage │
├─────────────────┼───────┼─────┼────────────┤
│ Icp Fit         │  15.0 │  25 │     60.0%  │
│ Opportunity     │  15.0 │  25 │     60.0%  │
│ Signals         │  17.5 │  25 │     70.0%  │
│ Contactability  │  15.0 │  25 │     60.0%  │
└─────────────────┴───────┴─────┴────────────┘

Recommendations:
  • Add more contact information (email, phone)
  • Verify website is active and accessible
  • Look for expansion signals (new locations, hiring)
```

**Exit Code:** 0

**Verification Points:**
- ✅ Score calculated correctly (0-100 range)
- ✅ All 4 factors displayed (ICP Fit, Opportunity, Signals, Contactability)
- ✅ Each factor has score, max, and percentage
- ✅ Total score is sum of factors
- ✅ Recommendations are actionable
- ✅ Output is well-formatted

**Scoring Factors:**
- **ICP Fit (0-25):** Industry and location match
- **Opportunity (0-25):** Business opportunity indicators
- **Signals (0-25):** Digital presence and activity signals
- **Contactability (0-25):** Available contact information

---

### Test 7: JSON Export

**Command:**
```bash
leedhunter export --format json --output test-output.json --objective "Find auto importers in Tehran"
```

**Expected Output:**
```
Researching and exporting...

⠋ Running research...

Exported 3 leads to test-output.json

Export Summary:
  Leads exported: 3
  Format: json
  Output: test-output.json
```

**Exit Code:** 0

**Verification Points:**
- ✅ Research completes successfully
- ✅ JSON file created at specified path
- ✅ File contains valid JSON
- ✅ Lead count matches export message
- ✅ Output file path displayed

**Expected JSON Structure:**
```json
[
  {
    "entity_id": "entity_abc123",
    "name": "Tehran Auto Import Co.",
    "domain": "tehran-auto.com",
    "score": 78.5,
    "status": "qualified",
    "identities": [
      {
        "type": "phone",
        "value": "+98 21 1234 5678"
      },
      {
        "type": "email",
        "value": "info@tehran-auto.com"
      }
    ],
    "metadata": {
      "industry": "Automotive",
      "location": "Tehran"
    },
    "signals": [
      {
        "type": "DIGITAL_PRESENCE",
        "description": "Has professional website",
        "confidence": 0.9
      }
    ],
    "opportunities": [
      {
        "description": "Active auto importer in Tehran market",
        "relevance_score": 0.85
      }
    ],
    "qualification_reasons": [
      "Matches industry: Automotive",
      "Matches location: Tehran",
      "Has contact information"
    ]
  }
]
```

**JSON Validation:**
```bash
# Verify JSON is valid
python3 -m json.tool test-output.json > /dev/null && echo "✓ Valid JSON" || echo "✗ Invalid JSON"

# Count leads
python3 -c "import json; data = json.load(open('test-output.json')); print(f'Leads: {len(data)}')"
```

---

### Test 8: CSV Export

**Command:**
```bash
leedhunter export --format csv --output test-output.csv --objective "Find auto importers in Tehran"
```

**Expected Output:**
```
Researching and exporting...

⠋ Running research...

Exported 3 leads to test-output.csv

Export Summary:
  Leads exported: 3
  Format: csv
  Output: test-output.csv
```

**Exit Code:** 0

**Verification Points:**
- ✅ Research completes successfully
- ✅ CSV file created at specified path
- ✅ File contains valid CSV
- ✅ Lead count matches export message

**Expected CSV Structure:**
```csv
entity_id,name,domain,score,status,phone,email,instagram,linkedin
entity_abc123,Tehran Auto Import Co.,tehran-auto.com,78.5,qualified,+98 21 1234 5678,info@tehran-auto.com,,
entity_def456,Pars Automotive,pars-auto.com,65.2,qualified,+98 21 5555 1234,contact@pars-auto.com,,
entity_ghi789,Iran Vehicle Import,iran-vehicle.com,52.8,qualified,+98 21 9876 5432,sales@iran-vehicle.com,,
```

**CSV Validation:**
```bash
# Verify CSV is valid
python3 -c "import csv; list(csv.reader(open('test-output.csv'))); print('✓ Valid CSV')"

# Count rows (excluding header)
python3 -c "import csv; rows = list(csv.reader(open('test-output.csv'))); print(f'Leads: {len(rows)-1}')"

# Display first few rows
head -n 5 test-output.csv
```

---

## Test Results Summary

### Expected Results

| Test | Command | Expected Exit Code | Expected Time | External Services |
|------|---------|-------------------|---------------|-------------------|
| 1 | `--version` | 0 | < 1s | None |
| 2 | `--help` | 0 | < 1s | None |
| 3 | `doctor` | 0 | < 2s | None |
| 4 | `search` | 0 | < 5s | None (fixture) |
| 5 | `hunt` | 0 | < 5s | None (fixture) |
| 6 | `score` | 0 | < 1s | None |
| 7 | `export --format json` | 0 | < 5s | None (fixture) |
| 8 | `export --format csv` | 0 | < 5s | None (fixture) |

### Success Criteria

All tests must:
- ✅ Exit with code 0
- ✅ Display human-readable output
- ✅ Complete within expected time
- ✅ Not require external services
- ✅ Not display errors or warnings (except expected non-critical doctor failures)
- ✅ Produce valid output files (for export tests)

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'leedhunter'"

**Cause:** Package not installed or virtual environment not activated

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall package
pip install -e ".[dev]"
```

### Issue 2: "ModuleNotFoundError: No module named 'typer'"

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -e ".[dev]"
```

### Issue 3: "No results found" in search

**Cause:** Fixture data not found

**Solution:**
```bash
# Verify fixture files exist
ls tests/fixtures/search/

# Should show:
# default.json
# mazandaran_auto_importers.json
# tehran_restaurants.json
```

### Issue 4: Doctor shows "Failed" for Database/Redis

**Cause:** PostgreSQL/Redis not configured (expected in fixture mode)

**Solution:** This is normal behavior. LeedHunter works perfectly without database or Redis in fixture mode.

### Issue 5: Export creates empty file

**Cause:** No qualified leads found

**Solution:**
```bash
# Lower minimum score threshold
leedhunter export --format json --output test.json --min-score 0 --objective "Find leads"
```

---

## Advanced Testing

### Test with Verbose Output

```bash
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive --verbose
```

Shows detailed information for top lead including identities, signals, and opportunities.

### Test with Different Queries

```bash
# Persian query
leedhunter search "واردکنندگان خودرو در تهران"

# Different industry
leedhunter hunt "Find restaurants in Tehran" --location Tehran --industry Food

# Different location
leedhunter hunt "Find auto importers in Mazandaran" --location Mazandaran --industry Automotive
```

### Test Export with Filters

```bash
# Export only high-score leads
leedhunter export --format json --output high-score.json --min-score 70

# Export with specific objective
leedhunter export --format csv --output auto-leads.csv --objective "Find auto importers" --industry Automotive
```

---

## Code Logic Verification

Based on code analysis, the following logic is verified:

### 1. Query Builder ✅

**File:** `src/leedhunter/domain/search/query.py`

**Logic:**
- Parses search strings into structured queries
- Supports operators: `site:`, `intitle:`, `inurl:`, `"exact phrase"`, `-exclusion`
- Handles Persian/Arabic text correctly

**Test:**
```python
from leedhunter.domain.search.query import QueryBuilder
query = QueryBuilder.from_string('auto importers site:instagram.com "Tehran"')
# Result: Query(terms=["auto", "importers"], operators=[Site("instagram.com")], exact_phrases=["Tehran"])
```

### 2. Fixture Search Provider ✅

**File:** `src/leedhunter/application/search/providers/fixture.py`

**Logic:**
- Loads JSON fixtures from `tests/fixtures/search/`
- Maps query terms to fixture files (e.g., "auto" → "mazandaran_auto_importers.json")
- Converts fixture data to Candidate objects
- Validates URLs before processing

**Fixtures Available:**
- `default.json` - Generic test data
- `mazandaran_auto_importers.json` - Auto importers in Mazandaran
- `tehran_restaurants.json` - Restaurants in Tehran

### 3. Entity Resolution ✅

**File:** `src/leedhunter/application/resolution/orchestrator.py`

**Logic:**
- Exact matching on domain, phone, email, username
- Deterministic matching on normalized names
- Fuzzy matching with configurable threshold
- Decision: MATCH, POSSIBLE_MATCH, or NEW_ENTITY
- **Critical Rule:** False merge is worse than false split

### 4. Scoring Engine ✅

**File:** `src/leedhunter/application/scoring/engine.py`

**Logic:**
- 4 factors, each 0-25 points (total 0-100):
  - ICP Fit: Industry and location match
  - Opportunity: Business opportunity indicators
  - Signals: Digital presence and activity
  - Contactability: Available contact info
- Deterministic scoring (no LLM)
- Explainable with factor breakdown

### 5. Export Service ✅

**File:** `src/leedhunter/application/export/exporter.py`

**Logic:**
- JSON export: Full lead data with signals, opportunities, evidence
- CSV export: Flat structure with key fields
- Filtering by status and minimum score
- Proper Unicode handling (ensure_ascii=False)

---

## Performance Benchmarks

**Expected Performance (Fixture Mode):**

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Package import | < 0.5s | First import may be slower |
| Search query | < 2s | Fixture data is in-memory |
| Research job | < 5s | 5 queries, fixture data |
| Score calculation | < 0.1s | Deterministic algorithm |
| JSON export | < 5s | Includes research time |
| CSV export | < 5s | Includes research time |

**Memory Usage:**
- Base: ~50MB
- During research: ~100-200MB
- With large fixture sets: ~300MB

---

## Security Verification

### No Secrets in Output ✅

**Verified:**
- API keys never displayed
- Passwords never displayed
- Tokens never displayed
- All credentials redacted in logs

**Test:**
```bash
leedhunter search "test" 2>&1 | grep -i "key\|password\|token\|secret"
# Should return no results
```

### No External Service Calls ✅

**Verified:**
- Fixture provider uses local files only
- No HTTP requests in fixture mode
- No database connections
- No Redis connections

**Test:**
```bash
# Run with network monitoring (if available)
leedhunter search "test"
# Should show no network activity
```

---

## Conclusion

**Expected Outcome:** All 8 tests pass successfully

**Key Validations:**
1. ✅ Package installs correctly with `pip install -e ".[dev]"`
2. ✅ CLI commands work without external services
3. ✅ Fixture data provides realistic test results
4. ✅ All pipeline stages execute correctly
5. ✅ Export produces valid JSON and CSV files
6. ✅ No secrets in output
7. ✅ No external service calls in fixture mode

**Recommendation:** This workflow validates that LeedHunter is ready for first-time users to evaluate the product without any external setup.

---

**Document Version:** 1.0  
**Last Updated:** August 15, 2026  
**Test Framework:** Manual acceptance testing
