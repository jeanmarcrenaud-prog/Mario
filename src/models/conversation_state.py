from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ConversationState:
    """État de la conversation."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """Ajoute un message à la conversation."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Retourne tous les messages."""
        return self.messages.copy()
    
    def get_last_message(self) -> Optional[Dict[str, str]]:
        """Retourne le dernier message."""
        return self.messages[-1] if self.messages else None
    
    def clear(self):
        """Efface tous les messages."""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def get_message_count(self) -> int:
        """Retourne le nombre de messages."""
        return len(self.messages)
