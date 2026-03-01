"""
Interface Web Gradio pour l'Assistant Vocal Intelligent
"""

import gradio as gr
from gradio import themes
import threading
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from src.utils.logger import logger
from src.services.audio_controller import AudioController

class GradioWebInterface:
    """
    Interface web Gradio avancée pour l'assistant vocal.
    """
    
    def __init__(self, assistant_controller):
        self.assistant = assistant_controller
        self.demo = None
        self.chat_history = []
        self.audio_controller = AudioController()
        self._initialize_components()
        logger.info("GradioWebInterface initialisé")
    
    def _initialize_components(self):
        """Initialise les composants de l'interface."""
        self.app_state = None
        self.status_text = None
        self.system_stats = None
        self.chatbot = None
        self.user_input = None
        # ... autres composants
    
    def create_interface(self) -> gr.Blocks:
        """Crée l'interface Gradio complète."""
        with gr.Blocks(title="Assistant Vocal Intelligent") as demo:
            self.demo = demo
            self._setup_state()
            self._create_layout()
            self._setup_events()
            demo.load(self._on_interface_load, outputs=[self.status_text, self.system_stats])
        
        logger.info("Interface Gradio créée")
        return demo
    
    def _setup_state(self):
        """Configure l'état de l'application."""
        self.app_state = gr.State({
            "is_listening": False,
            "current_model": self.assistant.settings.llm_model,
            "current_voice": self.assistant.settings.voice_name,
            "recording": False
        })
    
    def _create_layout(self):
        """Crée la disposition principale de l'interface."""
        self._create_header()
        with gr.Row():
            with gr.Column(scale=1):
                self._create_control_panel()
            with gr.Column(scale=3):
                self._create_main_tabs()
    
    def _create_header(self):
        """Crée l'en-tête de l'interface."""
        gr.HTML("""
        <style>
            .header-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header-title {
                font-size: 2.5em;
                font-weight: bold;
                color: white;
                margin: 0;
            }
            .header-subtitle {
                font-size: 1.2em;
                color: rgba(255,255,255,0.9);
                margin-top: 5px;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-ready { background-color: #22c55e; }
            .status-listening { background-color: #3b82f6; animation: pulse 1s infinite; }
            .status-processing { background-color: #f59e0b; animation: pulse 0.5s infinite; }
            .status-error { background-color: #ef4444; }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .dark .header-container {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            }
        </style>
        <div class="header-container">
            <h1 class="header-title">🎤 Assistant Vocal Intelligent</h1>
            <p class="header-subtitle">Votre compagnon IA avec reconnaissance et synthèse vocale</p>
        </div>
        """)
    
    def _create_control_panel(self):
        """Crée le panneau de contrôle."""
        gr.Markdown("## ⚙️ Configuration")
        
        with gr.Row():
            self.theme_toggle = gr.Button("🌙 Mode Sombre", size="sm")
        
        self._create_status_section()
        self._create_audio_controls()
        self._create_ai_controls()
        self._create_system_stats()
    
    def _create_status_section(self):
        """Crée la section de statut."""
        with gr.Group():
            self.status_text = gr.Textbox(
                label="📊 Statut",
                lines=4,
                value="🟢 Interface chargée - Prêt à démarrer",
                interactive=False
            )
            
            with gr.Row():
                self.start_btn = gr.Button("▶️ Démarrer", variant="primary", scale=1)
                self.stop_btn = gr.Button("⏹️ Arrêter", variant="stop", scale=1)
    
    def _create_audio_controls(self):
        """Crée les contrôles audio."""
        with gr.Accordion("🎤 Audio", open=True):
            self.mic_dropdown = gr.Dropdown(
                label="Microphone",
                choices=self._get_microphone_choices(),
                value=self._get_default_microphone(),
                interactive=True
            )
            
            self.voice_dropdown = gr.Dropdown(
                label="🗣️ Voix",
                choices=self._get_voice_choices(),
                value=self._get_default_voice(),
                interactive=True
            )
            
            self.speed_slider = gr.Slider(
                label="⏩ Vitesse de parole",
                minimum=0.5,
                maximum=2.0,
                value=1.0,
                step=0.1
            )
    
    def _create_ai_controls(self):
        """Crée les contrôles d'intelligence artificielle."""
        with gr.Accordion("🤖 Intelligence", open=True):
            self.model_dropdown = gr.Dropdown(
                label="Modèle IA",
                choices=self._get_model_choices(),
                value=self._get_default_model(),
                interactive=True
            )
            
            self.temperature_slider = gr.Slider(
                label="🌡️ Créativité",
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.1
            )
    
    def _create_system_stats(self):
        """Crée la section des statistiques système."""
        with gr.Group():
            self.system_stats = gr.Textbox(
                label="🖥️ Système",
                lines=3,
                interactive=False
            )
            
            self.refresh_stats_btn = gr.Button("🔄 Actualiser stats", size="sm")
    
    def _create_main_tabs(self):
        """Crée les onglets principaux."""
        with gr.Tabs():
            self._create_conversation_tab()
            self._create_files_tab()
            self._create_prompts_tab()
            self._create_settings_tab()
    
    def _create_conversation_tab(self):
        """Crée l'onglet de conversation."""
        with gr.Tab("💬 Conversation"):
            self._build_chat_interface()
            self._build_voice_commands()
    
    def _build_chat_interface(self):
        """Construit l'interface de chat."""
        self.chatbot = gr.Chatbot(label="Discussion", height=400)
        
        with gr.Row():
            self.user_input = gr.Textbox(
                label="Votre message",
                placeholder="Tapez votre message ou parlez après avoir dit 'Mario'...",
                scale=4,
                lines=2
            )
            
            with gr.Column(scale=1):
                self.send_btn = gr.Button("📤 Envoyer", variant="primary")
                self.clear_btn = gr.Button("🧹 Effacer", size="sm")
                self.refresh_chat_btn = gr.Button("🔄 Actualiser", size="sm")
    
    def _build_voice_commands(self):
        """Construit les commandes vocales."""
        with gr.Group():
            gr.Markdown("### 🎤 Commandes vocales")
            with gr.Row():
                self.record_btn = gr.Button("🎤 Enregistrer", variant="secondary")
                self.listen_btn = gr.Button("👂 Écouter", variant="secondary")
            
            self.voice_command_status = gr.Textbox(
                label="Statut vocal",
                value="Prêt",
                interactive=False
            )
    
    def _create_files_tab(self):
        """Crée l'onglet de gestion des fichiers."""
        with gr.Tab("📁 Fichiers"):
            self._build_file_analysis_interface()
            self._build_project_analysis_interface()
            self._build_analysis_history()
    
    def _build_file_analysis_interface(self):
        """Construit l'interface d'analyse de fichiers."""
        gr.Markdown("## 📁 Analyse de fichiers et projets avec IA")
        
        with gr.Tabs():
            with gr.Tab("📄 Fichiers individuels"):
                with gr.Row():
                    with gr.Column():
                        self.file_upload = gr.File(
                            label="Glissez-déposez des fichiers",
                            file_types=[".txt", ".py", ".md", ".json", ".csv", ".html", ".css", ".js"],
                            type="filepath"
                        )
                        
                        with gr.Row():
                            self.analyze_btn = gr.Button("🔍 Analyser avec IA", variant="primary")
                            self.summarize_btn = gr.Button("📝 Résumer", variant="secondary")
                    
                    with gr.Column():
                        self.file_result = gr.Textbox(
                            label="Résultat de l'analyse",
                            lines=10,
                            interactive=False
                        )
    
    def _build_project_analysis_interface(self):
        """Construit l'interface d'analyse de projets."""
        with gr.Tab("🏗️ Projets complets"):
            with gr.Row():
                with gr.Column():
                    self._build_project_input_section()
                    self._build_project_analysis_controls()
                
                with gr.Column():
                    self.project_result = gr.Textbox(
                        label="Rapport d'analyse du projet",
                        lines=15,
                        interactive=False
                    )
            
            self._build_project_summary_section()
    
    def _build_project_input_section(self):
        """Construit la section d'entrée du projet."""
        self.project_path = gr.Textbox(
            label="Chemin du projet",
            placeholder="C:/chemin/vers/votre/projet ou laissez vide pour le dossier courant",
            value=".",
            interactive=True
        )
        
        self.current_dir_btn = gr.Button("📂 Utiliser dossier courant", size="sm")
    
    def _build_project_analysis_controls(self):
        """Construit les contrôles d'analyse de projet."""
        with gr.Row():
            self.analyze_project_btn = gr.Button("🔍 Analyser projet", variant="primary", scale=2)
            self.export_json_btn = gr.Button("💾 Export JSON", scale=1)
            self.export_md_btn = gr.Button("📄 Export Markdown", scale=1)
        
        self.project_depth = gr.Slider(
            label="Profondeur d'analyse",
            minimum=1,
            maximum=5,
            value=2,
            step=1
        )
    
    def _build_project_summary_section(self):
        """Construit la section de résumé du projet."""
        with gr.Group():
            gr.Markdown("### 📊 Résumé de l'analyse")
            with gr.Row():
                self.project_summary = gr.Textbox(
                    label="Résumé",
                    lines=3,
                    interactive=False
                )
            
            with gr.Row():
                self.key_points = gr.Dataframe(
                    label="Points clés",
                    headers=["Point important"],
                    datatype=["str"],
                    interactive=False
                )
    
    def _build_analysis_history(self):
        """Construit l'historique des analyses."""
        gr.Markdown("### 📈 Historique des analyses")
        self.analysis_history = gr.Dataframe(
            label="Analyses récentes",
            headers=["Type", "Cible", "Date", "Statut"],
            datatype=["str", "str", "str", "str"],
            interactive=False
        )
    
    def _create_prompts_tab(self):
        """Crée l'onglet de gestion des prompts personnalisés."""
        with gr.Tab("🎯 Prompts"):
            self._build_prompt_library()
            self._build_prompt_editor()
            self._build_prompt_preview()
            self._build_prompt_advanced_config()
    
    def _build_prompt_library(self):
        """Construit la bibliothèque de prompts."""
        gr.Markdown("## 🎯 Prompts Personnalisés")
        gr.Markdown("Créez et utilisez des prompts spécialisés pour des tâches récurrentes.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Bibliothèque de Prompts")
                self.prompt_list = gr.Dropdown(
                    label="Prompts sauvegardés",
                    choices=self._get_saved_prompts(),
                    interactive=True
                )
                
                with gr.Row():
                    self.load_prompt_btn = gr.Button("📥 Charger")
                    self.delete_prompt_btn = gr.Button("🗑️ Supprimer")
                
                self._build_prompt_categories()
    
    def _build_prompt_categories(self):
        """Construit les catégories de prompts."""
        prompt_categories = [
            "Analyse de code", "Résumé de texte", "Explication technique",
            "Génération de documentation", "Correction de bugs",
            "Optimisation de code", "Traduction", "Création de contenu"
        ]
        
        self.prompt_category = gr.Dropdown(
            label="Catégorie",
            choices=prompt_categories,
            value="Analyse de code",
            interactive=True
        )
    
    def _build_prompt_editor(self):
        """Construit l'éditeur de prompts."""
        with gr.Column(scale=2):
            gr.Markdown("### ✏️ Création/Édition de Prompt")
            self.prompt_name = gr.Textbox(
                label="Nom du prompt",
                placeholder="Ex: Analyse code Python",
                max_lines=1
            )
            
            self.prompt_description = gr.Textbox(
                label="Description",
                placeholder="Description courte de ce que fait ce prompt",
                lines=2
            )
            
            self.prompt_template = gr.Textbox(
                label="Template du prompt",
                placeholder=self._get_prompt_template_placeholder(),
                lines=10,
                max_lines=15
            )
            
            self._build_prompt_variables_editor()
    
    def _get_prompt_template_placeholder(self) -> str:
        """Retourne le placeholder pour le template de prompt."""
        return """Utilisez {input} pour le contenu utilisateur
Exemple:
Analysez ce code et expliquez sa fonction:
{input}

Fournissez:
1. Résumé de la fonctionnalité
2. Points clés de l'implémentation
3. Suggestions d'amélioration"""
    
    def _build_prompt_variables_editor(self):
        """Construit l'éditeur de variables de prompt."""
        gr.Markdown("### 📝 Variables personnalisées")
        self.prompt_variables = gr.Textbox(
            label="Variables supplémentaires (séparées par des virgules)",
            placeholder="langage,framework,version",
            value=""
        )
        
        with gr.Row():
            self.save_prompt_btn = gr.Button("💾 Sauvegarder", variant="primary")
            self.test_prompt_btn = gr.Button("🧪 Tester")
            self.clear_prompt_btn = gr.Button("🧹 Effacer")
    
    def _build_prompt_preview(self):
        """Construit la prévisualisation du prompt."""
        with gr.Group():
            gr.Markdown("### 🎯 Test du Prompt")
            
            with gr.Row():
                self._build_prompt_input_section()
                self._build_prompt_preview_section()
            
            self.prompt_test_result = gr.Textbox(
                label="Résultat du test",
                lines=6,
                interactive=False
            )
            
            self.use_in_chat_btn = gr.Button("💬 Utiliser dans le chat")
    
    def _build_prompt_input_section(self):
        """Construit la section d'entrée du prompt."""
        with gr.Column():
            self.prompt_input = gr.Textbox(
                label="Contenu d'entrée",
                placeholder="Entrez le texte/code à analyser...",
                lines=5
            )
            
            self.prompt_custom_vars = gr.Textbox(
                label="Valeurs des variables (format: var1=valeur1,var2=valeur2)",
                placeholder="langage=Python,framework=FastAPI",
                lines=2
            )
    
    def _build_prompt_preview_section(self):
        """Construit la section de prévisualisation du prompt."""
        with gr.Column():
            self.prompt_preview = gr.Textbox(
                label="Prompt généré",
                lines=8,
                interactive=False
            )
    
    def _build_prompt_advanced_config(self):
        """Construit la configuration avancée des prompts."""
        with gr.Accordion("⚙️ Configuration avancée", open=False):
            with gr.Row():
                self.prompt_temperature = gr.Slider(
                    label="Température",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1
                )
                
                self.prompt_max_tokens = gr.Number(
                    label="Tokens maximum",
                    value=2000,
                    precision=0
                )
            
            self.prompt_system_message = gr.Textbox(
                label="Message système (optionnel)",
                placeholder="Instructions supplémentaires pour l'IA",
                lines=3
            )
        
        self._setup_prompt_events()
    
    def _create_settings_tab(self):
        """Crée l'onglet des paramètres avancés."""
        with gr.Tab("🔧 Paramètres"):
            self._build_settings_interface()
    
    def _build_settings_interface(self):
        """Construit l'interface des paramètres."""
        gr.Markdown("## 🔧 Paramètres avancés")
        
        with gr.Tabs():
            self._build_system_settings_tab()
            self._build_audio_settings_tab()
            self._build_monitoring_tab()
            self._build_logs_tab()
    
    def _build_system_settings_tab(self):
        """Construit l'onglet de configuration système."""
        with gr.Tab("🖥️ Système"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🎛️ Paramètres système")
                    self.auto_start_checkbox = gr.Checkbox(
                        label="Démarrage automatique",
                        value=True
                    )
                    
                    self.web_port_number = gr.Number(
                        label="Port Web",
                        value=self.assistant.settings.web_port,
                        precision=0
                    )
                    
                    self.save_settings_btn = gr.Button("💾 Sauvegarder")
                
                with gr.Column():
                    gr.Markdown("### 📈 Performance")
                    self.performance_info = gr.Textbox(
                        label="Informations de performance",
                        lines=8,
                        interactive=False
                    )
                    
                    with gr.Row():
                        self.test_all_btn = gr.Button("🧪 Tester tous les services")
                        self.optimize_btn = gr.Button("⚡ Optimiser", variant="primary")
    
    def _build_audio_settings_tab(self):
        """Construit l'onglet de configuration audio."""
        with gr.Tab("🔊 Audio"):
            self._build_audio_configuration()
    
    def _build_audio_configuration(self):
        """Construit la configuration audio complète."""
        gr.Markdown("### 🔊 Configuration Audio")
        
        with gr.Row():
            self._build_audio_input_section()
            self._build_audio_output_section()
        
        self._build_advanced_audio_settings()
        self._build_audio_control_buttons()
        self._setup_audio_events()
    
    def _build_audio_input_section(self):
        """Construit la section d'entrée audio."""
        with gr.Column():
            gr.Markdown("#### 🎤 Entrée Audio")
            self.audio_mic_dropdown = gr.Dropdown(
                label="Microphone (périphériques recommandés)",
                choices=self._get_microphone_choices(),
                value=self._get_default_microphone(),
                interactive=True,
                allow_custom_value=True
            )
            
            self.show_all_mics_btn = gr.Button("🔍 Voir tous les microphones", size="sm")
            self.all_mics_dropdown = gr.Dropdown(
                label="Tous les microphones (avancé)",
                choices=self._get_all_audio_devices("input"),
                visible=False,
                interactive=True,
                allow_custom_value=True
            )
            
            self.test_mic_btn = gr.Button("🎤 Tester le microphone", variant="secondary")
            self.mic_test_status = gr.Textbox(
                label="Test microphone",
                lines=2,
                interactive=False,
                value="Cliquez pour tester"
            )
    
    def _build_audio_output_section(self):
        """Construit la section de sortie audio."""
        with gr.Column():
            gr.Markdown("#### 🔈 Sortie Audio")
            self.audio_output_dropdown = gr.Dropdown(
                label="Sortie audio (périphériques recommandés)",
                choices=self._get_audio_output_choices(),
                value=self._get_default_audio_output(),
                interactive=True
            )
            
            self.show_all_outputs_btn = gr.Button("🔍 Voir toutes les sorties", size="sm")
            self.all_outputs_dropdown = gr.Dropdown(
                label="Toutes les sorties audio (avancé)",
                choices=self._get_all_audio_devices("output"),
                visible=False,
                interactive=True
            )
            
            self.test_speaker_btn = gr.Button("🔊 Tester la sortie", variant="secondary")
            self.speaker_test_status = gr.Textbox(
                label="Test sortie audio",
                lines=2,
                interactive=False,
                value="Cliquez pour tester"
            )
    
    def _build_advanced_audio_settings(self):
        """Construit les paramètres audio avancés."""
        with gr.Accordion("⚙️ Paramètres audio avancés", open=False):
            with gr.Row():
                self.audio_volume = gr.Slider(
                    label="🔊 Volume général",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.8,
                    step=0.1
                )
                
                self.mic_sensitivity = gr.Slider(
                    label="🎤 Sensibilité microphone",
                    minimum=0.1,
                    maximum=2.0,
                    value=1.0,
                    step=0.1
                )
            
            with gr.Row():
                self.silence_delay = gr.Slider(
                    label="⏱️ Délai de silence (secondes)",
                    minimum=0.5,
                    maximum=5.0,
                    value=2.0,
                    step=0.5
                )
                
                self.vad_threshold = gr.Slider(
                    label="📊 Seuil détection vocale",
                    minimum=0.1,
                    maximum=0.9,
                    value=0.5,
                    step=0.1
                )
    
    def _build_audio_control_buttons(self):
        """Construit les boutons de contrôle audio."""
        with gr.Row():
            self.save_audio_btn = gr.Button("💾 Sauvegarder paramètres audio", variant="primary")
            self.apply_audio_btn = gr.Button("🔄 Appliquer maintenant")
            self.reset_audio_btn = gr.Button("🔄 Réinitialiser")
        
        self.audio_settings_status = gr.Textbox(
            label="Statut audio",
            lines=3,
            interactive=False,
            value="Configuration audio prête"
        )
    
    def _build_monitoring_tab(self):
        """Construit l'onglet de monitoring."""
        with gr.Tab("📊 Monitoring"):
            self._build_monitoring_interface()
    
    def _build_monitoring_interface(self):
        """Construit l'interface de monitoring."""
        gr.Markdown("### 📊 Statistiques en temps réel")
        
        with gr.Row():
            self.resource_usage = gr.Textbox(
                label="Utilisation des ressources",
                lines=8,
                interactive=False
            )
        
        with gr.Row():
            with gr.Column():
                self.system_health = gr.Textbox(
                    label="Santé du système",
                    lines=4,
                    interactive=False
                )
            with gr.Column():
                self.trend_analysis = gr.Textbox(
                    label="Analyse des tendances",
                    lines=4,
                    interactive=False
                )
        
        with gr.Row():
            self.refresh_performance_btn = gr.Button("🔄 Actualiser")
            self.detailed_report_btn = gr.Button("📋 Rapport détaillé")
            self.aggressive_optimize_btn = gr.Button("🧨 Optimisation agressive", variant="secondary")
        
        self._build_threshold_configuration()
    
    def _build_threshold_configuration(self):
        """Construit la configuration des seuils."""
        gr.Markdown("### ⚙️ Configuration des seuils")
        with gr.Row():
            self.cpu_threshold = gr.Number(label="Seuil CPU (%)", value=80, precision=0)
            self.memory_threshold = gr.Number(label="Seuil Mémoire (%)", value=85, precision=0)
            self.gpu_threshold = gr.Number(label="Seuil GPU (%)", value=85, precision=0)
        
        self.update_thresholds_btn = gr.Button("💾 Mettre à jour seuils")
    
    def _build_logs_tab(self):
        """Construit l'onglet des logs."""
        with gr.Tab("📜 Logs"):
            self._build_logs_interface()
    
    def _build_logs_interface(self):
        """Construit l'interface des logs."""
        self.logs_display = gr.Textbox(
            label="Logs en temps réel",
            lines=12,
            interactive=False,
            max_lines=20
        )
        
        with gr.Row():
            self.log_level = gr.Dropdown(
                label="Niveau de log",
                choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                value="INFO"
            )
            self.clear_logs_btn = gr.Button("🗑️ Effacer logs")
    
    # === Méthodes utilitaires ===
    
    def _setup_events(self):
        """Configure tous les événements de l'interface."""
        self._setup_main_control_events()
        self._setup_chat_events()
        self._setup_file_events()
        self._setup_audio_events()
        self._setup_settings_events()
        self._setup_performance_events()
    
    def _setup_main_control_events(self):
        """Configure les événements des contrôles principaux."""
        self.start_btn.click(
            self._start_assistant,
            inputs=[self.mic_dropdown, self.voice_dropdown, self.model_dropdown, self.speed_slider],
            outputs=[self.status_text]
        )
        
        self.stop_btn.click(
            self._stop_assistant,
            outputs=[self.status_text]
        )
    
    def _setup_chat_events(self):
        """Configure les événements du chat."""
        self.user_input.submit(
            self._handle_user_message,
            inputs=[self.user_input, self.model_dropdown, self.temperature_slider],
            outputs=[self.chatbot, self.user_input, self.status_text],
            show_progress=True
        )
        
        self.send_btn.click(
            self._handle_user_message,
            inputs=[self.user_input, self.model_dropdown, self.temperature_slider],
            outputs=[self.chatbot, self.user_input, self.status_text],
            show_progress=True
        )
        
        self.clear_btn.click(
            self._clear_conversation,
            outputs=[self.chatbot, self.status_text]
        )
        
        self.refresh_chat_btn.click(
            self._refresh_chat,
            outputs=[self.chatbot]
        )
    
    def _setup_file_events(self):
        """Configure les événements de gestion des fichiers."""
        self.file_upload.change(
            self._handle_file_upload,
            inputs=[self.file_upload],
            outputs=[self.file_result, self.status_text]
        )
        
        self.analyze_btn.click(
            self._analyze_files_with_ai,
            inputs=[self.file_upload, self.model_dropdown],
            outputs=[self.file_result, self.status_text]
        )
        
        self.summarize_btn.click(
            self._summarize_file,
            inputs=[self.file_upload, self.model_dropdown],
            outputs=[self.file_result, self.status_text]
        )
        
        self.analyze_project_btn.click(
            self._analyze_project,
            inputs=[self.project_path, self.project_depth],
            outputs=[self.project_result, self.project_summary, self.key_points, self.status_text]
        )
        
        self.export_json_btn.click(
            self._export_project_analysis,
            inputs=[self.project_path, gr.State("json")],
            outputs=[self.file_result, self.status_text]
        )
        
        self.export_md_btn.click(
            self._export_project_analysis,
            inputs=[self.project_path, gr.State("markdown")],
            outputs=[self.file_result, self.status_text]
        )
        
        self.current_dir_btn.click(
            self._get_current_directory,
            outputs=[self.project_path, self.status_text]
        )
    
    def _setup_settings_events(self):
        """Configure les événements des paramètres."""
        self.save_settings_btn.click(
            self._save_settings,
            inputs=[self.auto_start_checkbox, self.web_port_number],
            outputs=[self.status_text]
        )
        
        self.test_all_btn.click(
            self._test_all_services,
            outputs=[self.performance_info, self.status_text]
        )
        
        self.optimize_btn.click(
            self._optimize_performance,
            outputs=[self.performance_info, self.status_text]
        )
        
        self.refresh_stats_btn.click(
            self._update_system_stats,
            outputs=[self.system_stats, self.status_text]
        )
    
    def _setup_performance_events(self):
        """Configure les événements de performance."""
        self.refresh_performance_btn.click(
            self._refresh_performance,
            outputs=[self.resource_usage, self.status_text]
        )
        
        self.detailed_report_btn.click(
            self._get_detailed_performance_report,
            outputs=[self.resource_usage, self.system_health, self.trend_analysis, self.status_text]
        )

        self.aggressive_optimize_btn.click(
            self._aggressive_optimize,
            outputs=[self.performance_info, self.status_text]
        )

        self.update_thresholds_btn.click(
            self._update_thresholds,
            inputs=[self.cpu_threshold, self.memory_threshold, self.gpu_threshold],
            outputs=[self.status_text]
        )
    
    # === Méthodes de callback ===
    
    def _on_interface_load(self) -> Tuple[str, str]:
        """Callback au chargement de l'interface."""
        status = "🟢 Interface chargée - Assistant prêt"
        stats = self._get_system_stats_text()
        return status, stats
    
    def _start_assistant(self, mic_index: str, voice: str, model: str, speed: float) -> str:
        """Démarre l'assistant avec configuration."""
        try:
            self.assistant.settings.voice_name = voice
            self.assistant.settings.llm_model = model
            self.assistant.wake_word_service.start_detection(int(mic_index.split(':')[0]))
            return "▶️ Assistant démarré - En attente du mot-clé 'Mario'"
        except Exception as e:
            logger.error(f"Erreur démarrage: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _stop_assistant(self) -> str:
        """Arrête l'assistant."""
        try:
            self.assistant.wake_word_service.stop_detection()
            return "⏹️ Assistant arrêté"
        except Exception as e:
            logger.error(f"Erreur arrêt: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _handle_user_message(self, message: str, model: str, temperature: float) -> Tuple[List, str, str]:
        """Traite un message utilisateur."""
        if not message or not message.strip():
            return self._get_chat_history(), "", "📝 Message vide ignoré"
        
        try:
            if model != self.assistant.settings.llm_model:
                self.assistant.llm_service.set_model(model)
                self.assistant.settings.llm_model = model
            
            response = self.assistant.process_user_message(message)
            self.assistant.speak_response(response)
            updated_history = self._refresh_conversation()
            
            status = f"✅ Réponse générée ({len(response)} caractères)"
            return self._get_chat_history(), "", status
            
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            error_msg = "[ERREUR] Impossible de traiter votre message"
            status = f"❌ Erreur: {str(e)}"
            error_history = self._get_chat_history() + [{"role": "assistant", "content": error_msg}]
            return error_history, "", status
    
    def _clear_conversation(self) -> Tuple[List, str]:
        """Efface la conversation."""
        try:
            self.assistant.clear_conversation()
            return [], "🧹 Conversation effacée"
        except Exception as e:
            logger.error(f"Erreur effacement conversation: {e}")
            return self._get_chat_history(), f"❌ Erreur: {str(e)}"
    
    def _refresh_conversation(self) -> List:
        """Rafraîchit la conversation."""
        try:
            history = self.assistant.get_conversation_history()
            formatted_history = []
            
            for msg in history:
                if isinstance(msg, dict):
                    role = msg.get("role", "")
                    content = msg.get("content", "").strip()
                    
                    if content:
                        if role == "user":
                            formatted_history.append([content, None])
                        elif role == "assistant":
                            if formatted_history and formatted_history[-1][1] is None:
                                formatted_history[-1][1] = content
                            else:
                                formatted_history.append([None, content])
            
            logger.info(f"✅ Conversation rafraîchie - {len(formatted_history)} messages")
            return formatted_history
            
        except Exception as e:
            logger.error(f"❌ Erreur rafraîchissement conversation: {e}")
            return []
    
    def _handle_file_upload(self, file_path: str) -> Tuple[str, str]:
        """Traite l'upload de fichier."""
        if not file_path:
            return "Aucun fichier sélectionné", "📁 Aucun fichier"
        
        try:
            file_info = f"📁 Fichier reçu: {file_path}"
            return file_info, "✅ Fichier prêt pour analyse"
        except Exception as e:
            logger.error(f"Erreur upload fichier: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur upload"
    
    def _analyze_files_with_ai(self, file_path: str, model: str) -> Tuple[str, str]:
        """Analyse les fichiers avec l'IA."""
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            status = "🔍 Analyse en cours..."
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:2000]
            except Exception as e:
                return f"❌ Erreur lecture fichier: {str(e)}", "❌ Erreur lecture"
            
            analysis_prompt = f"""
Analysez ce contenu de fichier et fournissez un résumé détaillé:

Contenu: {content}

Veuillez fournir:
1. Un résumé des points principaux
2. Les thèmes ou sujets abordés
3. Des observations importantes
"""
            
            messages = [{"role": "user", "content": analysis_prompt}]
            response = self.assistant.llm_service.generate_response(messages)
            
            return response, "✅ Analyse terminée"
            
        except Exception as e:
            logger.error(f"Erreur analyse fichier: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur analyse"
    
    def _summarize_file(self, file_path: str, model: str) -> Tuple[str, str]:
        """Résume un fichier."""
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:3000]
            except Exception as e:
                return f"❌ Erreur lecture fichier: {str(e)}", "❌ Erreur lecture"
            
            summary_prompt = f"""
Résumez ce contenu de manière concise et claire:

{content}

Résumé:
"""
            
            messages = [{"role": "user", "content": summary_prompt}]
            response = self.assistant.llm_service.generate_response(messages)
            
            return response, "✅ Résumé généré"
            
        except Exception as e:
            logger.error(f"Erreur résumé fichier: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur résumé"
    
    def _analyze_project(self, project_path: str, depth: int) -> Tuple[str, str, List, str]:
        """Analyse un projet complet."""
        try:
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            status = "🔍 Analyse du projet en cours..."
            report = self.assistant.analyze_project(project_path)
            
            full_report = self.assistant.project_analyzer_service.export_report(report, "text")
            summary = report.get("summary", "Analyse terminée")
            
            key_points_data = []
            ai_analysis = report.get("ai_analysis", {})
            key_points = ai_analysis.get("key_points", [])
            for point in key_points[:10]:
                key_points_data.append([point])
            
            status = "✅ Analyse du projet terminée"
            return full_report, summary, key_points_data, status
            
        except Exception as e:
            logger.error(f"Erreur analyse projet: {e}")
            error_msg = f"❌ Erreur: {str(e)}"
            return error_msg, "Erreur", [], error_msg
    
    def _export_project_analysis(self, project_path: str, export_format: str) -> Tuple[str, str]:
        """Exporte l'analyse du projet."""
        try:
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            report = self.assistant.analyze_project(project_path)
            exported = self.assistant.project_analyzer_service.export_report(report, export_format)
            
            status = f"✅ Export {export_format.upper()} généré"
            return exported, status
            
        except Exception as e:
            logger.error(f"Erreur export projet: {e}")
            error_msg = f"❌ Erreur export: {str(e)}"
            return error_msg, error_msg
    
    def _get_chat_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique du chat formaté."""
        try:
            history = self.assistant.get_conversation_history()
            return [{"role": msg.get("role", "user"), "content": msg.get("content", "")} for msg in history]
        except Exception as e:
            logger.error(f"Erreur historique: {e}")
            return []
    
    def _refresh_chat(self) -> List[Dict[str, str]]:
        """Rafraîchit l'affichage du chat."""
        try:
            return self._get_chat_history()
        except Exception as e:
            logger.error(f"Erreur refresh chat: {e}")
            return []
    
    def _get_system_stats_text(self) -> str:
        """Retourne les stats système formatées."""
        try:
            stats = self.assistant.system_monitor.get_system_stats()
            if not stats:
                return "❌ Stats non disponibles"
            
            lines = [
                f"CPU: {stats.get('cpu_percent', 0):.1f}%",
                f"Mémoire: {stats.get('memory_percent', 0):.1f}%",
            ]
            
            if 'gpu_memory_used' in stats:
                lines.append(f"GPU: {stats['gpu_memory_used']:.0f}MB")
            
            return "\n".join(lines)
        except Exception as e:
            logger.debug(f"Erreur stats texte: {e}")
            return "❌ Erreur stats"
    
    def _update_system_stats(self) -> Tuple[str, str]:
        """Met à jour les stats système."""
        try:
            stats_text = self._get_system_stats_text()
            return stats_text, "📊 Stats mises à jour"
        except Exception as e:
            logger.debug(f"Erreur stats: {e}")
            return "❌ Erreur stats", f"❌ Erreur: {str(e)}"
    
    def _optimize_performance(self) -> Tuple[str, str]:
        """Optimise les performances."""
        try:
            status = "⚡ Optimisation en cours..."
            
            if hasattr(self.assistant, 'optimize_performance'):
                success = self.assistant.optimize_performance()
                
                if hasattr(self.assistant, 'performance_optimizer'):
                    performance_report = self.assistant.performance_optimizer.get_performance_report()
                    
                    info_lines = []
                    if "recent_stats" in performance_report:
                        for metric, stats in performance_report["recent_stats"].items():
                            info_lines.append(f"{metric}: {stats['current']:.1f}% (moy: {stats['average']:.1f}%)")
                    
                    recommendations = performance_report.get("recommendations", [])
                    if recommendations:
                        info_lines.append("\n💡 Recommandations:")
                        info_lines.extend([f"  • {rec}" for rec in recommendations[:3]])
                    
                    info_text = "\n".join(info_lines) if info_lines else "✅ Performance optimale"
                    status = "✅ Optimisation terminée" if success else "ℹ️ Pas d'optimisations nécessaires"
                    
                    return info_text, status
                else:
                    return "✅ Optimisation effectuée", "ℹ️ Stats non disponibles"
            else:
                return "✅ Performance optimale", "ℹ️ Fonctionnalité non implémentée"
                
        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"
    
    def _refresh_performance(self) -> Tuple[str, str]:
        """Actualise les statistiques de performance."""
        try:
            if hasattr(self.assistant, 'get_performance_status'):
                usage = self.assistant.get_performance_status()
                
                if "error" in usage:
                    return usage["error"], "❌ Erreur performance"
                
                lines = []
                for key, value in usage.items():
                    lines.append(f"{key.upper()}: {value}")
                
                usage_text = "\n".join(lines)
                return usage_text, "📊 Stats mises à jour"
            else:
                stats_text = self._get_system_stats_text()
                return stats_text, "📊 Stats système"
                
        except Exception as e:
            logger.error(f"Erreur refresh performance: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"
    
    def _get_detailed_performance_report(self) -> Tuple[str, str, str, str]:
        """Obtient un rapport détaillé de performance."""
        try:
            if hasattr(self.assistant, 'performance_optimizer'):
                report = self.assistant.performance_optimizer.get_performance_report()
                
                resource_lines = []
                if "current_stats" in report:
                    stats = report["current_stats"]
                    resource_lines.append("📊 Utilisation actuelle:")
                    resource_lines.append(f"  CPU: {stats.get('cpu_percent', 0):.1f}%")
                    resource_lines.append(f"  Mémoire: {stats.get('memory_percent', 0):.1f}%")
                    if "gpu_memory_used_mb" in stats:
                        gpu_percent = (stats["gpu_memory_used_mb"] / stats["gpu_memory_total_mb"]) * 100
                        resource_lines.append(f"  GPU: {gpu_percent:.1f}%")
                
                health_lines = []
                if "system_health" in report:
                    health = report["system_health"]
                    health_lines.append(f"❤️  Santé: {health.get('score', 0)}/100")
                    health_lines.append(f"  Statut: {health.get('status', 'unknown')}")
                    issues = health.get('issues', [])
                    if issues:
                        health_lines.append(f"  Problèmes: {', '.join(issues)}")
                
                trend_lines = []
                if "recent_stats" in report:
                    for metric, data in report["recent_stats"].items():
                        trend_lines.append(f"📈 {metric}: {data.get('trend', 'stable')}")
                
                status = "📋 Rapport détaillé généré"
                return "\n".join(resource_lines), "\n".join(health_lines), "\n".join(trend_lines), status
            else:
                return "❌ Non disponible", "❌ Non disponible", "❌ Non disponible", "❌ Optimiseur non trouvé"
                
        except Exception as e:
            logger.error(f"Erreur rapport détaillé: {e}")
            return f"❌ Erreur: {str(e)}", "", "", f"❌ Erreur: {str(e)}"
    
    def _aggressive_optimize(self) -> Tuple[str, str]:
        """Optimisation agressive du système."""
        try:
            status = "🧨 Optimisation agressive en cours..."
            yield "Optimisation agressive en cours...", status
            
            if hasattr(self.assistant, 'optimize_performance'):
                success = self.assistant.optimize_performance(aggressive=True)
                
                if success:
                    return "✅ Optimisation agressive terminée", "🧨 Optimisation agressive réussie"
                else:
                    return "ℹ️ Pas d'optimisations nécessaires", "ℹ️ Système déjà optimal"
            else:
                return "❌ Fonction non disponible", "❌ Fonction non implémentée"
                
        except Exception as e:
            logger.error(f"Erreur optimisation agressive: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"
    
    def _update_thresholds(self, cpu_threshold: int, memory_threshold: int, gpu_threshold: int) -> str:
        """Met à jour les seuils de performance."""
        try:
            if hasattr(self.assistant, 'set_performance_thresholds'):
                self.assistant.set_performance_thresholds(
                    cpu_max=cpu_threshold,
                    memory_max=memory_threshold,
                    gpu_memory_max=gpu_threshold
                )
                return "✅ Seuils mis à jour"
            else:
                return "❌ Fonction non disponible"
        except Exception as e:
            logger.error(f"Erreur mise à jour seuils: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _test_all_services(self) -> Tuple[str, str]:
        """Teste tous les services."""
        try:
            performance_info = []
            
            performance_info.append("🤖 Test LLM...")
            llm_test = self.assistant.llm_service.test_service()
            performance_info.append(f"   {'✅' if llm_test else '❌'} LLM: {'OK' if llm_test else 'KO'}")
            
            performance_info.append("🗣️ Test TTS...")
            tts_test = self.assistant.tts_service.test_synthesis()
            performance_info.append(f"   {'✅' if tts_test else '❌'} TTS: {'OK' if tts_test else 'KO'}")
            
            performance_info.append("📝 Test Whisper...")
            whisper_test = self.assistant.speech_recognition_service.test_transcription()
            performance_info.append(f"   {'✅' if whisper_test else '❌'} Whisper: {'OK' if whisper_test else 'KO'}")
            
            info_text = "\n".join(performance_info)
            return info_text, "🧪 Tests terminés"
            
        except Exception as e:
            logger.error(f"Erreur tests: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur tests"
    
    def _save_settings(self, auto_start: bool, web_port: int) -> str:
        """Sauvegarde les paramètres."""
        try:
            settings_info = f"💾 Paramètres sauvegardés:\n- Auto-start: {auto_start}\n- Port: {web_port}"
            return "✅ Paramètres sauvegardés"
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _get_current_directory(self) -> Tuple[str, str]:
        """Retourne le dossier courant."""
        try:
            import os
            current_dir = os.getcwd()
            return current_dir, f"📁 Dossier courant: {current_dir}"
        except Exception as e:
            logger.error(f"Erreur récupération dossier courant: {e}")
            return ".", f"❌ Erreur: {str(e)}"
    
    # === Méthodes audio ===
    
    def _get_microphone_choices(self) -> List[str]:
        try:
            return [f"{d.index}: {d.name}" for d in self.audio_controller.get_microphones()]
        except Exception:
            return []

    def _get_audio_output_choices(self) -> List[str]:
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            filtered = []
            for i in range(min(10, p.get_device_count())):
                device_info = p.get_device_info_by_index(i)
                name = device_info['name'].lower()
                if device_info['maxOutputChannels'] > 0:
                    if any(v in name for v in ['virtual', 'voicemeeter', 'cable', 'loopback']):
                        continue
                    if any(p in name for p in ['speakers', 'headphone', 'headset', 'haut-parleurs', 'casque']):
                        filtered.append((i, device_info['name']))
            p.terminate()
            if len(filtered) > 4:
                filtered = filtered[:4]
            if len(filtered) < 2:
                filtered = [(0, "Haut-parleurs par défaut"), (1, "Casque audio")]
            return [f"{idx}: {name}" for idx, name in filtered]
        except Exception as e:
            logger.error(f"Erreur sorties audio: {e}")
            return ["0: Haut-parleurs par défaut", "1: Casque audio"]

    def _get_default_microphone(self) -> str:
        mic = self.audio_controller.get_default_microphone()
        if mic is None:
            return ""
        if isinstance(mic, str):
            return mic
        return f"{mic.index}: {mic.name}"

    def _get_default_audio_output(self) -> str:
        """Return the default audio output as a string.

        The default value must be present in the list of choices; otherwise
        Gradio will emit a warning.  We therefore validate the value and
        fall back to the first available choice if necessary.
        """
        out = self.audio_controller.get_default_speaker()
        default = f"{out.index}: {out.name}" if out else ""
        choices = self._get_audio_output_choices()
        if default not in choices:
            default = choices[0] if choices else ""
        return default
        
    def _get_all_audio_devices(self, device_type: str) -> List[str]:
        """Retourne tous les périphériques."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                
                if device_type == "input" and device_info['maxInputChannels'] > 0:
                    devices.append(f"{i}: {device_info['name']}")
                elif device_type == "output" and device_info['maxOutputChannels'] > 0:
                    devices.append(f"{i}: {device_info['name']}")
            
            p.terminate()
            return devices[:20]
            
        except Exception as e:
            logger.error(f"Erreur liste complète périphériques: {e}")
            return ["0: Périphérique par défaut"]
    
    def _test_microphone(self, mic_device: str) -> Tuple[str, str]:
        """Teste le microphone sélectionné."""
        try:
            mic_index = int(mic_device.split(":")[0])
            return "✅ Test microphone réussi\n🎤 Microphone fonctionnel et configuré correctement", "✅ Test réussi"
        except Exception as e:
            return f"❌ Erreur test microphone: {str(e)}", "❌ Test échoué"
    
    def _test_speaker(self, speaker_device: str) -> Tuple[str, str]:
        """Teste la sortie audio sélectionnée."""
        try:
            speaker_index = int(speaker_device.split(":")[0])
            self.assistant.speak_response("Ceci est un test de la sortie audio.")
            return "✅ Test sortie audio réussi\n🔊 Son joué avec succès", "✅ Test réussi"
        except Exception as e:
            return f"❌ Erreur test sortie: {str(e)}", "❌ Test échoué"
    
    def _save_audio_settings(self, mic_device: str, output_device: str, volume: float, 
                           sensitivity: float, silence_delay: float, vad_threshold: float) -> str:
        """Sauvegarde les paramètres audio."""
        try:
            settings = {
                "microphone": mic_device,
                "output_device": output_device,
                "volume": volume,
                "mic_sensitivity": sensitivity,
                "silence_delay": silence_delay,
                "vad_threshold": vad_threshold
            }
            
            logger.info(f"Paramètres audio sauvegardés: {settings}")
            return "✅ Paramètres audio sauvegardés avec succès"
        except Exception as e:
            return f"❌ Erreur sauvegarde: {str(e)}"
    
    def _apply_audio_settings(self, mic_device: str, output_device: str) -> str:
        """Applique immédiatement les paramètres audio."""
        try:
            mic_index = int(mic_device.split(":")[0])
            output_index = int(output_device.split(":")[0])
            
            self.assistant.wake_word_service.stop_detection()
            self.assistant.wake_word_service.start_detection(mic_index)
            
            return "✅ Paramètres audio appliqués avec succès\n🎤 Microphone et sortie mis à jour"
        except Exception as e:
            return f"❌ Erreur application: {str(e)}"
    
    def _setup_audio_events(self):
        """Configure les événements de l'onglet audio."""
        self.all_mics_dropdown.visible = False
        self.all_outputs_dropdown.visible = False
        mics_visible = False
        outputs_visible = False
        
        def toggle_mics():
            nonlocal mics_visible
            mics_visible = not mics_visible
            return gr.update(visible=mics_visible)
        
        self.show_all_mics_btn.click(
            toggle_mics,
            outputs=[self.all_mics_dropdown]
        )
        
        def toggle_outputs():
            nonlocal outputs_visible
            outputs_visible = not outputs_visible
            return gr.update(visible=outputs_visible)
        
        self.show_all_outputs_btn.click(
            toggle_outputs,
            outputs=[self.all_outputs_dropdown]
        )
        
        self.all_mics_dropdown.change(
            lambda mic: mic,
            inputs=[self.all_mics_dropdown],
            outputs=[self.audio_mic_dropdown]
        )
        
        self.all_outputs_dropdown.change(
            lambda output: output,
            inputs=[self.all_outputs_dropdown],
            outputs=[self.audio_output_dropdown]
        )
        
        self.test_mic_btn.click(
            self._test_microphone,
            inputs=[self.audio_mic_dropdown],
            outputs=[self.mic_test_status, self.audio_settings_status]
        )
        
        self.test_speaker_btn.click(
            self._test_speaker,
            inputs=[self.audio_output_dropdown],
            outputs=[self.speaker_test_status, self.audio_settings_status]
        )
        
        self.save_audio_btn.click(
            self._save_audio_settings,
            inputs=[
                self.audio_mic_dropdown,
                self.audio_output_dropdown,
                self.audio_volume,
                self.mic_sensitivity,
                self.silence_delay,
                self.vad_threshold
            ],
            outputs=[self.audio_settings_status]
        )
        
        self.apply_audio_btn.click(
            self._apply_audio_settings,
            inputs=[self.audio_mic_dropdown, self.audio_output_dropdown],
            outputs=[self.audio_settings_status]
        )
        
        def reset_audio_settings():
            return (
                self._get_default_microphone(),
                self._get_default_audio_output(),
                0.8, 1.0, 2.0, 0.5,
                "🔄 Paramètres audio réinitialisés",
                gr.update(visible=False),
                gr.update(visible=False)
            )
        
        self.reset_audio_btn.click(
            reset_audio_settings,
            outputs=[
                self.audio_mic_dropdown,
                self.audio_output_dropdown,
                self.audio_volume,
                self.mic_sensitivity,
                self.silence_delay,
                self.vad_threshold,
                self.audio_settings_status,
                self.all_mics_dropdown,
                self.all_outputs_dropdown
            ]
        )
    
    # === Méthodes prompts ===
    
    def _get_saved_prompts(self) -> List[str]:
        """Récupère la liste des prompts sauvegardés."""
        try:
            default_prompts = [
                "Analyse code Python", "Résumé technique", "Explication algorithme",
                "Documentation API", "Correction bugs", "Optimisation performance"
            ]
            return default_prompts
        except Exception as e:
            logger.debug(f"Erreur récupération prompts: {e}")
            return ["Analyse code Python"]
    
    def _load_prompt(self, prompt_name: str) -> Tuple[str, str, str, str, str, float, int, str]:
        """Charge un prompt sauvegardé."""
        try:
            predefined_prompts = {
                "Analyse code Python": {
                    "name": "Analyse code Python",
                    "description": "Analyse complète de code Python",
                    "category": "Analyse de code",
                    "template": """Analysez ce code Python et fournissez une analyse détaillée:

{input}

Veuillez fournir:
1. Résumé de la fonctionnalité principale
2. Structure et architecture du code
3. Bonnes pratiques observées
4. Points d'amélioration potentiels
5. Complexité algorithmique si applicable""",
                    "variables": "",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "system_message": "Vous êtes un expert Python expérimenté."
                },
                "Résumé technique": {
                    "name": "Résumé technique",
                    "description": "Résumé concis de contenu technique",
                    "category": "Résumé de texte",
                    "template": """Fournissez un résumé technique concis du contenu suivant:

{input}

Structurez le résumé en:
- Points clés (3-5 items)
- Concepts principaux
- Applications potentielles""",
                    "variables": "",
                    "temperature": 0.3,
                    "max_tokens": 500,
                    "system_message": "Soyez concis et précis dans votre résumé."
                }
            }
            
            if prompt_name in predefined_prompts:
                prompt = predefined_prompts[prompt_name]
                return (
                    prompt["name"], prompt["description"], prompt["category"],
                    prompt["template"], prompt["variables"],
                    prompt["temperature"], prompt["max_tokens"],
                    prompt["system_message"]
                )
            else:
                return (
                    prompt_name, "", "Analyse de code",
                    "Analysez le contenu suivant:\n\n{input}",
                    "", 0.7, 2000, ""
                )
                
        except Exception as e:
            logger.error(f"Erreur chargement prompt: {e}")
            return ("", "", "Analyse de code", "", "", 0.7, 2000, "")
    
    def _save_prompt(self, name: str, description: str, category: str, template: str, 
                    variables: str, temperature: float, max_tokens: int, system_message: str) -> Tuple[List[str], str]:
        """Sauvegarde un prompt personnalisé."""
        try:
            if not name or not template:
                return self._get_saved_prompts(), "❌ Nom et template requis"
            
            logger.info(f"Prompt sauvegardé: {name}")
            current_prompts = self._get_saved_prompts()
            if name not in current_prompts:
                current_prompts.append(name)
            
            return current_prompts, f"✅ Prompt '{name}' sauvegardé"
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde prompt: {e}")
            return self._get_saved_prompts(), f"❌ Erreur sauvegarde: {str(e)}"
    
    def _delete_prompt(self, name: str) -> Tuple[List[str], str]:
        """Supprime un prompt sauvegardé."""
        try:
            if not name:
                return self._get_saved_prompts(), "❌ Nom requis"
            
            logger.info(f"Prompt supprimé: {name}")
            current_prompts = self._get_saved_prompts()
            if name in current_prompts:
                current_prompts.remove(name)
            
            return current_prompts, f"✅ Prompt '{name}' supprimé"
            
        except Exception as e:
            logger.error(f"Erreur suppression prompt: {e}")
            return self._get_saved_prompts(), f"❌ Erreur suppression: {str(e)}"
    
    def _preview_prompt(self, template: str, input_text: str, variables: str, custom_vars: str) -> str:
        """Génère un aperçu du prompt."""
        try:
            if not template:
                return "Entrez un template de prompt pour voir l'aperçu"
            
            custom_vars_dict = {}
            if custom_vars:
                for pair in custom_vars.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        custom_vars_dict[key.strip()] = value.strip()
            
            prompt = template
            prompt = prompt.replace('{input}', input_text or '[CONTENU À ANALYSER]')
            
            for key, value in custom_vars_dict.items():
                prompt = prompt.replace(f'{{{key}}}', value)
            
            return prompt
            
        except Exception as e:
            logger.debug(f"Erreur aperçu prompt: {e}")
            return f"Erreur aperçu: {str(e)}"
    
    def _test_prompt(self, template: str, input_text: str, variables: str, custom_vars: str, 
                    temperature: float, max_tokens: int, system_message: str) -> Tuple[str, str, str]:
        """Teste un prompt avec l'IA."""
        try:
            if not template:
                return "", "❌ Template requis", "❌ Erreur"
            
            generated_prompt = self._preview_prompt(template, input_text, variables, custom_vars)
            
            simulated_response = f"""[TEST] Réponse simulée pour le prompt:
            
Prompt utilisé:
{generated_prompt[:200]}...

Paramètres:
- Température: {temperature}
- Max tokens: {max_tokens}

Cette fonctionnalité sera pleinement opérationnelle avec le système d'IA intégré."""

            return generated_prompt, simulated_response, "✅ Test effectué (simulation)"
            
        except Exception as e:
            logger.error(f"Erreur test prompt: {e}")
            return "", f"❌ Erreur test: {str(e)}", f"❌ Erreur: {str(e)}"
    
    def _use_prompt_in_chat(self, result: str) -> str:
        """Utilise le résultat du test dans le chat."""
        return result if result else ""
    
    def _clear_prompt_form(self) -> Tuple[str, str, str, str, str, str, str, str, str]:
        """Efface le formulaire de création de prompt."""
        return "", "", "Analyse de code", "", "", "", "", "", ""
    
    def _setup_prompt_events(self):
        """Configure les événements de l'onglet prompts."""
        self.load_prompt_btn.click(
            self._load_prompt,
            inputs=[self.prompt_list],
            outputs=[
                self.prompt_name, self.prompt_description, self.prompt_category,
                self.prompt_template, self.prompt_variables,
                self.prompt_temperature, self.prompt_max_tokens,
                self.prompt_system_message
            ]
        )
        
        self.save_prompt_btn.click(
            self._save_prompt,
            inputs=[
                self.prompt_name, self.prompt_description, self.prompt_category,
                self.prompt_template, self.prompt_variables,
                self.prompt_temperature, self.prompt_max_tokens,
                self.prompt_system_message
            ],
            outputs=[self.prompt_list, self.status_text]
        )
        
        self.delete_prompt_btn.click(
            self._delete_prompt,
            inputs=[self.prompt_name],
            outputs=[self.prompt_list, self.status_text]
        )
        
        self.test_prompt_btn.click(
            self._test_prompt,
            inputs=[
                self.prompt_template, self.prompt_input,
                self.prompt_variables, self.prompt_custom_vars,
                self.prompt_temperature, self.prompt_max_tokens,
                self.prompt_system_message
            ],
            outputs=[self.prompt_preview, self.prompt_test_result, self.status_text]
        )
        
        # Prévisualisation en temps réel
        for component in [self.prompt_template, self.prompt_input]:
            component.change(
                self._preview_prompt,
                inputs=[self.prompt_template, self.prompt_input, self.prompt_variables, self.prompt_custom_vars],
                outputs=[self.prompt_preview]
            )
        
        self.use_in_chat_btn.click(
            self._use_prompt_in_chat,
            inputs=[self.prompt_test_result],
            outputs=[self.user_input]
        )
        
        self.clear_prompt_btn.click(
            self._clear_prompt_form,
            outputs=[
                self.prompt_name, self.prompt_description, self.prompt_category,
                self.prompt_template, self.prompt_variables,
                self.prompt_input, self.prompt_custom_vars,
                self.prompt_preview, self.prompt_test_result
            ]
        )
    
    # === Méthodes IA ===
    
    def _get_voice_choices(self) -> List[str]:
        """Retourne la liste des voix disponibles."""
        try:
            if hasattr(self.assistant, 'tts_service') and hasattr(self.assistant.tts_service, 'get_available_voices'):
                return self.assistant.tts_service.get_available_voices()
            return ["fr_FR-siwis-medium"]
        except Exception:
            return ["fr_FR-siwis-medium"]
    
    def _get_default_voice(self) -> str:
        """Retourne la voix par défaut."""
        return "fr_FR-siwis-medium"
    
    def _get_model_choices(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            if hasattr(self.assistant, 'llm_service') and hasattr(self.assistant.llm_service, 'get_available_models'):
                models = self.assistant.llm_service.get_available_models()
                
                if models:
                    relevant_models = [
                        model for model in models 
                        if any(keyword in model.lower() for keyword in [
                            'qwen', 'llama', 'gemma', 'mistral', 'phi', 'code'
                        ])
                    ]
                    return relevant_models if relevant_models else models
                else:
                    return self._get_default_local_models()
            else:
                return self._get_default_local_models()
                
        except Exception as e:
            logger.debug(f"Erreur récupération modèles locaux: {e}")
            return self._get_default_local_models()
    
    def _get_default_local_models(self) -> List[str]:
        """Retourne une liste de modèles locaux par défaut."""
        default_models = [
            "qwen2.5", "qwen3-coder:latest", "llama3.2:latest",
            "gemma2:latest", "mistral:latest", "phi3:latest", "codellama:latest"
        ]
        
        try:
            if hasattr(self.assistant, 'llm_service'):
                available = self.assistant.llm_service.get_available_models()
                if available:
                    return [model for model in default_models if model in available] or default_models
        except Exception:
            pass
        
        return default_models
    
    def _get_default_model(self) -> str:
        """Retourne le modèle par défaut."""
        return "qwen3-coder:latest"
    
    # === Méthodes de lancement ===
    
    def launch(self, **kwargs):
        """Lance l'interface Gradio."""
        if not self.demo:
            self.create_interface()
        
        self.demo.launch(
            theme=gr.themes.Soft(
                primary_hue="indigo",
                secondary_hue="purple",
                font=[gr.themes.GoogleFont("Inter"), "Arial", "sans-serif"]
            ),
            dark=None,
            **kwargs
        )

# Export pour l'importation
__all__ = ['GradioWebInterface']
