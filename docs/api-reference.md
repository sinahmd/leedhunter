# LeedHunter API Reference

## Architecture Overview

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

## Domain Layer

### Models

#### SearchIntent
Represents the user's prospecting objective.

```python
from leedhunter.domain.models import SearchIntent

intent = SearchIntent(
    objective="Find auto importers in Mazandaran",
    location="Mazandaran",
    industry="Automotive",
    constraints=["used"],
)
```

#### SearchQuery
Structured search query representation.

```python
from leedhunter.domain.search.query import Query, QueryBuilder

# Using builder
query = (
    QueryBuilder()
    .add_term("import")
    .add_exact_phrase("واردات خودرو")
    .add_site("instagram.com")
    .build()
)
```

#### Entity
Canonical real-world business entity.

```python
from leedhunter.domain.models import Entity, EntityIdentity, EntityIdentityType

entity = Entity(
    id="entity_1",
    canonical_name="Example Corp",
    canonical_domain="example.com",
    identities=[
        EntityIdentity(
            type=EntityIdentityType.PHONE,
            value="+98 912 123 4567",
            normalized_value="09121234567",
            source="instagram",
            source_url="https://instagram.com/example",
        )
    ],
)
```

#### Evidence
Factual observation about an entity.

```python
from leedhunter.domain.models import Evidence

evidence = Evidence(
    entity_id="entity_1",
    claim="Opening new branch",
    value="Opening new branch in Sari",
    source="instagram",
    source_url="https://instagram.com/example/123",
    confidence=0.85,
)
```

#### Signal
Inferred business signal.

```python
from leedhunter.domain.models import Signal, SignalType

signal = Signal(
    entity_id="entity_1",
    signal_type=SignalType.EXPANSION,
    description="Business expanding to new locations",
    confidence=0.8,
)
```

#### Lead
Qualified business lead.

```python
from leedhunter.domain.models import Lead, LeadStatus

lead = Lead(
    entity=entity,
    signals=[signal],
    opportunities=[opportunity],
    evidence=[evidence],
    score=85.0,
    status=LeadStatus.QUALIFIED,
)
```

## Application Layer

### Search Planning

```python
from leedhunter.domain.search.planner import SearchPlanner

planner = SearchPlanner()
analysis, queries = planner.plan_search(intent, max_queries=10)
```

### Candidate Pipeline

```python
from leedhunter.application.pipeline import CandidatePipeline

pipeline = CandidatePipeline()
result = pipeline.process(raw_results, source="instagram", query_id="query_1")
```

### Entity Resolution

```python
from leedhunter.application.resolution import EntityResolutionOrchestrator

orchestrator = EntityResolutionOrchestrator()
result = orchestrator.resolve(candidate, existing_entities)
# result.decision: MATCH, POSSIBLE_MATCH, NEW_ENTITY
```

### Evidence Collection

```python
from leedhunter.application.evidence import EvidenceCollector

collector = EvidenceCollector()
evidence_list = collector.collect_from_candidate(entity_id, candidate)
```

### Signal Detection

```python
from leedhunter.application.signals import SignalDetector

detector = SignalDetector()
signals = detector.detect_batch(entity_id, evidence_list, identities)
```

### Opportunity Identification

```python
from leedhunter.application.opportunities import OpportunityEngine

engine = OpportunityEngine()
opportunities = engine.identify(entity_id, signals)
```

### Qualification

```python
from leedhunter.application.qualification import QualificationEngine

engine = QualificationEngine()
result = engine.qualify(entity, signals, opportunities)
# result.status: QUALIFIED, DISQUALIFIED
```

### Scoring

```python
from leedhunter.application.scoring import ScoringEngine

engine = ScoringEngine()
breakdown = engine.calculate_score(entity, signals, opportunities)
# breakdown.total_score: 0-100
```

## LLM Integration

### LLM Provider

```python
from leedhunter.application.llm import LLMProvider, LLMResponseParser

# Parse LLM response
parser = LLMResponseParser()
result = parser.parse(response, IntentAnalysisResult)
```

### Mock Provider (for testing)

```python
from leedhunter.application.llm import MockLLMProvider

provider = MockLLMProvider(responses={"test": '{"result": "ok"}'})
response = await provider.generate("test prompt")
```

## Infrastructure

### Database

```python
from leedhunter.infrastructure.database import get_session, EntityRepository

async with get_session() as session:
    repo = EntityRepository(session)
    entity = await repo.save(entity)
```

### Sandbox

```python
from leedhunter.infrastructure.sandbox import SandboxManager

sandbox = SandboxManager()
if sandbox.validate_url("https://example.com"):
    # Safe to fetch
    pass
```

### Security

```python
from leedhunter.infrastructure.security import InputSanitizer, CredentialRedactor

sanitizer = InputSanitizer()
if sanitizer.detect_injection_attempt(text):
    # Handle injection attempt
    pass

redactor = CredentialRedactor()
safe_text = redactor.redact(text_with_credentials)
```

## Export

```python
from leedhunter.application.export import ExportService, ExportOptions, ExportFormat

service = ExportService()
options = ExportOptions(format=ExportFormat.JSON, include_signals=True)
json_output = service.export_leads(leads, options)
```

## Research Trace

```python
from leedhunter.application.trace import ResearchTracer, TraceEventType

tracer = ResearchTracer()
tracer.start_trace("research_1")
tracer.record_event(TraceEventType.QUERY_GENERATED, metadata={"query": "test"})
tracer.end_trace("research_1", success=True)
report = tracer.generate_report("research_1")
```
