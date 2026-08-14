# Contributing to LeedHunter

Thank you for your interest in contributing to LeedHunter! This guide will help you get started.

## Project Status

LeedHunter is currently in **Alpha** stage. The architecture is established, but the product is not yet production-ready.

## Supported Environments

- **Python:** 3.10, 3.11, 3.12
- **Operating Systems:** Linux (Ubuntu 22.04+), Windows 10/11
- **Databases:** PostgreSQL 15+ (optional for development)
- **Cache:** Redis 7+ (optional for development)

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sinahmd/leedhunter.git
cd leedhunter
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -e .

# Development dependencies
pip install -e ".[dev]"

# Optional: LLM provider dependencies
pip install -e ".[llm-anthropic]"
pip install -e ".[llm-openai]"
pip install -e ".[llm-all]"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=leedhunter

# Run specific test file
pytest tests/domain/test_models.py
```

### 6. Code Quality Checks

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Format code
ruff format src/ tests/
```

## Code Architecture

LeedHunter follows clean architecture:

```
CLI/API
    ↓
Application Layer (use cases)
    ↓
Domain Layer (business logic)
    ↑
Infrastructure Layer (external integrations)
```

**Key Principles:**
- Domain layer has no external dependencies
- Use protocols/interfaces for abstraction
- All LLM output must be schema-validated
- Persian/Unicode is first-class
- False merge is worse than false split

## Adding a New Search Provider

1. Create `src/leedhunter/application/search/providers/your_provider.py`
2. Implement `SearchProvider` protocol
3. Add configuration to `config.py`
4. Add tests in `tests/providers/`
5. Update CLI provider selection
6. Document in `docs/provider-guide.md`

## Adding a Database Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Review the generated migration
# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

## Commit Style

Use conventional commits:

```
type(scope): description

Examples:
feat(search): add Brave search provider
fix(entity): prevent false merges
docs(readme): update installation instructions
test(llm): add Anthropic adapter tests
```

## Pull Request Process

1. Create a branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit PR with clear description
7. Wait for CI checks to pass
8. Request review from maintainers

## Required CI Checks

- All tests pass on Linux and Windows
- Python 3.10, 3.11, 3.12
- Ruff linting passes
- mypy type checking passes
- Package builds successfully
- `twine check` passes

## Test Expectations

- All new code should have tests
- Tests must pass without external API keys
- Use mock providers for external services
- Test Persian/Unicode handling
- Test error cases

## Documentation Expectations

- Update README for user-facing changes
- Add docstrings to public functions
- Update API reference for new modules
- Add examples for new features

## How Maintainers Review

1. Code quality and style
2. Test coverage
3. Architecture compliance
4. Documentation completeness
5. Security considerations

## Requesting Help

- Open a GitHub issue for bugs
- Use discussions for questions
- Tag maintainers for urgent issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
