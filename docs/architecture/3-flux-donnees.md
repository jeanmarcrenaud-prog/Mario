# Flux de Données

## Vue d'ensemble

Le flux de données dans Mario suit ces étapes :

```
Audio → Transcription → Intent → LLM → Génération → TTS → Audio de réponse
```

## Diagramme complet

```
┌─────────────┐
│  Microphone │
└──────┬──────┘
       │ Raw Audio (numpy array)
       ▼
┌──────────────────────────┐
│   WhisperSpeech          │
│   RecognitionAdapter      │  (src/adapters/)
└────────┬─────────────────┘
         │ Text: "Bonjour, vous avez des messages ?"
         │
         ▼
┌──────────────────────────┐
│    IntentRouter          │
│      (Intent Detection)  │  (src/core/intent_router.py)
└────────┬─────────────────┘
         │ Intent: "MESSAGES"
         │
         ▼
┌──────────────────────────┐
│  LLMService              │
│  (Response Generation)   │  (src/core/llm_service.py)
└────────┬─────────────────┘
         │ Text: "Oui ! Vous avez 3 messages"
         │
         ▼
┌──────────────────────────┐
│   PiperTextToSpeech      │
│      Adapter             │  (src/adapters/)
└────────┬─────────────────┘
         │ Audio numpy
         │
         ▼
┌──────────────────────────┐
│   Audio Output           │
│  (Haut-parleur)         │  (src/interfaces/)
└──────────────────────────┘

┌─────────────┐
│   Vues      │
│  (Web/Console)
└─────────────┘
```

## Étapes détaillées

### 1. Capture Audio

```python
# src/interfaces/microphone.py

class MicrophoneInput:
    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self.sample_rate = 16000
        
    def record(self, duration_ms: int) -> np.ndarray:
        """
        Capture audio depuis le micro
        
        Args:
            duration_ms: Durée de capture en millisecondes
            
        Returns:
            NumPy array d'échantillons audio (int16)
        """
        # Configuration sounddevice
        stream = stream(input_channel=self.device_index,
                       samplerate=self.sample_rate,
                       channels=1)
        data, _ = stream.read(int(self.sample_rate * duration_ms / 1000))
        
        # Normalization
        gain = 0.5
        return data
```

### 2. Reconnaissance Vocale (STT)

```python
# src/adapters/speech_recognition_whisper_adapter.py

class WhisperSpeechRecognitionAdapter:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
        
    def transcribe_array(self, audio: np.ndarray, **kwargs) -> str:
        """
        Convert l'audio RAW en texte
        
        Args:
            audio: NumPy array audio (int16 ou float32)
            kwargs: Options (language="fr", etc)
            
        Returns:
            Texte transcrit
        """
        # Normalisation
        if audio.dtype == np.int16:
            audio_float = audio.astype(np.float32) / 32768.0
        
        # Transcription Whisper
        result = self.model.transcribe(
            audio_float,
            language=kwargs.get("language", "fr"),
            fp16=False
        )
        
        return result["text"]
```

### 3. Rôles Intent

```python
# src/core/intent_router.py

class IntentRouter:
    def __init__(self):
        self.intents_config = {
            "MESSAGES": {
                "description": "Gestion des messages",
                "keywords": ["message", "nouveau", "attendu"],
                "handler": "message_handler"
            },
            "MUSIC": {
                "description": "Jeu de musique",
                "keywords": ["musique", "play", "lecture"],
                "handler": "music_handler"
            }
        }
        
    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Classifie l'intent d'un texte
        
        Args:
            text: Texte transcrit
            
        Returns:
            Dict avec "intent", "confidence", "handler"
        """
        text_lower = text.lower()
        for intent, config in self.intents_config.items():
            if any(keyword in text_lower for keyword in config["keywords"]):
                return {
                    "intent": intent,
                    "confidence": 0.85,  # Exemple
                    "handler": config["handler"]
                }
        return None  # Pas d'intent reconnu
```

### 4. Génération LLM

```python
# src/core/llm_service.py

class LLMService:
    def __init__(self):
        self.system_prompt = """Tu es Mario, assistant vocal.
Répond de manière amicale et concise.
"""
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Génère une réponse à l'histoire de conversation.
        
        Args:
            messages: Liste de dicts {"role": "user|assistant", "content": "text"}
            
        Returns:
            Chaine réponse
        """
        # Assembler le prompt avec l'histoire
        conversation = self.format_conversation(messages)
        
        # Appeler le modèle LLM
        response = self.llm.generate(conversation + self.system_prompt)
        
        return response
    
    def format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Formate l'histoire en prompt."""
        lines = []
        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")
            lines.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(lines)
```

### 5. Synthèse TTS

```python
# src/adapters/tts_piper_adapter.py

class PiperTextToSpeechAdapter:
    def __init__(self, voice: str = "fr_FR-siwis-medium"):
        self.voice = voice
        self.model = piper.load_model(self.voice)
        
    def synthesize(self, text: str, **kwargs) -> np.ndarray:
        """
        Synthétise du texte en audio.
        
        Args:
            text: Texte à synthétiser
            kwargs: Options (speed=0.9, etc)
            
        Returns:
            NumPy array audio (float32)
        """
        # Générer l'audio
        audio = self.model.generate(
            text=text,
            speed=kwargs.get("speed", 1.0),
            **kwargs
        )
        
        return audio  # NumPy float32
```

### 6. Sortie Audio

```python
# src/interfaces/audio_output.py

class AudioOutput:
    def __init__(self, device_index: int = -1):
        self.device_index = device_index
        self.sample_rate = 16000
        
    def play(self, audio: np.ndarray):
        """
        Joue l'audio sur les haut-parleurs.
        
        Args:
            audio: NumPy array audio (float32)
        """
        # Convertir float32 vers int16 pour sortie
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Jouer avec sounddevice ou ALSA
        stream = stream(output_channel=self.device_index,
                       samplerate=self.sample_rate,
                       channels=1)
        stream.write(audio_int16)
        
    def save(self, audio: np.ndarray, path: str):
        """
        Sauvegarde l'audio dans un fichier.
        """
        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
```

### 7. Vues

```python
# src/views/web_interface.py

class WebInterface:
    def __init__(self, service: ConversationService):
        self.service = service
        self.app = GradioInterface()
        
    def on_message(self, message: str):
        """
        Traite un message de l'interface web.
        
        Args:
            message: Message utilisateur texte
        """
        # Appeller la logique métier
        response = self.service.process_message(message)
        
        return response
```

## Gestion État

### 1. Conversation History

```python
# Gestion l'historique conversationnel

class ConversationState:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        
    def add_message(self, role: str, content: str):
        """
        Ajouter un message histoire.
        
        Args:
            role: "user" ou "assistant"
            content: Texte du message
        """
        self.history.append({
            "role": role,
            "content": content
        })
        
    def get_history(self, max_messages: int = None) -> List[Dict[str, str]]:
        """
        Récupère l'histoire (optionnel limit).
        """
        if max_messages:
            return self.history[-max_messages:]
        return self.history
```

### 2. Gestion mémoire modèle

```python
# src/adapters/speech_recognition_whisper_adapter.py

class WhisperSpeechRecognitionAdapter:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
        
    def unload_model(self) -> None:
        """
        Décharge le modèle de mémoire GPU.
        """
        import torch
        if self.model and torch.cuda.is_available():
            del self.model
            torch.cuda.empty_cache()
            
    def clear_cache(self) -> None:
        """
        Nettoie le cache entre les inférences.
        """
        if self.model and torch.cuda.is_available():
            torch.cuda.empty_cache()
```

## Monitoring Performance

```python
# src/core/performance_optimizer.py

class PerformanceCounter:
    def __init__(self):
        start_time = time()
        total_tokens_generated = 0
        
    def record_usage(self, tokens: int):
        """
        Enregistre l'usage pour surveillance.
        
        Args:
            tokens: Nombre de tokens générés
        """
        self.tokens_generated += tokens
        
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance.
        
        Returns:
            Dict avec:
            - tokens_generated
            - tokens_per_minute
            - session_duration_minutes
            - etc
        """
        duration = time() - start_time
        return {
            "duration": duration,
            "tokens_generated": self.tokens_generated,
            "tokens_per_minute": self.tokens_generated / duration if duration else 0
        }
```
