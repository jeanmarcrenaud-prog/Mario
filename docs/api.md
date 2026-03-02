# Documentation API

## Services

### LLMService

Service principal pour les interactions avec les modèles de langage.

```python
from src.services.llm_service import LLMService, OllamaLLMAdapter, SimulatedLLMAdapter
```

#### Méthodes

##### `LLMService.create_with_ollama(model_name: str, base_url: str) -> LLMService`
Crée un service LLM avec Ollama.

```python
service = LLMService.create_with_ollama("qwen3-coder:latest")
```

##### `LLMService.create_with_simulation(fake_responses: dict) -> LLMService`
Crée un service LLM simulé pour les tests.

```python
service = LLMService.create_with_simulation({"hello": "Hi!"})
```

##### `generate_response(messages: List[Dict]) -> str`
Génère une réponse à partir de messages.

```python
messages = [{"role": "user", "content": "Bonjour"}]
response = service.generate_response(messages)
```

##### `generate_analysis(prompt: str) -> str`
Génère une analyse du projet.

```python
analysis = service.generate_analysis("Analyse ce code Python")
```

##### `generate_recommendations(analysis: str) -> List[str]`
Génère des recommandations basées sur une analyse.

```python
recommendations = service.generate_recommendations(analysis)
```

---

### AudioPipeline

Pipeline audio pour la reconnaissance vocale et la synthèse.

```python
from src.core.audio_pipeline import AudioPipeline
```

#### Méthodes

##### `__init__(wake_word_service, speech_recognition_service, tts_service, settings)`

##### `start()`
Démarre le pipeline audio.

##### `stop()`
Arrête le pipeline audio.

##### `speak(text: str) -> bool`
Synthétise et joue le texte.

```python
audio_pipeline.speak("Bonjour! Comment allez-vous?")
```

##### `set_transcription_callback(callback)`
Définit le callback appelé lors de la transcription.

```python
def on_transcribe(text):
    print(f"Transcrit: {text}")

audio_pipeline.set_transcription_callback(on_transcribe)
```

##### `get_latency_stats() -> Dict`
Retourne les statistiques de latence.

```python
stats = audio_pipeline.get_latency_stats()
# {"transcription_avg": 0.5, "tts_avg": 0.3, ...}
```

##### `optimize_performance(aggressive: bool) -> bool`
Optimise les performances du pipeline.

```python
audio_pipeline.optimize_performance(aggressive=True)
```

---

### SystemMonitor

Monitoring système pour CPU, mémoire, GPU, etc.

```python
from src.utils.system_monitor import SystemMonitor
```

#### Méthodes

##### `get_system_info() -> dict`
Informations générales sur le système.

```python
monitor = SystemMonitor()
info = monitor.get_system_info()
```

##### `get_detailed_system_info() -> Dict`
Informations détaillées incluant GPU, réseau, processus.

##### `get_gpu_info() -> List[Dict]`
Informations sur les GPU.

```python
gpus = monitor.get_gpu_info()
for gpu in gpus:
    print(f"GPU: {gpu['name']}")
    print(f"VRAM: {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB")
```

##### `get_cpu_temp() -> Optional[float]`
Température CPU.

##### `get_gpu_temp() -> Optional[float]`
Température GPU (NVIDIA).

---

### Settings

Configuration de l'application.

```python
from src.models.settings import Settings
```

#### Attributs

| Attribut | Type | Défaut | Description |
|----------|------|--------|-------------|
| `microphone_index` | int | 0 | Index du microphone |
| `voice_name` | str | fr_FR-siwis-medium | Voix TTS |
| `llm_model` | str | qwen3-coder:latest | Modèle LLM |
| `speech_speed` | float | 1.0 | Vitesse de parole |
| `wake_word` | str | mario | Mot-clé |
| `web_port` | int | 7860 | Port interface web |
| `sample_rate` | int | 16000 | Fréquence audio |
| `chunk_size` | int | 1024 | Taille du chunk audio |
| `audio_buffer_size` | int | 3 | Taille du buffer |
| `enable_low_latency` | bool | False | Mode faible latence |

---

### ErrorHandler

Gestionnaire d'erreurs centralisé.

```python
from src.utils.error_guard import ErrorHandler, get_error_handler, safe_run, retry
```

#### Utilisation

```python
# Gestionnaire global
handler = get_error_handler()
handler.handle(Exception("Erreur"), "contexte")

# Décorateur safe_run
@safe_run("Module", return_on_error=-1)
def ma_fonction():
    # code qui peut échouer
    pass

# Décorateur retry
@retry(max_attempts=3, delay=1.0)
def fonction_avec_retry():
    # code qui peut échouer
    pass
```

---

## Interfaces

### GradioWebInterface

Interface web Gradio.

```python
from src.views.web_interface_gradio import GradioWebInterface
```

#### Méthodes

##### `create_interface() -> gr.Blocks`
Crée l'interface Gradio.

##### `launch(**kwargs)`
Lance l'interface.

```python
interface = GradioWebInterface(assistant_controller)
interface.launch(server_name="0.0.0.0", server_port=7860)
```
