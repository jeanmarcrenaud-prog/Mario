"""
Gestionnaire de Prompts pour l'Assistant Vocal
============================================

Gère le stockage, la création et l'utilisation de prompts personnalisés.
"""

import json
import os
from typing import Dict, List, Optional
from ..utils.logger import logger

class PromptManager:
    """Gestionnaire de prompts personnalisés."""
    
    def __init__(self, prompts_file: str = "prompts.json"):
        """
        Initialise le gestionnaire de prompts.
        
        Args:
            prompts_file (str): Chemin du fichier de stockage des prompts
        """
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()
        logger.info(f"PromptManager initialisé avec {len(self.prompts)} prompts")
    
    def _load_prompts(self) -> Dict:
        """
        Charge les prompts depuis le fichier.
        
        Returns:
            Dict: Dictionnaire des prompts
        """
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Créer des prompts par défaut
                default_prompts = self._get_default_prompts()
                self._save_prompts(default_prompts)
                return default_prompts
        except Exception as e:
            logger.error(f"Erreur chargement prompts: {e}")
            return self._get_default_prompts()
    
    def _save_prompts(self, prompts: Dict):
        """
        Sauvegarde les prompts dans le fichier.
        
        Args:
            prompts (Dict): Dictionnaire des prompts à sauvegarder
        """
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde prompts: {e}")
    
    def _get_default_prompts(self) -> Dict:
        """
        Retourne les prompts par défaut.
        
        Returns:
            Dict: Prompts par défaut
        """
        return {
            "analyse_code_python": {
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
                "variables": [],
                "temperature": 0.7,
                "max_tokens": 2000,
                "system_message": "Vous êtes un expert Python expérimenté."
            },
            "resume_technique": {
                "name": "Résumé technique",
                "description": "Résumé concis de contenu technique",
                "category": "Résumé de texte",
                "template": """Fournissez un résumé technique concis du contenu suivant:

{input}

Structurez le résumé en:
- Points clés (3-5 items)
- Concepts principaux
- Applications potentielles""",
                "variables": [],
                "temperature": 0.3,
                "max_tokens": 500,
                "system_message": "Soyez concis et précis dans votre résumé."
            }
        }
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """
        Récupère un prompt par son ID.
        
        Args:
            prompt_id (str): ID du prompt
            
        Returns:
            Optional[Dict]: Prompt trouvé ou None
        """
        return self.prompts.get(prompt_id)
    
    def get_prompt_by_name(self, name: str) -> Optional[Dict]:
        """
        Récupère un prompt par son nom.
        
        Args:
            name (str): Nom du prompt
            
        Returns:
            Optional[Dict]: Prompt trouvé ou None
        """
        for prompt in self.prompts.values():
            if prompt.get("name") == name:
                return prompt
        return None
    
    def get_all_prompts(self) -> Dict:
        """
        Récupère tous les prompts.
        
        Returns:
            Dict: Tous les prompts
        """
        return self.prompts
    
    def get_prompt_names(self) -> List[str]:
        """
        Récupère la liste des noms de prompts.
        
        Returns:
            List[str]: Liste des noms de prompts
        """
        return [prompt["name"] for prompt in self.prompts.values()]
    
    def get_prompts_by_category(self, category: str) -> List[Dict]:
        """
        Récupère les prompts d'une catégorie donnée.
        
        Args:
            category (str): Catégorie recherchée
            
        Returns:
            List[Dict]: Liste des prompts de la catégorie
        """
        return [prompt for prompt in self.prompts.values() if prompt.get("category") == category]
    
    def save_prompt(self, prompt_id: str, prompt_data: Dict) -> bool:
        """
        Sauvegarde un prompt.
        
        Args:
            prompt_id (str): ID du prompt
            prompt_data (Dict): Données du prompt
            
        Returns:
            bool: Succès de la sauvegarde
        """
        try:
            self.prompts[prompt_id] = prompt_data
            self._save_prompts(self.prompts)
            logger.info(f"Prompt sauvegardé: {prompt_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde prompt {prompt_id}: {e}")
            return False
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Supprime un prompt.
        
        Args:
            prompt_id (str): ID du prompt à supprimer
            
        Returns:
            bool: Succès de la suppression
        """
        try:
            if prompt_id in self.prompts:
                del self.prompts[prompt_id]
                self._save_prompts(self.prompts)
                logger.info(f"Prompt supprimé: {prompt_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur suppression prompt {prompt_id}: {e}")
            return False
    
    def generate_prompt_text(self, prompt_template: str, input_text: str, custom_variables: Dict = None) -> str:
        """
        Génère le texte final du prompt avec les variables.
        
        Args:
            prompt_template (str): Template du prompt
            input_text (str): Texte d'entrée
            custom_variables (Dict): Variables personnalisées
            
        Returns:
            str: Prompt généré
        """
        try:
            # Remplacer le placeholder principal
            prompt = prompt_template.replace('{input}', input_text or '')
            
            # Remplacer les variables personnalisées
            if custom_variables:
                for key, value in custom_variables.items():
                    prompt = prompt.replace(f'{{{key}}}', str(value))
            
            return prompt
        except Exception as e:
            logger.error(f"Erreur génération prompt: {e}")
            return prompt_template

# Export
__all__ = ['PromptManager']
