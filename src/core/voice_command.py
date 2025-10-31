import os
import re
import logging
from pathlib import Path
from ..utils.file_analyzer import FileAnalyzer
logger = logging.getLogger("AssistantVocal")
class VoiceCommandProcessor:
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        # ... autres initialisations
    
    def process_command(self, text):
        text_lower = text.lower()
        
        # Commande d'analyse d'arborescence
        if "analyse" in text_lower and ("fichiers" in text_lower or "arborescence" in text_lower):
            return self.analyze_files_command(text)
        
        # ... autres commandes
    
    def analyze_files_command(self, text):
        """Traite la commande d'analyse de fichiers"""
        try:
            # Essayer d'extraire le chemin depuis la commande
            path = self.extract_path_from_command(text)
            
            if not path:
                # Utiliser le répertoire courant par défaut
                path = os.getcwd()
            
            logger.info(f"🔍 Analyse de l'arborescence : {path}")
            
            # Analyser les fichiers
            file_stats, total_stats, file_types, error = self.file_analyzer.analyze_directory(path)
            
            if error:
                return {
                    'response': f"Erreur lors de l'analyse: {error}",
                    'action': 'error'
                }
            
            # Générer le résumé vocal
            summary = self.file_analyzer.generate_summary(total_stats, file_types)
            
            # Générer le rapport détaillé pour l'interface
            report = self.file_analyzer.get_detailed_report(file_stats, total_stats, file_types)
            
            return {
                'response': summary,
                'action': 'file_analysis',
                'data': report,
                'detailed_report': self.format_detailed_report(report)
            }
            
        except Exception as e:
            logger.error(f"Erreur commande analyse fichiers: {e}")
            return {
                'response': "Désolé, une erreur s'est produite lors de l'analyse des fichiers",
                'action': 'error'
            }
    
    def extract_path_from_command(self, text):
        """Extrait un chemin de la commande vocale"""
        # Recherche des motifs courants
        patterns = [
            r"dans\s+(.+)",
            r"du\s+(.+)",
            r"sur\s+(.+)",
            r"chemin\s+(.+)",
            r"répertoire\s+(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                # Nettoyer le chemin (enlever la ponctuation finale)
                path = re.sub(r'[.,;!?]$', '', path)
                
                # Vérifier si le chemin existe
                if os.path.exists(path):
                    return path
        
        return None
    
    def format_detailed_report(self, report):
        """Formate le rapport détaillé pour l'affichage"""
        lines = [
            "📊 RAPPORT DÉTAILLÉ",
            "=" * 50,
            f"Fichiers analysés : {report['summary']['total_files']}",
            f"Lignes totales : {report['summary']['total_lines']:,}",
            f"Mots totaux : {report['summary']['total_words']:,}",
            f"Taille totale : {report['summary']['total_size_mb']:.2f} MB",
            "",
            "📁 TYPES DE FICHIERS:"
        ]
        
        for ext, count in report['file_types'].items():
            lines.append(f"  {ext or 'Sans extension'} : {count}")
        
        if report['largest_files']:
            lines.extend(["", "🏆 PLUS GROS FICHIERS:"])
            for i, file_info in enumerate(report['largest_files'][:3], 1):
                size_mb = file_info['size_bytes'] / 1024 / 1024
                lines.append(f"  {i}. {Path(file_info['path']).name} ({size_mb:.1f} MB)")
        
        if report['error_files']:
            lines.extend(["", f"❌ FICHIERS AVEC ERREURS ({len(report['error_files'])}):"])
            for f in report['error_files'][:3]:
                lines.append(f"  {Path(f['path']).name}")
        
        return "\n".join(lines)
