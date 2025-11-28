import os
import json
import ast
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from abc import ABC, abstractmethod
from ..utils.logger import logger

class ILLMAdapter(ABC):
    """Interface pour les adaptateurs LLM."""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Génère une réponse à partir des messages."""
        pass
    
    def generate_analysis(self, prompt: str) -> str:
        """
        Optionnel: génère une analyse à partir d'un prompt.
        Par défaut, utilise generate_response.
        """
        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages)
    
    def generate_recommendations(self, analysis: str) -> List[str]:
        """
        Optionnel: génère des recommandations à partir d'une analyse.
        Retourne une liste vide si non supporté.
        """
        return []

class SimulatedLLMAdapter(ILLMAdapter):
    """Adaptateur simulé pour le développement et les tests."""
    
    def __init__(self, fake_responses: Optional[Dict[str, str]] = None):
        self.fake_responses = fake_responses or {}
        logger.info("SimulatedLLMAdapter initialisé")
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Génère une réponse simulée."""
        # Créer une clé basée sur le contenu du message
        content = messages[-1]["content"] if messages else ""
        
        # Chercher une réponse prédéfinie
        for key, response in self.fake_responses.items():
            if key in content:
                return response
        
        # Réponse par défaut basée sur le contenu
        if "Analyse ce projet" in content:
            return """Analyse du projet simulée:
            
1. Architecture modulaire bien structurée
2. Bonnes pratiques de codage respectées
3. Gestion des dépendances claire
4. Code bien documenté
5. Tests unitaires présents"""
        elif "recommandations" in content.lower():
            return """1. [Optimisation des performances]
2. [Amélioration de la documentation]
3. [Refactorisation du code]
4. [Ajout de tests]
5. [Sécurité renforcée]"""
        else:
            return "Réponse simulée du LLM"

class ProjectAnalyzerService:
    """Service d'analyse complète de projets avec IA."""
    
    def __init__(self, llm_adapter: ILLMAdapter):
        self.llm_adapter = llm_adapter
        logger.info("ProjectAnalyzerService initialisé avec adaptateur")
    
    def analyze_project(self, project_path: str, depth: int = 2) -> Dict[str, any]:
        """
        Analyse complète d'un projet.
        
        Args:
            project_path: Chemin du projet
            depth: Profondeur d'analyse des dossiers
            
        Returns:
            Rapport d'analyse complet
        """
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                raise FileNotFoundError(f"Projet non trouvé: {project_path}")
            
            logger.info(f"🔍 Analyse du projet: {project_path}")
            
            # 1. Structure du projet
            structure = self._analyze_structure(project_path, depth)
            
            # 2. Fichiers de code principaux (limités pour réduire la taille)
            code_files = self._get_code_files(project_path, max_files=3)
            
            # 3. Dépendances
            dependencies = self._analyze_dependencies(project_path)
            
            # 4. Analyse détaillée avec IA
            ai_analysis = self._analyze_with_ai(project_path, code_files, structure, dependencies)
            
            # 5. Recommandations
            recommendations = self._generate_recommendations(ai_analysis)
            
            report = {
                "project_name": project_path.name,
                "path": str(project_path),
                "structure": structure,
                "code_files": code_files,
                "dependencies": dependencies,
                "ai_analysis": ai_analysis,
                "recommendations": recommendations,
                "summary": self._generate_summary(structure, code_files, dependencies, ai_analysis)
            }
            
            logger.info("✅ Analyse du projet terminée")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse projet: {e}")
            return self._get_error_report(str(e))
    
    def _analyze_structure(self, project_path: Path, depth: int) -> Dict:
        """Analyse la structure du projet."""
        try:
            structure = {
                "directories": [],
                "files": [],
                "total_files": 0,
                "total_dirs": 0
            }
            
            # Parcourir récursivement avec limite de profondeur
            for root, dirs, files in os.walk(project_path):
                current_depth = root[len(str(project_path)):].count(os.sep)
                if current_depth <= depth:
                    rel_path = os.path.relpath(root, project_path)
                    if rel_path != ".":
                        structure["directories"].append({
                            "path": rel_path,
                            "files_count": len(files)
                        })
                        structure["total_dirs"] += 1
                    
                    for file in files:
                        file_path = os.path.join(rel_path, file) if rel_path != "." else file
                        structure["files"].append({
                            "path": file_path,
                            "size": os.path.getsize(os.path.join(root, file)),
                            "extension": os.path.splitext(file)[1]
                        })
                        structure["total_files"] += 1
            
            return structure
            
        except Exception as e:
            logger.error(f"Erreur analyse structure: {e}")
            return {"error": str(e)}
    
    def _get_code_files(self, project_path: Path, max_files: int = 3) -> List[Dict]:
        """Récupère les fichiers de code importants (limités pour réduire la taille)."""
        try:
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php'}
            code_files = []
            
            for root, _, files in os.walk(project_path):
                for file in files:
                    if len(code_files) >= max_files:
                        break
                    if os.path.splitext(file)[1].lower() in code_extensions:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_path)
                        
                        # Lire le contenu (limité à 1KB pour l'analyse)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1000)  # Limite de 1KB
                        except Exception:
                            content = "[Impossible de lire le fichier]"
                        
                        # Extraire uniquement la structure/fonctions principales
                        structured_content = self._extract_file_structure(content, os.path.splitext(file)[1])
                        
                        code_files.append({
                            "path": rel_path,
                            "extension": os.path.splitext(file)[1],
                            "size": os.path.getsize(file_path),
                            "preview": structured_content
                        })
                if len(code_files) >= max_files:
                    break
            
            return code_files
            
        except Exception as e:
            logger.error(f"Erreur récupération fichiers code: {e}")
            return []
    
    def _extract_file_structure(self, content: str, extension: str) -> str:
        """Extrait la structure du fichier au lieu du contenu complet."""
        try:
            if extension == '.py':
                # Pour Python, extraire les imports et définitions de fonctions/classes
                lines = content.split('\n')
                important_lines = []
                
                for line in lines:
                    line_stripped = line.strip()
                    if (line_stripped.startswith('import ') or 
                        line_stripped.startswith('from ') or
                        line_stripped.startswith('class ') or
                        line_stripped.startswith('def ') or
                        line_stripped.startswith('#')):
                        important_lines.append(line_stripped)
                        if len(important_lines) >= 10:  # Limite de 10 lignes
                            break
                
                return '\n'.join(important_lines) if important_lines else "[Structure Python]"
            
            elif extension in ['.js', '.ts']:
                # Pour JavaScript/TypeScript, extraire les imports et définitions
                lines = content.split('\n')
                important_lines = []
                
                for line in lines:
                    line_stripped = line.strip()
                    if (line_stripped.startswith('import ') or 
                        line_stripped.startswith('export ') or
                        line_stripped.startswith('class ') or
                        line_stripped.startswith('function ') or
                        line_stripped.startswith('const ') or
                        line_stripped.startswith('//')):
                        important_lines.append(line_stripped)
                        if len(important_lines) >= 10:
                            break
                
                return '\n'.join(important_lines) if important_lines else "[Structure JS/TS]"
            
            else:
                # Pour d'autres langages, limiter à 200 caractères
                return content[:200] + "..." if len(content) > 200 else content
                
        except Exception:
            return "[Structure extraite]"
    
    def _analyze_dependencies(self, project_path: Path) -> Dict:
        """Analyse les dépendances du projet."""
        try:
            dependencies = {
                "python": [],
                "npm": [],
                "requirements": [],
                "package_json": {}
            }
            
            # requirements.txt
            req_file = project_path / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file, 'r') as f:
                        deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        dependencies["python"] = deps[:10]  # Limiter à 10 dépendances
                except Exception as e:
                    logger.warning(f"Erreur lecture requirements.txt: {e}")
            
            # package.json
            package_file = project_path / "package.json"
            if package_file.exists():
                try:
                    with open(package_file, 'r') as f:
                        package_data = json.load(f)
                        dependencies["package_json"] = {
                            "name": package_data.get("name", ""),
                            "version": package_data.get("version", ""),
                            "dependencies": list(package_data.get("dependencies", {}).keys())[:10],
                            "devDependencies": list(package_data.get("devDependencies", {}).keys())[:5]
                        }
                        dependencies["npm"] = list(package_data.get("dependencies", {}).keys())[:10]
                except Exception as e:
                    logger.warning(f"Erreur lecture package.json: {e}")
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Erreur analyse dépendances: {e}")
            return {"error": str(e)}
    
    def _analyze_with_ai(self, project_path: Path, code_files: List[Dict], structure: Dict, dependencies: Dict) -> Dict:
        """Analyse détaillée avec l'IA."""
        try:
            # Préparer le prompt pour l'analyse (beaucoup plus concis)
            code_samples = []
            for file_info in code_files[:3]:  # Limiter à 3 fichiers
                code_samples.append(f"Fichier: {file_info['path']}\nStructure:\n{file_info['preview']}")
            
            prompt = f"""
            Analyse ce projet de développement logiciel de manière concise:
            
            Structure: {structure.get('total_dirs', 0)} dossiers, {structure.get('total_files', 0)} fichiers
            Dépendances: Python({len(dependencies.get('python', []))}), NPM({len(dependencies.get('npm', []))})
            
            Fichiers analysés:
            {chr(10).join(code_samples)}
            
            Points clés seulement (3-5 items max):
            """
            
            analysis = self.llm_adapter.generate_analysis(prompt)
            
            return {
                "full_analysis": analysis,
                "key_points": self._extract_key_points(analysis)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse IA: {e}")
            return {"error": f"Analyse IA échouée: {str(e)}"}
    
    def _extract_key_points(self, analysis: str) -> List[str]:
        """Extrait les points clés de l'analyse."""
        try:
            # Extraire les points avec des regex simples
            points = []
            
            # Points numérotés
            numbered_points = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)', analysis, re.DOTALL)
            points.extend(numbered_points[:5])  # Limiter à 5 points
            
            # Points en tirets
            bullet_points = re.findall(r'[-*]\s*(.*?)(?=\n[-*]|\n\n|$)', analysis, re.DOTALL)
            points.extend(bullet_points[:3])  # Limiter à 3 points
            
            return list(set(points))[:5]  # Supprimer les doublons, max 5 points
            
        except Exception as e:
            logger.warning(f"Erreur extraction points: {e}")
            return []
    
    def _generate_recommendations(self, ai_analysis: Dict) -> List[str]:
        """Génère des recommandations basées sur l'analyse."""
        try:
            # Essayer d'utiliser la méthode spécialisée de l'adaptateur
            try:
                recommendations = self.llm_adapter.generate_recommendations(ai_analysis.get("full_analysis", ""))
                if recommendations:
                    return recommendations
            except:
                pass  # Fallback vers l'approche manuelle
            
            analysis_text = ai_analysis.get("full_analysis", "")
            
            prompt = f"""
            Basé sur cette analyse: {analysis_text[:500]}
            3 recommandations concrètes maximum:
            """
            
            recommendations_text = self.llm_adapter.generate_analysis(prompt)
            
            # Extraire les recommandations
            recommendations = re.findall(r'\d+\.\s*([^\n]+)', recommendations_text)
            return recommendations if recommendations else ["Analyse terminée"]
            
        except Exception as e:
            logger.warning(f"Erreur génération recommandations: {e}")
            return ["Analyse du projet terminée"]
    
    def _generate_summary(self, structure: Dict, code_files: List[Dict], dependencies: Dict, ai_analysis: Dict) -> str:
        """Génère un résumé de l'analyse."""
        try:
            total_files = structure.get('total_files', 0)
            total_dirs = structure.get('total_dirs', 0)
            python_deps = len(dependencies.get('python', []))
            npm_deps = len(dependencies.get('npm', []))
            
            summary = f"""
            📊 Résumé: {total_dirs} dossiers, {total_files} fichiers
            📦 Dépendances: {python_deps} Python, {npm_deps} NPM
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.warning(f"Erreur génération résumé: {e}")
            return "Analyse du projet terminée"
    
    def _get_error_report(self, error: str) -> Dict:
        """Retourne un rapport d'erreur."""
        return {
            "error": error,
            "project_name": "Erreur",
            "summary": f"❌ Erreur d'analyse: {error}"
        }
    
    def export_report(self, report: Dict, format: str = "json") -> str:
        """Exporte le rapport dans différents formats."""
        try:
            if format.lower() == "json":
                return json.dumps(report, indent=2, ensure_ascii=False)
            elif format.lower() == "markdown":
                return self._report_to_markdown(report)
            elif format.lower() == "text":
                return self._report_to_text(report)
            else:
                raise ValueError(f"Format non supporté: {format}")
                
        except Exception as e:
            logger.error(f"Erreur export rapport: {e}")
            return f"Erreur export: {str(e)}"
    
    def _report_to_markdown(self, report: Dict) -> str:
        """Convertit le rapport en Markdown."""
        try:
            md = f"""# 📊 Analyse: {report.get('project_name', 'Inconnu')}

{report.get('summary', '')}

## 🎯 Analyse
{report.get('ai_analysis', {}).get('full_analysis', 'Aucune analyse disponible')}

## 💡 Recommandations
"""
            for i, rec in enumerate(report.get('recommendations', []), 1):
                md += f"{i}. {rec}\n"
            
            return md
            
        except Exception as e:
            logger.error(f"Erreur conversion Markdown: {e}")
            return f"# Erreur\n{str(e)}"
    
    def _report_to_text(self, report: Dict) -> str:
        """Convertit le rapport en texte brut."""
        try:
            text = f"""
ANALYSE: {report.get('project_name', 'Inconnu')}
{'='*30}

{report.get('summary', '')}

ANALYSE:
{report.get('ai_analysis', {}).get('full_analysis', 'Aucune analyse disponible')}

RECOMMANDATIONS:
"""
            for i, rec in enumerate(report.get('recommendations', []), 1):
                text += f"  {i}. {rec}\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Erreur conversion texte: {e}")
            return f"ERREUR\n{str(e)}"
