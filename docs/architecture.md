# LeedHunter Architecture

## Overview

LeedHunter follows clean architecture with clear separation of concerns.

```
┌─────────────────────────────────────────────┐
│                  CLI/API                     │
├─────────────────────────────────────────────┤
│              Application Layer              │
│  (Use cases, orchestration, providers)       │
├─────────────────────────────────────────────┤
│                Domain Layer                  │
│  (Business logic, models, services)          │
├─────────────────────────────────────────────┤
│            Infrastructure Layer              │
│  (Database, cache, external APIs)            │
└─────────────────────────────────────────────┘
```

## Layers

### Domain Layer

Pure business logic with no external dependencies.

**Key components:**
- Models: Entity, Candidate, Evidence, Signal, Lead
- Services: EntityResolution, Scoring, Qualification
- Query: Search query AST and builder
- Normalization: Persian/Unicode text processing

### Application Layer

Orchestration and use cases.

**Key components:**
- Research Orchestrator: End-to-end research pipeline
- Search Providers: Tavily, Brave, Fixture
- LLM Providers: Anthropic, OpenAI, Mock
- Pipeline: Candidate normalization and extraction

### Infrastructure Layer

External integrations.

**Key components:**
- Database: PostgreSQL via SQLAlchemy
- Cache: Redis (optional)
- Security: Credential redaction, input sanitization

## Dependency Direction

```
CLI → Application → Domain ← Infrastructure
```

Domain layer never depends on:
- FastAPI, Typer, SQLAlchemy
- Redis, Celery
- External API SDKs
- Browser implementations
