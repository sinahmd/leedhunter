# LeedHunter Real Provider Test Guide

**Version:** 0.1.0  
**Last Updated:** August 15, 2026  
**Purpose:** Guide for testing real search providers after fixture mode passes

---

## Overview

This guide covers testing LeedHunter with real search providers (Tavily, Brave) after the fixture mode workflow has been validated. Real providers enable actual web search results instead of test data.

**Prerequisite:** All fixture mode tests must pass before testing real providers.

**Important:** This guide never asks you to paste API keys into chat. All configuration is done via local `.env` files or environment variables.

---

## Provider Credentials Required

### Tavily Search API

**Provider:** Tavily  
**Website:** https://tavily.com/  
**Free Tier:** 1,000 searches/month  
**API Key Variable:** `LEEDHUNTER_SEARCH_TAVILY_API_KEY`

**What You Need:**
- Tavily account (free signup)
- API key from Tavily dashboard

**Where to Get It:**
1. Go to https://tavily.com/
2. Click "Get Started" or "Sign Up"
3. Create account with email
4. Verify email address
5. Go to Dashboard → API Keys
6. Copy your API key (starts with `tvly-`)

### Brave Search API

**Provider:** Brave  
**Website:** https://brave.com/search/api/  
**Free Tier:** 2,000 queries/month  
**API Key Variable:** `LEEDHUNTER_SEARCH_BRAVE_API_KEY`

**What You Need:**
- Brave account (free signup)
- API key from Brave dashboard

**Where to Get It:**
1. Go to https://brave.com/search/api/
2. Click "Get Started"
3. Create Brave account
4. Go to Dashboard → API Keys
5. Click "Create API Key"
6. Copy your API key

---

## Configuration

### Option 1: Environment Variables (Recommended)

Set environment variables in your terminal:

**Linux/macOS:**
```bash
# For Tavily
export LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
export LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here

# For Brave
export LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
export LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_key_here
```

**Windows (PowerShell):**
```powershell
# For Tavily
$env:LEEDHUNTER_SEARCH_DEFAULT_PROVIDER="tavily"
$env:LEEDHUNTER_SEARCH_TAVILY_API_KEY="tvly-your_key_here"

# For Brave
$env:LEEDHUNTER_SEARCH_DEFAULT_PROVIDER="brave"
$env:LEEDHUNTER_SEARCH_BRAVE_API_KEY="BSA-your_key_here"
```

**Windows (CMD):**
```cmd
# For Tavily
set LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
set LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here

# For Brave
set LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
set LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_key_here
```

### Option 2: .env File (For Development)

Create or edit `.env` file in project root:

```env
# Search Provider Configuration
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here

# OR for Brave
# LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
# LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_key_here
```

**Security Note:** `.env` file is in `.gitignore` and will not be committed to version control.

---

## Verification Steps

### Step 1: Verify Variables Exist

Before running tests, verify your API key is configured:

**Linux/macOS:**
```bash
# Check Tavily
echo "Tavily key length: ${#LEEDHUNTER_SEARCH_TAVILY_API_KEY}"

# Check Brave
echo "Brave key length: ${#LEEDHUNTER_SEARCH_BRAVE_API_KEY}"
```

**Windows (PowerShell):**
```powershell
# Check Tavily
Write-Host "Tavily key length: $($env:LEEDHUNTER_SEARCH_TAVILY_API_KEY.Length)"

# Check Brave
Write-Host "Brave key length: $($env:LEEDHUNTER_SEARCH_BRAVE_API_KEY.Length)"
```

**Expected Result:** Key length should be > 0 (typically 20-40 characters)

### Step 2: Verify Key Format

**Tavily:** Should start with `tvly-`  
**Brave:** Should start with `BSA-` (older keys may not have prefix)

### Step 3: Run Doctor Check

```bash
leedhunter doctor
```

**Expected Output:**
- LLM Provider should show "Disabled (optional)" or "No API key (optional)"
- All critical checks should pass
- Database/Redis failures are expected and acceptable

---

## Smoke Tests

### Test 1: Basic Search (Tavily)

**Command:**
```bash
leedhunter search "auto importers in Tehran" --provider tavily --max-results 5
```

**Expected Behavior:**
- Exit code: 0
- Displays "Searching: auto importers in Tehran"
- Shows progress spinner
- Displays 5 or fewer results in table format
- Results are real web search results (not fixture data)
- Completes in < 10 seconds

**Budget Controls:**
- Max results: 5 (conservative)
- Timeout: 30 seconds (default)
- Single query only

**What to Look For:**
- ✅ Real business names (not test data)
- ✅ Real domains (not example.com)
- ✅ Real phone numbers (if available)
- ✅ Source shows "tavily" (not "fixture")

### Test 2: Basic Search (Brave)

**Command:**
```bash
leedhunter search "auto importers in Tehran" --provider brave --max-results 5
```

**Expected Behavior:**
- Same as Tavily test
- Source shows "brave" (not "fixture")

### Test 3: Research Job with Real Provider

**Command:**
```bash
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive --max-queries 2 --provider tavily
```

**Expected Behavior:**
- Exit code: 0
- Shows "Starting research: Find auto importers in Tehran"
- Generates 2 queries (limited by --max-queries)
- Executes queries with real provider
- Displays research summary with metrics
- Shows qualified leads (if any)
- Completes in < 30 seconds

**Budget Controls:**
- Max queries: 2 (very conservative)
- Min score: 50.0 (default)
- Provider: tavily or brave

**What to Look For:**
- ✅ Queries executed > 0
- ✅ Candidates found > 0 (may be 0 if no matches)
- ✅ Duration < 30 seconds
- ✅ No API errors
- ✅ No rate limit errors

### Test 4: Export with Real Provider

**Command:**
```bash
leedhunter export --format json --output real-test.json --objective "Find auto importers in Tehran" --max-queries 2
```

**Expected Behavior:**
- Runs research with real provider
- Exports results to JSON file
- Displays export summary

**Verification:**
```bash
# Check file exists
ls -lh real-test.json

# Validate JSON
python3 -m json.tool real-test.json > /dev/null && echo "✓ Valid JSON"

# Count leads
python3 -c "import json; data = json.load(open('real-test.json')); print(f'Leads: {len(data)}')"

# Clean up
rm real-test.json
```

---

## Budget and Safety Controls

### Built-in Budget Limits

LeedHunter enforces multiple budget controls to prevent runaway API usage:

| Control | Default | Description |
|---------|---------|-------------|
| `--max-queries` | 5 | Maximum search queries per research job |
| `--max-results` | 10 | Maximum results per search query |
| `--min-score` | 50.0 | Minimum lead score to qualify |
| Research timeout | 3600s | Maximum research duration |
| Candidate limit | 1000 | Maximum candidates per research job |

### Conservative Testing Parameters

For initial testing, use these conservative parameters:

```bash
# Minimal search test
leedhunter search "test query" --max-results 3

# Minimal research test
leedhunter hunt "test objective" --max-queries 1 --min-score 70

# Minimal export test
leedhunter export --format json --output test.json --objective "test"
```

### API Quota Awareness

**Tavily Free Tier:**
- 1,000 searches/month
- ~33 searches/day
- Rate limit: 100 requests/minute

**Brave Free Tier:**
- 2,000 queries/month
- ~66 queries/day
- Rate limit: 1 query/second

**Monitoring Usage:**
- Check Tavily dashboard: https://tavily.com/dashboard
- Check Brave dashboard: https://brave.com/search/api/dashboard

---

## Error Handling

### Common Errors and Solutions

#### Error 1: "API key not configured"

**Message:**
```
Error: Tavily API key not configured
```

**Cause:** Environment variable not set

**Solution:**
```bash
export LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here
```

#### Error 2: "Invalid API key"

**Message:**
```
Error: Authentication failed (401)
```

**Cause:** Invalid or expired API key

**Solution:**
1. Verify key is correct (no extra spaces)
2. Check key hasn't expired
3. Generate new key if needed

#### Error 3: "Rate limit exceeded"

**Message:**
```
Error: Rate limit exceeded (429)
```

**Cause:** Too many requests

**Solution:**
1. Wait 1 minute and retry
2. Reduce `--max-queries` and `--max-results`
3. Check quota on provider dashboard

#### Error 4: "Search timeout"

**Message:**
```
Error: Search timeout after 30 seconds
```

**Cause:** Network issue or provider slowdown

**Solution:**
1. Check internet connection
2. Try again (may be temporary)
3. Reduce `--max-results`

#### Error 5: "No results found"

**Message:**
```
No results found
```

**Cause:** Query didn't match any results

**Solution:**
1. Try different query terms
2. Remove location/industry filters
3. Check if provider is working: `leedhunter search "test"`

---

## Test Scenarios

### Scenario 1: Quick Validation (30 seconds)

**Goal:** Verify provider works without consuming much quota

**Commands:**
```bash
# Test 1: Simple search
leedhunter search "test" --max-results 1

# Test 2: Real query
leedhunter search "auto importers Tehran" --max-results 3

# Test 3: Research with minimal queries
leedhunter hunt "Find auto importers" --max-queries 1
```

**Total API Calls:** ~5 searches  
**Quota Used:** < 1% of free tier

### Scenario 2: Feature Validation (2 minutes)

**Goal:** Test all real-provider features

**Commands:**
```bash
# Test 1: Search with provider flag
leedhunter search "auto importers" --provider tavily --max-results 5

# Test 2: Research with location
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive --max-queries 2

# Test 3: Score a lead
leedhunter score "Test Business" --phone --email --website

# Test 4: Export JSON
leedhunter export --format json --output test.json --max-queries 1

# Test 5: Export CSV
leedhunter export --format csv --output test.csv --max-queries 1

# Clean up
rm test.json test.csv
```

**Total API Calls:** ~10-15 searches  
**Quota Used:** < 2% of free tier

### Scenario 3: Production Simulation (5 minutes)

**Goal:** Simulate production-like usage

**Commands:**
```bash
# Full research job
leedhunter hunt "Find qualified auto importers in Tehran and Mazandaran" \
  --location "Tehran, Mazandaran" \
  --industry "Automotive" \
  --max-queries 5 \
  --min-score 60 \
  --verbose

# Export results
leedhunter export --format json --output production-test.json \
  --objective "Find auto importers" \
  --location "Tehran" \
  --industry "Automotive"

# Verify output
python3 -c "import json; data = json.load(open('production-test.json')); print(f'Found {len(data)} leads')"

# Clean up
rm production-test.json
```

**Total API Calls:** ~25-30 searches  
**Quota Used:** < 3% of free tier

---

## Performance Expectations

### Response Times

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Single search | 2-5 seconds | Depends on query complexity |
| Research (2 queries) | 10-20 seconds | Includes processing time |
| Research (5 queries) | 20-40 seconds | May hit rate limits |
| Export | 5-10 seconds | Depends on research time |

### Rate Limiting

**Tavily:**
- 100 requests/minute
- Automatic retry with backoff
- No action needed from user

**Brave:**
- 1 query/second
- Automatic retry with backoff
- May slow down research jobs

### Quota Consumption

**Conservative Testing:**
- 10-20 searches per test session
- ~0.5-1% of monthly free tier
- Can test daily without quota concerns

**Moderate Testing:**
- 50-100 searches per day
- ~2-3% of monthly free tier
- Comfortable for regular development

**Heavy Testing:**
- 200+ searches per day
- ~10% of monthly free tier
- Monitor quota on dashboard

---

## Troubleshooting

### Issue: Provider Not Available

**Symptoms:**
```
Error: Provider 'tavily' not available
```

**Solution:**
1. Check API key is set: `echo $LEEDHUNTER_SEARCH_TAVILY_API_KEY`
2. Check key length > 0
3. Restart terminal after setting environment variables

### Issue: Fixture Data Returned Instead of Real Results

**Symptoms:**
- Source shows "fixture" instead of "tavily" or "brave"
- Results look like test data

**Solution:**
1. Verify provider is set: `export LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily`
2. Or use `--provider` flag: `leedhunter search "test" --provider tavily`

### Issue: Slow Performance

**Symptoms:**
- Searches take > 10 seconds
- Research jobs timeout

**Solution:**
1. Check internet connection
2. Reduce `--max-results` and `--max-queries`
3. Try at different time (provider may be under load)

### Issue: No Results for Valid Query

**Symptoms:**
- Query should return results but returns 0

**Solution:**
1. Try simpler query: `leedhunter search "test"`
2. Remove special characters from query
3. Check provider dashboard for API status

---

## Security Best Practices

### API Key Security

1. **Never commit API keys to version control**
   - `.env` is in `.gitignore`
   - Never paste keys in chat or documentation

2. **Use environment variables for production**
   - More secure than `.env` files
   - Can be managed by deployment tools

3. **Rotate keys regularly**
   - Generate new keys every 90 days
   - Revoke compromised keys immediately

4. **Use separate keys for development/production**
   - Development: Personal account with free tier
   - Production: Dedicated account with appropriate plan

### Network Security

1. **Use HTTPS only** (default in LeedHunter)
2. **Validate SSL certificates** (enabled by default)
3. **Use timeouts** (30 second default)
4. **Handle rate limits gracefully** (built-in retry logic)

---

## Next Steps

After real provider tests pass:

1. **Test with LLM integration** (optional)
   - Requires Anthropic or OpenAI API key
   - Enables AI-powered intent analysis and evidence extraction

2. **Test with database persistence** (optional)
   - Requires PostgreSQL setup
   - Enables cross-session entity resolution

3. **Deploy to production**
   - Set up production API keys
   - Configure monitoring and alerting
   - Set appropriate budget limits

---

## Summary

### Required Credentials

| Provider | Variable | Where to Get | Free Tier |
|----------|----------|--------------|-----------|
| Tavily | `LEEDHUNTER_SEARCH_TAVILY_API_KEY` | https://tavily.com/ | 1,000/month |
| Brave | `LEEDHUNTER_SEARCH_BRAVE_API_KEY` | https://brave.com/search/api/ | 2,000/month |

### Configuration

```env
# Choose one provider
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here

# OR
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_key_here
```

### Quick Test

```bash
# Verify configuration
leedhunter doctor

# Test search
leedhunter search "test query" --max-results 3

# Test research
leedhunter hunt "test objective" --max-queries 1
```

### Budget Safety

- Start with conservative limits (`--max-queries 1`, `--max-results 3`)
- Monitor quota on provider dashboard
- Use free tier for development/testing
- Upgrade only when needed for production

---

**Document Version:** 1.0  
**Last Updated:** August 15, 2026  
**Next Phase:** Phase 6 - Production-readiness verdict
