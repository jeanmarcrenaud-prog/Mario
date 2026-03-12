🎙️ Assistant Vocal Intelligent — Mario

Un assistant vocal local modulaire/MVC en Python : écoute, transcrit, répond et parle en utilisant OpenAI Whisper (STT), Piper (TTS), détection mot-clé (Vosk), Gradio (web), Console et ePaper. Adapté PC ou Raspberry Pi.

▶️🚀 Fonctionnalités
	🎧 Reconnaissance vocale (Whisper, GPU CUDA si dispo)

	🗣️ Synthèse vocale naturelle (Piper TTS)

	🧠 Détection mot-clé ("Hey Mario", vosk)

	🤖 **Intelligence Artificielle Intégrée**
		- Détection automatique Ollama/LM Studio
		- Rafraîchissement automatique des modèles LLM
		- Monitoring des services en temps réel
		- Support multi-modèles avec fallback

	💬 Interfaces graphiques : Gradio (web), Console, ePaper

	🧩 Architecture MVC modulaire — tous les modules sont extensibles et interchangeables

	🧪 Prêt pour les tests unitaires et utilisation de mocks (adapters/mock)

	🔄 Gestion historique, états de conversation, user profiles, settings
	
	🔧 Injection de dépendances — composition root pour assemblage propre

📁 Structure du projet
```
Mario/
├── .github/workflows       # GitHub Actions CI/CD
├── .gitattributes          # Configuration Git LFS
├── .gitignore              # Fichiers à ignorer
├── CONTRIBUTING.md         # Guide de contribution
├── README.md               # Ce fichier
├── config.yaml             # Configuration globale
├── prompts.json            # Prompts personnalisés
├── pyproject.toml          # Configuration Python/Poetry
├── pytest.ini              # Configuration pytest
├── requirements.txt        # Dépendances Python
│
├── voices/                 # Modèles vocaux TTS (Git LFS)
│   └── fr_FR-siwis-medium/
│
├── src/                    # Code source principal
│   ├── core/               # Services métier
│   │
│   ├── adapters/           # Interfaces matérielles/API
│   │   └── mock/           # Mocks pour tests
│   │
│   ├── services/           # Services (STT, TTS, Wake Word)
│   │
│   ├── interfaces/         # Interfaces (microphone, etc.)
│   │
│   ├── views/              # Interfaces utilisateur
│   │
│   ├── controllers/        # Contrôleurs principaux
│   │
│   ├── models/             # Modèles de données
│   │
│   ├── events/             # Système d'événements
│   │
│   └── config/             # Gestion configuration
│
└── tests/                  # Tests unitaires & fonctionnels
    ├── test_core/
    ├── test_services/       # Tests services (STT, TTS, Wake Word)
    ├── test_adapters/      # Tests adapters & mocks
    ├── test_ui/
    ├── test_models/
    └── test_performance/   # Tests de performance
```
```

▶️⚙️ Installation

	1.Clone le dépôt
		git clone https://github.com/jeanmarcrenaud-prog/Mario
		cd Mario

	2.Crée un environnement virtuel
		python -m venv venv
		source venv/bin/activate (Linux/macOS)
		venv\Scripts\activate (Windows)

	3.Installe les dépendances
		pip install -r requirements.txt

Astuce : Installe PyTorch avec CUDA pour booster Whisper si tu as un GPU (Instruction PyTorch)

▶️ Utilisation

	Lancer simplement :

		python run.py

	Ou en mode debug :
		python run.py --debug

▶️Interfaces disponibles

	Interface		Accès					Fonctionnalités
	🎤 Micro		Audio direct			Écoute, transcription, réponse vocale
	💻 Console		Terminal				Chat texte, commandes, debug
	🌐 Web			http://localhost:7860	Interface complète avec onglets
	📱 ePaper		Matériel				Affichage physique minimaliste
	
	Onglets Web Disponibles
	1.💬 Conversation - Chat vocal avec historique
	2.📁 Fichiers - Analyse de fichiers et projets
	3.🎯 Prompts - Création de prompts personnalisés
	4.🔧 Paramètres - Configuration système et performance
	5.🧠 **LLM Monitor** - Surveillance des modèles IA (nouveau!)

🤖 Configuration Intelligence Artificielle

	Services Supportés:
	- **Ollama** (http://localhost:11434) - Recommandé pour l'IA locale
	- **LM Studio** (http://localhost:1234) - Alternative robuste
	- **Mode Simulation** - Fallback sans service IA

	Configuration automatique:
	- Détection des services en cours d'exécution
	- Sélection intelligente du modèle actif
	- Rafraîchissement automatique au démarrage
	- Monitoring temps réel dans l'interface

	Modèles par défaut:
	- Ollama: "minimax-m2:cloud"
	- LM Studio: "qwen/qwen3.5-9b"
	- Configuration dans config.yaml


🧰 Technologies principales

	Domaine					Bibliothèque
	Reconnaissance vocale	openai-whisper
	Synthèse vocale			piper-tts
	Détection mot-clé		vosk
	GUI/Web					gradio
	Audio HW				sounddevice, pyaudio
	Monitoring système		psutil
	Audio/NumPy				numpy, librosa

🧪 Développement & Extensions

	Approche MVC — chaque partie est interchangeable (service, vue, contrôleur, modèle)
	
	Injection de dépendances — composition root dans src/core/app_factory.py

	Mocks/Adapters : pour tests unitaires et debug offline

	Ajout d'un module :

	Créer sa classe dans le dossier adapté

	Implémenter l'interface appropriée (ITTSAdapter, ISpeechRecognitionAdapter, etc.)

	Enregistrer dans la factory app_factory.py

	Configuration dynamique (YAML)

🧑‍💻 Contribuer

	Contributions bienvenues !
	Consulte le fichier CONTRIBUTING.md

🪪 Licence	

	Licence MIT.

🧩 Auteur

	Jean-Marc Renaud — Créateur et développeur principal.
