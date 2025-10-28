import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..utils.logger import logger
from ..core.llm_client import LLMClient

class SelfImprover:
    """Classe pour l'auto-amélioration des fichiers du projet."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.project_root = Path(__file__).parent.parent.parent
        self.last_sent_content = {}  # Stocker le dernier contenu envoyé à Ollama
        self.analysis_history = {}   # Historique complet des analyses
    
    def analyze_project_structure(self) -> Dict:
        """Analyse la structure du projet."""
        structure = {
            "fichiers_python": [],
            "fichiers_documentation": [],
            "fichiers_configuration": [],
            "statistiques": {}
        }
        
        try:
            python_files = list(self.project_root.rglob("*.py"))
            md_files = list(self.project_root.rglob("*.md"))
            config_files = list(self.project_root.rglob("*.json")) + list(self.project_root.rglob("*.yaml")) + list(self.project_root.rglob("*.toml"))
            
            structure["fichiers_python"] = [str(f) for f in python_files]
            structure["fichiers_documentation"] = [str(f) for f in md_files]
            structure["fichiers_configuration"] = [str(f) for f in config_files]
            
            structure["statistiques"] = {
                "total_fichiers_python": len(python_files),
                "total_fichiers_doc": len(md_files),
                "total_fichiers_config": len(config_files)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse structure projet: {e}")
        
        return structure
    
    def get_file_content_preview(self, file_path: Path, max_lines: int = 50) -> str:
        """Retourne un aperçu du contenu d'un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            preview = f"=== CONTENU DE {file_path.name} ===\n"
            preview += f"Lignes totales: {len(lines)}\n"
            preview += f"Premières {min(max_lines, len(lines))} lignes:\n\n"
            
            for i, line in enumerate(lines[:max_lines]):
                preview += f"{i+1:3d}: {line.rstrip()}\n"
            
            if len(lines) > max_lines:
                preview += f"\n... ({len(lines) - max_lines} lignes supplémentaires)"
            
            return preview
        except Exception as e:
            return f"Erreur lecture fichier {file_path}: {e}"
    
    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyse un fichier Python pour détecter les améliorations possibles."""
        improvements = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "suggestions": [],
            "errors": [],
            "metrics": {},
            "content_preview": "",
            "timestamp": self._get_timestamp()
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Stocker l'aperçu du contenu
            improvements["content_preview"] = self.get_file_content_preview(file_path, 30)
            
            # Métriques de base
            lines = content.splitlines()
            improvements["metrics"] = {
                "lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "functions": len(re.findall(r'^def\s+\w+', content, re.MULTILINE)),
                "classes": len(re.findall(r'^class\s+\w+', content, re.MULTILINE)),
                "imports": len(re.findall(r'^import\s+\w+', content, re.MULTILINE)),
                "size_kb": len(content) / 1024
            }
            
            # Vérifications automatiques
            self._check_python_quality(improvements, content, file_path)
            
            # Analyse avec LLM pour des suggestions intelligentes
            llm_suggestions, sent_content, analysis_details = self._get_llm_suggestions(file_path, content)
            improvements["suggestions"].extend(llm_suggestions)
            
            # Stocker le contenu envoyé à Ollama dans l'historique
            analysis_id = f"{file_path.name}_{self._get_timestamp()}"
            self.analysis_history[analysis_id] = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "timestamp": improvements["timestamp"],
                "content_sent": sent_content,
                "suggestions_received": llm_suggestions,
                "analysis_details": analysis_details,
                "metrics": improvements["metrics"]
            }
            
            # Garder aussi une référence rapide
            self.last_sent_content[str(file_path)] = self.analysis_history[analysis_id]
            
        except Exception as e:
            improvements["errors"].append(f"Erreur analyse fichier: {e}")
            logger.error(f"Erreur analyse {file_path}: {e}")
        
        return improvements
    
    def _check_python_quality(self, improvements: Dict, content: str, file_path: Path):
        """Vérifie la qualité du code Python."""
        try:
            # Vérifier les docstrings
            if not re.search(r'""".*?"""', content, re.DOTALL) and not re.search(r"'''.*?'''", content, re.DOTALL):
                improvements["suggestions"].append("[DOC] Ajouter des docstrings aux fonctions principales")
            
            # Vérifier les type hints
            functions_without_hints = re.findall(r'def\s+(\w+)\([^)]*\)(?!\s*->)', content)
            if functions_without_hints:
                improvements["suggestions"].append(f"[TYPING] Ajouter des type hints aux fonctions: {', '.join(functions_without_hints[:2])}")
            
            # Vérifier la longueur des lignes
            long_lines = []
            for i, line in enumerate(content.splitlines(), 1):
                if len(line) > 100:
                    long_lines.append(i)
            if long_lines:
                improvements["suggestions"].append(f"[PEP8] Lignes trop longues (>100 chars) aux lignes: {long_lines[:3]}")
            
            # Vérifier les imports
            imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
            imports_from = re.findall(r'^from\s+(\w+)', content, re.MULTILINE)
            all_imports = imports + imports_from
            
        except Exception as e:
            logger.warning(f"Erreur vérification qualité {file_path}: {e}")
    
    def _get_llm_suggestions(self, file_path: Path, content: str) -> Tuple[List[str], str, Dict]:
        """Obtient des suggestions d'amélioration via LLM."""
        try:
            # Préparer le contenu à envoyer (limité pour éviter les tokens excessifs)
            sent_content = content[:3500] + ("..." if len(content) > 3500 else "")
            
            prompt = f"""
            ANALYSE DE FICHIER PYTHON - {file_path.name}

            CONTENU DU FICHIER (extrait):
            ```python
            {sent_content}
            ```

            TÂCHE: Analyser ce code Python et proposer des améliorations concrètes et actionnables.

            POINTS À EXAMINER par ordre de priorité:
            1. [CRITIQUE] Erreurs, bugs ou problèmes de sécurité
            2. [PEP8] Conformité aux standards Python
            3. [DOC] Documentation et clarté du code
            4. [PERF] Optimisations des performances
            5. [STRUCTURE] Améliorations architecturales

            FORMAT DE RÉPONSE ATTENDU:
            - [CATÉGORIE] Description concise de l'amélioration
            - Exemple: "[PEP8] La fonction à la ligne 23 dépasse 100 caractères"
            - Maximum 5 suggestions les plus importantes.

            Réponse concise et technique.
            """
            
            suggestions = []
            analysis_details = {
                "file_name": file_path.name,
                "content_length": len(content),
                "sent_content_length": len(sent_content),
                "timestamp": self._get_timestamp()
            }
            
            # Appel à LLM
            response = ""
            for token in self.llm_client.chat_stream([
                {"role": "system", "content": "Expert en qualité de code Python. Formatte les suggestions avec des catégories claires comme [PEP8], [DOC], [PERF]."},
                {"role": "user", "content": prompt}
            ]):
                response += token
            
            analysis_details["llm_response"] = response
            
            # Parser la réponse
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('[') and ']' in line:
                    # Extraire la catégorie et la suggestion
                    category_end = line.find(']')
                    category = line[:category_end+1]
                    suggestion_text = line[category_end+1:].strip()
                    
                    if suggestion_text and len(suggestion_text) > 5:
                        suggestions.append(f"{category} {suggestion_text}")
            
            # Si pas de format détecté, prendre les lignes qui commencent par -
            if not suggestions:
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') and len(line) > 10:
                        suggestions.append(line[1:].strip())
            
            # Limiter à 5 suggestions
            suggestions = suggestions[:5]
            
            return suggestions, prompt, analysis_details
            
        except Exception as e:
            logger.error(f"Erreur analyse LLM pour {file_path}: {e}")
            return [f"[ERREUR] Problème analyse LLM: {e}"], "", {}
    
    def get_analysis_history(self) -> Dict:
        """Retourne l'historique complet des analyses."""
        return self.analysis_history
    
    def get_file_analysis_history(self, file_path: str) -> List[Dict]:
        """Retourne l'historique des analyses pour un fichier spécifique."""
        file_history = []
        for analysis_id, analysis_data in self.analysis_history.items():
            if analysis_data["file_path"] == file_path:
                file_history.append(analysis_data)
        
        # Trier par timestamp
        file_history.sort(key=lambda x: x["timestamp"], reverse=True)
        return file_history
    
    def generate_detailed_analysis_report(self, file_path: str) -> str:
        """Génère un rapport détaillé d'analyse pour un fichier spécifique."""
        file_history = self.get_file_analysis_history(file_path)
        
        if not file_history:
            return f"Aucune analyse trouvée pour {file_path}"
        
        latest_analysis = file_history[0]
        
        report = [
            f"📊 RAPPORT DÉTAILLÉ D'ANALYSE",
            f"Fichier: {latest_analysis['file_name']}",
            f"Chemin: {file_path}",
            f"Timestamp: {latest_analysis['timestamp']}",
            "=" * 60,
            "",
            f"📈 MÉTRIQUES:",
            f"• Lignes: {latest_analysis['metrics']['lines']}",
            f"• Fonctions: {latest_analysis['metrics']['functions']}",
            f"• Classes: {latest_analysis['metrics']['classes']}",
            f"• Taille: {latest_analysis['metrics']['size_kb']:.1f} KB",
            "",
            f"💡 SUGGESTIONS REÇUES ({len(latest_analysis['suggestions_received'])}):"
        ]
        
        for i, suggestion in enumerate(latest_analysis['suggestions_received'], 1):
            report.append(f"{i}. {suggestion}")
        
        report.extend([
            "",
            "📤 CONTENU ENVOYÉ À OLLAMA:",
            f"Longueur: {latest_analysis['analysis_details']['sent_content_length']} caractères",
            "─" * 40
        ])
        
        # Ajouter le contenu envoyé (tronqué si trop long)
        content_preview = latest_analysis['content_sent']
        if len(content_preview) > 1000:
            content_preview = content_preview[:1000] + "\n... [contenu tronqué]"
        report.append(content_preview)
        
        return "\n".join(report)
    
    def get_content_sent_to_ollama(self, file_path: str) -> str:
        """Retourne le contenu exact envoyé à Ollama pour un fichier."""
        file_history = self.get_file_analysis_history(file_path)
        
        if not file_history:
            return f"Aucune analyse récente pour {file_path}"
        
        latest_analysis = file_history[0]
        return latest_analysis['content_sent']
    
    def generate_improvement_plan(self) -> Dict:
        """Génère un plan d'amélioration pour tout le projet."""
        structure = self.analyze_project_structure()
        improvement_plan = {
            "project_structure": structure,
            "file_analysis": [],
            "priority_improvements": [],
            "summary": {},
            "analysis_timestamp": self._get_timestamp()
        }
        
        # Analyser les fichiers Python principaux (limiter pour performance)
        python_files = [Path(f) for f in structure["fichiers_python"] if "test" not in f.lower()]
        files_to_analyze = python_files[:8]  # Limiter à 8 fichiers
        
        for py_file in files_to_analyze:
            try:
                analysis = self.analyze_python_file(py_file)
                improvement_plan["file_analysis"].append(analysis)
                
                # Extraire les suggestions prioritaires
                for suggestion in analysis["suggestions"]:
                    priority = "medium"
                    if any(keyword in suggestion.lower() for keyword in 
                          ['critique', 'erreur', 'bug', 'security', 'sécurité', 'error']):
                        priority = "high"
                    elif any(keyword in suggestion.lower() for keyword in 
                           ['pep8', 'doc', 'documentation']):
                        priority = "low"
                    
                    improvement_plan["priority_improvements"].append({
                        "file": str(py_file),
                        "file_name": py_file.name,
                        "suggestion": suggestion,
                        "priority": priority
                    })
                
            except Exception as e:
                logger.error(f"Erreur analyse {py_file}: {e}")
                improvement_plan["file_analysis"].append({
                    "file_path": str(py_file),
                    "errors": [f"Erreur analyse: {e}"],
                    "suggestions": []
                })
        
        # Générer un résumé
        total_suggestions = sum(len(analysis.get("suggestions", [])) for analysis in improvement_plan["file_analysis"])
        high_priority = len([imp for imp in improvement_plan["priority_improvements"] if imp["priority"] == "high"])
        medium_priority = len([imp for imp in improvement_plan["priority_improvements"] if imp["priority"] == "medium"])
        
        improvement_plan["summary"] = {
            "total_files_analyzed": len(improvement_plan["file_analysis"]),
            "total_suggestions": total_suggestions,
            "high_priority_suggestions": high_priority,
            "medium_priority_suggestions": medium_priority,
            "estimated_improvement_time": f"{(high_priority * 10 + medium_priority * 5)} minutes"
        }
        
        return improvement_plan
    
    def implement_suggestion(self, file_path: str, suggestion: str) -> Dict:
        """Implémente une suggestion d'amélioration."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"success": False, "error": "Fichier non trouvé"}
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Demander à l'LLM de générer la version améliorée
            prompt = f"""
            FICHIER ORIGINAL à améliorer:
            ```python
            {content}
            ```

            SUGGESTION À IMPLÉMENTER: {suggestion}

            TÂCHE: Réécrire le fichier en implémentant cette suggestion.
            CONSIGNES:
            - Garder EXACTEMENT la même fonctionnalité
            - Améliorer seulement la qualité comme suggéré
            - Respecter les standards Python
            - Ne pas ajouter de fonctionnalités supplémentaires

            Retourne seulement le code Python amélioré, sans explications.
            """
            
            improved_content = ""
            for token in self.llm_client.chat_stream([
                {"role": "system", "content": "Expert en refactoring Python. Réécris le code en implémentant les améliorations demandées sans changer les fonctionnalités."},
                {"role": "user", "content": prompt}
            ]):
                improved_content += token
            
            # Extraire le code du markdown si présent
            code_match = re.search(r'```python\n(.*?)\n```', improved_content, re.DOTALL)
            if code_match:
                improved_content = code_match.group(1)
            
            # Nettoyer le contenu
            improved_content = improved_content.strip()
            
            # Sauvegarder la version originale
            backup_path = file_path_obj.with_suffix(file_path_obj.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Écrire la version améliorée
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(improved_content)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "original_lines": len(content.splitlines()),
                "improved_lines": len(improved_content.splitlines()),
                "file_size_change": len(improved_content) - len(content)
            }
            
        except Exception as e:
            logger.error(f"Erreur implémentation suggestion {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_timestamp(self):
        """Retourne un timestamp formaté."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
