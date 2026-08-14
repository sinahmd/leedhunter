# LeedHunter Production-Readiness Baseline

**Date:** 2026-08-12
**Auditor:** Claude (automated baseline)
**Repository:** leedHunterAi

---

## 1. Codebase Statistics

| Metric | Value |
|--------|-------|
| Source files (src/) | 73 |
| Test files (tests/) | 93 |
| Domain layer files | 6 |
| Application layer files | 45 |
| Infrastructure layer files | 12 |
| CLI files | 2 |

---

## 2. Previously Reported Issue Classification

### Critical Issues

| Issue | Status | Evidence |
|-------|--------|----------|
| Fixture path bug (0 results) | **FIXED** | `fixture.py:50-52` now uses `_find_fixtures_dir()` with 3 fallback strategies |
| `.env.example` corruption | **FIXED** | Line 46 no longer has pytest command appended |
| Export command stubbed | **FIXED** | `cli/__init__.py` now wires to `ExportService` and `ResearchOrchestrator` |
| No real search provider | **CONFIRMED** | `web.py:70` and `agentreach.py:77` raise `NotImplementedError` |

### High Issues

| Issue | Status | Evidence |
|-------|--------|----------|
| DB repositories unused | **CONFIRMED** | `orchestrator/research.py` creates entities in-memory, never calls `EntityRepository` |
| id() for provenance | **CONFIRMED** | `signals/detector.py:117`, `opportunities/engine.py:104`, `fixture.py:238` use `str(id(...))` |
| Broad except in orchestrator | **CONFIRMED** | `research.py:283` catches all exceptions silently |
| SafeFormatter unused | **CONFIRMED** | `logging.py:29` defines `setup_logging()` without SafeFormatter; only `setup_safe_logging()` uses it |
| Hard-coded DB password | **CONFIRMED** | `alembic.ini:39` has `postgresql://leedhunter:leedhunter@localhost:5432/leedhunter` |
| Provider --option not wired | **CONFIRMED** | `cli/__init__.py:103-104` hardcodes `FixtureSearchProvider()` ignoring `--provider` option |

### Medium Issues

| Issue | Status | Evidence |
|-------|--------|----------|
| Alembic bypasses Settings | **CONFIRMED** | `alembic/env.py:52-56` uses `os.getenv` directly |
| Empty API key accepted | **CONFIRMED** | `config.py:87-92` `validate_api_key` is no-op |
| Doctor swallows exceptions | **CONFIRMED** | `cli/doctor.py:42,56,70` bare `except Exception` |
| No retry/timeout logic | **CONFIRMED** | Config values exist (`timeout=30.0`, `max_retries=3`) but never used in search execution |
| Research budget not enforced | **CONFIRMED** | `orchestrator/research.py:57-58` defines `max_queries=5`, `max_candidates_per_query=20` but only `max_queries` is used |
| Duplicate Query models | **CONFIRMED** | `domain/models.py` has `SearchQuery`, `domain/search/query.py` has `Query` — providers use `SearchQuery`, planner uses `Query` |
| No partial-result behavior | **CONFIRMED** | Research either succeeds fully or fails; no partial result reporting |

### Low Issues

| Issue | Status | Evidence |
|-------|--------|----------|
| No LICENSE file | **CONFIRMED** | No LICENSE file in repository root |
| No CONTRIBUTING.md | **CONFIRMED** | No contributing guidelines |
| No SECURITY.md | **CONFIRMED** | No security policy |
| No CI/CD | **CONFIRMED** | No `.github/workflows/` directory |
| No CHANGELOG | **CONFIRMED** | No CHANGELOG.md |
| No CODE_OF_CONDUCT.md | **CONFIRMED** | No code of conduct |

### Fixed Issues (from previous audit)

| Issue | Status | Evidence |
|-------|--------|----------|
| Fixture path bug | **FIXED** | Multi-strategy directory search in `fixture.py` |
| `.env.example` corruption | **FIXED** | Clean line 46 |
| Export command stubbed | **FIXED** | Full implementation with research + export pipeline |

---

## 3. Confirmed Defects (Detailed)

### DEF-001: Research budget enforcement incomplete
- **File:** `src/leedhunter/application/orchestrator/research.py:57-58`
- **Evidence:** `max_candidates_per_query=20` is defined but never applied to search results
- **Impact:** Unbounded candidate collection could cause memory/performance issues
- **Severity:** High

### DEF-002: Unstable provenance IDs
- **Files:** `signals/detector.py:117`, `opportunities/engine.py:104`, `fixture.py:238`
- **Evidence:** Uses `str(id(python_object))` which changes between runs
- **Impact:** Evidence/signal/opportunity references break across sessions
- **Severity:** High

### DEF-003: Provider selection not wired
- **File:** `src/leedhunter/cli/__init__.py:103-104`
- **Evidence:** `search_provider = FixtureSearchProvider()` ignores `--provider` option
- **Impact:** CLI `--provider` flag is non-functional
- **Severity:** High

### DEF-004: Duplicate query models
- **Files:** `domain/models.py` (SearchQuery), `domain/search/query.py` (Query)
- **Evidence:** Providers use `SearchQuery`, planner uses `Query`, orchestrator converts between them
- **Impact:** Confusion, potential data loss during conversion
- **Severity:** Medium

### DEF-005: SafeFormatter not default
- **File:** `src/leedhunter/logging.py:29`
- **Evidence:** `setup_logging()` does not use `SafeFormatter`; credentials could appear in logs
- **Impact:** Credential leakage in production logs
- **Severity:** High

### DEF-006: Hard-coded database credentials
- **File:** `alembic.ini:39`
- **Evidence:** `sqlalchemy.url = postgresql://leedhunter:leedhunter@localhost:5432/leedhunter`
- **Impact:** Credentials in version control
- **Severity:** High

### DEF-007: No transaction boundaries in research
- **File:** `src/leedhunter/application/orchestrator/research.py`
- **Evidence:** Research creates entities/signals/opportunities without database transactions
- **Impact:** Partial research cannot be resumed; no idempotency
- **Severity:** Medium

### DEF-008: No SSRF protection in providers
- **Files:** `application/search/providers/web.py`, `agentreach.py`
- **Evidence:** No URL validation before making HTTP requests
- **Impact:** Potential SSRF if providers are used with user-supplied URLs
- **Severity:** Medium

### DEF-009: No cancellation support
- **File:** `src/leedhunter/application/orchestrator/research.py`
- **Evidence:** No asyncio.CancelledError handling, no graceful shutdown
- **Impact:** Long-running research jobs cannot be cancelled
- **Severity:** Medium

### DEF-010: Incomplete research budget enforcement
- **File:** `src/leedhunter/application/orchestrator/research.py:57-58`
- **Evidence:** `max_runtime_seconds` and `max_llm_calls` from spec not implemented
- **Impact:** No safety limits on research duration or LLM usage
- **Severity:** High

---

## 4. Architectural Recommendations

### REC-001: Unify Query models
**Action:** Delete `SearchQuery` from `domain/models.py`, use `Query` from `domain/search/query.py` everywhere.
**Rationale:** Eliminates confusion and conversion layer.

### REC-002: Make SafeFormatter the default
**Action:** Modify `setup_logging()` to use `SafeFormatter` by default.
**Rationale:** Prevents credential leakage in production.

### REC-003: Wire provider selection
**Action:** Create provider registry, wire `--provider` CLI option to registry lookup.
**Rationale:** Enables multiple provider support.

### REC-004: Add domain ID generation
**Action:** Replace `str(id(...))` with deterministic IDs (UUID or hash-based).
**Rationale:** Enables persistence and cross-session references.

### REC-005: Enforce research budgets
**Action:** Add checks in orchestrator loop for max_candidates, max_runtime, max_llm_calls.
**Rationale:** Safety control against runaway research.

### REC-006: Add URL validation
**Action:** Use `SandboxManager.validate_url()` before all HTTP requests.
**Rationale:** SSRF prevention.

### REC-007: Add cancellation support
**Action:** Add `asyncio.CancelledError` handling, graceful shutdown signal.
**Rationale:** User control over long-running operations.

### REC-008: Add retry with backoff
**Action:** Implement exponential backoff for provider failures.
**Rationale:** Reliability for flaky external services.

### REC-009: Add partial result reporting
**Action:** Track which providers succeeded/failed, report partial coverage.
**Rationale:** Transparency when some sources fail.

### REC-010: Add research resumability
**Action:** Persist research state, allow resuming interrupted jobs.
**Rationale:** Long research jobs should survive interruptions.

---

## 5. Optional Future Improvements

### IMP-001: Real web search provider
- Implement HTTP-based search using official APIs (Bing, Google Custom Search)
- Add terms-of-service compliance review

### IMP-002: LLM integration
- Add Anthropic/OpenAI adapter behind LLMProvider protocol
- Schema-validated responses only
- Evidence-scoped prompts

### IMP-003: Database persistence
- Wire EntityRepository, EvidenceRepository, etc. to orchestrator
- Add PostgreSQL integration tests

### IMP-004: Redis caching
- Cache search results, entity lookups
- Rate limiting state

### IMP-005: Research trace persistence
- Store traces in database
- Query/export trace history

### IMP-006: CLI progress bars
- Real-time progress for long-running operations
- Estimated time remaining

### IMP-007: Export formats
- Add Excel export
- Add custom field selection
- Add filtering by score/status

### IMP-008: Entity resolution quality metrics
- Track precision/recall/F1 against evaluation dataset
- Alert on false merge rate increase

### IMP-009: Multi-language support
- Add Arabic, Turkish normalization
- Add RTL text support

### IMP-010: Web UI
- Dashboard for research jobs
- Entity browser
- Lead management

---

## 6. Implementation Priority Matrix

### Phase 1: Release Blockers (Critical)
1. Fix research budget enforcement (DEF-001, DEF-010)
2. Fix unstable provenance IDs (DEF-002)
3. Wire provider selection (DEF-003)
4. Make SafeFormatter default (DEF-005)
5. Remove hard-coded credentials (DEF-006)

### Phase 2: Correctness & Persistence (High)
6. Unify Query models (REC-001)
7. Add URL validation (REC-006)
8. Add retry with backoff (REC-008)
9. Add partial result reporting (REC-009)
10. Wire database repositories

### Phase 3: Reliability & Security (High)
11. Add cancellation support (REC-007)
12. Add research resumability (IMP-010)
13. Add SSRF protection (DEF-008)
14. Add transaction boundaries (DEF-007)

### Phase 4: Provider Integration (Medium)
15. Implement real search provider
16. Add provider contract tests
17. Add provider health monitoring

### Phase 5: Open-Source Release (Medium)
18. Add LICENSE file
19. Add CONTRIBUTING.md
20. Add SECURITY.md
21. Add CI/CD workflows
22. Add CHANGELOG.md

### Phase 6: LLM Integration (Low)
23. Implement LLM provider adapter
24. Add schema validation
25. Add prompt injection protection

---

## 7. Summary

**Current State:** Alpha/Prototype
- Demo workflow functional with fixture data
- Core domain logic well-implemented
- 508+ tests passing
- Critical integration defects identified

**Release Blockers:** 5 items (Phase 1)
**High Priority:** 5 items (Phase 2)
**Medium Priority:** 4 items (Phase 3-4)
**Low Priority:** 6 items (Phase 5-6)

**Recommendation:** Complete Phase 1 before any external release. Phase 2 before beta release. Phase 5 before open-source publication.
