# Optimisation GPU pour Mario Assistant Vocal

### Problématiques

1. **Under-utilisation du GPU NVIDIA RTX 5080**
   - Whisper ne tire pas parti de CUDA pour l'inference
   - Pas de configuration explicite pour GPU dans le code

2. **Optimisations manuelles nécessaires**
   - PyTorch doit être installé avec CUDA support
   - Whisper doit être forcé à utiliser le GPU

### Solutions techniques

#### 1. Installation de PyTorch avec CUDA

```python
# Installation recommandée pour RTX 5080
torch==2.5.1+cu121 torchvision==0.16.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

#### 2. Configuration de Whisper pour GPU

Dans `src/adapters/speech_recognition_whisper_adapter.py`:

```python
import torch
from openai.whisper import load_model

class WhisperSpeechRecognitionAdapter:
    def __init__(self, config=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = load_model("base.en", device=self.device)
        
    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result["text"]
```

#### 3. Optimisation GPU avancée

Ajouter un fichier `src/adapters/gpu_manager.py`:

```python
import torch
import GPUtil

class GPUManager:
    def __init__(self):
        self.available = torch.cuda.is_available()
        self.gpus = GPUtil.getGPUs() if self.available else []
        
    def get_gpu_memory(self):
        if not self.available:
            return 0, 0
        gpu = self.gpus[0]
        return gpu.memoryUsed, gpu.memoryTotal
    
    def clear_gpu_cache(self):
        if self.available:
            torch.cuda.empty_cache()
```

### Benchmarking

Ajouter un test de performance dans `tests/performance/test_gpu_usage.py`:

```python
import time
import torch

def test_gpu_transcription_speed():
    # Test transcription avec et sans GPU
    # Timer pour mesurer le temps de transciption
    # Comparaison avant/après optimisation
    pass
```

### Priorités

1. Installer PyTorch avec CUDA
2. Mettre à jour Whisper adapter pour GPU
3. Intégrer GPUManager dans l'application
4. Ajouter tests de benchmark
