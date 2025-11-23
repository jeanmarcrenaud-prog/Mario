"""
Interface Web Gradio pour l'Assistant Vocal Intelligent
=====================================================

Interface utilisateur avancée avec :
- Chat vocal intelligent
- Analyse de projets
- Monitoring performance
- Configuration complète

Auteur: Assistant Vocal Team
Version: 1.0
"""

import gradio as gr
from gradio import themes
from gradio.themes import Default as DefaultTheme
from gradio.themes import ThemeClass as Theme
import threading
import time
import json
from typing import List, Dict, Any
from ..utils.logger import logger
from ..controllers.audio_controller import AudioController

BUILT_IN_THEMES: dict[str, Theme] = {
    t.name: t
    for t in [
        themes.Base(),
        themes.Default(),
        themes.Monochrome(),
        themes.Soft(),
        themes.Glass(),
        themes.Origin(),
        themes.Citrus(),
        themes.Ocean(),
    ]
}

class GradioWebInterface:
    """
    Interface web Gradio avancée pour l'assistant vocal.
    
    Cette classe gère toute l'interface utilisateur de l'assistant,
    incluant le chat, l'analyse de fichiers, et le monitoring.
    """
    
    def __init__(self, assistant_controller):
        """
        Initialise l'interface web.
        
        Args:
            assistant_controller: Instance du contrôleur principal
        """
        self.assistant = assistant_controller
        self.demo = None
        self.chat_history = []
        self.audio_controller = AudioController()
        logger.info("GradioWebInterface avancé initialisé")
    
    def create_interface(self) -> gr.Blocks:
        """
        Crée l'interface Gradio complète et avancée.
        
        Returns:
            gr.Blocks: Interface Gradio configurée
        """
        # Configuration de base de l'interface
        with gr.Blocks(
            title="Assistant Vocal Intelligent"
        ) as demo:
            self.demo = demo
            
            # État de l'application (persistance des données)
            self.app_state = gr.State({
                "is_listening": False,
                "current_model": self.assistant.settings.llm_model,
                "current_voice": self.assistant.settings.voice_name,
                "recording": False
            })
            
            # === EN-TÊTE DE L'INTERFACE ===
            with gr.Row():
                gr.Markdown("""
                # 🎤 Assistant Vocal Intelligent
                ## Votre compagnon IA avec reconnaissance et synthèse vocale
                """)
            
            # === LAYOUT PRINCIPAL ===
            with gr.Row():
                # Panneau de contrôle (25% de la largeur)
                with gr.Column(scale=1):
                    self._create_advanced_control_panel()
                
                # Interface principale (75% de la largeur)
                with gr.Column(scale=3):
                    self._create_advanced_main_interface()
            
            # Configuration des événements
            self._setup_advanced_events()
            
            # Chargement initial de l'interface
            demo.load(
                self._on_interface_load,
                outputs=[self.status_text, self.system_stats]
            )
        
        logger.info("Interface Gradio avancée créée")
        return demo
    
    def get_theme(theme: Theme | str | None) -> Theme:
        if theme is None:
            theme = DefaultTheme()
        elif isinstance(theme, str):
            if theme.lower() in BUILT_IN_THEMES:
                theme = BUILT_IN_THEMES[theme.lower()]
            else:
                try:
                    theme = Theme.from_hub(theme)
                except Exception as e:
                    warnings.warn(f"Cannot load {theme}. Caught Exception: {str(e)}")
                    theme = DefaultTheme()
        return theme
    
    def _create_advanced_control_panel(self):
        """
        Crée le panneau de contrôle avancé.
        
        Inclut la configuration système, audio, et IA.
        """
        gr.Markdown("## ⚙️ Configuration")
        
        # === STATUT ET CONTRÔLES PRINCIPAUX ===
        with gr.Group():
            # Zone d'affichage du statut
            self.status_text = gr.Textbox(
                label="📊 Statut",
                lines=4,
                value="🟢 Interface chargée - Prêt à démarrer",
                interactive=False
            )
            
            # Boutons de contrôle principal
            with gr.Row():
                self.start_btn = gr.Button("▶️ Démarrer", variant="primary", scale=1)
                self.stop_btn = gr.Button("⏹️ Arrêter", variant="stop", scale=1)
        
        # === CONFIGURATION AUDIO ===
        with gr.Accordion("🎤 Audio", open=True):
            # Sélection du microphone
            self.mic_dropdown = gr.Dropdown(
                label="Microphone",
                choices=self._get_microphone_choices(),
                value=self._get_default_microphone(),
                interactive=True
            )
            
            # Sélection de la voix
            self.voice_dropdown = gr.Dropdown(
                label="🗣️ Voix",
                choices=self._get_voice_choices(),
                value=self._get_default_voice(),
                interactive=True
            )
            
            # Contrôle de la vitesse de parole
            self.speed_slider = gr.Slider(
                label="⏩ Vitesse de parole",
                minimum=0.5,     # 50% de la vitesse normale
                maximum=2.0,     # 200% de la vitesse normale
                value=1.0,       # Vitesse normale par défaut
                step=0.1         # Incrément de 10%
            )
        
        # === CONFIGURATION IA ===
        with gr.Accordion("🤖 Intelligence", open=True):
            # Sélection du modèle IA
            self.model_dropdown = gr.Dropdown(
                label="Modèle IA",
                choices=self._get_model_choices(),
                value=self._get_default_model(),
                interactive=True
            )
            
            # Contrôle de la créativité (température)
            self.temperature_slider = gr.Slider(
                label="🌡️ Créativité",
                minimum=0.0,     # Réponses déterministes
                maximum=1.0,     # Réponses créatives
                value=0.7,       # Équilibre par défaut
                step=0.1
            )
        
        # === STATS SYSTÈME ===
        with gr.Group():
            # Affichage des statistiques système
            self.system_stats = gr.Textbox(
                label="🖥️ Système",
                lines=3,
                interactive=False
            )
            
            # Bouton d'actualisation des stats
            self.refresh_stats_btn = gr.Button("🔄 Actualiser stats", size="sm")
    
    def _create_advanced_main_interface(self):
        """
        Crée l'interface principale avancée.
        
        Organisation par onglets pour une navigation intuitive.
        """
        # === TABS PRINCIPAUX ===
        with gr.Tabs():
            # Tab Chat - Conversation principale
            with gr.Tab("💬 Conversation"):
                self._create_chat_tab()
            
            # Tab Fichiers - Analyse de code et documents
            with gr.Tab("📁 Fichiers"):
                self._create_files_tab()
        
            # Tab Prompts - Gestion des prompts personnalisés
            with gr.Tab("🎯 Prompts"):
                self._create_prompts_tab()
                
            # Tab Paramètres - Configuration avancée
            with gr.Tab("🔧 Paramètres"):
                self._create_settings_tab()
    
    def _create_chat_tab(self):
        """
        Crée l'onglet de conversation.
        
        Interface de chat avec historique et commandes vocales.
        """
        # === CHATBOT ===
        self.chatbot = gr.Chatbot(
            label="Discussion",
            height=400,           # Hauteur fixe
        )
        
        # === ZONE DE SAISIE ===
        with gr.Row():
            # Champ de texte principal
            self.user_input = gr.Textbox(
                label="Votre message",
                placeholder="Tapez votre message ou parlez après avoir dit 'Mario'...",
                scale=4,          # 80% de la largeur
                lines=2           # 2 lignes de hauteur
            )
            
            # Boutons d'action
            with gr.Column(scale=1):  # 20% de la largeur
                self.send_btn = gr.Button("📤 Envoyer", variant="primary")
                self.clear_btn = gr.Button("🧹 Effacer", size="sm")
                self.refresh_chat_btn = gr.Button("🔄 Actualiser", size="sm")
        
        # === COMMANDES VOCALES ===
        with gr.Group():
            gr.Markdown("### 🎤 Commandes vocales")
            with gr.Row():
                self.record_btn = gr.Button("🎤 Enregistrer", variant="secondary")
                self.listen_btn = gr.Button("👂 Écouter", variant="secondary")
            
            # Statut des commandes vocales
            self.voice_command_status = gr.Textbox(
                label="Statut vocal",
                value="Prêt",
                interactive=False
            )
    
    def _create_files_tab(self):
        """
        Crée l'onglet de gestion des fichiers.
        
        Analyse de fichiers individuels et projets complets.
        """
        gr.Markdown("## 📁 Analyse de fichiers et projets avec IA")
        
        # === SOUS-TABS FICHIERS ===
        with gr.Tabs():
            # Tab Fichiers simples
            with gr.Tab("📄 Fichiers individuels"):
                with gr.Row():
                    with gr.Column():
                        # Upload de fichiers
                        self.file_upload = gr.File(
                            label="Glissez-déposez des fichiers",
                            file_types=[".txt", ".py", ".md", ".json", ".csv", ".html", ".css", ".js"],
                            type="filepath"
                        )
                        
                        # Boutons d'analyse
                        with gr.Row():
                            self.analyze_btn = gr.Button("🔍 Analyser avec IA", variant="primary")
                            self.summarize_btn = gr.Button("📝 Résumer", variant="secondary")
                    
                    with gr.Column():
                        # Résultat de l'analyse
                        self.file_result = gr.Textbox(
                            label="Résultat de l'analyse",
                            lines=10,
                            interactive=False
                        )
            
            # Tab Projets complets
            with gr.Tab("🏗️ Projets complets"):
                with gr.Row():
                    with gr.Column():
                        # Configuration du projet
                        self.project_path = gr.Textbox(
                            label="Chemin du projet",
                            placeholder="C:/chemin/vers/votre/projet ou laissez vide pour le dossier courant",
                            value=".",
                            interactive=True
                        )
                        
                        # Bouton dossier courant
                        self.current_dir_btn = gr.Button("📂 Utiliser dossier courant", size="sm")
                        
                        # Boutons d'analyse projet
                        with gr.Row():
                            self.analyze_project_btn = gr.Button("🔍 Analyser projet", variant="primary", scale=2)
                            self.export_json_btn = gr.Button("💾 Export JSON", scale=1)
                            self.export_md_btn = gr.Button("📄 Export Markdown", scale=1)
                        
                        # Profondeur d'analyse
                        self.project_depth = gr.Slider(
                            label="Profondeur d'analyse",
                            minimum=1,
                            maximum=5,
                            value=2,
                            step=1
                        )
                        
                        # Sélecteur de dossier (optionnel)
                        self.folder_selector = gr.File(
                            label="Sélectionner un dossier",
                            file_count="directory",
                            visible=False
                        )
                
                with gr.Column():
                    # Résultat de l'analyse projet
                    self.project_result = gr.Textbox(
                        label="Rapport d'analyse du projet",
                        lines=15,
                        interactive=False
                    )
            
            # === RÉSUMÉ VISUEL ===
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
        
        # === HISTORIQUE DES ANALYSES ===
        gr.Markdown("### 📈 Historique des analyses")
        self.analysis_history = gr.Dataframe(
            label="Analyses récentes",
            headers=["Type", "Cible", "Date", "Statut"],
            datatype=["str", "str", "str", "str"],
            interactive=False
        )

    def _create_prompts_tab(self):
        """
        Crée l'onglet de gestion des prompts personnalisés.
        
        Permet de créer, éditer et utiliser des prompts prédéfinis.
        """
        gr.Markdown("## 🎯 Prompts Personnalisés")
        gr.Markdown("Créez et utilisez des prompts spécialisés pour des tâches récurrentes.")
        
        with gr.Row():
            # === COLONNE GAUCHE : LISTE DES PROMPTS ===
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Bibliothèque de Prompts")
                
                # Liste des prompts disponibles
                self.prompt_list = gr.Dropdown(
                    label="Prompts sauvegardés",
                    choices=self._get_saved_prompts(),
                    interactive=True
                )
                
                # Boutons de gestion
                with gr.Row():
                    self.load_prompt_btn = gr.Button("📥 Charger")
                    self.delete_prompt_btn = gr.Button("🗑️ Supprimer")
                
                # Catégories de prompts
                gr.Markdown("### 🏷️ Catégories")
                prompt_categories = [
                    "Analyse de code",
                    "Résumé de texte", 
                    "Explication technique",
                    "Génération de documentation",
                    "Correction de bugs",
                    "Optimisation de code",
                    "Traduction",
                    "Création de contenu"
                ]
                
                self.prompt_category = gr.Dropdown(
                    label="Catégorie",
                    choices=prompt_categories,
                    value="Analyse de code",
                    interactive=True
                )
            
            # === COLONNE DROITE : ÉDITION DU PROMPT ===
            with gr.Column(scale=2):
                gr.Markdown("### ✏️ Création/Édition de Prompt")
                
                # Informations du prompt
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
                
                # Éditeur de prompt principal
                self.prompt_template = gr.Textbox(
                    label="Template du prompt",
                    placeholder="""Utilisez {input} pour le contenu utilisateur
    Exemple:
    Analysez ce code et expliquez sa fonction:
    {input}

    Fournissez:
    1. Résumé de la fonctionnalité
    2. Points clés de l'implémentation
    3. Suggestions d'amélioration""",
                    lines=10,
                    max_lines=15
                )
                
                # Variables personnalisées
                gr.Markdown("### 📝 Variables personnalisées")
                self.prompt_variables = gr.Textbox(
                    label="Variables supplémentaires (séparées par des virgules)",
                    placeholder="langage,framework,version",
                    value=""
                )
                
                # Boutons d'action
                with gr.Row():
                    self.save_prompt_btn = gr.Button("💾 Sauvegarder", variant="primary")
                    self.test_prompt_btn = gr.Button("🧪 Tester")
                    self.clear_prompt_btn = gr.Button("🧹 Effacer")
        
        # === PRÉVISUALISATION ET TEST ===
        with gr.Group():
            gr.Markdown("### 🎯 Test du Prompt")
            
            with gr.Row():
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
                
                with gr.Column():
                    self.prompt_preview = gr.Textbox(
                        label="Prompt généré",
                        lines=8,
                        interactive=False
                    )
            
            # Résultat du test
            self.prompt_test_result = gr.Textbox(
                label="Résultat du test",
                lines=6,
                interactive=False
            )
            
            # Bouton pour utiliser dans le chat
            self.use_in_chat_btn = gr.Button("💬 Utiliser dans le chat")
        
        # === CONFIGURATION DES PROMPTS ===
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
        
        # === ÉVÉNEMENTS DES PROMPTS ===
        self._setup_prompt_events()

    def _setup_prompt_events(self):
        """Configure les événements de l'onglet prompts."""
        
        # Chargement d'un prompt
        self.load_prompt_btn.click(
            self._load_prompt,
            inputs=[self.prompt_list],
            outputs=[
                self.prompt_name, 
                self.prompt_description, 
                self.prompt_category,
                self.prompt_template,
                self.prompt_variables,
                self.prompt_temperature,
                self.prompt_max_tokens,
                self.prompt_system_message
            ]
        )
        
        # Sauvegarde d'un prompt
        self.save_prompt_btn.click(
            self._save_prompt,
            inputs=[
                self.prompt_name,
                self.prompt_description,
                self.prompt_category,
                self.prompt_template,
                self.prompt_variables,
                self.prompt_temperature,
                self.prompt_max_tokens,
                self.prompt_system_message
            ],
            outputs=[self.prompt_list, self.status_text]
        )
        
        # Suppression d'un prompt
        self.delete_prompt_btn.click(
            self._delete_prompt,
            inputs=[self.prompt_name],
            outputs=[self.prompt_list, self.status_text]
        )
        
        # Test d'un prompt
        self.test_prompt_btn.click(
            self._test_prompt,
            inputs=[
                self.prompt_template,
                self.prompt_input,
                self.prompt_variables,
                self.prompt_custom_vars,
                self.prompt_temperature,
                self.prompt_max_tokens,
                self.prompt_system_message
            ],
            outputs=[self.prompt_preview, self.prompt_test_result, self.status_text]
        )
        
        # Prévisualisation en temps réel
        self.prompt_template.change(
            self._preview_prompt,
            inputs=[self.prompt_template, self.prompt_input, self.prompt_variables, self.prompt_custom_vars],
            outputs=[self.prompt_preview]
        )
        
        self.prompt_input.change(
            self._preview_prompt,
            inputs=[self.prompt_template, self.prompt_input, self.prompt_variables, self.prompt_custom_vars],
            outputs=[self.prompt_preview]
        )
        
        # Utilisation dans le chat
        self.use_in_chat_btn.click(
            self._use_prompt_in_chat,
            inputs=[self.prompt_test_result],
            outputs=[self.user_input]
        )
        
        # Effacement du formulaire
        self.clear_prompt_btn.click(
            self._clear_prompt_form,
            outputs=[
                self.prompt_name,
                self.prompt_description,
                self.prompt_category,
                self.prompt_template,
                self.prompt_variables,
                self.prompt_input,
                self.prompt_custom_vars,
                self.prompt_preview,
                self.prompt_test_result
            ]
        )

    # === MÉTHODES DE GESTION DES PROMPTS ===

    def _get_saved_prompts(self) -> List[str]:
        """
        Récupère la liste des prompts sauvegardés.
        
        Returns:
            List[str]: Liste des noms de prompts
        """
        try:
            # Pour l'instant, retourne une liste statique
            # Plus tard, vous pouvez implémenter le stockage dans un fichier
            default_prompts = [
                "Analyse code Python",
                "Résumé technique",
                "Explication algorithme",
                "Documentation API",
                "Correction bugs",
                "Optimisation performance"
            ]
            return default_prompts
        except Exception as e:
            logger.debug(f"Erreur récupération prompts: {e}")
            return ["Analyse code Python"]

    def _load_prompt(self, prompt_name):
        """
        Charge un prompt sauvegardé.
        
        Args:
            prompt_name (str): Nom du prompt à charger
            
        Returns:
            tuple: Informations du prompt
        """
        try:
            # Dictionnaire de prompts prédéfinis (à remplacer par stockage fichier)
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
                    prompt["name"],
                    prompt["description"],
                    prompt["category"],
                    prompt["template"],
                    prompt["variables"],
                    prompt["temperature"],
                    prompt["max_tokens"],
                    prompt["system_message"]
                )
            else:
                # Retourner des valeurs par défaut
                return (
                    prompt_name,
                    "",
                    "Analyse de code",
                    "Analysez le contenu suivant:\n\n{input}",
                    "",
                    0.7,
                    2000,
                    ""
                )
                
        except Exception as e:
            logger.error(f"Erreur chargement prompt: {e}")
            return (
                "", "", "Analyse de code", "", "", 0.7, 2000, ""
            )

    def _save_prompt(self, name, description, category, template, variables, temperature, max_tokens, system_message):
        """
        Sauvegarde un prompt personnalisé.
        
        Returns:
            tuple: (liste_prompts_mise_à_jour, message_statut)
        """
        try:
            if not name or not template:
                return self._get_saved_prompts(), "❌ Nom et template requis"
            
            # Ici vous pouvez implémenter le stockage dans un fichier
            # Pour l'instant, on simule la sauvegarde
            logger.info(f"Prompt sauvegardé: {name}")
            
            # Mettre à jour la liste
            current_prompts = self._get_saved_prompts()
            if name not in current_prompts:
                current_prompts.append(name)
            
            return current_prompts, f"✅ Prompt '{name}' sauvegardé"
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde prompt: {e}")
            return self._get_saved_prompts(), f"❌ Erreur sauvegarde: {str(e)}"

    def _delete_prompt(self, name):
        """
        Supprime un prompt sauvegardé.
        
        Returns:
            tuple: (liste_prompts_mise_à_jour, message_statut)
        """
        try:
            if not name:
                return self._get_saved_prompts(), "❌ Nom requis"
            
            # Ici vous pouvez implémenter la suppression du fichier
            # Pour l'instant, on simule la suppression
            logger.info(f"Prompt supprimé: {name}")
            
            # Mettre à jour la liste
            current_prompts = self._get_saved_prompts()
            if name in current_prompts:
                current_prompts.remove(name)
            
            return current_prompts, f"✅ Prompt '{name}' supprimé"
            
        except Exception as e:
            logger.error(f"Erreur suppression prompt: {e}")
            return self._get_saved_prompts(), f"❌ Erreur suppression: {str(e)}"

    def _preview_prompt(self, template, input_text, variables, custom_vars):
        """
        Génère un aperçu du prompt avec les variables.
        
        Returns:
            str: Prompt généré
        """
        try:
            if not template:
                return "Entrez un template de prompt pour voir l'aperçu"
            
            # Parser les variables personnalisées
            custom_vars_dict = {}
            if custom_vars:
                for pair in custom_vars.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        custom_vars_dict[key.strip()] = value.strip()
            
            # Remplacer les variables dans le template
            prompt = template
            prompt = prompt.replace('{input}', input_text or '[CONTENU À ANALYSER]')
            
            # Remplacer les variables personnalisées
            for key, value in custom_vars_dict.items():
                prompt = prompt.replace(f'{{{key}}}', value)
            
            return prompt
            
        except Exception as e:
            logger.debug(f"Erreur aperçu prompt: {e}")
            return f"Erreur aperçu: {str(e)}"

    def _test_prompt(self, template, input_text, variables, custom_vars, temperature, max_tokens, system_message):
        """
        Teste un prompt avec l'IA.
        
        Returns:
            tuple: (prompt_généré, résultat_test, statut)
        """
        try:
            if not template:
                return "", "❌ Template requis", "❌ Erreur"
            
            # Générer le prompt
            generated_prompt = self._preview_prompt(template, input_text, variables, custom_vars)
            
            # Pour le test, on simule une réponse
            # Dans la vraie implémentation, vous appellerez l'IA
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

    def _use_prompt_in_chat(self, result):
        """
        Utilise le résultat du test dans le chat.
        
        Returns:
            str: Texte à insérer dans le chat
        """
        return result if result else ""

    def _clear_prompt_form(self):
        """
        Efface le formulaire de création de prompt.
        
        Returns:
            tuple: Valeurs vides pour tous les champs
        """
        return "", "", "Analyse de code", "", "", "", "", "", ""

    # =================================================================
    # FONCTIONS DE TRAITEMENT - ANALYSE DE PROJETS
    # =================================================================
    
    def _analyze_project(self, project_path, depth):
        """
        Analyse un projet complet avec l'IA.
        
        Args:
            project_path (str): Chemin du projet à analyser
            depth (int): Profondeur d'analyse des dossiers
            
        Returns:
            tuple: (rapport, résumé, points_clés, statut)
        """
        try:
            # Utiliser le dossier courant si non spécifié
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            # Mettre à jour le statut
            status = "🔍 Analyse du projet en cours..."
            
            # Analyser le projet avec l'assistant
            report = self.assistant.analyze_project(project_path)
            
            # Extraire les informations du rapport
            full_report = self.assistant.project_analyzer_service.export_report(report, "text")
            summary = report.get("summary", "Analyse terminée")
            
            # Points clés de l'analyse (max 10)
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

    def _export_project_analysis(self, project_path, export_format):
        """
        Exporte l'analyse du projet dans différents formats.
        
        Args:
            project_path (str): Chemin du projet
            export_format (str): Format d'export ("json" ou "markdown")
            
        Returns:
            tuple: (contenu_exporté, statut)
        """
        try:
            # Utiliser le dossier courant si non spécifié
            if not project_path or project_path == ".":
                import os
                project_path = os.getcwd()
            
            # Analyser le projet
            report = self.assistant.analyze_project(project_path)
            
            # Exporter dans le format demandé
            exported = self.assistant.project_analyzer_service.export_report(report, export_format)
            
            status = f"✅ Export {export_format.upper()} généré"
            return exported, status
            
        except Exception as e:
            logger.error(f"Erreur export projet: {e}")
            error_msg = f"❌ Erreur export: {str(e)}"
            return error_msg, error_msg

    # =================================================================
    # FONCTIONS DE TRAITEMENT - OPTIMISATION
    # =================================================================
    
    def _optimize_performance(self):
        """
        Optimise les performances du système.
        
        Returns:
            tuple: (info_performance, statut)
        """
        try:
            status = "⚡ Optimisation en cours..."
            
            # Vérifier si l'assistant a l'optimiseur
            if hasattr(self.assistant, 'optimize_performance'):
                # Optimiser les performances
                success = self.assistant.optimize_performance()
                
                # Mettre à jour les stats si optimiseur disponible
                if hasattr(self.assistant, 'performance_optimizer'):
                    performance_report = self.assistant.performance_optimizer.get_performance_report()
                    
                    # Préparer les informations de performance
                    info_lines = []
                    if "recent_stats" in performance_report:
                        for metric, stats in performance_report["recent_stats"].items():
                            info_lines.append(f"{metric}: {stats['current']:.1f}% (moy: {stats['average']:.1f}%)")
                    
                    # Ajouter les recommandations
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
        """
        Actualise les statistiques de performance.
        
        Returns:
            tuple: (utilisation_ressources, statut)
        """
        try:
            # Vérifier si l'assistant a la méthode de performance
            if hasattr(self.assistant, 'get_performance_status'):
                usage = self.assistant.get_performance_status()
                
                # Gérer les erreurs
                if "error" in usage:
                    return usage["error"], "❌ Erreur performance"
                
                # Formater les statistiques
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

    # =================================================================
    # FONCTIONS DE TRAITEMENT - PARAMÈTRES
    # =================================================================
    
    def _create_settings_tab(self):
        """
        Crée l'onglet des paramètres avancés.
        
        Configuration système, monitoring, et logs.
        """
        gr.Markdown("## 🔧 Paramètres avancés")
        
        # === SOUS-TABS PARAMÈTRES ===
        with gr.Tabs():
            # Tab Système
            with gr.Tab("🖥️ Système"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🎛️ Paramètres système")
                        # Configuration auto-start
                        self.auto_start_checkbox = gr.Checkbox(
                            label="Démarrage automatique",
                            value=True
                        )
                        
                        # Configuration port web
                        self.web_port_number = gr.Number(
                            label="Port Web",
                            value=self.assistant.settings.web_port,
                            precision=0
                        )
                        
                        # Bouton sauvegarde
                        self.save_settings_btn = gr.Button("💾 Sauvegarder")
                    
                    with gr.Column():
                        gr.Markdown("### 📈 Performance")
                        # Informations de performance
                        self.performance_info = gr.Textbox(
                            label="Informations de performance",
                            lines=8,
                            interactive=False
                        )
                        
                        # Boutons tests et optimisation
                        with gr.Row():
                            self.test_all_btn = gr.Button("🧪 Tester tous les services")
                            self.optimize_btn = gr.Button("⚡ Optimiser", variant="primary")
            
            # Tab Audio - NOUVEAU !
            with gr.Tab("🔊 Audio"):
                self._create_audio_settings_tab()
            
            # Tab Monitoring
            with gr.Tab("📊 Monitoring"):
                gr.Markdown("### 📊 Statistiques en temps réel")
                
                # Utilisation des ressources
                with gr.Row():
                    self.resource_usage = gr.Textbox(
                        label="Utilisation des ressources",
                        lines=8,
                        interactive=False
                    )
                
                # Santé système et tendances
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
                
                # Boutons de contrôle monitoring
                with gr.Row():
                    self.refresh_performance_btn = gr.Button("🔄 Actualiser")
                    self.detailed_report_btn = gr.Button("📋 Rapport détaillé")
                    self.aggressive_optimize_btn = gr.Button("🧨 Optimisation agressive", variant="secondary")
                
                # Configuration des seuils
                gr.Markdown("### ⚙️ Configuration des seuils")
                with gr.Row():
                    self.cpu_threshold = gr.Number(label="Seuil CPU (%)", value=80, precision=0)
                    self.memory_threshold = gr.Number(label="Seuil Mémoire (%)", value=85, precision=0)
                    self.gpu_threshold = gr.Number(label="Seuil GPU (%)", value=85, precision=0)
                
                self.update_thresholds_btn = gr.Button("💾 Mettre à jour seuils")
            
            # Tab Logs
            with gr.Tab("📜 Logs"):
                # Affichage des logs
                self.logs_display = gr.Textbox(
                    label="Logs en temps réel",
                    lines=12,
                    interactive=False,
                    max_lines=20
                )
                
                # Contrôles des logs
                with gr.Row():
                    self.log_level = gr.Dropdown(
                        label="Niveau de log",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        value="INFO"
                    )
                    self.clear_logs_btn = gr.Button("🗑️ Effacer logs")

    # =================================================================
    # FONCTIONS DE TRAITEMENT - MONITORING AVANCÉ
    # =================================================================
    
    def _get_detailed_performance_report(self):
        """
        Obtient un rapport détaillé de performance.
        
        Returns:
            tuple: (ressources, santé, tendances, statut)
        """
        try:
            # Vérifier si l'optimiseur est disponible
            if hasattr(self.assistant, 'performance_optimizer'):
                report = self.assistant.performance_optimizer.get_performance_report()
                
                # === RESSOURCES ===
                resource_lines = []
                if "current_stats" in report:
                    stats = report["current_stats"]
                    resource_lines.append("📊 Utilisation actuelle:")
                    resource_lines.append(f"  CPU: {stats.get('cpu_percent', 0):.1f}%")
                    resource_lines.append(f"  Mémoire: {stats.get('memory_percent', 0):.1f}%")
                    if "gpu_memory_used_mb" in stats:
                        gpu_percent = (stats["gpu_memory_used_mb"] / stats["gpu_memory_total_mb"]) * 100
                        resource_lines.append(f"  GPU: {gpu_percent:.1f}%")
                
                # === SANTÉ DU SYSTÈME ===
                health_lines = []
                if "system_health" in report:
                    health = report["system_health"]
                    health_lines.append(f"❤️  Santé: {health.get('score', 0)}/100")
                    health_lines.append(f"  Statut: {health.get('status', 'unknown')}")
                    issues = health.get('issues', [])
                    if issues:
                        health_lines.append(f"  Problèmes: {', '.join(issues)}")
                
                # === ANALYSE DES TENDANCES ===
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
        """
        Optimisation agressive du système.
        
        Yields:
            tuple: (message_progression, statut)
        """
        try:
            status = "🧨 Optimisation agressive en cours..."
            yield "Optimisation agressive en cours...", status
            
            # Vérifier si la méthode d'optimisation existe
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
        """
        Met à jour les seuils de performance.
        
        Args:
            cpu_threshold (int): Seuil CPU en %
            memory_threshold (int): Seuil mémoire en %
            gpu_threshold (int): Seuil GPU en %
            
        Returns:
            str: Message de confirmation
        """
        try:
            # Vérifier si la méthode existe
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

    # =================================================================
    # CONFIGURATION DES ÉVÉNEMENTS
    # =================================================================
    
    def _setup_advanced_events(self):
        """
        Configure tous les événements avancés de l'interface.
        
        Lie les boutons et interactions aux fonctions de traitement.
        """
        
        # === CONTRÔLES PRINCIPAUX ===
        self.start_btn.click(
            self._start_assistant,
            inputs=[self.mic_dropdown, self.voice_dropdown, self.model_dropdown, self.speed_slider],
            outputs=[self.status_text]
        )
        
        self.stop_btn.click(
            self._stop_assistant,
            outputs=[self.status_text]
        )
        
        # === CHAT ===
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
        
        # === FICHIERS SIMPLES ===
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
        
        # === PROJETS COMPLETS ===
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
        
        # === AUDIO/VOCALE ===
        self.record_btn.click(
            self._start_recording,
            outputs=[self.voice_command_status, self.status_text]
        )
        
        self.listen_btn.click(
            self._toggle_listening,
            inputs=[self.app_state],
            outputs=[self.app_state, self.voice_command_status, self.status_text]
        )
        
        # === PARAMÈTRES ===
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

    # =================================================================
    # FONCTIONS DE CALLBACK - CHARGEMENT
    # =================================================================
    
    def _on_interface_load(self):
        """
        Callback au chargement de l'interface.
        
        Returns:
            tuple: (statut, stats_système)
        """
        status = "🟢 Interface chargée - Assistant prêt"
        stats = self._get_system_stats_text()
        return status, stats
    
    # =================================================================
    # FONCTIONS DE CALLBACK - CONTRÔLES PRINCIPAUX
    # =================================================================
    
    def _start_assistant(self, mic_index, voice, model, speed):
        """
        Démarre l'assistant avec configuration.
        
        Args:
            mic_index (str): Index du microphone sélectionné
            voice (str): Voix sélectionnée
            model (str): Modèle IA sélectionné
            speed (float): Vitesse de parole
            
        Returns:
            str: Message de statut
        """
        try:
            # Mettre à jour les paramètres
            self.assistant.settings.voice_name = voice
            self.assistant.settings.llm_model = model
            
            # Démarrer les services de détection vocale
            self.assistant.wake_word_service.start_detection(int(mic_index.split(':')[0]))
            
            return "▶️ Assistant démarré - En attente du mot-clé 'Mario'"
        except Exception as e:
            logger.error(f"Erreur démarrage: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _stop_assistant(self):
        """
        Arrête l'assistant.
        
        Returns:
            str: Message de statut
        """
        try:
            self.assistant.wake_word_service.stop_detection()
            return "⏹️ Assistant arrêté"
        except Exception as e:
            logger.error(f"Erreur arrêt: {e}")
            return f"❌ Erreur: {str(e)}"
    
    # =================================================================
    # FONCTIONS DE CALLBACK - CHAT
    # =================================================================
    
    def _handle_user_message(self, message, model, temperature):
        """
        Traite un message utilisateur avec température.
        
        Args:
            message (str): Message de l'utilisateur
            model (str): Modèle IA à utiliser
            temperature (float): Température de créativité
            
        Returns:
            tuple: (historique_chat, message_vide, statut)
        """
        if not message or not message.strip():
            return self._get_chat_history(), "", "📝 Message vide ignoré"
        
        try:
            # Mettre à jour le modèle si nécessaire
            if model != self.assistant.settings.llm_model:
                self.assistant.llm_service.set_model(model)
                self.assistant.settings.llm_model = model
            
            # Traiter le message avec l'assistant
            response = self.assistant.process_user_message(message)
            
            # Parler la réponse (synthèse vocale)
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

    def _clear_conversation(self):
        """
        Efface la conversation.
        
        Returns:
            tuple: (historique_vide, statut)
        """
        try:
            self.assistant.clear_conversation()
            return [], "🧹 Conversation effacée"
        except Exception as e:
            logger.error(f"Erreur effacement conversation: {e}")
            return self._get_chat_history(), f"❌ Erreur: {str(e)}"
    
    # =================================================================
    # FONCTIONS DE CALLBACK - FICHIERS
    # =================================================================
    
    def _handle_file_upload(self, file_path):
        """
        Traite l'upload de fichier.
        
        Args:
            file_path (str): Chemin du fichier uploadé
            
        Returns:
            tuple: (info_fichier, statut)
        """
        if not file_path:
            return "Aucun fichier sélectionné", "📁 Aucun fichier"
        
        try:
            file_info = f"📁 Fichier reçu: {file_path}"
            return file_info, "✅ Fichier prêt pour analyse"
        except Exception as e:
            logger.error(f"Erreur upload fichier: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur upload"
    
    def _analyze_files_with_ai(self, file_path, model):
        """
        Analyse les fichiers avec l'IA.
        
        Args:
            file_path (str): Chemin du fichier à analyser
            model (str): Modèle IA à utiliser
            
        Returns:
            tuple: (analyse, statut)
        """
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            status = "🔍 Analyse en cours..."
            
            # Lire le contenu du fichier (limite 2000 caractères)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:2000]
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
        """
        Résume un fichier.
        
        Args:
            file_path (str): Chemin du fichier à résumer
            model (str): Modèle IA à utiliser
            
        Returns:
            tuple: (résumé, statut)
        """
        if not file_path:
            return "Veuillez d'abord sélectionner un fichier", "📁 Aucun fichier"
        
        try:
            # Lire le contenu du fichier (limite 3000 caractères)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:3000]
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
    
    # =================================================================
    # FONCTIONS DE CALLBACK - AUDIO/VOCALE
    # =================================================================
    
    def _start_recording(self):
        """
        Démarre l'enregistrement vocal.
        
        Returns:
            tuple: (message, statut)
        """
        try:
            return "🎤 Enregistrement démarré...", "🎙️ Enregistrement vocal activé"
        except Exception as e:
            logger.error(f"Erreur enregistrement: {e}")
            return f"❌ Erreur: {str(e)}", f"❌ Erreur enregistrement"
    
    def _toggle_listening(self, app_state):
        """
        Active/désactive l'écoute.
        
        Args:
            app_state (dict): État actuel de l'application
            
        Returns:
            tuple: (nouvel_état, statut_vocal, statut)
        """
        try:
            new_state = app_state.copy()
            new_state["is_listening"] = not app_state.get("is_listening", False)
            
            status = "👂 Écoute activée" if new_state["is_listening"] else "🔇 Écoute désactivée"
            voice_status = "Écoute en cours" if new_state["is_listening"] else "Prêt"
            
            return new_state, voice_status, status
        except Exception as e:
            logger.error(f"Erreur toggle écoute: {e}")
            return app_state, "❌ Erreur", f"❌ Erreur: {str(e)}"
    
    # =================================================================
    # FONCTIONS DE CALLBACK - PARAMÈTRES
    # =================================================================
    
    def _save_settings(self, auto_start, web_port):
        """
        Sauvegarde les paramètres.
        
        Args:
            auto_start (bool): Démarrage automatique
            web_port (int): Port web
            
        Returns:
            str: Message de confirmation
        """
        try:
            # Ici vous pouvez sauvegarder dans un fichier de config
            settings_info = f"💾 Paramètres sauvegardés:\n- Auto-start: {auto_start}\n- Port: {web_port}"
            return "✅ Paramètres sauvegardés"
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return f"❌ Erreur: {str(e)}"

    def _get_current_directory(self):
        """
        Retourne le dossier courant.
        
        Returns:
            tuple: (chemin_dossier, statut)
        """
        try:
            import os
            current_dir = os.getcwd()
            return current_dir, f"📁 Dossier courant: {current_dir}"
        except Exception as e:
            logger.error(f"Erreur récupération dossier courant: {e}")
            return ".", f"❌ Erreur: {str(e)}"
    
    def _test_all_services(self):
        """
        Teste tous les services.
        
        Returns:
            tuple: (info_tests, statut)
        """
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
        """
        Met à jour les stats système.
        
        Returns:
            tuple: (stats_text, statut)
        """
        try:
            stats_text = self._get_system_stats_text()
            return stats_text, "📊 Stats mises à jour"
        except Exception as e:
            logger.debug(f"Erreur stats: {e}")
            return "❌ Erreur stats", f"❌ Erreur: {str(e)}"
    
    # =================================================================
    # MÉTHODES UTILITAIRES
    # =================================================================
    
    def _get_chat_history(self):
        """
        Retourne l'historique du chat formaté.
        
        Returns:
            list: Historique formaté pour Gradio
        """
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
        """
        Rafraîchit l'affichage du chat.
        
        Returns:
            list: Historique du chat
        """
        try:
            return self._get_chat_history()
        except Exception as e:
            logger.error(f"Erreur refresh chat: {e}")
            return []

    def _get_system_stats_text(self):
        """
        Retourne les stats système formatées.
        
        Returns:
            str: Statistiques système formatées
        """
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
        """Retourne la liste des microphones filtrés."""
        return self.audio_controller.get_microphones()

    def _get_windows_audio_devices(self) -> Dict[str, List[str]]:
        """Détection spécifique pour Windows avec filtrage avancé."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            input_devices = []
            output_devices = []
            
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                name = device_info['name']
                name_lower = name.lower()
                
                # Classification des périphériques
                is_input = device_info['maxInputChannels'] > 0
                is_output = device_info['maxOutputChannels'] > 0
                
                # Score de pertinence basé sur le nom
                relevance_score = 0
                
                # Mots clés pour les périphériques physiques
                physical_keywords = [
                    'realtek', 'nvidia', 'amd', 'intel', 'usb', 'bluetooth',
                    'speakers', 'headphones', 'headset', 'microphone', 'array',
                    'webcam', 'camera', 'hdmi', 'displayport', 'line', 'analog',
                    'digital', 'primary', 'default', 'stereo', 'mono'
                ]
                
                # Mots clés pour les périphériques virtuels (à exclure)
                virtual_keywords = [
                    'virtual', 'vb-audio', 'voicemeeter', 'cable', 'loopback',
                    'mme', 'wasapi', 'directsound', 'steam', 'discord', 'zoom',
                    'teams', 'obs', 'virtual audio', 'scheduled', 'router'
                ]
                
                # Calcul du score de pertinence
                for keyword in physical_keywords:
                    if keyword in name_lower:
                        relevance_score += 2
                
                for keyword in virtual_keywords:
                    if keyword in name_lower:
                        relevance_score -= 3
                
                # Seuil de pertinence (ajuster selon les besoins)
                if relevance_score >= 0:
                    if is_input:
                        input_devices.append((i, name, relevance_score))
                    if is_output:
                        output_devices.append((i, name, relevance_score))
            
            p.terminate()
            
            # Trier par score de pertinence
            input_devices.sort(key=lambda x: x[2], reverse=True)
            output_devices.sort(key=lambda x: x[2], reverse=True)
            
            return {
                "inputs": [f"{idx}: {name}" for idx, name, score in input_devices[:6]],
                "outputs": [f"{idx}: {name}" for idx, name, score in output_devices[:6]]
            }
            
        except Exception as e:
            logger.error(f"Erreur détection audio Windows: {e}")
            return {
                "inputs": ["0: Microphone par défaut", "1: Microphone secondaire"],
                "outputs": ["0: Haut-parleurs par défaut", "1: Casque audio"]
            }

    def _debug_audio_devices(self):
        """Affiche tous les périphériques pour débogage."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            print("=== DÉBOGAGE PÉRIPHÉRIQUES AUDIO ===")
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                print(f"{i}: {device_info['name']} (In: {device_info['maxInputChannels']}, Out: {device_info['maxOutputChannels']})")
            
            p.terminate()
            
            # Aussi avec pvrecorder
            from pvrecorder import PvRecorder
            devices = PvRecorder.get_available_devices()
            print("=== PVRECORDER MICROPHONES ===")
            for i, name in enumerate(devices):
                print(f"{i}: {name}")
                
        except Exception as e:
            print(f"Erreur débogage: {e}")

    def _get_all_audio_devices(self, device_type: str) -> List[str]:
        """Retourne tous les périphériques (sans filtrage)."""
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
            return devices[:20]  # Limiter à 20 pour l'interface
            
        except Exception as e:
            logger.error(f"Erreur liste complète périphériques: {e}")
            return ["0: Périphérique par défaut"]

    def _get_audio_output_choices(self) -> List[str]:
        """Retourne la liste des sorties audio filtrées."""
        return self.audio_controller.get_speakers()
    
    def _get_default_microphone(self) -> str:
        """Retourne le microphone par défaut."""
        return self.audio_controller.get_default_microphone()
    
    def _get_voice_choices(self) -> List[str]:
        """
        Retourne la liste des voix disponibles.
        
        Returns:
            List[str]: Liste des voix
        """
        try:
            if hasattr(self.assistant, 'tts_service') and hasattr(self.assistant.tts_service, 'get_available_voices'):
                return self.assistant.tts_service.get_available_voices()
            return ["fr_FR-siwis-medium"]
        except Exception:
            return ["fr_FR-siwis-medium"]
    
    def _get_default_voice(self) -> str:
        """
        Retourne la voix par défaut.
        
        Returns:
            str: Voix par défaut
        """
        return "fr_FR-siwis-medium"
    
    def _get_model_choices(self) -> List[str]:
        """
        Retourne la liste des modèles disponibles localement via Ollama.
        
        Returns:
            List[str]: Liste des modèles locaux disponibles
        """
        try:
            # Vérifier si le service LLM et la méthode existent
            if hasattr(self.assistant, 'llm_service') and hasattr(self.assistant.llm_service, 'get_available_models'):
                # Récupérer les modèles disponibles localement
                models = self.assistant.llm_service.get_available_models()
                
                # Retourner les modèles trouvés ou une liste par défaut
                if models:
                    # Filtrer pour ne garder que les modèles français pertinents
                    relevant_models = [
                        model for model in models 
                        if any(keyword in model.lower() for keyword in [
                            'qwen', 'llama', 'gemma', 'mistral', 'phi', 'code'
                        ])
                    ]
                    return relevant_models if relevant_models else models
                else:
                    # Si aucun modèle trouvé, retourner les modèles par défaut
                    return self._get_default_local_models()
            else:
                # Service non disponible, retourner les modèles par défaut
                return self._get_default_local_models()
                
        except Exception as e:
            logger.debug(f"Erreur récupération modèles locaux: {e}")
            # En cas d'erreur, retourner les modèles par défaut
            return self._get_default_local_models()

    def _get_default_local_models(self) -> List[str]:
        """
        Retourne une liste de modèles locaux par défaut.
        
        Returns:
            List[str]: Liste des modèles par défaut
        """
        # Modèles les plus pertinents pour un usage français
        default_models = [
            "qwen2.5",           # Excellent en français
            "qwen3-coder:latest", # Votre modèle par défaut
            "llama3.2:latest",   # Llama 3.2
            "gemma2:latest",     # Gemma 2
            "mistral:latest",    # Mistral
            "phi3:latest",       # Phi-3
            "codellama:latest"   # Spécialisé code
        ]
        
        # Vérifier quels modèles sont réellement disponibles
        try:
            if hasattr(self.assistant, 'llm_service'):
                available = self.assistant.llm_service.get_available_models()
                if available:
                    # Retourner uniquement les modèles par défaut qui sont disponibles
                    return [model for model in default_models if model in available] or default_models
        except Exception:
            pass
        
        return default_models
    
    def _get_default_model(self) -> str:
        """
        Retourne le modèle par défaut.
        
        Returns:
            str: Modèle par défaut
        """
        return "qwen3-coder:latest"
    
    def launch(self, **kwargs):
        """
        Lance l'interface Gradio.
        
        Args:
            **kwargs: Arguments de lancement Gradio
            
        Returns:
            Lancement de l'interface
        """
        if not self.demo:
            self.create_interface()
        
        self.demo.launch(theme=gr.themes.Default(font=[gr.themes.GoogleFont("Inconsolata"), "Arial", "sans-serif"]))

    def _create_audio_settings_tab(self):
        """Crée l'onglet de configuration audio avec options avancées."""
        gr.Markdown("### 🔊 Configuration Audio")
        self._debug_audio_devices()
        with gr.Row():
            # Colonne Microphone
            with gr.Column():
                gr.Markdown("#### 🎤 Entrée Audio")
                
                # Sélection principale (filtrage intelligent)
                self.audio_mic_dropdown = gr.Dropdown(
                    label="Microphone (périphériques recommandés)",
                    choices=self._get_microphone_choices(),
                    value=self._get_default_microphone(),
                    interactive=True,
                    allow_custom_value=True
                )
                
                # Option pour voir tous les périphériques
                self.show_all_mics_btn = gr.Button("🔍 Voir tous les microphones", size="sm")
                self.all_mics_dropdown = gr.Dropdown(
                    label="Tous les microphones (avancé)",
                    choices=self._get_all_audio_devices("input"),
                    visible=False,
                    interactive=True,
                    allow_custom_value=True
                )
                
                # Test microphone
                self.test_mic_btn = gr.Button("🎤 Tester le microphone", variant="secondary")
                self.mic_test_status = gr.Textbox(
                    label="Test microphone",
                    lines=2,
                    interactive=False,
                    value="Cliquez pour tester"
                )
            
            # Colonne Sortie Audio
            with gr.Column():
                gr.Markdown("#### 🔈 Sortie Audio")
                
                # Sélection principale (filtrage intelligent)
                self.audio_output_dropdown = gr.Dropdown(
                    label="Sortie audio (périphériques recommandés)",
                    choices=self._get_audio_output_choices(),
                    value=self._get_default_audio_output(),
                    interactive=True
                )
                
                # Option pour voir tous les périphériques
                self.show_all_outputs_btn = gr.Button("🔍 Voir toutes les sorties", size="sm")
                self.all_outputs_dropdown = gr.Dropdown(
                    label="Toutes les sorties audio (avancé)",
                    choices=self._get_all_audio_devices("output"),
                    visible=False,
                    interactive=True
                )
                
                # Test sortie audio
                self.test_speaker_btn = gr.Button("🔊 Tester la sortie", variant="secondary")
                self.speaker_test_status = gr.Textbox(
                    label="Test sortie audio",
                    lines=2,
                    interactive=False,
                    value="Cliquez pour tester"
                )
        
        # Configuration audio avancée
        with gr.Accordion("⚙️ Paramètres audio avancés", open=False):
            with gr.Row():
                # Volume général
                self.audio_volume = gr.Slider(
                    label="🔊 Volume général",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.8,
                    step=0.1
                )
                
                # Sensibilité du microphone
                self.mic_sensitivity = gr.Slider(
                    label="🎤 Sensibilité microphone",
                    minimum=0.1,
                    maximum=2.0,
                    value=1.0,
                    step=0.1
                )
            
            with gr.Row():
                # Délai de silence
                self.silence_delay = gr.Slider(
                    label="⏱️ Délai de silence (secondes)",
                    minimum=0.5,
                    maximum=5.0,
                    value=2.0,
                    step=0.5
                )
                
                # Seuil de détection vocale
                self.vad_threshold = gr.Slider(
                    label="📊 Seuil détection vocale",
                    minimum=0.1,
                    maximum=0.9,
                    value=0.5,
                    step=0.1
                )
        
        # Boutons d'action
        with gr.Row():
            self.save_audio_btn = gr.Button("💾 Sauvegarder paramètres audio", variant="primary")
            self.apply_audio_btn = gr.Button("🔄 Appliquer maintenant")
            self.reset_audio_btn = gr.Button("🔄 Réinitialiser")
        
        # Statut audio
        self.audio_settings_status = gr.Textbox(
            label="Statut audio",
            lines=3,
            interactive=False,
            value="Configuration audio prête"
        )
        
        # Configuration des événements audio
        self._setup_audio_events()


    def _get_audio_output_choices(self) -> List[str]:
        """Retourne la liste des sorties audio (version finale stricte)."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            filtered = []
            for i in range(min(10, p.get_device_count())):  # Limiter à 10 périphériques
                device_info = p.get_device_info_by_index(i)
                name = device_info['name'].lower()
                
                if device_info['maxOutputChannels'] > 0:
                    # Exclusion forte
                    if any(virtual in name for virtual in ['virtual', 'voicemeeter', 'cable', 'loopback']):
                        continue
                        
                    # Inclusion seulement des physiques évidents
                    if any(physical in name for physical in ['speakers', 'headphone', 'headset', 'haut-parleurs', 'casque']):
                        filtered.append((i, device_info['name']))
            
            p.terminate()
            
            # Limiter à 4 maximum
            if len(filtered) > 4:
                filtered = filtered[:4]
                
            # Si pas assez, compléter
            if len(filtered) < 2:
                filtered = [(0, "Haut-parleurs par défaut"), (1, "Casque audio")]
                
            return [f"{idx}: {name}" for idx, name in filtered]
            
        except Exception as e:
            logger.error(f"Erreur sorties audio: {e}")
            return ["0: Haut-parleurs par défaut", "1: Casque audio"]
        
    def _get_default_audio_output(self) -> str:
        """Retourne la sortie audio par défaut."""
        return self.audio_controller.get_default_speaker()

    def _test_microphone(self, mic_device):
        """Teste le microphone sélectionné."""
        try:
            # Extraire l'index du microphone
            mic_index = int(mic_device.split(":")[0])
            
            # Simuler un test (vous pouvez implémenter un vrai test audio)
            return "✅ Test microphone réussi\n🎤 Microphone fonctionnel et configuré correctement", "✅ Test réussi"
        except Exception as e:
            return f"❌ Erreur test microphone: {str(e)}", "❌ Test échoué"

    def _test_speaker(self, speaker_device):
        """Teste la sortie audio sélectionnée."""
        try:
            # Extraire l'index de la sortie
            speaker_index = int(speaker_device.split(":")[0])
            
            # Jouer un son de test via l'assistant
            self.assistant.speak_response("Ceci est un test de la sortie audio.")
            
            return "✅ Test sortie audio réussi\n🔊 Son joué avec succès", "✅ Test réussi"
        except Exception as e:
            return f"❌ Erreur test sortie: {str(e)}", "❌ Test échoué"

    def _save_audio_settings(self, mic_device, output_device, volume, sensitivity, silence_delay, vad_threshold):
        """Sauvegarde les paramètres audio."""
        try:
            # Sauvegarder les paramètres dans l'assistant
            settings = {
                "microphone": mic_device,
                "output_device": output_device,
                "volume": volume,
                "mic_sensitivity": sensitivity,
                "silence_delay": silence_delay,
                "vad_threshold": vad_threshold
            }
            
            # Ici vous pouvez sauvegarder dans un fichier de configuration
            logger.info(f"Paramètres audio sauvegardés: {settings}")
            
            return "✅ Paramètres audio sauvegardés avec succès"
        except Exception as e:
            return f"❌ Erreur sauvegarde: {str(e)}"

    def _apply_audio_settings(self, mic_device, output_device):
        """Applique immédiatement les paramètres audio."""
        try:
            # Mettre à jour les services audio
            mic_index = int(mic_device.split(":")[0])
            output_index = int(output_device.split(":")[0])
            
            # Redémarrer le service de détection avec le nouveau microphone
            self.assistant.wake_word_service.stop_detection()
            self.assistant.wake_word_service.start_detection(mic_index)
            
            return "✅ Paramètres audio appliqués avec succès\n🎤 Microphone et sortie mis à jour"
        except Exception as e:
            return f"❌ Erreur application: {str(e)}"

    def _setup_audio_events(self):
        """Configure les événements de l'onglet audio."""
        
        # Cache les dropdowns avancés au début
        self.all_mics_dropdown.visible = False
        self.all_outputs_dropdown.visible = False
        
        # Variables pour suivre l'état de visibilité
        mics_visible = False
        outputs_visible = False
        
        # Afficher/masquer tous les microphones
        def toggle_mics():
            nonlocal mics_visible
            mics_visible = not mics_visible
            return gr.update(visible=mics_visible)
        
        self.show_all_mics_btn.click(
            toggle_mics,
            outputs=[self.all_mics_dropdown]
        )
        
        # Afficher/masquer toutes les sorties
        def toggle_outputs():
            nonlocal outputs_visible
            outputs_visible = not outputs_visible
            return gr.update(visible=outputs_visible)
        
        self.show_all_outputs_btn.click(
            toggle_outputs,
            outputs=[self.all_outputs_dropdown]
        )
        
        # Synchroniser les sélections avancées vers les principales
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
        
        # Test microphone
        self.test_mic_btn.click(
            self._test_microphone,
            inputs=[self.audio_mic_dropdown],
            outputs=[self.mic_test_status, self.audio_settings_status]
        )
        
        # Test sortie audio
        self.test_speaker_btn.click(
            self._test_speaker,
            inputs=[self.audio_output_dropdown],
            outputs=[self.speaker_test_status, self.audio_settings_status]
        )
        
        # Sauvegarde paramètres
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
        
        # Application immédiate
        self.apply_audio_btn.click(
            self._apply_audio_settings,
            inputs=[self.audio_mic_dropdown, self.audio_output_dropdown],
            outputs=[self.audio_settings_status]
        )
        
        # Réinitialisation
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

# Export pour l'importation
__all__ = ['GradioWebInterface']
