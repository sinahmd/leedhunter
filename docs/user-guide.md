# LeedHunter User Guide

## Overview

LeedHunter is an AI-powered prospect research engine that turns a prospecting objective into a deduplicated, evidence-backed set of qualified business opportunities.

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd leedhunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

### 1. Health Check

Verify your installation:

```bash
leedhunter doctor
```

This checks:
- Python version
- Required packages
- Database connection
- Redis connection

### 2. Search for Leads

Search for business leads:

```bash
leedhunter search "auto importers mazandaran"
```

### 3. Run Research Job

Run a full research job:

```bash
leedhunter hunt "Find auto importers in Mazandaran" --location "Mazandaran" --industry "Automotive"
```

### 4. Score a Lead

Calculate lead score:

```bash
leedhunter score "Test Business" --phone --email --website --industry automotive
```

## CLI Commands

### `leedhunter doctor`

Check system health and configuration.

```bash
leedhunter doctor
```

### `leedhunter search`

Execute a search query.

```bash
leedhunter search <query> [options]

Options:
  --provider, -p    Search provider to use
  --max-results, -n Maximum number of results
  --verbose, -v     Show detailed output
```

### `leedhunter hunt`

Run a full research job.

```bash
leedhunter hunt <objective> [options]

Options:
  --location, -l    Target location
  --industry, -i    Target industry
  --max-queries, -q Maximum queries to generate
  --verbose, -v     Show detailed output
```

### `leedhunter score`

Score a lead.

```bash
leedhunter score <entity-name> [options]

Options:
  --phone      Entity has phone
  --email      Entity has email
  --website    Entity has website
  --industry   Industry
  --location   Location
```

### `leedhunter export`

Export leads and results.

```bash
leedhunter export [options]

Options:
  --format, -f    Export format (json, csv)
  --output, -o    Output file path
  --status, -s    Filter by status
```

## Configuration

LeedHunter uses environment variables for configuration. Copy `.env.example` to `.env` and update:

```env
# Database
LEEDHUNTER_DB_HOST=localhost
LEEDHUNTER_DB_PORT=5432
LEEDHUNTER_DB_USER=leedhunter
LEEDHUNTER_DB_PASSWORD=your_password
LEEDHUNTER_DB_NAME=leedhunter

# Redis
LEEDHUNTER_REDIS_HOST=localhost
LEEDHUNTER_REDIS_PORT=6379

# LLM (optional)
LEEDHUNTER_LLM_PROVIDER=anthropic
LEEDHUNTER_LLM_API_KEY=your_api_key

# Sandbox
LEEDHUNTER_SANDBOX_MAX_MEMORY_MB=1024
LEEDHUNTER_SANDBOX_TIMEOUT=60
```

## Persian/Arabic Support

LeedHunter fully supports Persian and Arabic text:

- Automatic normalization (ي→ی, ك→ک)
- Persian digit conversion
- ZWNJ handling
- Mixed-script support

Example:

```bash
leedhunter search "واردکنندگان خودرو در مازندران"
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U leedhunter -d leedhunter -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping
```

### Missing Dependencies

```bash
pip install -e ".[dev]"
```

## Support

For issues and questions:
- Check the documentation
- Review test files for examples
- Open an issue on GitHub
