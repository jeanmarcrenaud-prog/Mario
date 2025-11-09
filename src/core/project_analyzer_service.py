import os
import json
import ast
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..utils.logger import logger

class ProjectAnalyzerService:
    """Service d'analyse complète de projets avec IA."""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        logger.info("ProjectAnalyzerService initialisé")
    
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
            
            # 2. Fichiers de code principaux
            code_files = self._get_code_files(project_path)
            
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
    
    def _get_code_files(self, project_path: Path) -> List[Dict]:
        """Récupère les fichiers de code importants."""
        try:
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php'}
            code_files = []
            
            for root, _, files in os.walk(project_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in code_extensions:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_path)
                        
                        # Lire le contenu (limité à 5KB pour l'analyse)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(5000)  # Limite de 5KB
                        except Exception:
                            content = "[Impossible de lire le fichier]"
                        
                        code_files.append({
                            "path": rel_path,
                            "extension": os.path.splitext(file)[1],
                            "size": os.path.getsize(file_path),
                            "preview": content[:500] + "..." if len(content) > 500 else content
                        })
            
            return code_files
            
        except Exception as e:
            logger.error(f"Erreur récupération fichiers code: {e}")
            return []
    
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
                        dependencies["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
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
                            "dependencies": list(package_data.get("dependencies", {}).keys()),
                            "devDependencies": list(package_data.get("devDependencies", {}).keys())
                        }
                        dependencies["npm"] = list(package_data.get("dependencies", {}).keys())
                except Exception as e:
                    logger.warning(f"Erreur lecture package.json: {e}")
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Erreur analyse dépendances: {e}")
            return {"error": str(e)}
    
    def _analyze_with_ai(self, project_path: Path, code_files: List[Dict], structure: Dict, dependencies: Dict) -> Dict:
        """Analyse détaillée avec l'IA."""
        try:
            # Préparer le prompt pour l'analyse
            code_samples = []
            for file_info in code_files[:5]:  # Limiter à 5 fichiers
                code_samples.append(f"Fichier: {file_info['path']}\n```{file_info['extension'][1:]}\n{file_info['preview']}\n```")
            
            prompt = f"""
            Analyse ce projet de développement logiciel :
            
            **Structure du projet:**
            Dossiers: {len(structure.get('directories', []))}
            Fichiers: {structure.get('total_files', 0)}
            
            **Dépendances principales:**
            Python: {', '.join(dependencies.get('python', [])[:10])}
            NPM: {', '.join(dependencies.get('npm', [])[:10])}
            
            **Extraits de code:**
            {chr(10).join(code_samples[:1000])}  # Limiter la longueur
            
            Fournis une analyse complète incluant:
            1. Architecture et structure du projet
            2. Technologies utilisées
            3. Points forts et faiblesses
            4. Complexité du code
            5. Bonnes pratiques observées
            6. Problèmes potentiels identifiés
            """
            
            messages = [{"role": "user", "content": prompt}]
            analysis = self.llm_service.generate_response(messages)
            
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
            points.extend(numbered_points[:10])  # Limiter à 10 points
            
            # Points en tirets
            bullet_points = re.findall(r'[-*]\s*(.*?)(?=\n[-*]|\n\n|$)', analysis, re.DOTALL)
            points.extend(bullet_points[:5])  # Limiter à 5 points
            
            return list(set(points))[:10]  # Supprimer les doublons, max 10 points
            
        except Exception as e:
            logger.warning(f"Erreur extraction points: {e}")
            return []
    
    def _generate_recommendations(self, ai_analysis: Dict) -> List[str]:
        """Génère des recommandations basées sur l'analyse."""
        try:
            analysis_text = ai_analysis.get("full_analysis", "")
            
            prompt = f"""
            Basé sur cette analyse de projet:
            {analysis_text[:1000]}  # Limiter la longueur
            
            Fournis 5 recommandations concrètes pour améliorer ce projet:
            1. [Recommandation technique]
            2. [Amélioration de structure]
            3. [Optimisation de performance]
            4. [Bonnes pratiques]
            5. [Sécurité ou maintenance]
            """
            
            messages = [{"role": "user", "content": prompt}]
            recommendations_text = self.llm_service.generate_response(messages)
            
            # Extraire les recommandations
            recommendations = re.findall(r'\d+\.\s*\[([^\]]+)\]', recommendations_text)
            return recommendations if recommendations else ["Aucune recommandation spécifique générée"]
            
        except Exception as e:
            logger.warning(f"Erreur génération recommandations: {e}")
            return ["Analyse du projet terminée - Consultez le rapport complet"]
    
    def _generate_summary(self, structure: Dict, code_files: List[Dict], dependencies: Dict, ai_analysis: Dict) -> str:
        """Génère un résumé de l'analyse."""
        try:
            total_files = structure.get('total_files', 0)
            total_dirs = structure.get('total_dirs', 0)
            python_deps = len(dependencies.get('python', []))
            npm_deps = len(dependencies.get('npm', []))
            
            summary = f"""
            📊 **Résumé de l'analyse**:
            - 📁 {total_dirs} dossiers, {total_files} fichiers
            - 🐍 {python_deps} dépendances Python
            - 📦 {npm_deps} dépendances NPM
            - 🎯 {len(code_files)} fichiers de code analysés
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
            md = f"""# 📊 Analyse du projet: {report.get('project_name', 'Inconnu')}

## {report.get('summary', '')}

## 🏗️ Structure
- Dossiers: {report.get('structure', {}).get('total_dirs', 0)}
- Fichiers: {report.get('structure', {}).get('total_files', 0)}

## 📦 Dépendances
- Python: {len(report.get('dependencies', {}).get('python', []))} packages
- NPM: {len(report.get('dependencies', {}).get('npm', []))} packages

## 🎯 Analyse détaillée
{report.get('ai_analysis', {}).get('full_analysis', 'Aucune analyse disponible')[:2000]}...

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
ANALYSE DU PROJET: {report.get('project_name', 'Inconnu')}
{'='*50}

{report.get('summary', '')}

STRUCTURE:
  Dossiers: {report.get('structure', {}).get('total_dirs', 0)}
  Fichiers: {report.get('structure', {}).get('total_files', 0)}

DÉPENDANCES:
  Python: {len(report.get('dependencies', {}).get('python', []))} packages
  NPM: {len(report.get('dependencies', {}).get('npm', []))} packages

ANALYSE DÉTAILLÉE:
{report.get('ai_analysis', {}).get('full_analysis', 'Aucune analyse disponible')[:1000]}...

RECOMMANDATIONS:
"""
            for i, rec in enumerate(report.get('recommendations', []), 1):
                text += f"  {i}. {rec}\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Erreur conversion texte: {e}")
            return f"ERREUR\n{str(e)}"
