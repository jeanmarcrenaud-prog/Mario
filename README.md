# 🎙️ Assistant Vocal Intelligent

Un assistant vocal local en **Python**, capable d’écouter, transcrire, répondre et parler grâce à des modèles **OpenAI Whisper**, **Piper TTS** et **Gradio**.  
Conçu pour fonctionner hors ligne et offrir une expérience fluide sur PC ou microcontrôleur compatible.

---

## 🚀 Fonctionnalités principales

- 🎧 **Reconnaissance vocale (Speech-to-Text)**  
  Basée sur [Whisper](https://github.com/openai/whisper), avec accélération GPU (CUDA si disponible).

- 🗣️ **Synthèse vocale (Text-to-Speech)**  
  Propulsée par [Piper TTS](https://github.com/rhasspy/piper), pour une voix naturelle et rapide.

- 🧠 **Détection de mot-clé ("Hotword Detection")**  
  Utilise [Picovoice Porcupine](https://github.com/Picovoice/porcupine) pour activer l’écoute à la voix.

- 💬 **Interface graphique (UI)**  
  Développée avec [Gradio](https://gradio.app/) — une interface web moderne pour interagir avec l’assistant.

- 🧩 **Architecture modulaire**  
  Les modules de reconnaissance, synthèse, interface et gestion système sont indépendants et extensibles.

---

## 📁 Structure du projet

```
.
├── run.py                     # Point d'entrée principal
├── requirement.txt            # Dépendances Python
├── .gitignore                 # Fichiers/dossiers ignorés par Git
├── README.md                  # Ce fichier
├── CONTRIBUTING.md            # Guide de contribution
└── src/
    ├── main.py                # Classe principale AssistantVocal
    ├── core/                  # Logique interne (STT, TTS, hotword, etc.)
    ├── ui/                    # Interface Gradio / console
    ├── utils/                 # Outils : logger, config, monitoring
    └── config/                # Fichiers de configuration
```

---

## ⚙️ Installation

### 1️⃣ Cloner le dépôt

```bash
git clone https://github.com/<ton-utilisateur>/<ton-projet>.git
cd <ton-projet>
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirement.txt
```

> 💡 Pour de meilleures performances, installe PyTorch avec CUDA si ton GPU le supporte :
> [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

---

## ▶️ Utilisation

Lancer simplement :

```bash
python run.py
```

L’assistant :
- initialise la détection vocale,
- écoute le micro,
- transcrit les phrases détectées,
- répond via synthèse vocale et interface Gradio.

Les logs sont disponibles dans le fichier :
```
logs/assistant.log
```

---

## 🧰 Technologies principales

| Domaine | Bibliothèque |
|----------|---------------|
| Reconnaissance vocale | `openai-whisper` |
| Synthèse vocale | `piper-tts` |
| Détection mot-clé | `pvporcupine`, `pvrecorder` |
| Interface utilisateur | `gradio` |
| Monitoring système | `psutil` |
| Traitement audio | `pyaudio`, `librosa`, `numpy` |

---

## 🧪 Développement

### Lancer en mode debug

```bash
python run.py --debug
```

### Ajouter un module
Chaque module suit la même logique :
- définir une classe dédiée (ex: `SpeechRecognizer`, `TextToSpeech`)
- déclarer son interface publique
- l’enregistrer dans `AssistantVocal`

---

## 🧑‍💻 Contribuer

Les contributions sont bienvenues !  
Consultez le fichier [`CONTRIBUTING.md`](CONTRIBUTING.md) pour les bonnes pratiques et la gestion des issues/pull requests.

---

## 🪪 Licence

Ce projet est distribué sous licence MIT.  
Voir le fichier `LICENSE` (à ajouter si manquant).

---

## 🧩 Auteurs

- **Jean-Marc Renaud** — Créateur & développeur principal  
  Contributions ouvertes à toute personne souhaitant améliorer le projet.

---
