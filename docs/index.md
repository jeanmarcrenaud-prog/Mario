# Mario - Assistant Vocal Intelligent

Mario est un assistant vocal intelligent qui combine reconnaissance vocale, synthèse vocale et intelligence artificielle pour créer une expérience conversationnelle naturelle.

## Fonctionnalités

### 🎤 Reconnaissance Vocale
- Utilise **Whisper** pour la transcription automatique de la parole
- Support multi-langues (-Français par défaut)
- Détection de mot-clé "Hey Mario" avec **Vosk**

### 🗣️ Synthèse Vocale
- **Piper TTS** pour une synthèse vocale naturelle
- Plusieurs voix disponibles
- Contrôle de la vitesse de parole

### 🤖 Intelligence Artificielle
- Intégration **Ollama** pour les modèles LLM locaux
- Support de plusieurs modèles (qwen3-coder, llama3, etc.)
- Analyse de projets et génération de recommandations

### 💻 Interfaces Multiples
- **Gradio** - Interface web moderne et interactive
- **Console** - Interface en ligne de commande
- Support pour affichage ePaper

### ⚡ Optimisations
- Mode faible latence configurable
- Suivi des performances audio
- Monitoring système (CPU, GPU, mémoire)

## Architecture

```
src/
├── core/           # Logique métier principale
├── services/      # Services (LLM, TTS, STT, Wake Word)
├── adapters/      # Adaptateurs pour les bibliothèques externes
├── views/         # Interfaces utilisateur
├── models/        # Modèles de données
├── utils/         # Utilitaires
└── interfaces/   # Définitions des interfaces
```

## Installation

Voir [Guide d'installation](installation.md)

## Utilisation

### Interface Web
```bash
python run.py
```

### Console
```bash
python -m src.core.app_runner
```

## Configuration

Le fichier `config.yaml` permet de configurer:
- Le microphone par défaut
- La voix TTS
- Le modèle LLM
- Le port de l'interface web

## Tests

```bash
# Exécuter tous les tests
pytest

# Avec couverture
pytest --cov=src
```

## Contribution

Les contributions sont les bienvenues! Veuillez lire le guide de contribution avant de soumettre une PR.

## Licence

MIT License
