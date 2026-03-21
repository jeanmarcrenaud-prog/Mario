🎙️ Assistant Vocal Intelligent — Mario

Un assistant vocal local modulaire/MVC en Python : écoute, transcrit, répond et parle en utilisant OpenAI Whisper (STT), Piper (TTS), détection mot-clé (Vosk), Gradio (web), Console et ePaper. Adapté PC ou Raspberry Pi.

▶️🚀 Fonctionnalités
	🎧 Reconnaissance vocale (Whisper, GPU CUDA si dispo)

	🗣️ Synthèse vocale naturelle (Piper TTS)

	🧠 Détection mot-clé ("Hey Mario", vosk)

	🤖 **Intelligence Artificielle Complète**
		- **Auto-détection** Ollama → LM Studio → Simulation
		- **5+ modèles** LM Studio vs 1 Ollama disponibles
		- **Interface Gradio** avec contrôles LLM complets
		- **Changement dynamique** de modèle sans redémarrage
		- **Monitoring temps réel** : statut service, modèles, connexion
		- **Tests intégrés** de santé des services LLM

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
	5.🤖 **Intelligence** - Contrôles LLM complets (nouveau!)
		- Selection service (Ollama/LM Studio/Auto/Simulation)
		- Choix modèle dynamique avec refresh
		- Tests de connexion temps réel
		- Configuration créative (temperature, tokens)

🤖 Configuration Intelligence Artificielle

	Services Supportés:
	- **Ollama** (http://localhost:11434) - Service local prioritaire
	- **LM Studio** (http://localhost:1234) - Plus de modèles disponibles (5+ vs 1 Ollama)
	- **Mode Simulation** - Fallback intelligent sans service IA

	Auto-Détection Intelligente:
	- **Priorité** : Ollama (11434) → LM Studio (1234) → Simulation
	- **Sélection automatique** du premier service disponible
	- **Changement dynamique** de modèle sans redémarrage
	- **Monitoring temps réel** : statut, modèles, tests de santé

	Interface Gradio LLM (Onglet "🤖 Intelligence"):
	- Affichage service actif : Ollama/LM Studio/Simulation
	- Forçage service : Auto/Ollama/LM Studio/Simulation  
	- Liste modèles dynamique avec bouton refresh (🔄)
	- Tests connexion LLM (🧪) avec feedback temps réel
	- Configuration avancée : Créativité (temperature) + Tokens max

	Modèles Actifs:
	- **Ollama** : 1 modèle (minimax-m2:cloud)
	- **LM Studio** : 5 modèles (qwen3.5-9b, text-embedding-nomic, etc.)
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

	Mocks/Adapters : pour tests unitaires et debug offline

	🧪 Tests & Qualité Code
		- **320+ tests** (72%+ réussite, 27%+ coverage)
		- **Mypy type safety** : C+ (97% réduction erreurs, production-ready)
		- **Ruff lint** : 92% improvement, 0 bare except, 0 unused imports
		- Configuration CI/CD optimisée pour tests et linters

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
