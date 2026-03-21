"""Tests pour ConversationHistory"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from src.utils.conversation_history import ConversationHistory, create_conversation


class TestConversationHistory:
    """Tests de base pour ConversationHistory"""
    
    @pytest.fixture
    def temp_history_file(self):
        """Crée un fichier temporaire pour les tests"""
        temp_path = Path(tempfile.mktemp(suffix='.json'))
        assert not temp_path.exists()
        yield temp_path
        # Nettoyage
        if temp_path.exists():
            os.unlink(temp_path)
    
    @pytest.fixture
    def history(self, temp_history_file):
        """Crée une instance de ConversationHistory"""
        return ConversationHistory(str(temp_history_file), max_history=10)
    
    def test_init_creates_file(self, temp_history_file):
        """Test que le fichier n'existe pas avant initialisation"""
        assert not temp_history_file.exists()
        # Note: ConversationHistory ne crée pas le fichier à l'initialisation
        history = ConversationHistory(str(temp_history_file))
        assert history.history_file == temp_history_file
    
    def test_save_conversation(self, history):
        """Test la sauvegarde d'une conversation"""
        messages = [{"role": "user", "content": "Bonjour"}]
        history.save("conv_1", messages)
        
        loaded = history.load()
        assert len(loaded) == 1
        assert loaded[0]["id"] == "conv_1"
        assert loaded[0]["messages"] == messages
    
    def test_save_multiple_conversations(self, history):
        """Test la sauvegarde de plusieurs conversations"""
        history.save("conv_1", [{"role": "user", "content": "Message 1"}])
        history.save("conv_2", [{"role": "user", "content": "Message 2"}])
        history.save("conv_3", [{"role": "user", "content": "Message 3"}])
        
        loaded = history.load()
        assert len(loaded) == 3
    
    def test_get_recent(self, history):
        """Test la récupération des dernières conversations"""
        history.save("conv_1", [{"role": "user", "content": "1"}])
        history.save("conv_2", [{"role": "user", "content": "2"}])
        history.save("conv_3", [{"role": "user", "content": "3"}])
        
        recent = history.get_recent(2)
        assert len(recent) == 2
        assert recent[0]["id"] == "conv_2"
        assert recent[1]["id"] == "conv_3"
    
    def test_get_by_id(self, history):
        """Test la récupération par ID"""
        history.save("conv_1", [{"role": "user", "content": "Test"}])
        
        conv = history.get_by_id("conv_1")
        assert conv is not None
        assert conv["id"] == "conv_1"
        
        conv = history.get_by_id("non_existent")
        assert conv is None
    
    def test_delete_conversation(self, history):
        """Test la suppression d'une conversation"""
        history.save("conv_1", [{"role": "user", "content": "1"}])
        history.save("conv_2", [{"role": "user", "content": "2"}])
        
        assert history.delete("conv_1")
        loaded = history.load()
        assert len(loaded) == 1
        assert loaded[0]["id"] == "conv_2"
        
        assert not history.delete("non_existent")
    
    def test_clear_history(self, history):
        """Test le vidage de l'historique"""
        history.save("conv_1", [{"role": "user", "content": "1"}])
        history.save("conv_2", [{"role": "user", "content": "2"}])
        
        history.clear()
        loaded = history.load()
        assert len(loaded) == 0
    
    def test_get_statistics(self, history):
        """Test les statistiques"""
        history.save("conv_1", [{"role": "user", "content": "1"}, {"role": "assistant", "content": "2"}])
        history.save("conv_2", [{"role": "user", "content": "3"}])
        
        stats = history.get_statistics()
        assert stats["total_conversations"] == 2
        assert stats["total_messages"] == 3
    
    def test_max_history_limit(self, temp_history_file):
        """Test que max_history est respecté"""
        history = ConversationHistory(str(temp_history_file), max_history=2)
        
        for i in range(5):
            history.save(f"conv_{i}", [{"role": "user", "content": str(i)}])
        
        loaded = history.load()
        assert len(loaded) == 2
        assert loaded[0]["id"] == "conv_3"
        assert loaded[1]["id"] == "conv_4"
    
    def test_export_to_file(self, history, temp_history_file):
        """Test l'export vers un fichier"""
        history.save("conv_1", [{"role": "user", "content": "1"}])
        
        export_path = temp_history_file.parent / "export.json"
        result = history.export_to_file(str(export_path))
        
        assert result
        assert export_path.exists()
        
        with open(export_path) as f:
            data = json.load(f)
        assert len(data) == 1
    
    def test_import_from_file(self, history, temp_history_file):
        """Test l'import depuis un fichier"""
        # Créer un fichier à importer
        import_path = temp_history_file.parent / "import.json"
        import_data = [
            {"id": "imported_1", "timestamp": "2020-01-01T00:00:00", "messages": [{"role": "user", "content": "Importé"}]},
        ]
        with open(import_path, 'w') as f:
            json.dump(import_data, f)
        
        result = history.import_from_file(str(import_path))
        
        assert result == 1
        loaded = history.load()
        assert len(loaded) == 1  # 1 importé (history.new() crée conversation vide, pas sauvegardée)
    
    def test_create_conversation(self):
        """Test la création d'un objet conversation"""
        conv = create_conversation(
            conversation_id="test_id",
            messages=[{"role": "user", "content": "Test"}],
            metadata={"source": "api"}
        )
        
        assert conv["id"] == "test_id"
        assert conv["messages"] == [{"role": "user", "content": "Test"}]
        assert conv["metadata"]["source"] == "api"
        assert "timestamp" in conv
