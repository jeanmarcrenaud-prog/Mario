import gradio as gr
import threading
import numpy as np
import time
from typing import List, Dict, Optional
from pathlib import Path
from ..config import config
from ..core.wake_word_detector import WakeWordDetector
from ..core.speech_recognition import SpeechRecognizer
from ..core.text_to_speech import TextToSpeech
from ..core.llm_client import LLMClient
from ..utils.logger import logger
from ..utils.file_analyzer import FileAnalyzer
from ..utils.audio_player import AudioPlayer
from .interface_helpers import InterfaceHelpers
from .analysis_manager import AnalysisManager
import pyaudio

class AssistantInterface:
    def __init__(self, speech_recognizer= None, tts=None):
        self.wake_detector = WakeWordDetector()
        self.speech_recognizer = speech_recognizer or SpeechRecognizer()
        self.tts = tts
        logger.info("TextToSpeech initialisé")
        self.audio_player = AudioPlayer()  # Externalisé
        self.llm_client = LLMClient()
        self.file_analyzer = FileAnalyzer()
        self.helpers = InterfaceHelpers()  # Helper pour les opérations communes
        self.analysis_manager = AnalysisManager(self.file_analyzer, self.llm_client)  # Gestion analyse
        
        self.chat_history: List[Dict[str, str]] = []
        self.listening_thread: Optional[threading.Thread] = None
        self.current_ollama_model = ""
        self.current_piper_voice = ""
        self.current_speed = 1.0
        self.default_mic_index = 0
        self.is_running = False
        self.chat_update_lock = threading.Lock()
        self.demo = None
        
        self._initialize_components()

    def _initialize_components(self):
        """Initialise les composants principaux."""
        if not self.wake_detector.initialize_porcupine():
            logger.warning("Porcupine non initialisé")

    def create_interface(self) -> gr.Blocks:
        """Crée l'interface Gradio."""
        with gr.Blocks(title="Assistant Vocal", theme=self.helpers.get_theme()) as demo:
            self.demo = demo

            with gr.Row():
                with gr.Column(scale=1):
                    self._create_control_panel()
                with gr.Column(scale=3):
                    self._create_chat_interface()
                    self._create_file_analysis_section()

            self._setup_events()
            demo.load(
                self._auto_start_listening,
                inputs=self._get_load_inputs(),
                outputs=[self.status_text],
            )
        logger.info("Interface chargée et prête")
        self._announce_ready()
        return demo

    def _announce_ready(self):
        """Annonce que l'interface est prête."""
        self.tts.say("On démarre le chat, Mario")

    def _create_file_analysis_section(self):
        """Crée la section d'analyse de fichiers."""
        with gr.Accordion("[STATS] Analyse d'Arborescence", open=False):
            gr.Markdown("Analyser tous les fichiers texte d'un dossier et envoyer à Ollama")
            
            with gr.Row():
                self.analysis_path = gr.Textbox(
                    label="Chemin du dossier à analyser",
                    placeholder="/chemin/vers/le/dossier ou laissez vide pour le dossier courant",
                    value=str(Path.cwd())
                )
                self.analysis_btn = gr.Button("[RECHERCHE] Analyser", variant="secondary")
                self.send_to_ollama_btn = gr.Button("[IA] Analyser avec Ollama", variant="primary")
            
            with gr.Row():
                self.analysis_report = gr.Textbox(
                    label="Rapport d'analyse",
                    lines=10,
                    max_lines=20,
                    interactive=False,
                    show_copy_button=True
                )
            
            self.analysis_summary = gr.Textbox(
                label="Résumé vocal",
                lines=2,
                interactive=False
            )

    def _create_control_panel(self):
        """Crée le panneau de contrôle avec gestion robuste des périphériques audio."""
        import sounddevice as sd

        gr.Markdown("# [MICRO] Assistant Vocal")

        # --- Détection des périphériques d'entrée audio ---
        try:
            devices = sd.query_devices()
            mic_choices = [
                f"{i}: {d['name']}" for i, d in enumerate(devices)
                if d.get("max_input_channels", 0) > 0
            ]
        except Exception as e:
            logger.warning(f"[AUDIO] Impossible de récupérer la liste des microphones : {e}")
            mic_choices = []

        # --- Valeur par défaut sécurisée ---
        default_mic = mic_choices[0] if mic_choices else None
        if not mic_choices:
            logger.warning("[AUDIO] Aucun microphone détecté — l'enregistrement audio sera désactivé.")
            gr.Markdown("⚠️ **Aucun microphone détecté.** Veuillez en connecter un et redémarrer l'application.")

        # --- Composants principaux ---
        self.mic_dropdown = gr.Dropdown(
            label="Microphone",
            choices=mic_choices,
            value=default_mic,
            interactive=True,
        )

        self.whisper_model_dropdown = gr.Dropdown(
            label="Modèle Whisper",
            choices=["tiny", "base", "small", "medium", "large"],
            value="large",
        )

        self.piper_dropdown = gr.Dropdown(
            label="Voix Piper",
            choices=self.helpers.get_piper_voices(),
            value=config.DEFAULT_PIPER_VOICE,
        )

        self.ollama_dropdown = gr.Dropdown(
            label="Modèle Ollama",
            choices=self.helpers.get_ollama_models(),
            value=self.helpers.get_default_ollama_model(),
        )

        self.speed_slider = gr.Slider(
            label="Vitesse de parole", minimum=0.5, maximum=1.5, value=1.0, step=0.05
        )

        self.stop_btn = gr.Button("Arrêter l'écoute", variant="stop")
        self.restart_btn = gr.Button("Redémarrer l'écoute", variant="primary")

        self.status_text = gr.Textbox(
            label="Statut", lines=5, value="Initialisation...", interactive=False
        )

        # Composant visuel pour l’état du micro
        self.mic_status = gr.HTML(
            f"""
            <div style="padding:8px;border-radius:8px;background:#f4f4f4;margin-top:8px;">
              {'<span style="color:green;font-weight:bold;">🎙️ Microphone détecté</span>'
                if mic_choices else
               '<span style="color:red;font-weight:bold;">❌ Aucun microphone détecté</span>'}
            </div>
            """
        )

        def monitor_microphones():
            """Surveille la disponibilité des périphériques audio et met à jour dynamiquement l’interface."""
            previous_state = bool(mic_choices)

            while True:
                try:
                    devices = sd.query_devices()
                    has_input = any(d.get("max_input_channels", 0) > 0 for d in devices)

                    if has_input != previous_state:
                        previous_state = has_input
                        status_html = (
                            "<div style='color: green; font-weight: bold;'>🎙️ Microphone détecté</div>"
                            if has_input else
                            "<div style='color: red; font-weight: bold;'>❌ Aucun microphone détecté</div>"
                        )

                        logger.info(
                            "[AUDIO] État du microphone changé : %s",
                            "disponible" if has_input else "déconnecté"
                        )

                        # Rafraîchit le HTML via une file de mise à jour Gradio
                        self.mic_status.update(value=status_html)

                except Exception as e:
                    logger.warning(f"[AUDIO] Erreur de surveillance micro : {e}")

                time.sleep(5)  # vérifie toutes les 5 secondes

        # Thread en arrière-plan pour la surveillance
        threading.Thread(target=monitor_microphones, daemon=True).start()

    def _create_chat_interface(self):
        """Crée l'interface de chat."""
        self.chatbot = gr.Chatbot(label="Conversation", type="messages")

        self.user_input = gr.Textbox(
            label="Votre message", placeholder="Tapez votre message ici..."
        )

        self.file_upload = gr.File(
            label="Glissez-déposez un fichier texte ici",
            file_types=[".txt", ".py", ".md", ".json", ".csv", ".html", ".css", ".js", ".yaml", ".ini", ".log"],
            type="filepath"
        )

        self.refresh_btn = gr.Button("[ACTUALISER] Actualiser", visible=True)

    def _setup_events(self):
        """Configure les événements de l'interface."""
        # Événements de contrôle audio
        self.stop_btn.click(self._stop_listening, outputs=[self.status_text])
        self.restart_btn.click(
            self._restart_listening,
            inputs=self._get_restart_inputs(),
            outputs=[self.status_text],
        )

        # Événements de chat
        self.user_input.submit(
            self._handle_user_message,
            inputs=self._get_chat_inputs(),
            outputs=[self.chatbot, self.user_input],
        )

        # Événements de fichiers
        self.file_upload.change(
            self._handle_file_upload,
            inputs=[self.file_upload],
            outputs=[self.chatbot, self.user_input]
        )

        # Événements d'analyse
        self.analysis_btn.click(
            self._analyze_directory,
            inputs=[self.analysis_path],
            outputs=[self.analysis_report, self.analysis_summary]
        )

        self.send_to_ollama_btn.click(
            self._analyze_with_ollama,
            inputs=[self.analysis_path, self.ollama_dropdown],
            outputs=[self.analysis_report, self.analysis_summary, self.chatbot]
        )

        # Actualisation
        self.refresh_btn.click(
            lambda: self.chat_history_gradio,
            inputs=[],
            outputs=[self.chatbot]
        )

        # Configuration audio
        self._setup_audio_callbacks()

    def _get_load_inputs(self):
        """Retourne les inputs pour le chargement."""
        return [
            self.mic_dropdown,
            self.whisper_model_dropdown,
            self.piper_dropdown,
            self.ollama_dropdown,
            self.speed_slider,
        ]

    def _get_restart_inputs(self):
        """Retourne les inputs pour le redémarrage."""
        return self._get_load_inputs()

    def _get_chat_inputs(self):
        """Retourne les inputs pour le chat."""
        return [
            self.user_input,
            self.ollama_dropdown,
            self.piper_dropdown,
            self.speed_slider,
        ]

    def _analyze_with_ollama(self, path, ollama_model):
        """Analyse avec Ollama via le AnalysisManager."""
        try:
            result = self.analysis_manager.analyze_with_ollama(
                path, ollama_model, self.chat_update_lock
            )
            
            if result["error"]:
                return result["report"], result["summary"], self.chat_history_gradio
            
            # Mettre à jour le chat
            with self.chat_update_lock:
                self.chat_history.append({
                    "role": "assistant", 
                    "content": result["chat_message"]
                })
            
            return result["report"], result["summary"], self.chat_history_gradio
            
        except Exception as e:
            error_msg = f"[ERREUR] Erreur analyse Ollama : {str(e)}"
            logger.error(error_msg)
            return error_msg, "Erreur", self.chat_history_gradio

    def _analyze_directory(self, path):
        """Analyse simple d'arborescence."""
        try:
            result = self.analysis_manager.analyze_directory(path)
            
            if result["error"]:
                return result["report"], result["summary"]
            
            # Ajouter au chat
            with self.chat_update_lock:
                self.chat_history.append({
                    "role": "assistant", 
                    "content": f"[STATS] Analyse terminée : {result['summary']}"
                })
            
            return result["report"], result["summary"]
            
        except Exception as e:
            error_msg = f"[ERREUR] Erreur analyse : {str(e)}"
            logger.error(error_msg)
            return error_msg, "Erreur"

    def _handle_file_upload(self, filepath):
        """Traite l'upload de fichier."""
        try:
            if not filepath:
                return self.chat_history_gradio, ""
            
            result = self.analysis_manager.analyze_single_file(
                filepath, self.current_ollama_model, self.chat_update_lock
            )
            
            # Mettre à jour le chat
            with self.chat_update_lock:
                self.chat_history.append({"role": "user", "content": result["user_message"]})
                self.chat_history.append({"role": "assistant", "content": result["assistant_message"]})
            
            return self.chat_history_gradio, ""
            
        except Exception as e:
            logger.error(f"Erreur upload fichier : {e}")
            with self.chat_update_lock:
                self.chat_history.append({
                    "role": "assistant", 
                    "content": f"[ERREUR] Erreur upload : {str(e)}"
                })
            
            return self.chat_history_gradio, ""

    def _handle_user_message(self, message, ollama_model, piper_voice, speed):
        """Traite un message utilisateur."""
        if not message:
            return self.chat_history_gradio, ""

        with self.chat_update_lock:
            self.chat_history.append({"role": "user", "content": message})

        # Générer la réponse via LLM
        response = self.helpers.generate_llm_response(
            self.llm_client, ollama_model, self.chat_history
        )

        with self.chat_update_lock:
            self.chat_history.append({"role": "assistant", "content": response})

        # Synthèse vocale
        self.helpers.play_tts_response(
            self.tts, piper_voice, response, speed, self.audio_player
        )

        return self.chat_history_gradio, ""

    def _process_audio_input(self, audio_data: np.ndarray):
        """Traite l'audio capturé."""
        try:
            # Transcription
            text = self.helpers.transcribe_audio(self.speech_recognizer, audio_data)
            if not text:
                return

            # Détection commande analyse
            if self.helpers.is_analysis_command(text):
                self._handle_voice_analysis_command(text)
                return

            # Traitement chat normal
            with self.chat_update_lock:
                self.chat_history.append({"role": "user", "content": text})
            
            if self.chatbot:
                self.chatbot.value = self.chat_history_gradio
            
            # Génération réponse
            response = self.helpers.generate_llm_response(
                self.llm_client, self.current_ollama_model, [{"role": "user", "content": text}]
            )
            
            with self.chat_update_lock:
                self.chat_history.append({"role": "assistant", "content": response})
            
            if self.chatbot:
                self.chatbot.value = self.chat_history_gradio
            
            # Synthèse vocale
            self.helpers.play_tts_response(
                self.tts, self.current_piper_voice, response, self.current_speed, self.audio_player
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement audio: {e}")
            with self.chat_update_lock:
                self.chat_history.append({"role": "assistant", "content": f"[ERREUR] {str(e)}"})

    def _handle_voice_analysis_command(self, text):
        """Traite les commandes vocales d'analyse."""
        try:
            path = self.helpers.extract_path_from_command(text) or Path.cwd()
            
            result = self.analysis_manager.analyze_with_ollama(
                str(path), self.current_ollama_model, self.chat_update_lock
            )
            
            if not result["error"]:
                with self.chat_update_lock:
                    self.chat_history.append({
                        "role": "assistant", 
                        "content": result["chat_message"]
                    })
                
                if self.chatbot:
                    self.chatbot.value = self.chat_history_gradio
                
                # Synthèse vocale du résumé
                self.helpers.play_tts_response(
                    self.tts, self.current_piper_voice, result["summary"], 
                    self.current_speed, self.audio_player
                )
                
        except Exception as e:
            logger.error(f"Erreur commande vocale analyse: {e}")

    # Méthodes techniques (restent légères)
    def _setup_audio_callbacks(self):
        """Configure les callbacks audio."""
        self.wake_detector.set_wake_word_callback(
            lambda: logger.info("Mot-clé détecté!")
        )
        self.wake_detector.set_audio_callback(self._process_audio_input)

    def _auto_start_listening(self, mic_label, whisper_model, piper_voice, ollama_model, speed):
        """Démarrage automatique de l'écoute."""
        return self.helpers.auto_start_listening(
            self, mic_label, whisper_model, piper_voice, ollama_model, speed
        )

    def _start_listening_internal(self, mic_index: int):
        """Démarrage interne de l'écoute."""
        self.helpers.start_listening_internal(self.wake_detector, mic_index)

    def _stop_listening(self):
        """Arrêt de l'écoute."""
        return self.helpers.stop_listening(self.wake_detector)

    def _restart_listening(self, mic_label, whisper_model, piper_voice, ollama_model, speed):
        """Redémarrage de l'écoute."""
        return self.helpers.restart_listening(
            self, mic_label, whisper_model, piper_voice, ollama_model, speed
        )

    @property
    def chat_history_gradio(self):
        """Retourne l'historique du chat formaté pour Gradio."""
        with self.chat_update_lock:
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.chat_history
            ]

    def _get_chat_updates(self):
        """Retourne les mises à jour du chat."""
        return self.chat_history_gradio
