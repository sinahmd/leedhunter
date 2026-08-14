# LeedHunter Implementation Plan v0.1

## Phase Order

```
Phase 0:  Repository Bootstrap          ✅ COMPLETE
Phase 1:  Domain Foundation             ✅ COMPLETE
Phase 2:  Database Layer                ← NEXT
Phase 3:  Persian / Unicode Infrastructure
Phase 4:  Search Domain / Query AST
Phase 5:  Search Planner
Phase 6:  Search Provider Interface
Phase 7:  Fixture Search Provider
Phase 8:  Candidate Pipeline
Phase 9:  Entity Resolution
Phase 10: Entity Graph
Phase 11: Evidence Engine
Phase 12: LLM Abstraction
Phase 13: Agent-Reach Adapter
Phase 14: Real Web Search
Phase 15: Search Quality Loop
Phase 16: Social Discovery
Phase 17: Enrichment
Phase 18: Signals
Phase 19: Opportunity Engine
Phase 20: Qualification
Phase 21: Scoring
Phase 22: CLI
Phase 23: JSON / CSV
Phase 24: Research Trace
Phase 25: Sandbox
Phase 26: End-to-End Benchmark
Phase 27: Hardening
Phase 28: Documentation
```

---

## Phase 0: Repository Bootstrap ✅

**Objective:** Establish project structure, dependencies, and basic CLI.

**Deliverables:**
- [x] Project directory structure (clean architecture)
- [x] pyproject.toml with dependencies
- [x] Configuration system (pydantic-settings)
- [x] CLI foundation (Typer)
- [x] Doctor command (health checks)
- [x] Initial test suite
- [x] Domain model stubs

**Success Criteria:**
- `leedhunter doctor` works
- `pytest` passes

---

## Phase 1: Domain Foundation ✅

**Objective:** Implement core domain models, services, and business logic.

**Deliverables:**
- [x] Enhanced domain models with validation
- [x] Entity Resolution Service
- [x] Scoring Service
- [x] Qualification Service
- [x] Domain Event System
- [x] Persian/Unicode Normalization
- [x] Domain service tests

**Key Components:**
- Entity resolution pipeline (exact → deterministic → fuzzy → semantic)
- Deterministic scoring from explicit factors
- Lead qualification with explainable reasons
- Event system for observability
- Persian text normalization (ي→ی, ك→ک, digits, ZWNJ)

---

## Phase 2: Database Layer ← CURRENT

**Objective:** Implement PostgreSQL persistence with SQLAlchemy and Alembic.

**Deliverables:**
- [ ] Database models (SQLAlchemy ORM)
- [ ] Alembic migrations setup
- [ ] Repository implementations
- [ ] Database connection management
- [ ] Initial schema migration
- [ ] Repository tests

**Key Components:**
- Entity table with uniqueness constraints
- Identity table (one-to-many with Entity)
- Evidence table
- Signal table
- Lead table
- Proper indexes for search performance

**Technical Requirements:**
- Use async SQLAlchemy with asyncpg
- Database-level constraints for uniqueness
- Alembic for all schema changes
- Connection pooling configuration

---

## Phase 3: Persian / Unicode Infrastructure

**Objective:** Enhance Persian support with database-level normalization.

**Deliverables:**
- [ ] Database collation settings for Persian
- [ ] Normalized columns for search
- [ ] Full-text search support (Persian)
- [ ] Normalization in repository layer
- [ ] Tests with Persian data

---

## Phase 4: Search Domain / Query AST

**Objective:** Implement structured query representation.

**Deliverables:**
- [ ] Query AST (Abstract Syntax Tree)
- [ ] Query builder with operators
- [ ] Query validation
- [ ] Query rendering to string
- [ ] Support for Persian/Arabic in queries

**Operators:**
- `site:`
- `intitle:`
- `inurl:`
- `"exact phrase"`
- `OR`
- `-` (exclusion)

---

## Phase 5: Search Planner

**Objective:** Generate search strategies from intent.

**Deliverables:**
- [ ] Intent analyzer
- [ ] Concept extractor
- [ ] Query family generator
- [ ] Search strategy planner
- [ ] Tests with sample intents

---

## Phase 6: Search Provider Interface

**Objective:** Define and implement search provider abstraction.

**Deliverables:**
- [ ] SearchProvider protocol
- [ ] Provider registry
- [ ] Provider selection logic
- [ ] Rate limiting per provider
- [ ] Provider health checks

---

## Phase 7: Fixture Search Provider

**Objective:** Create test fixtures for realistic search results.

**Deliverables:**
- [ ] FixtureProvider implementation
- [ ] Sample fixture files (JSON)
- [ ] Realistic noisy results:
  - Duplicates
  - Different URLs
  - Different names
  - Persian/English variants
  - Irrelevant businesses
  - Same company on multiple platforms

**Fixture Examples:**
```
tests/fixtures/search/mazandaran_auto_importers.json
tests/fixtures/search/tehran_restaurants.json
```

---

## Phase 8: Candidate Pipeline

**Objective:** Process search results into candidates.

**Deliverables:**
- [ ] Result normalizer
- [ ] Candidate extractor
- [ ] Identity extractor
- [ ] Candidate deduplication
- [ ] Provenance tracking

---

## Phase 9: Entity Resolution

**Objective:** Implement full entity resolution pipeline.

**Deliverables:**
- [ ] Resolution orchestrator
- [ ] Exact matcher
- [ ] Deterministic matcher
- [ ] Fuzzy matcher
- [ ] Semantic matcher (LLM)
- [ ] Match explainability
- [ ] Entity pair evaluation dataset

**Evaluation Dataset:**
```json
{
  "candidate_a": "...",
  "candidate_b": "...",
  "label": "SAME"
}
```

Labels: SAME, DIFFERENT, AMBIGUOUS

Track: precision, recall, F1, false merge rate, false split rate

---

## Phase 10: Entity Graph

**Objective:** Build and maintain entity graph.

**Deliverables:**
- [ ] Entity graph structure
- [ ] Identity linking
- [ ] Graph traversal
- [ ] Merge/split operations
- [ ] Graph consistency checks

---

## Phase 11: Evidence Engine

**Objective:** Collect and manage evidence for entities.

**Deliverables:**
- [ ] Evidence collector
- [ ] Evidence validator
- [ ] Confidence scoring
- [ ] Source attribution
- [ ] Evidence deduplication

---

## Phase 12: LLM Abstraction

**Objective:** Create LLM provider abstraction.

**Deliverables:**
- [ ] LLMProvider protocol
- [ ] Anthropic adapter
- [ ] OpenAI adapter
- [ ] Google adapter
- [ ] Response validation
- [ ] Token counting
- [ ] Cost tracking

---

## Phase 13: Agent-Reach Adapter

**Objective:** Integrate Agent-Reach as provider.

**Deliverables:**
- [ ] AgentReachProvider implementation
- [ ] Authentication handling
- [ ] Rate limiting
- [ ] Error handling
- [ ] Fallback logic

---

## Phase 14: Real Web Search

**Objective:** Implement real web search providers.

**Deliverables:**
- [ ] Google Search provider
- [ ] Bing Search provider
- [ ] Result parsing
- [ ] Rate limiting
- [ ] Error handling

---

## Phase 15: Search Quality Loop

**Objective:** Improve search quality over time.

**Deliverables:**
- [ ] Query effectiveness tracking
- [ ] Result quality metrics
- [ ] Query refinement
- [ ] A/B testing framework

---

## Phase 16: Social Discovery

**Objective:** Discover social media profiles.

**Deliverables:**
- [ ] Instagram discovery
- [ ] LinkedIn discovery
- [ ] Profile extraction
- [ ] Cross-platform linking

---

## Phase 17: Enrichment

**Objective:** Enrich entities with additional data.

**Deliverables:**
- [ ] Website scraping
- [ ] Profile enrichment
- [ ] Contact extraction
- [ ] Business info extraction

---

## Phase 18: Signals

**Objective:** Identify business signals from evidence.

**Deliverables:**
- [ ] Signal detector
- [ ] Signal types implementation
- [ ] Confidence scoring
- [ ] Signal aggregation

---

## Phase 19: Opportunity Engine

**Objective:** Identify business opportunities from signals.

**Deliverables:**
- [ ] Opportunity detector
- [ ] Relevance scoring
- [ ] Opportunity ranking
- [ ] Opportunity explanation

---

## Phase 20: Qualification

**Objective:** Qualify leads based on signals and opportunities.

**Deliverables:**
- [ ] Qualification rules engine
- [ ] Threshold management
- [ ] Qualification reasons
- [ ] Batch qualification

---

## Phase 21: Scoring

**Objective:** Calculate deterministic lead scores.

**Deliverables:**
- [ ] ICP Fit calculator
- [ ] Opportunity calculator
- [ ] Signal calculator
- [ ] Contactability calculator
- [ ] Score explanation generator

---

## Phase 22: CLI

**Objective:** Complete CLI implementation.

**Deliverables:**
- [ ] Full command implementations
- [ ] Progress indicators
- [ ] Formatted output
- [ ] Verbose mode
- [ ] Error handling

---

## Phase 23: JSON / CSV

**Objective:** Export functionality.

**Deliverables:**
- [ ] JSON export
- [ ] CSV export
- [ ] Custom field selection
- [ ] Filtering options

---

## Phase 24: Research Trace

**Objective:** Full observability for research jobs.

**Deliverables:**
- [ ] Trace storage
- [ ] Trace visualization
- [ ] Performance metrics
- [ ] Debug information

---

## Phase 25: Sandbox

**Objective:** Isolate browser/provider execution.

**Deliverables:**
- [ ] Sandbox configuration
- [ ] Docker integration
- [ ] Resource limits
- [ ] Cleanup procedures

---

## Phase 26: End-to-End Benchmark

**Objective:** Comprehensive testing framework.

**Deliverables:**
- [ ] Benchmark scenarios
- [ ] Performance metrics
- [ ] Quality metrics
- [ ] Regression tests

---

## Phase 27: Hardening

**Objective:** Production readiness.

**Deliverables:**
- [ ] Security audit
- [ ] Performance optimization
- [ ] Error handling review
- [ ] Documentation review

---

## Phase 28: Documentation

**Objective:** Complete documentation.

**Deliverables:**
- [ ] API documentation
- [ ] User guide
- [ ] Developer guide
- [ ] Deployment guide

---

## Dependencies

```
Phase 0 (Bootstrap)
    ↓
Phase 1 (Domain Foundation)
    ↓
Phase 2 (Database Layer)
    ↓
Phase 3 (Persian Infrastructure)
    ↓
Phase 4 (Search Domain)
    ↓
Phase 5 (Search Planner)
    ↓
Phase 6 (Search Provider Interface)
    ↓
Phase 7 (Fixture Provider)
    ↓
Phase 8 (Candidate Pipeline)
    ↓
Phase 9 (Entity Resolution)
    ↓
Phase 10 (Entity Graph)
    ↓
Phase 11 (Evidence Engine)
    ↓
Phase 12 (LLM Abstraction)
    ↓
Phase 13-14 (External Providers)
    ↓
Phase 15-17 (Search & Enrichment)
    ↓
Phase 18-21 (Signals, Opportunities, Scoring)
    ↓
Phase 22-24 (CLI, Export, Tracing)
    ↓
Phase 25-28 (Sandbox, Benchmarking, Docs)
```

---

## Success Metrics

### Entity Resolution
- Precision: >95%
- Recall: >90%
- F1 Score: >92%
- False Merge Rate: <2%
- False Split Rate: <5%

### Search Quality
- Relevant results in top 10: >80%
- Entity coverage: >70%
- Duplicate detection: >95%

### Performance
- Research job (100 entities): <30 minutes
- Entity resolution (1000 candidates): <5 minutes
- Export (1000 leads): <10 seconds

---

## Risk Mitigation

### Technical Risks
1. **Provider rate limits** → Implement backoff, caching, multiple providers
2. **Entity resolution accuracy** → Conservative matching, human review for POSSIBLE_MATCH
3. **Persian text handling** → Comprehensive normalization, test with real data
4. **LLM reliability** → Schema validation, fallback to deterministic logic

### Business Risks
1. **Provider availability** → Multiple providers, graceful degradation
2. **Data quality** → Provenance tracking, confidence scores
3. **Cost control** → Research budgets, LLM call limits

---

## Quality Gates

Each phase must pass:
1. All tests pass
2. No critical architectural violations
3. Domain independence maintained
4. Persian support working
5. Provenance tracked
