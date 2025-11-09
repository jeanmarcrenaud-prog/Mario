import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..utils.file_analyzer import FileAnalyzer
from ..core.llm_client import LLMClient
from ..utils.logger import logger
import threading

class AnalysisManager:
    """Gère les analyses de fichiers et l'intégration avec Ollama."""
    
    def __init__(self, file_analyzer: FileAnalyzer, llm_client: LLMClient):
        self.file_analyzer = file_analyzer
        self.llm_client = llm_client

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
                    "summary": "Erreur lors de l'analyse",
                    "chat_message": f"[ERREUR] {error}"
                }
            
            # 2. Rapport de base
            report = self._generate_detailed_report(file_stats, total_stats, file_types)
            
            # 3. Préparation contexte Ollama
            ollama_context = self._prepare_ollama_context(file_stats, total_stats, file_types)
            
            # 4. Analyse intelligente
            intelligent_analysis = self._get_ollama_analysis(ollama_model, ollama_context)
            
            # 5. Rapport combiné
            combined_report = f"{report}\n\n[IA] ANALYSE INTELLIGENTE:\n{intelligent_analysis}"
            
            return {
                "error": False,
                "report": combined_report,
                "summary": f"Analyse Ollama terminée. {total_stats.get('files', 0)} fichiers analysés.",
                "chat_message": f"[STATS] Analyse Ollama terminée pour {path}\n\n{intelligent_analysis}"
            }
            
        except Exception as e:
            error_msg = f"[ERREUR] {str(e)}"
            logger.error(error_msg)
            return {
                "error": True,
                "report": error_msg,
                "summary": "Erreur",
                "chat_message": error_msg
            }

    def analyze_directory(self, path: str) -> Dict:
        """Analyse simple d'arborescence."""
        try:
            file_stats, total_stats, file_types, error = self.file_analyzer.analyze_directory(path)
            
            if error:
                return {
                    "error": True,
                    "report": f"[ERREUR] {error}",
                    "summary": "Erreur lors de l'analyse"
                }
            
            report = self._generate_detailed_report(file_stats, total_stats, file_types)
            summary = self.file_analyzer.generate_summary(total_stats, file_types)
            
            return {
                "error": False,
                "report": report,
                "summary": summary
            }
            
        except Exception as e:
            error_msg = f"[ERREUR] {str(e)}"
            logger.error(error_msg)
            return {
                "error": True,
                "report": error_msg,
                "summary": "Erreur"
            }

    def analyze_single_file(self, filepath: str, ollama_model: str, chat_lock: threading.Lock) -> Dict:
        """Analyse un fichier unique avec Ollama."""
        try:
            # Analyse de base du fichier
            file_info = self.file_analyzer.analyze_file(Path(filepath))
            
            if 'error' in file_info:
                return {
                    "user_message": f"[FICHIER] Erreur analyse {Path(filepath).name}",
                    "assistant_message": f"[ERREUR] {file_info['error']}"
                }
            
            # Lecture du contenu
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
            
            # Analyse avec Ollama
            analysis_response = self._analyze_single_file_with_ollama(
                ollama_model, Path(filepath).name, file_info, content
            )
            
            return {
                "user_message": f"[FICHIER] {Path(filepath).name} uploadé",
                "assistant_message": f"[IA] Analyse du fichier :\n{analysis_response}"
            }
            
        except Exception as e:
            error_msg = f"[ERREUR] {str(e)}"
            logger.error(error_msg)
            return {
                "user_message": f"[FICHIER] Erreur upload {Path(filepath).name}",
                "assistant_message": error_msg
            }

    def _prepare_ollama_context(self, file_stats, total_stats, file_types) -> Dict:
        """Prépare le contexte pour Ollama."""
        context = {
            "statistiques_globales": {
                "nombre_fichiers": total_stats.get('files', 0),
                "lignes_total": total_stats.get('lines', 0),
                "mots_total": total_stats.get('words', 0),
                "taille_total_mo": total_stats.get('size_bytes', 0) / 1024 / 1024
            },
            "repartition_fichiers": dict(file_types),
            "fichiers_principaux": [],
            "fichiers_python": []
        }
        
        # Fichiers principaux
        valid_files = [f for f in file_stats if 'error' not in f]
        if valid_files:
            largest_files = sorted(valid_files, key=lambda x: x['size_bytes'], reverse=True)[:5]
            for file_info in largest_files:
                context["fichiers_principaux"].append({
                    "nom": Path(file_info['path']).name,
                    "taille_ko": file_info['size_bytes'] / 1024,
                    "lignes": file_info['lines'],
                    "type": Path(file_info['path']).suffix
                })
        
        # Fichiers Python
        python_files = [f for f in valid_files if Path(f['path']).suffix == '.py']
        for py_file in python_files[:5]:
            try:
                with open(py_file['path'], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(3000)
                    
                    context["fichiers_python"].append({
                        "nom": Path(py_file['path']).name,
                        "lignes": py_file['lines'],
                        "fonctions": py_file.get('functions', 0),
                        "classes": py_file.get('classes', 0),
                        "imports": py_file.get('imports', 0),
                        "extrait": content[:800]
                    })
            except Exception:
                pass
        
        return context

    def _get_ollama_analysis(self, ollama_model: str, context: Dict) -> str:
        """Obtient l'analyse d'Ollama."""
        prompt = self._create_analysis_prompt(context)
        
        self.llm_client.set_model(ollama_model)
        analysis = ""
        
        for token in self.llm_client.chat_stream([
            {"role": "system", "content": "Expert en analyse de code. Fournis des insights techniques concis."},
            {"role": "user", "content": prompt}
        ]):
            analysis += token
        
        return analysis

    def _analyze_single_file_with_ollama(self, ollama_model: str, filename: str, file_info: Dict, content: str) -> str:
        """Analyse un fichier unique avec Ollama."""
        prompt = f"""
        Analyse ce fichier : {filename}
        
        Statistiques :
        - Taille : {file_info['size_bytes'] / 1024:.1f} KB
        - Lignes : {file_info['lines']}
        - Mots : {file_info['words']}
        
        Contenu (extrait) :
        {content[:1500]}
        
        Fournis une analyse concise du fichier.
        """
        
        self.llm_client.set_model(ollama_model)
        response = ""
        
        for token in self.llm_client.chat_stream([{"role": "user", "content": prompt}]):
            response += token
        
        return response

    def _create_analysis_prompt(self, context: Dict) -> str:
        """Crée le prompt d'analyse pour Ollama."""
        return f"""
        Analyse ce projet logiciel :

        STATISTIQUES:
        - Fichiers: {context['statistiques_globales']['nombre_fichiers']}
        - Lignes: {context['statistiques_globales']['lignes_total']:,}
        - Mots: {context['statistiques_globales']['mots_total']:,}
        - Taille: {context['statistiques_globales']['taille_total_mo']:.1f} MB

        TYPES DE FICHIERS:
        {json.dumps(context['repartition_fichiers'], indent=2, ensure_ascii=False)}

        Questions :
        1. Type de projet et architecture ?
        2. Technologies principales ?
        3. Points forts/faibles ?
        4. Recommandations ?

        Réponse concise et technique.
        """

    def _generate_detailed_report(self, file_stats, total_stats, file_types) -> str:
        """Génère un rapport détaillé."""
        report_lines = [
            "[STATS] RAPPORT D'ANALYSE",
            "=" * 60,
            f"Fichiers analysés : {total_stats.get('files', 0)}",
            f"Taille totale : {total_stats.get('size_bytes', 0) / 1024 / 1024:.2f} MB",
            f"Lignes totales : {total_stats.get('lines', 0):,}",
            f"Mots totaux : {total_stats.get('words', 0):,}",
            "",
            "RÉPARTITION PAR TYPE :"
        ]
        
        for ext, count in file_types.most_common():
            report_lines.append(f"  {ext} : {count} fichiers")
        
        valid_files = [f for f in file_stats if 'error' not in f]
        if valid_files:
            largest_files = sorted(valid_files, key=lambda x: x['size_bytes'], reverse=True)[:3]
            report_lines.extend(["", "PLUS GROS FICHIERS :"])
            for i, file_info in enumerate(largest_files, 1):
                size_mb = file_info['size_bytes'] / 1024 / 1024
                name = Path(file_info['path']).name
                report_lines.append(f"  {i}. {name} ({size_mb:.1f} MB)")
        
        return "\n".join(report_lines)
