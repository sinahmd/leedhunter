# Provider Guide

## Available Providers

### Search Providers

| Provider | Status | API Key Required | Cost |
|----------|--------|------------------|------|
| FixtureSearchProvider | ✅ Default | No | Free |
| TavilySearchProvider | ✅ Available | Yes | Free (1,000/month) |
| BraveSearchProvider | ✅ Available | Yes | $5/1,000 searches |

### LLM Providers

| Provider | Status | API Key Required | Cost |
|----------|--------|------------------|------|
| MockLLMProvider | ✅ Default | No | Free |
| AnthropicLLMProvider | ✅ Available | Yes | Pay-per-use |
| OpenAILLMProvider | ✅ Available | Yes | Pay-per-use |

## Configuration

### Search Providers

```env
# Default provider
LEEDHUNTER_SEARCH_DEFAULT_PROVIDER=fixture

# Tavily
LEEDHUNTER_SEARCH_TAVILY_API_KEY=your_key

# Brave
LEEDHUNTER_SEARCH_BRAVE_API_KEY=your_key
```

### LLM Providers

```env
# Enable LLM (optional)
LEEDHUNTER_LLM_ENABLED=true

# Provider selection
LEEDHUNTER_LLM_PROVIDER=anthropic  # or openai, openai_compatible

# API key
LEEDHUNTER_LLM_API_KEY=your_key

# For OpenAI-compatible endpoints
LEEDHUNTER_LLM_BASE_URL=http://localhost:11434/v1
```

## Adding a New Provider

### 1. Create Provider Class

```python
# src/leedhunter/application/search/providers/your_provider.py

from leedhunter.application.search.provider import SearchProvider, SearchResult

class YourSearchProvider(SearchProvider):
    @property
    def name(self) -> str:
        return "your_provider"

    async def search(self, query) -> SearchResult:
        # Implementation
        pass
```

### 2. Add Configuration

```python
# src/leedhunter/config.py

class SearchSettings(BaseSettings):
    your_provider_api_key: str = ""
```

### 3. Register Provider

```python
# src/leedhunter/cli/__init__.py

def _get_search_provider(name):
    if name == "your_provider":
        return YourSearchProvider(config)
```

### 4. Add Tests

```python
# tests/providers/test_your_provider.py

class MockYourProvider(SearchProvider):
    # Mock implementation for testing
    pass
```

### 5. Update Documentation

Add your provider to this guide and the README.

## Provider Interface

All search providers must implement:

```python
class SearchProvider(ABC):
    @property
    def name(self) -> str: ...

    @property
    def supported_operators(self) -> list[str]: ...

    async def search(self, query: Query) -> SearchResult: ...

    async def is_available(self) -> bool: ...

    async def get_health(self) -> ProviderHealth: ...
```

## Error Handling

Providers should raise specific errors:
- `AuthenticationError` - Invalid API key
- `RateLimitError` - Rate limit exceeded
- `NetworkError` - Connection issues
- `ProviderError` - General provider errors
