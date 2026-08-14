# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release engineering setup

## [0.1.0] - 2026-08-15

### Added
- Core domain models (Entity, Candidate, Evidence, Signal, Lead)
- Search query AST and builder
- Persian/Arabic Unicode normalization
- Entity resolution pipeline (exact, deterministic, fuzzy matching)
- Evidence collection and validation
- Signal detection
- Opportunity identification
- Lead qualification and scoring
- CLI with search, hunt, export commands
- Fixture search provider for testing
- Tavily search provider (optional)
- Brave search provider (optional)
- LLM abstraction layer (optional)
- Anthropic LLM provider adapter (optional)
- OpenAI LLM provider adapter (optional)
- Research orchestrator
- Export to JSON and CSV
- Research trace and observability
- Sandbox configuration
- Security hardening (credential redaction, input sanitization)
- PostgreSQL database models and migrations
- Redis caching support (optional)
- Comprehensive test suite

### Infrastructure
- Clean architecture (Domain, Application, Infrastructure layers)
- Pydantic settings management
- Alembic database migrations
- Typer CLI framework
- Rich terminal output

### Documentation
- Product specification
- Implementation plan
- User guide
- API reference

[Unreleased]: https://github.com/sinahmd/leedhunter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sinahmd/leedhunter/releases/tag/v0.1.0
