# LeedHunter Environment Prerequisites

**Version:** 0.1.0  
**Last Updated:** August 15, 2026

---

## Table of Contents

1. [Configuration Variables Reference](#1-configuration-variables-reference)
2. [No External Services Required Mode](#2-no-external-services-required-mode)
3. [Optional Database Configuration](#3-optional-database-configuration)
4. [Optional Redis Configuration](#4-optional-redis-configuration)
5. [Optional Search Provider Configuration](#5-optional-search-provider-configuration)
6. [Optional LLM Configuration](#6-optional-llm-configuration)
7. [Quick Start Guides](#7-quick-start-guides)

---

## 1. Configuration Variables Reference

### Application Settings

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_APP_NAME` | Application identification | Optional | `LeedHunter` | N/A - defaults provided |
| `LEEDHUNTER_VERSION` | Version tracking | Optional | `0.1.0` | N/A - defaults provided |
| `LEEDHUNTER_DEBUG` | Debug mode | Optional | `false` | N/A - set to `true` for development |
| `LEEDHUNTER_LOG_LEVEL` | Logging verbosity | Optional | `INFO` | N/A - options: DEBUG, INFO, WARNING, ERROR, CRITICAL |

### Database Configuration (PostgreSQL)

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_DB_HOST` | Database persistence | Optional | `localhost` | Your PostgreSQL server hostname |
| `LEEDHUNTER_DB_PORT` | Database persistence | Optional | `5432` | Your PostgreSQL server port |
| `LEEDHUNTER_DB_USER` | Database persistence | Optional | `leedhunter` | Create this user in PostgreSQL |
| `LEEDHUNTER_DB_PASSWORD` | Database persistence | Optional | `leedhunter` | Set when creating the user |
| `LEEDHUNTER_DB_NAME` | Database persistence | Optional | `leedhunter` | Create this database in PostgreSQL |

### Redis Configuration

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_REDIS_HOST` | Caching, rate limiting | Optional | `localhost` | Your Redis server hostname |
| `LEEDHUNTER_REDIS_PORT` | Caching, rate limiting | Optional | `6379` | Your Redis server port |
| `LEEDHUNTER_REDIS_PASSWORD` | Redis authentication | Optional | *(empty)* | Set if Redis requires auth |
| `LEEDHUNTER_REDIS_DB` | Redis database selection | Optional | `0` | Redis database number (0-15) |

### LLM Configuration

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_LLM_ENABLED` | LLM features | Optional | `false` | Set to `true` to enable LLM |
| `LEEDHUNTER_LLM_PROVIDER` | LLM provider selection | Optional | `anthropic` | Options: anthropic, openai, google, openai_compatible |
| `LEEDHUNTER_LLM_API_KEY` | LLM API access | Optional if enabled | *(empty)* | From your LLM provider dashboard |
| `LEEDHUNTER_LLM_BASE_URL` | Custom LLM endpoint | Optional | *(empty)* | For OpenAI-compatible providers |
| `LEEDHUNTER_LLM_MODEL` | Model selection | Optional | `claude-3-sonnet-20240229` | Model name from provider |
| `LEEDHUNTER_LLM_MAX_TOKENS` | Response length limit | Optional | `4096` | N/A - configure as needed |
| `LEEDHUNTER_LLM_TEMPERATURE` | Generation creativity | Optional | `0.2` | N/A - 0.0 to 1.0 |
| `LEEDHUNTER_LLM_TIMEOUT_SECONDS` | Request timeout | Optional | `60.0` | N/A - adjust for your needs |
| `LEEDHUNTER_LLM_MAX_CALLS_PER_RESEARCH` | Cost control | Optional | `10` | N/A - set based on budget |
| `LEEDHUNTER_LLM_MAX_COST_PER_RESEARCH` | Cost control | Optional | *(empty)* | N/A - set dollar limit |

### Search Configuration

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_SEARCH_DEFAULT_PROVIDER` | Search provider selection | Optional | `fixture` | Options: fixture, tavily, brave, web |
| `LEEDHUNTER_SEARCH_MAX_RESULTS_PER_QUERY` | Result limiting | Optional | `100` | N/A - adjust as needed |
| `LEEDHUNTER_SEARCH_TIMEOUT_SECONDS` | Search timeout | Optional | `30.0` | N/A - adjust for your needs |
| `LEEDHUNTER_SEARCH_TAVILY_API_KEY` | Tavily search | Required for Tavily | *(empty)* | Sign up at https://tavily.com/ |
| `LEEDHUNTER_SEARCH_BRAVE_API_KEY` | Brave search | Required for Brave | *(empty)* | Sign up at https://brave.com/search/api/ |

### Research Job Limits

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_RESEARCH_MAX_QUERIES` | Query budget | Optional | `100` | N/A - set based on needs |
| `LEEDHUNTER_RESEARCH_MAX_CANDIDATES` | Candidate budget | Optional | `1000` | N/A - set based on needs |
| `LEEDHUNTER_RESEARCH_MAX_PAGES_PER_ENTITY` | Page budget | Optional | `10` | N/A - set based on needs |
| `LEEDHUNTER_RESEARCH_MAX_RUNTIME_SECONDS` | Time budget | Optional | `3600` | N/A - 1 hour default |
| `LEEDHUNTER_RESEARCH_MAX_LLM_CALLS` | LLM budget | Optional | `100` | N/A - set based on needs |

### Sandbox Settings

| Variable | Required for | Required or Optional | Safe Example Value | Where User Obtains It |
|----------|--------------|---------------------|-------------------|----------------------|
| `LEEDHUNTER_SANDBOX_MAX_MEMORY_MB` | Memory limit | Optional | `1024` | N/A - adjust for your system |
| `LEEDHUNTER_SANDBOX_MAX_CPU_PERCENT` | CPU limit | Optional | `75.0` | N/A - adjust for your system |
| `LEEDHUNTER_SANDBOX_HEADLESS` | Browser mode | Optional | `true` | N/A - set to `false` for debugging |
| `LEEDHUNTER_SANDBOX_TIMEOUT` | Sandbox timeout | Optional | `60` | N/A - adjust as needed |

---

## 2. No External Services Required Mode

LeedHunter can operate completely offline with **zero external dependencies**. This mode is ideal for:

- First-time evaluation
- Development and testing
- Demos without internet access
- CI/CD pipelines

### Minimal Configuration

Create a `.env` file with:

```env
# Use fixture data (built-in test data)
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture

# Disable LLM features
LEEDHUNTER_LLM_ENABLED=false
```

### What Works in This Mode

| Feature | Status | Notes |
|---------|--------|-------|
| Fixture search | ✅ Working | Returns pre-defined test data |
| Candidate normalization | ✅ Working | Full normalization pipeline |
| Entity resolution | ✅ Working | Deterministic matching |
| Evidence collection | ✅ Working | From fixture data |
| Signal detection | ✅ Working | Deterministic signals |
| Opportunity identification | ✅ Working | Deterministic opportunities |
| Lead scoring | ✅ Working | Deterministic scoring algorithm |
| JSON export | ✅ Working | Full export capability |
| CSV export | ✅ Working | Full export capability |
| CLI commands | ✅ Working | All commands functional |
| Doctor health check | ✅ Working | Checks imports only |

### What Doesn't Work in This Mode

| Feature | Reason |
|---------|--------|
| Real web search | No search API configured |
| Database persistence | No PostgreSQL configured |
| Caching | No Redis configured |
| LLM enrichment | No LLM API configured |
| Entity management | Requires database |

### Commands to Test

```bash
# Install LeedHunter
pip install -e ".[dev]"

# Verify installation
leedhunter --version
leedhunter doctor

# Search using fixture data
leedhunter search "auto importers in Tehran"

# Run research job
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive

# Score a lead
leedhunter score "Example Automotive" --phone --email --website

# Export results
leedhunter export --format json --output test-output.json
leedhunter export --format csv --output test-output.csv
```

### Expected Output

All commands should:
- Exit with code 0
- Display Rich-formatted output
- Complete in under 5 seconds
- Not require internet access
- Not store data persistently

---

## 3. Optional Database Configuration

### What PostgreSQL Is Used For

| Use Case | Description |
|----------|-------------|
| Entity persistence | Store discovered entities permanently |
| Evidence storage | Store evidence with provenance |
| Lead management | Track lead status and history |
| Research history | Store completed research jobs |
| Deduplication | Cross-session entity resolution |

### PostgreSQL Variables Explained

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `LEEDHUNTER_DB_HOST` | PostgreSQL server hostname | `localhost` | Use `localhost` for local development |
| `LEEDHUNTER_DB_PORT` | PostgreSQL server port | `5432` | Standard PostgreSQL port |
| `LEEDHUNTER_DB_USER` | Database username | `leedhunter` | Create this user with appropriate permissions |
| `LEEDHUNTER_DB_PASSWORD` | Database password | *(empty)* | **Set a strong password in production** |
| `LEEDHUNTER_DB_NAME` | Database name | `leedhunter` | Create this database |

### Running PostgreSQL Locally

#### Option 1: Direct Installation

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create user and database
sudo -u postgres psql
CREATE USER leedhunter WITH PASSWORD 'your_secure_password';
CREATE DATABASE leedhunter OWNER leedhunter;
GRANT ALL PRIVILEGES ON DATABASE leedhunter TO leedhunter;
\q
```

**macOS (Homebrew):**
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Create user and database
createuser -s leedhunter
createdb leedhunter
psql -c "ALTER USER leedhunter WITH PASSWORD 'your_secure_password';"
```

**Windows:**
1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer and follow prompts
3. Remember the password you set for `postgres` user
4. Use pgAdmin or psql to create user and database

#### Option 2: Docker (Recommended for Development)

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: leedhunter-postgres
    environment:
      POSTGRES_USER: leedhunter
      POSTGRES_PASSWORD: leedhunter
      POSTGRES_DB: leedhunter
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U leedhunter"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

# Start PostgreSQL
docker compose up -d

# Verify it's running
docker compose ps
```

### Database Migrations

LeedHunter uses Alembic for database migrations.

#### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Check current migration status
alembic current

# View migration history
alembic history
```

#### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review generated migration
# Edit alembic/versions/xxxx_description.py if needed

# Apply migration
alembic upgrade head
```

### Can CLI Operate Without PostgreSQL?

**Yes, absolutely.** The CLI operates perfectly without PostgreSQL:

- All commands work in fixture mode
- Data is stored in-memory only
- Research results are not persisted
- No database errors - just no persistence

**When you need PostgreSQL:**
- You want to persist research results
- You want to track leads over time
- You want cross-session entity resolution
- You want to export historical data

### Configuration Example

```env
# .env file for PostgreSQL mode
LEEDHUNTER_DB_HOST=localhost
LEEDHUNTER_DB_PORT=5432
LEEDHUNTER_DB_USER=leedhunter
LEEDHUNTER_DB_PASSWORD=your_secure_password_here
LEEDHUNTER_DB_NAME=leedhunter

LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
LEEDHUNTER_LLM_ENABLED=false
```

---

## 4. Optional Redis Configuration

### What Redis Is Used For

| Use Case | Description | Current Status |
|----------|-------------|----------------|
| Search result caching | Cache API responses | ❌ Not implemented |
| Entity lookup caching | Speed up entity resolution | ❌ Not implemented |
| Rate limiting state | Track API rate limits | ❌ Not implemented |
| Provider throttling | Manage provider request rates | ❌ Not implemented |
| Research job queuing | Queue long-running jobs | ❌ Not implemented |
| Session state | Store temporary research state | ❌ Not implemented |

### Redis Variables Explained

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `LEEDHUNTER_REDIS_HOST` | Redis server hostname | `localhost` | Use `localhost` for local development |
| `LEEDHUNTER_REDIS_PORT` | Redis server port | `6379` | Standard Redis port |
| `LEEDHUNTER_REDIS_PASSWORD` | Redis authentication | *(empty)* | Set if Redis requires authentication |
| `LEEDHUNTER_REDIS_DB` | Redis database number | `0` | Use 0-15 for different namespaces |

### Is Redis Required for Current CLI?

**No.** Redis is **not required** for any current CLI functionality:

- All commands work without Redis
- No caching is implemented
- No rate limiting is implemented
- No job queuing is implemented

**When you need Redis:**
- When caching is implemented (future)
- When rate limiting is implemented (future)
- When job queuing is implemented (future)
- For high-throughput production use (future)

### Running Redis Locally

#### Option 1: Direct Installation

**Ubuntu/Debian:**
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

**macOS (Homebrew):**
```bash
# Install Redis
brew install redis

# Start Redis
brew services start redis

# Test connection
redis-cli ping
# Should return: PONG
```

**Windows:**
1. Download Redis for Windows from https://github.com/microsoftarchive/redis/releases
2. Run the installer
3. Redis will run as a Windows service

#### Option 2: Docker (Recommended for Development)

```bash
# Add to existing docker-compose.yml or create new one
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: leedhunter-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
EOF

# Start Redis
docker compose up -d

# Verify it's running
docker compose ps
redis-cli ping
```

### Configuration Example

```env
# .env file with Redis (for future use)
LEEDHUNTER_REDIS_HOST=localhost
LEEDHUNTER_REDIS_PORT=6379
LEEDHUNTER_REDIS_DB=0

LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
LEEDHUNTER_LLM_ENABLED=false
```

---

## 5. Optional Search Provider Configuration

### Provider Overview

| Provider | Type | API Key Required | Free Tier | Best For |
|----------|------|------------------|-----------|----------|
| `fixture` | Built-in | No | Unlimited | Testing, demos, development |
| `tavily` | Real search | Yes | 1,000 searches/month | Production web search |
| `brave` | Real search | Yes | 2,000 queries/month | Production web search |
| `web` | Real search | Yes | Varies | Custom implementations |

### Tavily Search Provider

**Website:** https://tavily.com/  
**Pricing:** Free tier with 1,000 searches/month  
**API Documentation:** https://docs.tavily.com/

#### Getting an API Key

1. Go to https://tavily.com/
2. Click "Get Started" or "Sign Up"
3. Create an account (email + password)
4. Verify your email address
5. Go to Dashboard → API Keys
6. Copy your API key (starts with `tvly-`)

#### Configuration

```env
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_api_key_here
```

#### Quota and Budget Behavior

| Tier | Monthly Searches | Rate Limit | Cost |
|------|------------------|------------|------|
| Free | 1,000 | 100/minute | $0 |
| Hobby | 5,000 | 100/minute | $20/month |
| Growth | 25,000 | 100/minute | $80/month |
| Enterprise | Custom | Custom | Contact sales |

**Budget Controls in LeedHunter:**
- `LEEDHUNTER_RESEARCH_MAX_QUERIES`: Limits queries per research job
- `LEEDHUNTER_RESEARCH_MAX_RUNTIME_SECONDS`: Limits research duration
- Provider-level rate limiting (built-in)

#### Payment Method

**Free tier:** No payment method required  
**Paid tiers:** Credit card required

#### Is Tavily Necessary for First Demo?

**No.** The `fixture` provider works perfectly for demos and first-time evaluation. Use Tavily when you need real web search results.

### Brave Search Provider

**Website:** https://brave.com/search/api/  
**Pricing:** Free tier with 2,000 queries/month  
**API Documentation:** https://brave.com/search/api/

#### Getting an API Key

1. Go to https://brave.com/search/api/
2. Click "Get Started"
3. Create a Brave account
4. Go to Dashboard → API Keys
5. Click "Create API Key"
6. Copy your API key

#### Configuration

```env
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_api_key_here
```

#### Quota and Budget Behavior

| Tier | Monthly Queries | Rate Limit | Cost |
|------|-----------------|------------|------|
| Free | 2,000 | 1 query/second | $0 |
| Base | 20,000 | 5 queries/second | $5/month |
| Pro | 200,000 | 20 queries/second | $50/month |
| Enterprise | Custom | Custom | Contact sales |

**Budget Controls in LeedHunter:**
- Same as Tavily (see above)

#### Payment Method

**Free tier:** No payment method required  
**Paid tiers:** Credit card required

#### Is Brave Necessary for First Demo?

**No.** Same as Tavily - use `fixture` provider for demos.

### Web Search Provider

**Status:** Not implemented (raises NotImplementedError)

This is a placeholder for custom web search implementations. Do not use in production.

### Provider Selection

LeedHunter automatically selects the provider based on:

1. **CLI `--provider` option** (highest priority)
2. **`LEEDHUNTER_SEARCH_DEFAULT_PROVIDER` environment variable**
3. **Available API keys** (if default is not set)
4. **Fallback to `fixture`** (if nothing else is available)

#### Example Configurations

**Fixture mode (no API keys):**
```env
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
```

**Tavily mode:**
```env
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here
```

**Brave mode:**
```env
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=brave
LEEDHUNTER_SEARCH_BRAVE_API_KEY=BSA-your_key_here
```

**Auto-detect (use first available):**
```env
# Don't set LEEDHUNTER_SEARCH_DEFAULT_PROVIDER
# LeedHunter will use the first provider with a valid API key
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here
```

---

## 6. Optional LLM Configuration

### What LLM Is Used For

| Use Case | Description | Current Status |
|----------|-------------|----------------|
| Intent analysis | Understand research objectives | ❌ Not implemented |
| Concept generation | Generate search concepts | ❌ Not implemented |
| Semantic evidence extraction | Extract insights from text | ❌ Not implemented |
| Entity comparison | Compare ambiguous entities | ❌ Not implemented |
| Opportunity identification | Identify business opportunities | ❌ Not implemented |
| Explanation generation | Generate human-readable explanations | ❌ Not implemented |

### LLM Variables Explained

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `LEEDHUNTER_LLM_ENABLED` | Enable LLM features | `false` | Set to `true` to use LLM |
| `LEEDHUNTER_LLM_PROVIDER` | LLM provider | `anthropic` | Options: anthropic, openai, google, openai_compatible |
| `LEEDHUNTER_LLM_API_KEY` | API key | *(empty)* | From your LLM provider |
| `LEEDHUNTER_LLM_BASE_URL` | Custom endpoint | *(empty)* | For OpenAI-compatible providers |
| `LEEDHUNTER_LLM_MODEL` | Model name | `claude-3-sonnet-20240229` | Model to use |
| `LEEDHUNTER_LLM_MAX_TOKENS` | Max response tokens | `4096` | Limit response length |
| `LEEDHUNTER_LLM_TEMPERATURE` | Generation temperature | `0.2` | 0.0 (deterministic) to 1.0 (creative) |
| `LEEDHUNTER_LLM_TIMEOUT_SECONDS` | Request timeout | `60.0` | Seconds to wait for response |
| `LEEDHUNTER_LLM_MAX_CALLS_PER_RESEARCH` | Call limit | `10` | Max LLM calls per research job |
| `LEEDHUNTER_LLM_MAX_COST_PER_RESEARCH` | Cost limit | *(empty)* | Dollar limit per research job |

### Supported Providers

#### Anthropic (Claude)

**Website:** https://www.anthropic.com/  
**Models:** Claude 3 Opus, Sonnet, Haiku  
**Pricing:** Pay-per-token

**Getting an API Key:**
1. Go to https://console.anthropic.com/
2. Create an account
3. Go to API Keys
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

**Configuration:**
```env
LEEDHUNTER_LLM_ENABLED=true
LEEDHUNTER_LLM_PROVIDER=anthropic
LEEDHUNTER_LLM_API_KEY=sk-ant-your_api_key_here
LEEDHUNTER_LLM_MODEL=claude-3-sonnet-20240229
```

**Required package:**
```bash
pip install leedhunter[llm-anthropic]
```

#### OpenAI (GPT)

**Website:** https://openai.com/  
**Models:** GPT-4, GPT-4 Turbo, GPT-3.5 Turbo  
**Pricing:** Pay-per-token

**Getting an API Key:**
1. Go to https://platform.openai.com/
2. Create an account
3. Go to API Keys
4. Create a new secret key
5. Copy the key (starts with `sk-`)

**Configuration:**
```env
LEEDHUNTER_LLM_ENABLED=true
LEEDHUNTER_LLM_PROVIDER=openai
LEEDHUNTER_LLM_API_KEY=sk-your_api_key_here
LEEDHUNTER_LLM_MODEL=gpt-4-turbo
```

**Required package:**
```bash
pip install leedhunter[llm-openai]
```

#### Google (Gemini)

**Website:** https://ai.google.dev/  
**Models:** Gemini Pro, Gemini Pro Vision  
**Pricing:** Free tier available

**Getting an API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Create a Google account (if needed)
3. Create API key
4. Copy the key

**Configuration:**
```env
LEEDHUNTER_LLM_ENABLED=true
LEEDHUNTER_LLM_PROVIDER=google
LEEDHUNTER_LLM_API_KEY=your_google_api_key_here
LEEDHUNTER_LLM_MODEL=gemini-pro
```

**Required package:**
```bash
pip install leedhunter[llm-google]
```

#### OpenAI-Compatible Providers

For providers that use OpenAI-compatible API format:

**Examples:**
- Ollama (local)
- LM Studio (local)
- vLLM (local)
- Together AI (cloud)
- Anyscale (cloud)

**Configuration:**
```env
LEEDHUNTER_LLM_ENABLED=true
LEEDHUNTER_LLM_PROVIDER=openai_compatible
LEEDHUNTER_LLM_BASE_URL=http://localhost:11434/v1
LEEDHUNTER_LLM_API_KEY=your_key_here
LEEDHUNTER_LLM_MODEL=llama2
```

### Does the Entire Product Work Without LLM?

**Yes, absolutely.** LLM is completely optional:

- All core features work without LLM
- Deterministic fallback for all operations
- No LLM errors or warnings
- Same output quality for fixture mode

**How the Deterministic Fallback Behaves:**

| Feature | With LLM | Without LLM |
|---------|----------|-------------|
| Intent analysis | AI-powered understanding | Keyword extraction |
| Concept generation | Semantic concepts | Term-based concepts |
| Evidence extraction | NLP extraction | Pattern matching |
| Entity comparison | Semantic similarity | Exact/deterministic matching |
| Opportunity identification | AI insights | Rule-based detection |
| Explanations | Natural language | Template-based |

### Is LLM Necessary for First Demo?

**No.** The deterministic fallback provides excellent results for:
- Testing
- Demos
- Development
- Most production use cases

Use LLM when you need:
- Better intent understanding
- Semantic evidence extraction
- More sophisticated opportunity identification

---

## 7. Quick Start Guides

### Guide 1: Zero-Configuration Demo (Recommended for First-Time Users)

**Goal:** Try LeedHunter without any setup

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/sinahmd/leedhunter.git
cd leedhunter

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# 3. Install
pip install -e ".[dev]"

# 4. Create minimal .env
echo 'LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
LEEDHUNTER_LLM_ENABLED=false' > .env

# 5. Verify installation
leedhunter --version
leedhunter doctor

# 6. Run demo workflow
leedhunter search "auto importers in Tehran"
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive
leedhunter score "Example Automotive" --phone --email --website
leedhunter export --format json --output demo-output.json
```

**What you get:**
- Working CLI with all commands
- Fixture-based search results
- Deterministic scoring
- JSON/CSV export
- No external dependencies

### Guide 2: Real Search Mode (For Production-Like Testing)

**Goal:** Test with real web search results

**Prerequisites:**
- Tavily or Brave API key (free tier available)

**Steps:**
```bash
# 1. Get API key (see Section 5)
# Tavily: https://tavily.com/ (1,000 free searches/month)
# Brave: https://brave.com/search/api/ (2,000 free queries/month)

# 2. Configure .env
cat > .env << 'EOF'
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_key_here
LEEDHUNTER_LLM_ENABLED=false
EOF

# 3. Test real search
leedhunter search "auto importers in Tehran" --provider tavily

# 4. Run research with real data
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive
```

**What you get:**
- Real web search results
- Actual business data
- Production-like experience
- API quota awareness

### Guide 3: Full Integration Mode (For Development)

**Goal:** Test with database persistence

**Prerequisites:**
- PostgreSQL 15+ running
- (Optional) Redis running

**Steps:**
```bash
# 1. Start PostgreSQL (see Section 3)
docker compose up -d  # If using Docker

# 2. Configure .env
cat > .env << 'EOF'
# Database
LEEDHUNTER_DB_HOST=localhost
LEEDHUNTER_DB_PORT=5432
LEEDHUNTER_DB_USER=leedhunter
LEEDHUNTER_DB_PASSWORD=leedhunter
LEEDHUNTER_DB_NAME=leedhunter

# Search (fixture for now)
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
LEEDHUNTER_LLM_ENABLED=false
EOF

# 3. Run migrations
alembic upgrade head

# 4. Test with persistence
leedhunter hunt "Find auto importers in Tehran" --location Tehran --industry Automotive
```

**What you get:**
- Persistent storage
- Cross-session data
- Entity management
- Research history

### Guide 4: Production Mode (For Real Use)

**Goal:** Full production setup

**Prerequisites:**
- PostgreSQL 15+ (production server)
- Redis 7+ (optional, for future caching)
- Tavily or Brave API key
- (Optional) LLM API key

**Steps:**
```bash
# 1. Set up production database
# Follow PostgreSQL production best practices
# - Strong passwords
# - SSL enabled
# - Connection pooling
# - Regular backups

# 2. Configure .env
cat > .env << 'EOF'
# Database
LEEDHUNTER_DB_HOST=your-db-host
LEEDHUNTER_DB_PORT=5432
LEEDHUNTER_DB_USER=leedhunter
LEEDHUNTER_DB_PASSWORD=your_secure_password_here
LEEDHUNTER_DB_NAME=leedhunter

# Redis (optional)
LEEDHUNTER_REDIS_HOST=your-redis-host
LEEDHUNTER_REDIS_PORT=6379

# Search
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=tvly-your_production_key

# LLM (optional)
LEEDHUNTER_LLM_ENABLED=true
LEEDHUNTER_LLM_PROVIDER=anthropic
LEEDHUNTER_LLM_API_KEY=sk-ant-your_production_key

# Production settings
LEEDHUNTER_DEBUG=false
LEEDHUNTER_LOG_LEVEL=WARNING
EOF

# 3. Run migrations
alembic upgrade head

# 4. Verify setup
leedhunter doctor

# 5. Run production research
leedhunter hunt "Your research objective" --location "Your Location" --industry "Your Industry"
```

**What you get:**
- Production-grade setup
- Real web search
- Persistent storage
- LLM-enhanced analysis
- Full observability

---

## Summary

### Minimum Requirements

**For Testing/Demo:**
- Python 3.10+
- No external services
- No API keys

**For Production-Like Testing:**
- Python 3.10+
- Tavily or Brave API key (free tier)
- No database required

**For Full Production:**
- Python 3.10+
- PostgreSQL 15+
- Tavily or Brave API key
- (Optional) Redis 7+
- (Optional) LLM API key

### Quick Reference

| Mode | Database | Redis | Search API | LLM API | Use Case |
|------|----------|-------|------------|---------|----------|
| Fixture | ❌ | ❌ | ❌ | ❌ | Testing, demos |
| Real Search | ❌ | ❌ | ✅ | ❌ | Production testing |
| Full Integration | ✅ | ❌ | ✅ | ❌ | Development |
| Production | ✅ | ✅ | ✅ | ✅ (optional) | Real use |

---

**Document Generated:** August 15, 2026  
**Version:** 1.0
