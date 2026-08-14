# Development Guide

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ (optional for development)
- Redis 7+ (optional for development)

### Setup

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Configure environment
5. Run tests

## Project Structure

```
leedhunter/
├── src/leedhunter/
│   ├── cli/              # Command-line interface
│   ├── domain/           # Business logic
│   ├── application/      # Use cases
│   └── infrastructure/   # External integrations
├── tests/
├── docs/
└── alembic/              # Database migrations
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow the coding standards:
- Type hints
- Docstrings
- Clean architecture

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Check Code Quality

```bash
ruff check src/ tests/
mypy src/
```

### 5. Submit PR

- Clear description
- Tests included
- Documentation updated

## Testing

### Unit Tests

```bash
pytest tests/domain/ -v
pytest tests/application/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### Coverage

```bash
pytest --cov=leedhunter --cov-report=html
```

## Debugging

### Enable Debug Logging

```env
LEEDHUNTER_DEBUG=true
LEEDHUNTER_LOG_LEVEL=DEBUG
```

### Use Verbose CLI

```bash
leedhunter hunt "objective" --verbose
```

## Common Tasks

### Add New Domain Model

1. Create model in `src/leedhunter/domain/models.py`
2. Add validation
3. Write tests
4. Update exports

### Add New Provider

1. Create provider in `src/leedhunter/application/search/providers/`
2. Implement `SearchProvider` interface
3. Add configuration
4. Write tests
5. Update CLI

### Add Database Migration

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Troubleshooting

### Import Errors

Ensure `src/` is in Python path:
```bash
pip install -e .
```

### Database Connection

Check PostgreSQL is running:
```bash
pg_isready
```

### Test Failures

Run with verbose output:
```bash
pytest -v --tb=long
```
