# LeedHunter

[![CI](https://github.com/sinahmd/leedhunter/actions/workflows/ci.yml/badge.svg)](https://github.com/sinahmd/leedhunter/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered prospect research engine for finding qualified business opportunities.**

> **Status: Alpha** - This project is under active development and not yet production-ready.

---

## What LeedHunter Does

LeedHunter turns a prospecting objective into a deduplicated, evidence-backed set of qualified business opportunities:

```
User Intent → Search → Candidates → Entity Resolution → Evidence → Signals → Opportunities → Scoring → Leads
```

**Core capabilities:**
- Structured search query generation
- Candidate discovery from multiple sources
- Entity resolution and deduplication
- Evidence collection with provenance
- Signal detection and opportunity identification
- Deterministic lead scoring
- JSON/CSV export

## What LeedHunter Does NOT Do

- ❌ Scrape social media platforms
- ❌ Send automated outreach
- ❌ Store personal data without consent
- ❌ Guarantee result accuracy
- ❌ Replace human judgment

## Current Working Features

| Capability | Status |
|---|---|
| Fixture search | ✅ Working |
| Candidate normalization | ✅ Working |
| Entity resolution | ✅ Working |
| Real web search | ⚠️ Provider-dependent |
| Database persistence | ⚠️ Requires PostgreSQL |
| LLM enrichment | ⚠️ Optional/provider-dependent |
| CSV/JSON export | ✅ Working |
| Production readiness | ❌ Not yet |

## Known Limitations

- Fixture-only demo without real search providers
- Database persistence requires PostgreSQL setup
- LLM features require API keys
- No web UI
- Limited provider ecosystem

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/sinahmd/leedhunter.git
cd leedhunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Install
pip install -e ".[dev]"

# Verify installation
leedhunter doctor
```

### Run Demo (No External Services Required)

```bash
# Search using fixture data
leedhunter search "auto importers Mazandaran"

# Run research job
leedhunter hunt "Find auto importers in Mazandaran" --location "Mazandaran" --industry "Automotive"

# Export results
leedhunter export --objective "Find auto importers" --format json
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Search Provider
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture
LEEDHUNTER_SEARCH_TAVILY_API_KEY=
LEEDHUNTER_SEARCH_BRAVE_API_KEY=

# LLM (Optional)
LEEDHUNTER_LLM_ENABLED=false
LEEDHUNTER_LLM_PROVIDER=anthropic
LEEDHUNTER_LLM_API_KEY=

# Database (Optional)
LEEDHUNTER_DB_HOST=localhost
LEEDHUNTER_DB_PORT=5432
LEEDHUNTER_DB_USER=leedhunter
LEEDHUNTER_DB_PASSWORD=
LEEDHUNTER_DB_NAME=leedhunter
```

### Optional Dependencies

```bash
# LLM providers
pip install leedhunter[llm-anthropic]
pip install leedhunter[llm-openai]
pip install leedhunter[llm-all]
```

---

## CLI Commands

```bash
# Health check
leedhunter doctor

# Search
leedhunter search "query" --provider tavily

# Research
leedhunter hunt "objective" --location "city" --industry "sector"

# Export
leedhunter export --format json --output leads.json

# Score
leedhunter score "Business Name" --phone --email --website
```

---

## Architecture

```
CLI/API
    ↓
Application Layer (orchestration, providers)
    ↓
Domain Layer (business logic, models)
    ↑
Infrastructure Layer (database, cache, APIs)
```

See [Architecture Documentation](docs/architecture.md) for details.

---

## Development

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=leedhunter

# Specific tests
pytest tests/domain/ -v
```

### Code Quality

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Format
ruff format src/ tests/
```

See [Development Guide](docs/development.md) for details.

---

## Security & Privacy

- API keys are never logged or exported
- External content is treated as untrusted
- Prompt injection is prevented
- Users control their own data

See [Security Policy](SECURITY.md) for details.

---

## Data Provider Terms

Users must comply with provider terms of service:
- [Tavily Terms](https://tavily.com/terms)
- [Brave Search Terms](https://brave.com/search/api/tos/)
- [Anthropic Terms](https://www.anthropic.com/policies/terms)
- [OpenAI Terms](https://openai.com/policies/terms-of-use)

---

## Roadmap

See [Roadmap](docs/roadmap.md) for planned features.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
