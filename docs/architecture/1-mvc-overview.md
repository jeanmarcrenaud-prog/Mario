# Vue d'ensemble de l'architecture MVC

## Architecture globale

Le projet Mario suit une architecture **MVC (Model-View-Controller)** avec une approche modulaire.

```
┌─────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                    │
│                   (Vue : Interfaces UI)                   │
│    ┌─────────────────┬─────────────────┬────────────┐   │
│    │   Web (Gradio)  │   Console       │   ePaper   │   │
│    └─────────────────┴─────────────────┴────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   CONTROLLER LAYER                        │
│              (Contrôleur : Gestion logique)               │
│    ┌─────────────────┬─────────────────┬────────────┐   │
│    │   Conversation   │   Audio Pipeline│   Wake     │   │
│    │    Handler       │     Manager     │  Word      │   │
│    └─────────────────┴─────────────────┴────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                          │
│                 (Services : Traitement données)           │
│    ┌─────────────────┬─────────────────┬────────────┐   │
│    │   STT Service   │  TTS Service    │  Intent    │   │
│    │   (Whisper)     │  (Piper)        │  Router    │   │
│    └─────────────────┴─────────────────┴────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   ADAPTER LAYER                           │
│         (Adaptateurs : Interfaces matérielles/APIs)       │
│    ┌─────────────────┬─────────────────┬────────────┐   │
│    │   Audio Device  │   Network API   │   Mock     │   │
│    │   Whisper       │   Vosk          │   Adapter  │   │
│    └─────────────────┴─────────────────┴────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Structure des dossiers

```
src/
├── adapters/           # Adaptateurs matériels/API
│   ├── speech_recognition_whisper_adapter.py
│   ├── speech_recognition_vosk_adapter.py
│   ├── tts_piper_adapter.py
│   └── mock/
│       ├── mock_audio_adapter.py
│       └── mock_recognition_adapter.py
│
├── services/           # Services métier
│   ├── conversation_service.py
│   ├── intent_service.py
│   └── storage_service.py
│
├── core/               # Logique principale
│   ├── app_factory.py      # Injection dépendances
│   ├── conversation_handler.py
│   ├── llm_service.py
│   ├── audio_pipeline.py
│   └── intent_router.py
│
├── controllers/        # Contrôleurs
│   └── main.py
│
├── views/              # Affichages
│   ├── web_interface.py
│   ├── console_interface.py
│   └── epaper_interface.py
│
├── models/             # Modèles données
│   └── message.py
│
└── interfaces/         # Interfaces (micro, audio)
    ├── microphone.py
    └── audio_output.py
```

## Principes clés

### 1. Séparation des responsabilités

- **Adapters** : Gèrent les interfaces externes (audio, API)
- **Services** : Logique métier (traitement STT/TTS, conversations)
- **Core** : Orchestration et coordination
- **Contrôleurs** : Gestion du cycle de vie d'opération
- **Vues** : Présentation des résultats

### 2. Injection de dépendances

```python
# src/core/app_factory.py

# Factory pattern pour créer les composants
class AppFactory:
    @staticmethod
    def create_app(config: dict) -> App:
        # Créer les adapters
        stt_adapter = WhisperSpeechRecognitionAdapter(model_name=config["model"])
        tts_adapter = PiperTextToSpeechAdapter(voice=config["voice"])
        
        # Créer les services
        conversation_service = ConversationService(
            stt_adapter=stt_adapter,
            tts_adapter=tts_adapter
        )
        
        # Créer le contrôleur
        conversation_controller = ConversationController(
            service=conversation_service
        )
        
        return conversation_controller
```

### 3. Interfaces et implémentations

```python
# Défini des interfaces abstraibles
from src.interfaces.speech_recognition import ISpeechRecognitionAdapter

# Implémentations interchangeables de classe
from src.adapters.whisper_adapter import WhisperSpeechRecognitionAdapter
from src.adapters.vosk_adapter import VoskSpeechRecognitionAdapter
from src.adapters.mock_adapter import MockSpeechRecognitionAdapter

class WhisperSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    pass

class VoskSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    pass
```

## Flux de données

### Flux conversation complet

```
1. INPUT AUDIO → Adaptateur (micro)
2. ADAPTATEUR → Service STT → Texte
3. TEXTE → Services Intent → Intent
4. INTENT → Service LLM → Response
5. RESPONSE → Service TTS → Audio
6. AUDIO → Adaptateur (sortie/haut-parleur)
7. AUDIO → Vues (Web/Console/ePaper)
```

## Avantages de cette architecture

- ✅ **Modularité** : Each component can be replaced independently
- ✅ **Testabilité** : Mock les adapters pour tests unitaires
- ✅ **Configuration dynamique** : Compose les composants via config YAML
- ✅ **Maintenance** : Chaque couche a une responsabilité claire
- ✅ **Extensibilité** : Ajout de nouveaux adapters/services facile

## Exemple de remplacement de composant

```python
# Configuration
config = {
    "stt": {
        "type": "whisper",
        "model": "small"
    },
    "tts": {
        "type": "piper", 
        "voice": "fr_FR-siwis-medium"
    },
    "wake_word": {
        "type": "vosk",
        "keyword": "hey mario"
    }
}

# Factory crée l'app avec ces config
app = AppFactory.create_app(config)

# Pour basculer en mode offline:
config = {"stt": {"type": "mock"}, "tts": {"type": "mock"}}
app2 = AppFactory.create_app(config)
```
