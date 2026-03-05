# Injection de Dépendances

## Overview

Mario utilise un pattern **Factory** avec **Injection de Dépendances** simple pour assembler les composants.

```
┌─────────────────────────────────────────────┐
│           Composition Root                   │
│          (Factory Pattern)                   │
└─────────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬────────────────┐
    │          │          │                │
    ▼          ▼          ▼                ▼
 Adapter A   Adapter B   Service X        Service Y
```

## Pattern d'Injection

### 1. Définir les interfaces

```python
# src/interfaces/speech_recognition.py
from abc import ABC, abstractmethod

class ISpeechRecognitionAdapter(ABC):
    @abstractmethod
    def transcribe_array(self, audio: np.ndarray) -> str:
        pass
    
    @abstractmethod
    def transcribe_file(self, path: str) -> str:
        pass
    
    @abstractmethod
    def unload_model(self) -> None:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass
```

### 2. Implémentations concrètes

```python
# src/adapters/whisper_adapter.py
class WhisperSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
        
    def transcribe_array(self, audio: np.ndarray) -> str:
        # Implementation Whisper
        pass
```

### 3. Composition Root

```python
# src/core/app_factory.py

class AppFactory:
    @staticmethod
    def create_app(config: dict) -> App:
        """Composeur des composants"""
        
        # Adapter STT
        stt_adapter = RecognizerFactory.create(config["stt"])
        
        # Adapter TTS
        tts_adapter = TextToSpeechFactory.create(config["tts"])
        
        # Adapter Wake Word
        wake_adapter = WakeWordFactory.create(config["wake_word"])
        
        # Services
        conversation_service = ConversationService(
            stt_adapter=stt_adapter,
            tts_adapter=tts_adapter,
            wake_adapter=wake_adapter
        )
        
        # Contrôleur
        controller = Controller(conversation_service)
        
        # Vues
        web_view = GradioInterface(controller)
        console_view = ConsoleInterface(controller)  
        epaper_view = EPaperInterface(controller)
        
        return ControllerAggregate(
            controller=controller,
            views=[web_view, console_view, epaper_view]
        )
```

### 4. Utilisation

```python
# src/main.py
from src.factory import AppFactory

def main():
    # Charger la config
    config = ConfigLoader()
    config_path = "config.yaml"
    config = config.load(config_path)
    
    # Créer l'application
    app = AppFactory.create_app(config)
    
    # Lancer
    app.run()
```

## Avantages

### 1. Interchangeabilité

```python
# Mode production
config = {
    "stt": {"type": "whisper", "model": "small"},
    "tts": {"type": "piper", "voice": "fr_FR-siwis"}
}

# Mode debug/offline
config = {
    "stt": {"type": "mock"},
    "tts": {"type": "mock"}
}

# Même factory, comportement différent
```

### 2. Facilités de tests

```python
# tests/factory/test_factory.py

def test_stt_adapter_with_mock():
    config = {"type": "mock"}
    adapter = RecognizerFactory.create(config)
    
    # Mocks pour tests unitaires
    assert adapter.transcribe_audio(audio) == "test response"

def test_tts_adapter_with_piper():
    config = {"type": "piper", "voice": "fr_FR-siwis-medium"}
    adapter = TextToSpeechFactory.create(config)
    
    response = adapter.synthesize("Hello")
    assert isinstance(response, np.ndarray)
```

### 3. Configuration dynamique

```python
# config.yaml
stt:
    type: whisper
    model: small
    fp16: false
    
tts:
    type: piper
    voice: fr_FR-siwis-medium
    
wake_word:
    type: vosk
    keyword: "hey mario"

# Factory utilise cette config pour assembler
```

## Best Practices

1. **Single Responsibility** : Chaque interface pour un concern unique
2. **Dependency Inversion** : Dépendre des interfaces, non des implémentations
3. **Composition Root Centralisé** : Un seul endroit pour créer les dépendances
4. **Mock pour Tests** : Interfaces de mock dans `src/adapters/mock/`

## Extensions

```python
# Ajouter un nouveau backend STT

1. Créer l'interface (si n'existe pas)
   src/interfaces/speech_recognition.py
   
class ISpeechRecognitionAdapter(ABC):
    @abstractmethod
    def transcribe(self, audio) -> str:
        pass

2. Implémentation
   src/adapters/new_backend_adapter.py
   
class NewBackendAdapter(ISpeechRecognitionAdapter):
    def transcribe(self, audio) -> str:
        # Implémentation
        pass

3. Mettre à jour factory
   src/core/app_factory.py
   
def create_app(config):
    if config["stt"]["type"] == "new_backend":
        return NewBackendAdapter()
```

## Exemple complet

```python
# config.yaml
app:
    stt:
        type: whisper
        model: base
    tts:
        type: piper
        voice: fr_FR-siwis-medium
        
    wake_word:
        type: vosk
        keyword: hey mario

# factory.py
from src.adapters.whisper_adapter import WhisperSpeechRecognitionAdapter
from src.adapters.piper_adapter import PiperTextToSpeechAdapter
from src.adapters.vosk_adapter import VoskWakeWordAdapter

class Factory:
    @staticmethod
    def create_stt(config) -> ISpeechRecognitionAdapter:
        if config["type"] == "whisper":
            return WhisperSpeechRecognitionAdapter(config["model"])
        raise ValueError("STT inconnu")
    
    @staticmethod
    def create_tts(config) -> ITTSAdapter:
        if config["type"] == "piper":
            return PiperTextToSpeechAdapter(config["voice"])
        raise ValueError("TTS inconnu")
    
    @staticmethod
    def create_wake(config) -> IWakeWordAdapter:
        if config["type"] == "vosk":
            return VoskWakeWordAdapter(config["keyword"])
        raise ValueError("Wake word inconnu")
```
