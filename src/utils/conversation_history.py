"""
Module pour gérer l'historique des conversations.
Stocke et récupère l'historique des interactions utilisateur-LLM.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.utils.logger import logger


class ConversationHistory:
    """Gère l'historique des conversations utilisateur-LLM."""
    
    def __init__(self, history_file: str = "conversations/history.json", max_history: int = 100):
        """
        Initialise l'historique des conversations.
        
        Args:
            history_file: Chemin du fichier JSON pour stocker l'historique
            max_history: Nombre maximum d'entrées à conserver
        """
        self.history_file = Path(history_file)
        self.max_history = max_history
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Crée le fichier d'historique s'il n'existe pas."""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, conversation_id: str, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Sauvegarde une conversation dans l'historique.
        
        Args:
            conversation_id: ID unique de la conversation
            messages: Liste des messages de la conversation
            metadata: Métadonnées supplémentaires
        """
        try:
            # Charger l'historique existant
            history = self.load()
            
            # Ajouter la nouvelle conversation
            conversation = create_conversation(conversation_id, messages, metadata)
            history.append(conversation)
            
            # Garder seulement les dernières entrées
            if len(history) > self.max_history:
                history = history[-self.max_history:]
            
            # Sauvegarder
            self._write_history(history)
            
            logger.debug("Conversation sauvegardée dans l'historique")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la conversation: {e}")
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Charge l'historique des conversations.
        
        Returns:
            Liste des conversations sauvegardées
        """
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
            
        except json.JSONDecodeError:
            logger.error("Erreur de décodage JSON dans l'historique")
            return []
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique: {e}")
            return []
    
    def _write_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Écrit l'historique dans le fichier JSON.
        
        Args:
            history: Liste des conversations à sauvegarder
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de l'historique: {e}")
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les dernières conversations.
        
        Args:
            limit: Nombre maximum de conversations à retourner
            
        Returns:
            Liste des dernières conversations
        """
        history = self.load()
        return history[-limit:] if len(history) >= limit else history
    
    def get_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une conversation par son ID.
        
        Args:
            conversation_id: ID unique de la conversation
            
        Returns:
            La conversation ou None si non trouvée
        """
        history = self.load()
        for conv in history:
            if conv.get('id') == conversation_id:
                return conv
        return None
    
    def delete(self, conversation_id: str) -> bool:
        """
        Supprime une conversation de l'historique.
        
        Args:
            conversation_id: ID de la conversation à supprimer
            
        Returns:
            True si supprimée, False si non trouvée
        """
        try:
            history = self.load()
            original_len = len(history)
            history = [c for c in history if c.get('id') != conversation_id]
            
            if len(history) < original_len:
                self._write_history(history)
                logger.debug(f"Conversation {conversation_id} supprimée")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la conversation: {e}")
            return False
    
    def clear(self) -> None:
        """Vide l'historique des conversations."""
        try:
            self._write_history([])
            logger.info("Historique des conversations vidé")
        except Exception as e:
            logger.error(f"Erreur lors du vidage de l'historique: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur l'historique.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        history = self.load()
        return {
            "total_conversations": len(history),
            "total_messages": sum(len(c.get('messages', [])) for c in history),
            "last_conversation": history[-1] if history else None,
            "oldest_conversation": history[0] if history else None
        }
    
    def export_to_file(self, filepath: str) -> bool:
        """
        Exporte l'historique vers un fichier.
        
        Args:
            filepath: Chemin du fichier de sortie
            
        Returns:
            True si export réussi, False sinon
        """
        try:
            history = self.load()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            logger.info(f"Historique exporté vers {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export de l'historique: {e}")
            return False
    
    def import_from_file(self, filepath: str) -> int:
        """
        Importe des conversations depuis un fichier.
        
        Args:
            filepath: Chemin du fichier d'import
            
        Returns:
            Nombre de conversations importées
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                new_history = json.load(f)
            
            if not isinstance(new_history, list):
                logger.error("Format JSON invalide pour l'import")
                return 0
            
            history = self.load()
            history.extend(new_history)
            
            # Garder seulement les dernières entrées
            if len(history) > self.max_history:
                history = history[-self.max_history:]
            
            self._write_history(history)
            logger.info(f"{len(new_history)} conversations importées")
            return len(new_history)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'import de l'historique: {e}")
            return 0


def create_conversation(conversation_id: str, messages: List[Dict[str, Any]], 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Crée un objet conversation prêt à être sauvegardé.
    
    Args:
        conversation_id: ID unique de la conversation
        messages: Liste des messages de la conversation
        metadata: Métadonnées supplémentaires
        
    Returns:
        Dictionnaire représentant la conversation
    """
    return {
        "id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
        "metadata": metadata or {}
    }
