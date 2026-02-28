# Documentation des dépendances - Assistant Vocal Mario

## Dépendances obligatoires

### Audio et ML
- `torch>=1.13.0` - Framework PyTorch pour le deep learning et l'acoustique
- `openai-whisper>=20231106` - Modèle de reconnaissance vocale
- `piper-tts>=1.2.0` - Synthèse vocale text-to-speech
- `onnxruntime>=1.16.0` - Runtime pour modèles ONNX

### Détection vocale et traitement
- `webrtcvad>=2.0.10` - Détection de voix active
- `pyaudio>=0.2.11` - Interface audio
- `pvrecorder>=1.1.1` - Enregistrement audio
- `librosa>=0.9.0` - Traitement audio et musiques
- `soundfile>=0.12.1` - Lecture/écriture audio
- `scipy>=1.10.0` - Calcul scientifique
- `numba>=0.57.0` - Compilation JIT
- `numpy>=1.21.0` - Calcul numérique
- `sounddevice>=0.5.2` - Accès microphone/haut-parleur (manquant dans pyproject.toml)

### Interface et API
- `gradio>=4.0.0` - Interface web
- `flask>=3.0.0` - Framework web
- `requests>=2.28.0` - Requêtes HTTP
- `python-dotenv>=1.0.0` - Gestion variables d'environnement (manquant dans pyproject.toml)

### Utilitaires
- `psutil>=5.9.0` - Surveillance système
- `tqdm>=4.65.0` - Barres de progression
- `typing-extensions>=4.8.0` - Typage avancé
- `dataclasses-json>=0.6.3` - Sérialisation JSON
- `colorlog>=6.8.0` - Logging coloré

### Développement et Tests
- `pytest>=8.0.0` - Cadre de test
- `pytest-cov>=4.1.0` - Couverture de test

## Dépendances optionnelles

### dans requirements.txt mais pas pyproject.toml
- `rich>=13.0.0`
- `prompt_toolkit>=3.0.0`
- `GPutil>=1.4.0`

## Notes

La configuration recommandée inclut:
1. PyTorch avec CUDA pour utiliser le GPU
2. Sounddevice pour la gestion du matériel audio
3. GPutil pour le monitoring GPU
4. Les dépendances Rich et prompt_toolkit pour l'interface console
