# LeedHunter Roadmap

## Current Status: Alpha

LeedHunter is in active development. The architecture is established, but the product is not yet production-ready.

## Completed Work

### Phase 0-1: Foundation ✅
- Repository structure
- Domain models
- Configuration system
- CLI framework

### Phase 2-3: Infrastructure ✅
- PostgreSQL database
- Alembic migrations
- Persian/Unicode normalization

### Phase 4-8: Search & Candidates ✅
- Query AST and builder
- Search planner
- Candidate pipeline
- Entity resolution

### Phase 9-12: Core Features ✅
- Evidence engine
- Signal detection
- Opportunity identification
- Scoring and qualification

### Phase 13-15: Providers ✅
- Search provider interface
- Tavily provider
- Brave provider
- LLM abstraction

### Phase 16-21: Advanced Features ✅
- Social discovery
- Enrichment
- Research orchestration
- Export (JSON/CSV)
- Research trace

### Phase 22-25: Production Readiness ✅
- CLI commands
- Security hardening
- Sandbox configuration
- End-to-end benchmarks

## Current Work

### Phase 26: Release Engineering 🔄
- [x] LICENSE
- [x] CONTRIBUTING.md
- [x] SECURITY.md
- [x] CI/CD workflows
- [ ] Package validation
- [ ] PyPI preparation

## Planned Work

### Phase 27: Database Integration
- [ ] Wire repositories to orchestrator
- [ ] Persist entities and leads
- [ ] Entity history tracking

### Phase 28: Real Provider Integration
- [ ] Production Tavily integration
- [ ] Production Brave integration
- [ ] Provider health monitoring

### Phase 29: LLM Integration
- [ ] Anthropic adapter production testing
- [ ] OpenAI adapter production testing
- [ ] Intent analysis with LLM
- [ ] Entity comparison with LLM

### Phase 30: Advanced Features
- [ ] Research resumability
- [ ] Background job processing
- [ ] Web UI dashboard
- [ ] API endpoints

### Phase 31: Production Hardening
- [ ] Performance optimization
- [ ] Load testing
- [ ] Security audit
- [ ] Documentation review

### Phase 32: Open Source Release
- [ ] PyPI publication
- [ ] GitHub release
- [ ] Community building
- [ ] Provider ecosystem

## Long-term Vision

### Search Engine
- Multiple search providers
- Custom search strategies
- Result quality scoring

### Entity Resolution
- ML-based matching
- Cross-language matching
- Real-time resolution

### Research Automation
- Scheduled research jobs
- Automated lead scoring
- CRM integration
