# 🤖 AGENTS.md - Mario Assistant Vocal Development Guide

## Build & Test Commands

### Running Tests
```bash
# Run all tests with coverage (80%+ required)
pytest -v --tb=short

# Run single test file
pytest tests/unit/core/test_core.py -v

# Run specific test case
pytest tests/unit/core/test_core.py::TestAudioPipeline::test_pipeline_init -v

# Run unit tests only
pytest tests/unit/ -m unit -v

# Run integration tests only
pytest tests/integration/ -m integration -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Watch mode (auto-reload on changes)
pytest -w src/ -v

# Skip slow tests
pytest -m "not slow" -v
```

### Linting & Formatting
```bash
# Check code style (flake8, ruff, mypy)
ruff check src/ tests/
flake8 src/ tests/
mypy src/

# Auto-format with black
black src/ tests/

# Fix import sorting
isort src/ tests/

# Full pre-commit check
pre-commit run --all-files
```

### Build & Deploy
```bash
# Install dependencies
pip install -e .

# Run development server
python src/main.py

# Build documentation
mkdocs build

# Generate coverage report
pytest --cov=src --cov-report=html

# Test LLM monitoring system
python demo_llm_monitoring.py

# Test LLM service detection
python test_llm_detection.py
```

## LLM Integration & Monitoring

### Services Supportés
```python
# Ollama - Recommandé pour IA locale
OllamaLLMAdapter(model_name="minimax-m2:cloud", base_url="http://localhost:11434")

# LM Studio - Alternative robuste  
LMStudioLLMAdapter(model_name="qwen/qwen3.5-9b", base_url="http://localhost:1234")
```

### Détection Automatique
```python
# Détection et création automatique du service LLM
from services.llm_service import LLMService

llm_service = LLMService.detect_and_create()
info = llm_service.get_service_info()
print(f"Service: {info['service_type']}, Model: {info['model']}")
```

### Monitoring Intégré
```python
# Dans SystemMonitor
from utils.system_monitor import SystemMonitor

monitor = SystemMonitor()
llm_info = monitor.refresh_llm_models()
print(f"LLM Service: {llm_info['service_type']}")
print(f"Active Model: {llm_info['active_model']}")
print(f"Available Models: {llm_info['available_models']}")
```

### Rafraîchissement Automatique
- ✅ **Au démarrage** : AppFactory appelle `system_monitor.refresh_llm_models()`
- ✅ **Logs informatifs** : État visible dans les logs d'application
- ✅ **Interface web** : Section LLM dans les informations système
- ✅ **Fallback intelligent** : Simulation si aucun service détecté

## Code Style Guidelines

### Imports (Standard Order)
```python
# 1. Standard library
import os
import sys
from typing import Optional, Dict, Any

# 2. Third-party
import numpy as np
from fastapi import FastAPI

# 3. Local imports
from src.core.audio_pipeline import AudioPipeline
from src.utils.logger import logger
```

### Formatting (Black + Ruff)
- Line length: 88 characters (Black default)
- Indentation: 4 spaces
- Blank lines: 2 between functions/classes, 1 between methods
- No trailing whitespace
- Always use double quotes for strings (`"`)

### Type Hints & Annotations
```python
# ALWAYS annotate function parameters and return types
def process_audio(data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
    """Process audio data and return analysis results."""
    ...

# Use Optional for nullable values
def get_device(name: str) -> Optional[AudioDevice]:
    ...

# Use Literal for constrained strings
from typing import Literal
Mode = Literal["low_latency", "balanced", "high_quality"]
```

### Naming Conventions
- **Classes**: PascalCase (`AudioPipeline`, `LLMService`)
- **Functions/Variables**: snake_case (`get_audio_data`, `sample_rate`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_CHUNK_SIZE`, `MAX_RETRIES`)
- **Private members**: Single underscore prefix (`_running_event`, `_audio_queue`)
- **Module-level constants**: UPPERCASE with descriptive names

### Error Handling
```python
# Use try-except for external calls (network, hardware)
try:
    result = await llm_service.generate(prompt)
except ConnectionError as e:
    logger.error(f"LLM connection failed: {e}")
    return None

# Wrap callbacks with exception isolation
def safe_callback(callback: Callable, *args):
    try:
        callback(*args)
    except Exception as e:
        logger.warning(f"Callback error: {e}")

# Use custom exceptions from src/core/exceptions.py
from src.core.exceptions import SpeechRecognitionError
```

### Documentation (Docstrings)
```python
def process_audio(data: np.ndarray) -> Dict[str, Any]:
    """
    Process audio data and return analysis results.
    
    Args:
        data: NumPy array of audio samples
        
    Returns:
            Dictionary with 'duration', 'sample_rate', 'channels'
            
    Raises:
        ValueError: If data is empty or invalid shape
        
    Example:
        >>> result = process_audio(audio_data)
        >>> print(result['duration'])
    """
```

### Architecture Patterns (MVC)
- **Models**: Data structures (`src/models/*.py`)
- **Views**: UI components (`src/views/*.py`, `src/adapters/`)
- **Services**: Business logic (`src/services/*.py`)
- **Core**: Shared utilities (`src/core/*.py`, `src/utils/*.py`)

### Testing Standards
- Write tests BEFORE implementing features (TDD)
- Use fixtures from `tests/conftest.py` for shared setup
- Mock external dependencies (network, hardware)
- Test edge cases and error paths
- Maintain 80%+ code coverage
- Name test functions: `test_<scenario>_<expected_result>`

### Git & Commits
```bash
# Use conventional commits
feat: Add new feature
fix: Fix bug
docs: Update documentation
refactor: Code restructuring without behavior change
test: Add or update tests
chore: Maintenance tasks

# Example
git commit -m "fix(audio): resolve memory leak in AudioPipeline"
```

### Performance Considerations
- Use `deque(maxlen=N)` for bounded collections (prevent memory leaks)
- Use `threading.Event` instead of plain bools for thread-safe state
- Avoid blocking operations in async contexts
- Implement connection pooling for external services
- Cache expensive computations with `functools.lru_cache`

### Security Best Practices
- Never commit secrets/API keys (use `.env` files)
- Validate all user inputs before processing
- Use parameterized queries for database access
- Sanitize file paths to prevent directory traversal
- Implement rate limiting for API endpoints

---

**Remember**: Write clean, maintainable code. When in doubt, ask: "Would another developer understand this in 6 months?"
