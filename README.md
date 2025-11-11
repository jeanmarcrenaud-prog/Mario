🎙️ Assistant Vocal Intelligent — Mario

Un assistant vocal local modulaire/MVC en Python : écoute, transcrit, répond et parle en utilisant OpenAI Whisper (STT), Piper (TTS), Picovoice Porcupine (détection mot-clé), Gradio (web), Console et ePaper. Adapté PC ou microcontrôleur.

▶️🚀 Fonctionnalités
	🎧 Reconnaissance vocale (Whisper, GPU CUDA si dispo)

	🗣️ Synthèse vocale naturelle (Piper TTS)

	🧠 Détection mot-clé ("Hey Mario", Porcupine)

	💬 Interfaces graphiques : Gradio (web), Console, ePaper

	🧩 Architecture MVC modulaire — tous les modules sont extensibles et interchangeables

	🧪 Prêt pour les tests unitaires et utilisation de mocks (adapters/mock)

	🔄 Gestion historique, états de conversation, user profiles, settings

📁 Structure du projet
	text
	src/
	├─ core/           # Services métier : conversation, STT, TTS, intent, wake word
	├─ adapters/       # Interfaces matérielles/API (micro, haut-parleur, ePaper, OpenAI)
	├─ ui/             # Vues : web (Gradio), console, epaper
	├─ controllers/    # Contrôleurs principaux (Assistant, Settings)
	├─ models/         # Modèles : user, conversation_state, settings
	├─ events/         # Events, bus de communication
	├─ config/         # Fichiers de configuration YAML
	├─ tests/          # Unit tests, mocks et factories
	run.py             # Point d’entrée principal
	requirements.txt   # Dépendances
	README.md
	CONTRIBUTING.md

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


🧰 Technologies principales

	Domaine					Bibliothèque
	Reconnaissance vocale	openai-whisper
	Synthèse vocale			piper-tts
	Détection mot-clé		pvporcupine, pvrecorder
	GUI/Web					gradio
	Audio HW				sounddevice, pyaudio
	Monitoring système		psutil
	Audio/NumPy				numpy, librosa

🧪 Développement & Extensions

	Approche MVC — chaque partie est interchangeable (service, vue, contrôleur, modèle)

	Mocks/Adapters : pour tests unitaires et debug offline

	Ajout d'un module :

	Créer sa classe dans le dossier adapté

	Respecter l’interface publique

	L’enregistrer dans le contrôleur métier ou assistant vocal

	Configuration dynamique (YAML)

🧑‍💻 Contribuer

	Contributions bienvenues !
	Consulte le fichier CONTRIBUTING.md

🪪 Licence	

	Licence MIT.

🧩 Auteur

	Jean-Marc Renaud — Créateur et développeur principal.
