import os
import re
from pathlib import Path
from collections import Counter, defaultdict
from ..utils.logger import logger

class FileAnalyzer:
    """Analyseur de fichiers texte pour l'assistant vocal"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', '.java', '.c', '.cpp', '.h'}
    
    def analyze_file(self, file_path):
        """Analyse un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            stats = {
                'path': str(file_path),
                'size_bytes': os.path.getsize(file_path),
                'lines': len(content.splitlines()),
                'words': len(re.findall(r'\w+', content)),
                'characters': len(content),
            }
            
            lines = content.splitlines()
            stats['non_empty_lines'] = len([line for line in lines if line.strip()])
            stats['empty_lines'] = stats['lines'] - stats['non_empty_lines']
            
            # Analyse spécifique Python
            if file_path.suffix == '.py':
                stats['imports'] = len(re.findall(r'^import\s+\w+', content, re.MULTILINE))
                stats['functions'] = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
                stats['classes'] = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
                stats['comments'] = len(re.findall(r'#.*$', content, re.MULTILINE))
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur analyse fichier {file_path}: {e}")
            return {'path': str(file_path), 'error': str(e)}
    
    def analyze_directory(self, root_path):
        """Analyse tous les fichiers texte d'une arborescence"""
        root_path = Path(root_path)
        
        if not root_path.exists():
            return None, "Le chemin spécifié n'existe pas"
        
        file_stats = []
        total_stats = defaultdict(int)
        file_types = Counter()
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                stats = self.analyze_file(file_path)
                file_stats.append(stats)
                
                if 'error' not in stats:
                    file_types[file_path.suffix] += 1
                    for key in ['size_bytes', 'lines', 'words', 'characters', 'non_empty_lines', 'empty_lines']:
                        total_stats[key] += stats.get(key, 0)
                    total_stats['files'] += 1
        
        return file_stats, total_stats, file_types, None
    
    def generate_summary(self, total_stats, file_types):
        """Génère un résumé vocal"""
        if not total_stats.get('files'):
            return "Aucun fichier texte trouvé dans l'arborescence"
        
        summary = f"""
        J'ai analysé {total_stats['files']} fichiers texte.
        Total de {total_stats['lines']} lignes et {total_stats['words']} mots.
        """
        
        # Ajouter les types de fichiers les plus courants
        if file_types:
            common_types = file_types.most_common(3)
            type_desc = ", ".join([f"{count} {ext} fichiers" for ext, count in common_types])
            summary += f" Principaux types: {type_desc}."
        
        return summary
    
    def get_detailed_report(self, file_stats, total_stats, file_types):
        """Rapport détaillé pour l'interface"""
        report = {
            'summary': {
                'total_files': total_stats.get('files', 0),
                'total_lines': total_stats.get('lines', 0),
                'total_words': total_stats.get('words', 0),
                'total_size_mb': total_stats.get('size_bytes', 0) / 1024 / 1024,
            },
            'file_types': dict(file_types),
            'largest_files': [],
            'error_files': [f for f in file_stats if 'error' in f]
        }
        
        # Top 5 des plus gros fichiers
        valid_files = [f for f in file_stats if 'error' not in f]
        if valid_files:
            report['largest_files'] = sorted(valid_files, 
                                           key=lambda x: x['size_bytes'], 
                                           reverse=True)[:5]
        
        return report
