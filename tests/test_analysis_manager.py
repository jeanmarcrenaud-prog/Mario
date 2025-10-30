# tests/test_analysis_manager.py
import pytest
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from src.ui.analysis_manager import AnalysisManager

class TestAnalysisManager:
    
    def test_initialization(self):
        """Test l'initialisation de AnalysisManager."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        assert manager.file_analyzer == mock_file_analyzer
        assert manager.llm_client == mock_llm_client

    @patch('src.ui.analysis_manager.Path')
    def test_analyze_with_ollama_success(self, mock_path):
        """Test l'analyse réussie avec Ollama."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        # Mock des résultats d'analyse
        mock_file_stats = [
            {'path': 'test.py', 'lines': 100, 'words': 500, 'size_bytes': 1024}
        ]
        mock_total_stats = {'files': 1, 'lines': 100, 'words': 500, 'size_bytes': 1024}
        mock_file_types = MagicMock()
        mock_file_types.most_common.return_value = [('.py', 1)]
        
        mock_file_analyzer.analyze_directory.return_value = (
            mock_file_stats, mock_total_stats, mock_file_types, None
        )
        
        # Mock Ollama
        mock_llm_client.set_model.return_value = True
        mock_llm_client.chat_stream.return_value = ["Analyse", " technique", " réussie"]
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_with_ollama("/test/path", "test-model", mock_chat_lock)
        
        assert result["error"] == False
        assert "Analyse Ollama terminée" in result["summary"]
        assert "[IA] ANALYSE INTELLIGENTE:" in result["report"]
        mock_file_analyzer.analyze_directory.assert_called_once_with("/test/path")

    @patch('src.ui.analysis_manager.Path')
    def test_analyze_with_ollama_error(self, mock_path):
        """Test l'analyse avec erreur de file_analyzer."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        mock_file_analyzer.analyze_directory.return_value = (
            [], {}, MagicMock(), "Erreur d'analyse"
        )
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_with_ollama("/test/path", "test-model", mock_chat_lock)
        
        assert result["error"] == True
        assert "[ERREUR]" in result["report"]
        assert "Erreur lors de l'analyse" in result["summary"]

    @patch('src.ui.analysis_manager.Path')
    def test_analyze_with_ollama_exception(self, mock_path):
        """Test l'analyse avec exception."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        mock_file_analyzer.analyze_directory.side_effect = Exception("Test error")
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_with_ollama("/test/path", "test-model", mock_chat_lock)
        
        assert result["error"] == True
        assert "[ERREUR]" in result["report"]

    def test_analyze_directory_success(self):
        """Test l'analyse simple de répertoire réussie."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        mock_file_stats = [{'path': 'test.py', 'lines': 100, 'words': 500, 'size_bytes': 1024}]
        mock_total_stats = {'files': 1, 'lines': 100, 'words': 500, 'size_bytes': 1024}
        mock_file_types = MagicMock()
        mock_file_types.most_common.return_value = [('.py', 1)]
        
        mock_file_analyzer.analyze_directory.return_value = (
            mock_file_stats, mock_total_stats, mock_file_types, None
        )
        mock_file_analyzer.generate_summary.return_value = "Résumé de test"
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_directory("/test/path")
        
        assert result["error"] == False
        assert "[STATS] RAPPORT D'ANALYSE" in result["report"]
        assert result["summary"] == "Résumé de test"

    def test_analyze_directory_error(self):
        """Test l'analyse de répertoire avec erreur."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        mock_file_analyzer.analyze_directory.return_value = (
            [], {}, MagicMock(), "Erreur d'analyse"
        )
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_directory("/test/path")
        
        assert result["error"] == True
        assert "[ERREUR]" in result["report"]

    def test_analyze_directory_exception(self):
        """Test l'analyse de répertoire avec exception."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        mock_file_analyzer.analyze_directory.side_effect = Exception("Test error")
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_directory("/test/path")
        
        assert result["error"] == True
        assert "[ERREUR]" in result["report"]

    @patch('src.ui.analysis_manager.open')
    def test_analyze_single_file_success(self, mock_open):
        """Test l'analyse de fichier unique réussie."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        # Mock de l'analyse de fichier
        mock_file_info = {
            'lines': 100, 'words': 500, 'size_bytes': 1024, 'functions': 5, 'classes': 2
        }
        mock_file_analyzer.analyze_file.return_value = mock_file_info
        
        # Mock de la lecture de fichier
        mock_file = MagicMock()
        mock_file.read.return_value = "contenu du fichier"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock Ollama
        mock_llm_client.set_model.return_value = True
        mock_llm_client.chat_stream.return_value = ["Analyse", " du fichier"]
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_single_file("/test/file.py", "test-model", mock_chat_lock)
        
        assert "uploadé" in result["user_message"]
        assert "[IA] Analyse du fichier" in result["assistant_message"]
        mock_file_analyzer.analyze_file.assert_called_once()

    @patch('src.ui.analysis_manager.open')
    def test_analyze_single_file_error(self, mock_open):
        """Test l'analyse de fichier avec erreur."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        mock_file_analyzer.analyze_file.return_value = {'error': 'Erreur fichier'}
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_single_file("/test/file.py", "test-model", mock_chat_lock)
        
        assert "Erreur analyse" in result["user_message"]
        assert "[ERREUR]" in result["assistant_message"]

    @patch('src.ui.analysis_manager.open')
    def test_analyze_single_file_exception(self, mock_open):
        """Test l'analyse de fichier avec exception."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        mock_chat_lock = MagicMock()
        
        mock_open.side_effect = Exception("Erreur lecture")
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        result = manager.analyze_single_file("/test/file.py", "test-model", mock_chat_lock)
        
        assert "Erreur upload" in result["user_message"]
        assert "[ERREUR]" in result["assistant_message"]

    def test_prepare_ollama_context(self):
        """Test la préparation du contexte Ollama."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        # Données de test
        file_stats = [
            {'path': 'big.py', 'lines': 500, 'words': 2000, 'size_bytes': 5000, 'functions': 10, 'classes': 3},
            {'path': 'small.txt', 'lines': 10, 'words': 50, 'size_bytes': 100},
            {'path': 'error.py', 'error': 'Erreur'}  # Fichier avec erreur
        ]
        total_stats = {'files': 2, 'lines': 510, 'words': 2050, 'size_bytes': 5100}
        
        from collections import Counter
        file_types = Counter({'.py': 1, '.txt': 1})
        
        context = manager._prepare_ollama_context(file_stats, total_stats, file_types)
        
        assert context["statistiques_globales"]["nombre_fichiers"] == 2
        assert context["repartition_fichiers"]['.py'] == 1
        assert len(context["fichiers_principaux"]) == 2  # Seulement les fichiers valides

    @patch('src.ui.analysis_manager.open')
    def test_prepare_ollama_context_with_python_files(self, mock_open):
        """Test la préparation du contexte avec fichiers Python."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        # Mock de la lecture de fichier Python
        mock_file = MagicMock()
        mock_file.read.return_value = "def test():\n    pass\n"
        mock_open.return_value.__enter__.return_value = mock_file
        
        file_stats = [
            {'path': 'test.py', 'lines': 10, 'words': 50, 'size_bytes': 100, 'functions': 1, 'classes': 0, 'imports': 2}
        ]
        total_stats = {'files': 1, 'lines': 10, 'words': 50, 'size_bytes': 100}
        
        from collections import Counter
        file_types = Counter({'.py': 1})
        
        context = manager._prepare_ollama_context(file_stats, total_stats, file_types)
        
        assert len(context["fichiers_python"]) == 1
        assert context["fichiers_python"][0]["nom"] == "test.py"

    def test_get_ollama_analysis(self):
        """Test l'obtention de l'analyse Ollama."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        # Mock Ollama
        mock_llm_client.set_model.return_value = True
        mock_llm_client.chat_stream.return_value = ["Analyse", " technique"]
        
        context = {
            "statistiques_globales": {"nombre_fichiers": 1, "lignes_total": 100, "mots_total": 500, "taille_total_mo": 0.1},
            "repartition_fichiers": {".py": 1},
            "fichiers_principaux": [],
            "fichiers_python": []
        }
        
        analysis = manager._get_ollama_analysis("test-model", context)
        
        assert analysis == "Analyse technique"
        mock_llm_client.set_model.assert_called_once_with("test-model")
        mock_llm_client.chat_stream.assert_called_once()

    @patch('src.ui.analysis_manager.open')
    def test_analyze_single_file_with_ollama(self, mock_open):
        """Test l'analyse de fichier unique avec Ollama."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        # Mock Ollama
        mock_llm_client.set_model.return_value = True
        mock_llm_client.chat_stream.return_value = ["Analyse", " fichier"]
        
        file_info = {'lines': 100, 'words': 500, 'size_bytes': 1024}
        content = "contenu du fichier"
        
        analysis = manager._analyze_single_file_with_ollama("test-model", "test.py", file_info, content)
        
        assert analysis == "Analyse fichier"
        mock_llm_client.set_model.assert_called_once_with("test-model")

    def test_create_analysis_prompt(self):
        """Test la création du prompt d'analyse."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()

        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)

        context = {
            "statistiques_globales": {
                "nombre_fichiers": 10,
                "lignes_total": 1500,
                "mots_total": 7500,
                "taille_total_mo": 2.5
            },
            "repartition_fichiers": {".py": 5, ".txt": 3, "": 2},
            "fichiers_principaux": [],
            "fichiers_python": []
        }

        prompt = manager._create_analysis_prompt(context)

        assert "Fichiers: 10" in prompt
        assert "Lignes: 1,500" in prompt
        # CORRECTION : Utiliser la chaîne exacte du prompt
        assert "Type de projet et architecture ?" in prompt


    def test_generate_detailed_report(self):
        """Test la génération du rapport détaillé."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        file_stats = [
            {'path': 'big.py', 'lines': 500, 'words': 2000, 'size_bytes': 5000000},
            {'path': 'small.txt', 'lines': 10, 'words': 50, 'size_bytes': 1000}
        ]
        total_stats = {'files': 2, 'lines': 510, 'words': 2050, 'size_bytes': 5001000}
        
        from collections import Counter
        file_types = Counter({'.py': 1, '.txt': 1})
        
        report = manager._generate_detailed_report(file_stats, total_stats, file_types)
        
        assert "[STATS] RAPPORT D'ANALYSE" in report
        assert "Fichiers analysés : 2" in report
        assert "RÉPARTITION PAR TYPE" in report
        assert ".py : 1 fichiers" in report

    def test_generate_detailed_report_empty(self):
        """Test la génération du rapport avec données vides."""
        mock_file_analyzer = MagicMock()
        mock_llm_client = MagicMock()
        
        manager = AnalysisManager(mock_file_analyzer, mock_llm_client)
        
        file_stats = []
        total_stats = {'files': 0, 'lines': 0, 'words': 0, 'size_bytes': 0}
        
        from collections import Counter
        file_types = Counter()
        
        report = manager._generate_detailed_report(file_stats, total_stats, file_types)
        
        assert "Fichiers analysés : 0" in report
        assert "Lignes totales : 0" in report

# Test pour la méthode manquante dans l'implémentation
def test_missing_imports():
    """Test que les imports nécessaires sont disponibles."""
    # Vérifier que Counter est disponible (utilisé dans file_types.most_common())
    from collections import Counter
    assert Counter is not None
