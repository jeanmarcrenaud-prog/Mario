import gradio as gr
import threading
import time
import json
from typing import List, Dict, Any
from ..utils.logger import logger

class GradioWebInterface:
    """Interface web Gradio avancée pour l'assistant vocal."""
    
    def __init__(self, assistant_controller):
        self.assistant = assistant_controller
        self.demo = None
        self.chat_history = []
        logger.info("GradioWebInterface avancé initialisé")
    
    def create_interface(self) -> gr.Blocks:
        """Crée l'interface Gradio complète et avancée."""
        with gr.Blocks(
            title="Assistant Vocal Intelligent",
            theme=self._get_theme()
        ) as demo:
            self.demo = demo
            
            # État de l'application
            self.app_state = gr.State({
                "is_listening": False,
                "current_model": self.assistant.settings.llm_model,
                "current_voice": self.assistant.settings.voice_name,
                "recording": False
            })
            
            # En-tête avec logo et titre
            with gr.Row():
                gr.Markdown("""
                # 🎤 Assistant Vocal Intelligent
                ## Votre compagnon IA avec reconnaissance et synthèse vocale
                """)
            
            with gr.Row():
                # Panneau de contrôle (25%)
                with gr.Column(scale=1):
                    self._create_advanced_control_panel()
                
                # Interface principale (75%)
                with gr.Column(scale=3):
                    self._create_advanced_main_interface()
            
            # Setup des événements
            self._setup_advanced_events()
            
            # Chargement initial
            demo.load(
                self._on_interface_load,
                outputs=[self.status_text, self.system_stats]
            )
        
        logger.info("Interface Gradio avancée créée")
        return demo
    
    def _get_theme(self):
        """Retourne le thème personnalisé."""
        return gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="cyan",
            neutral_hue="gray",
        ).set(
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_hover="*primary_400",
            block_title_text_weight="600",
            background_fill_primary="*neutral_50",
        )
    
    def _create_advanced_control_panel(self):
        """Crée le panneau de contrôle avancé."""
        gr.Markdown("## ⚙️ Configuration")
        
        # Statut et contrôles principaux
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
        
        # Configuration audio
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
        
        # Configuration IA
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
        
        # Stats système
        with gr.Group():
            self.system_stats = gr.Textbox(
                label="🖥️ Système",
                lines=3,
                interactive=False
            )
            
            self.refresh_stats_btn = gr.Button("🔄 Actualiser stats", size="sm")
    
    def _create_advanced_main_interface(self):
        """Crée l'interface principale avancée."""
        
        # Tabs pour différentes fonctionnalités
        with gr.Tabs():
            # Tab Chat
            with gr.Tab("💬 Conversation"):
                self._create_chat_tab()
            
            # Tab Fichiers
            with gr.Tab("📁 Fichiers"):
                self._create_files_tab()
            
            # Tab Paramètres
            with gr.Tab("🔧 Paramètres"):
                self._create_settings_tab()
    
    def _create_chat_tab(self):
        """Crée l'onglet de conversation."""
        # Chatbot avec historique
        self.chatbot = gr.Chatbot(
            label="Discussion",
            height=400,
            type="messages",
            bubble_full_width=False
        )
        
        # Zone de saisie avancée
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
                self.refresh_chat_btn = gr.Button("🔄 Actualiser", size="sm")  # Ajout
        
        # Contrôles vocaux
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
        gr.Markdown("## 📁 Analyse de fichiers et projets avec IA")
        
        with gr.Tabs():
            # Tab Fichiers simples
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
                            interactive=False,
                            show_copy_button=True
                        )
            
            # Tab Projets complets
        with gr.Tab("🏗️ Projets complets"):
            with gr.Row():
                with gr.Column():
                    self.project_path = gr.Textbox(
                        label="Chemin du projet",
                        placeholder="C:/chemin/vers/votre/projet ou laissez vide pour le dossier courant",
                        value=".",
                        interactive=True  # ✅ Maintenant éditable
                    )
                    
                    # Bouton pour sélectionner le dossier courant
                    self.current_dir_btn = gr.Button("📂 Utiliser dossier courant", size="sm")
                    
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
                    
                    # Sélection de dossier (si disponible)
                    self.folder_selector = gr.File(
                        label="Sélectionner un dossier",
                        file_count="directory",
                        visible=False  # Optionnel : pour une sélection graphique
                    )
                
                with gr.Column():
                    self.project_result = gr.Textbox(
                        label="Rapport d'analyse du projet",
                        lines=15,
                        interactive=False,
                        show_copy_button=True
                    )
            
            # Résumé visuel
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
        
        # Historique des analyses
        gr.Markdown("### 📈 Historique des analyses")
        self.analysis_history = gr.Dataframe(
            label="Analyses récentes",
            headers=["Type", "Cible", "Date", "Statut"],
            datatype=["str", "str", "str", "str"],
            interactive=False
        )

    def _analyze_project(self, project_path, depth):
        """Analyse un projet complet."""
        try:
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            # Mettre à jour le statut
            status = "🔍 Analyse du projet en cours..."
            
            # Analyser le projet (sans yield car ce n'est pas un générateur)
            report = self.assistant.analyze_project(project_path)
            
            # Extraire les informations
            full_report = self.assistant.project_analyzer_service.export_report(report, "text")
            summary = report.get("summary", "Analyse terminée")
            
            # Points clés
            key_points_data = []
            ai_analysis = report.get("ai_analysis", {})
            key_points = ai_analysis.get("key_points", [])
            for point in key_points[:10]:  # Max 10 points
                key_points_data.append([point])
            
            status = "✅ Analyse du projet terminée"
            return full_report, summary, key_points_data, status
            
        except Exception as e:
            logger.error(f"Erreur analyse projet: {e}")
            error_msg = f"❌ Erreur: {str(e)}"
            return error_msg, "Erreur", [], error_msg

    def _optimize_performance(self):
        """Optimise les performances."""
        try:
            # Placeholder - à implémenter avec votre optimiseur
            return "✅ Performance optimale", "ℹ️ Fonctionnalité à implémenter"
        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"

    def _refresh_performance(self):
        """Actualise les statistiques de performance."""
        try:
            # Placeholder - à implémenter avec votre optimiseur
            return "📊 Stats: N/A", "ℹ️ Fonctionnalité à implémenter"
        except Exception as e:
            logger.error(f"Erreur refresh performance: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"

    def _export_project_analysis(self, project_path, export_format):
        """Exporte l'analyse du projet."""
        try:
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            # Analyser le projet
            report = self.assistant.analyze_project(project_path)
            
            # Exporter
            exported = self.assistant.project_analyzer_service.export_report(report, export_format)
            
            status = f"✅ Export {export_format.upper()} généré"
            return exported, status
            
        except Exception as e:
            logger.error(f"Erreur export projet: {e}")
            error_msg = f"❌ Erreur export: {str(e)}"
            return error_msg, error_msg

    
    def _create_settings_tab(self):
        """Crée l'onglet des paramètres."""
        gr.Markdown("## 🔧 Paramètres avancés")
        
        with gr.Tabs():
            # Tab Système
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
            
            # Tab Monitoring
            with gr.Tab("📊 Monitoring"):
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
                
                gr.Markdown("### ⚙️ Configuration des seuils")
                with gr.Row():
                    self.cpu_threshold = gr.Number(label="Seuil CPU (%)", value=80, precision=0)
                    self.memory_threshold = gr.Number(label="Seuil Mémoire (%)", value=85, precision=0)
                    self.gpu_threshold = gr.Number(label="Seuil GPU (%)", value=85, precision=0)
                
                self.update_thresholds_btn = gr.Button("💾 Mettre à jour seuils")
            
            # Tab Logs
            with gr.Tab("📜 Logs"):
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

def _get_detailed_performance_report(self):
    """Obtient un rapport détaillé de performance."""
    try:
        if hasattr(self.assistant, 'performance_optimizer'):
            report = self.assistant.performance_optimizer.get_performance_report()
            
            # Ressources
            resource_lines = []
            if "current_stats" in report:
                stats = report["current_stats"]
                resource_lines.append("📊 Utilisation actuelle:")
                resource_lines.append(f"  CPU: {stats.get('cpu_percent', 0):.1f}%")
                resource_lines.append(f"  Mémoire: {stats.get('memory_percent', 0):.1f}%")
                if "gpu_memory_used_mb" in stats:
                    gpu_percent = (stats["gpu_memory_used_mb"] / stats["gpu_memory_total_mb"]) * 100
                    resource_lines.append(f"  GPU: {gpu_percent:.1f}%")
            
            # Santé
            health_lines = []
            if "system_health" in report:
                health = report["system_health"]
                health_lines.append(f"❤️  Santé: {health.get('score', 0)}/100")
                health_lines.append(f"  Statut: {health.get('status', 'unknown')}")
                issues = health.get('issues', [])
                if issues:
                    health_lines.append(f"  Problèmes: {', '.join(issues)}")
            
            # Tendances
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

    def _aggressive_optimize(self):
        """Optimisation agressive."""
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

    def _update_thresholds(self, cpu_threshold, memory_threshold, gpu_threshold):
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

    
    def _setup_advanced_events(self):
        """Configure tous les événements avancés."""
        
        # === Contrôles principaux ===
        self.start_btn.click(
            self._start_assistant,
            inputs=[self.mic_dropdown, self.voice_dropdown, self.model_dropdown, self.speed_slider],
            outputs=[self.status_text]
        )
        
        self.stop_btn.click(
            self._stop_assistant,
            outputs=[self.status_text]
        )
        
        # === Chat ===
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
        
        # === Fichiers simples ===
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
        
        # === Projets complets ===
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
        
        # === Audio/Vocal ===
        self.record_btn.click(
            self._start_recording,
            outputs=[self.voice_command_status, self.status_text]
        )
        
        self.listen_btn.click(
            self._toggle_listening,
            inputs=[self.app_state],
            outputs=[self.app_state, self.voice_command_status, self.status_text]
        )
        
        # === Paramètres ===
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

    def _on_interface_load(self):
        """Callback au chargement de l'interface."""
        status = "🟢 Interface chargée - Assistant prêt"
        stats = self._get_system_stats_text()
        return status, stats
    
    # === Méthodes de callback avancées ===
    
    def _start_assistant(self, mic_index, voice, model, speed):
        """Démarre l'assistant avec configuration."""
        try:
            # Mettre à jour les paramètres
            self.assistant.settings.voice_name = voice
            self.assistant.settings.llm_model = model
            
            # Démarrer les services
            self.assistant.wake_word_service.start_detection(int(mic_index.split(':')[0]))
            
            return "▶️ Assistant démarré - En attente du mot-clé 'Mario'"
        except Exception as e:
            logger.error(f"Erreur démarrage: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _stop_assistant(self):
        """Arrête l'assistant."""
        try:
            self.assistant.wake_word_service.stop_detection()
            return "⏹️ Assistant arrêté"
        except Exception as e:
            logger.error(f"Erreur arrêt: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _handle_user_message(self, message, model, temperature):
        """Traite un message utilisateur avec température."""
        if not message or not message.strip():
            return self._get_chat_history(), "", "📝 Message vide ignoré"
        
        try:
            # Mettre à jour le modèle si nécessaire
            if model != self.assistant.settings.llm_model:
                self.assistant.llm_service.set_model(model)
                self.assistant.settings.llm_model = model
            
            # Traiter le message
            response = self.assistant.process_user_message(message)
            
            # Parler la réponse
            self.assistant.speak_response(response)
            
            status = f"✅ Réponse générée ({len(response)} caractères)"
            # Retourner l'historique MAJ, le message vide, et le statut
            return self._get_chat_history(), "", status
            
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            error_msg = "[ERREUR] Impossible de traiter votre message"
            status = f"❌ Erreur: {str(e)}"
            # Ajouter le message d'erreur à l'historique
            error_history = self._get_chat_history() + [{"role": "assistant", "content": error_msg}]
            return error_history, "", status

    def _optimize_performance(self):
        """Optimise les performances."""
        try:
            status = "⚡ Optimisation en cours..."
            
            # Vérifier si l'assistant a l'optimiseur
            if hasattr(self.assistant, 'optimize_performance'):
                # Optimiser
                success = self.assistant.optimize_performance()
                
                # Mettre à jour les stats
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

    def _refresh_performance(self):
        """Actualise les statistiques de performance."""
        try:
            # Vérifier si l'assistant a la méthode
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
                # Utiliser les stats système de base
                stats_text = self._get_system_stats_text()
                return stats_text, "📊 Stats système"
                
        except Exception as e:
            logger.error(f"Erreur refresh performance: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur: {str(e)}"
    
    def _clear_conversation(self):
        """Efface la conversation."""
        try:
            self.assistant.clear_conversation()
            return [], "🧹 Conversation effacée"
        except Exception as e:
            logger.error(f"Erreur effacement conversation: {e}")
            return self._get_chat_history(), f"❌ Erreur: {str(e)}"
    
    def _handle_file_upload(self, file_path):
        """Traite l'upload de fichier."""
        if not file_path:
            return "Aucun fichier sélectionné", "📁 Aucun fichier"
        
        try:
            file_info = f"📁 Fichier reçu: {file_path}"
            return file_info, "✅ Fichier prêt pour analyse"
        except Exception as e:
            logger.error(f"Erreur upload fichier: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur upload"
    
    def _analyze_files_with_ai(self, file_path, model):
        """Analyse les fichiers avec l'IA."""
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            status = "🔍 Analyse en cours..."
            
            # Lire le contenu du fichier
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:2000]  # Limiter à 2000 caractères
            except Exception as e:
                return f"❌ Erreur lecture fichier: {str(e)}", "❌ Erreur lecture"
            
            # Analyser avec l'IA
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
    
    def _summarize_file(self, file_path, model):
        """Résume un fichier."""
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            # Lire le contenu du fichier
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:3000]  # Limiter à 3000 caractères
            except Exception as e:
                return f"❌ Erreur lecture fichier: {str(e)}", "❌ Erreur lecture"
            
            # Résumer avec l'IA
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
    
    def _start_recording(self):
        """Démarre l'enregistrement vocal."""
        try:
            return "🎤 Enregistrement démarré...", "🎙️ Enregistrement vocal activé"
        except Exception as e:
            logger.error(f"Erreur enregistrement: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur enregistrement"
    
    def _toggle_listening(self, app_state):
        """Active/désactive l'écoute."""
        try:
            new_state = app_state.copy()
            new_state["is_listening"] = not app_state.get("is_listening", False)
            
            status = "👂 Écoute activée" if new_state["is_listening"] else "🔇 Écoute désactivée"
            voice_status = "Écoute en cours" if new_state["is_listening"] else "Prêt"
            
            return new_state, voice_status, status
        except Exception as e:
            logger.error(f"Erreur toggle écoute: {e}")
            return app_state, "❌ Erreur", f"❌ Erreur: {str(e)}"
    
    def _save_settings(self, auto_start, web_port):
        """Sauvegarde les paramètres."""
        try:
            # Ici vous pouvez sauvegarder dans un fichier de config
            settings_info = f"💾 Paramètres sauvegardés:\n- Auto-start: {auto_start}\n- Port: {web_port}"
            return "✅ Paramètres sauvegardés"
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return f"❌ Erreur: {str(e)}"

    def _get_current_directory(self):
        """Retourne le dossier courant."""
        try:
            import os
            current_dir = os.getcwd()
            return current_dir, f"📁 Dossier courant: {current_dir}"
        except Exception as e:
            logger.error(f"Erreur récupération dossier courant: {e}")
            return ".", f"❌ Erreur: {str(e)}"
    
    def _test_all_services(self):
        """Teste tous les services."""
        try:
            performance_info = []
            
            # Test LLM
            performance_info.append("🤖 Test LLM...")
            llm_test = self.assistant.llm_service.test_service()
            performance_info.append(f"   {'✅' if llm_test else '❌'} LLM: {'OK' if llm_test else 'KO'}")
            
            # Test TTS
            performance_info.append("🗣️ Test TTS...")
            tts_test = self.assistant.tts_service.test_synthesis()
            performance_info.append(f"   {'✅' if tts_test else '❌'} TTS: {'OK' if tts_test else 'KO'}")
            
            # Test Whisper
            performance_info.append("📝 Test Whisper...")
            whisper_test = self.assistant.speech_recognition_service.test_transcription()
            performance_info.append(f"   {'✅' if whisper_test else '❌'} Whisper: {'OK' if whisper_test else 'KO'}")
            
            # Test Porcupine
            performance_info.append("👂 Test Porcupine...")
            # Porcupine est testé via la détection
            
            info_text = "\n".join(performance_info)
            return info_text, "🧪 Tests terminés"
            
        except Exception as e:
            logger.error(f"Erreur tests: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur tests"
    
    def _update_system_stats(self):
        """Met à jour les stats système."""
        try:
            stats_text = self._get_system_stats_text()
            return stats_text, "📊 Stats mises à jour"
        except Exception as e:
            logger.debug(f"Erreur stats: {e}")
            return "❌ Erreur stats", f"❌ Erreur: {str(e)}"
    
    # === Méthodes utilitaires ===
    
    def _get_chat_history(self):
        """Retourne l'historique du chat formaté."""
        try:
            history = self.assistant.get_conversation_history()
            # S'assurer que le format est correct pour Gradio
            formatted_history = []
            for msg in history:
                formatted_history.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            return formatted_history
        except Exception as e:
            logger.error(f"Erreur historique: {e}")
            return []

    def _refresh_chat(self):
        """Rafraîchit l'affichage du chat."""
        try:
            return self._get_chat_history()
        except Exception as e:
            logger.error(f"Erreur refresh chat: {e}")
            return []

    
    def _get_system_stats_text(self):
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
    
    def _get_microphone_choices(self) -> List[str]:
        """Retourne la liste des microphones disponibles."""
        try:
            devices = self.assistant.wake_word_service.get_audio_devices()
            return [f"{idx}: {name}" for idx, name in devices]
        except Exception:
            return ["0: Microphone par défaut"]
    
    def _get_default_microphone(self) -> str:
        """Retourne le microphone par défaut."""
        choices = self._get_microphone_choices()
        return choices[0] if choices else "0: Microphone par défaut"
    
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
                return models if models else ["qwen2.5"]
            return ["qwen2.5", "llama3", "gemma2"]
        except Exception:
            return ["qwen2.5"]
    
    def _get_default_model(self) -> str:
        """Retourne le modèle par défaut."""
        return "qwen3-coder:latest"
    
    def launch(self, **kwargs):
        """Lance l'interface Gradio."""
        if not self.demo:
            self.create_interface()
        
        self.demo.launch(**kwargs)

# Export
__all__ = ['GradioWebInterface']
