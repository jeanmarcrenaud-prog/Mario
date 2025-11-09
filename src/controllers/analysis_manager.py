# src/controller/analysis_manager.py
from typing import Dict
from pathlib import Path
from src.model.file_analyzer import FileAnalyzer
from src.model.ollama_client import OllamaClient
from src.utils.logger import logger
import threading

class AnalysisManager:
    """Gère les analyses de fichiers et l'intégration avec Ollama."""

    def __init__(self, file_analyzer: FileAnalyzer, ollama_client: OllamaClient):
        self.file_analyzer = file_analyzer
        self.ollama_client = ollama_client

    def analyze_with_ollama(self, path: str, ollama_model: str, chat_lock: threading.Lock) -> Dict:
        """Analyse une arborescence avec Ollama."""
        try:
            if not path:
                path = str(Path.cwd())

            logger.info(f"[RECHERCHE] Analyse avec Ollama : {path}")

            # 1. Analyse de base
            file_stats, total_stats, file_types, error = self.file_analyzer.analyze_directory(path)

            if error:
                return {
                    "error": True,
                    "report": f"[ERREUR] {error}",
                }

            # 2. Envoi à Ollama
            prompt = self._generate_prompt(file_stats, total_stats, file_types)
            response = self.ollama_client.generate(prompt, model=ollama_model)

            return {
                "error": False,
                "report": response,
            }

        except Exception as e:
            logger.error(f"[ERREUR] Analyse avec Ollama : {e}")
            return {
                "error": True,
                "report": f"[ERREUR] {e}",
            }

    def _generate_prompt(self, file_stats, total_stats, file_types):
        """Génère le prompt pour Ollama."""
        # Logique pour générer le prompt
        return "Analyse des fichiers..."
