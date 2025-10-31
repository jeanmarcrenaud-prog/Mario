import os
import tempfile
import pytest
from pathlib import Path
from collections import Counter, defaultdict  # Add these imports
from src.utils.file_analyzer import FileAnalyzer

class TestFileAnalyzer:
    """Comprehensive tests for FileAnalyzer class"""
    
    def setup_method(self):
        self.analyzer = FileAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_python_file(self):
        """Test analyzing a Python file with specific metrics"""
        python_content = '''
import os
import sys

class TestClass:
    def test_method(self):
        # This is a comment
        return "hello"

def test_function():
    """Docstring"""
    pass
'''
        python_file = Path(self.temp_dir) / "test.py"
        python_file.write_text(python_content)
        
        result = self.analyzer.analyze_file(str(python_file))
        
        assert result["error"] is False
        metadata = result["metadata"]
        assert metadata["imports"] == 2
        assert metadata["classes"] == 1
        assert metadata["functions"] == 1
        assert metadata["comments"] == 1
    
    def test_analyze_directory_success(self):
        """Test analyzing a directory with multiple files"""
        # Create test files
        files = {
            "test1.txt": "Line 1\nLine 2",
            "test2.py": "print('hello')",
            "test3.md": "# Header\nSome text"
        }
        
        for filename, content in files.items():
            file_path = Path(self.temp_dir) / filename
            file_path.write_text(content)
        
        file_stats, total_stats, file_types, error = self.analyzer.analyze_directory(self.temp_dir)
        
        assert error is None
        assert len(file_stats) == 3
        assert total_stats["files"] == 3
        assert file_types[".txt"] == 1
        assert file_types[".py"] == 1
        assert file_types[".md"] == 1
    
    def test_analyze_directory_nonexistent(self):
        """Test analyzing a non-existent directory"""
        file_stats, total_stats, file_types, error = self.analyzer.analyze_directory("/nonexistent/path")
        
        assert file_stats == []
        assert total_stats == defaultdict(int)  # Now this will work
        assert file_types == Counter()  # And this too
        assert error == "Le chemin spécifié n'existe pas"
    
    def test_analyze_directory_empty(self):
        """Test analyzing an empty directory"""
        file_stats, total_stats, file_types, error = self.analyzer.analyze_directory(self.temp_dir)
        
        assert error is None
        assert len(file_stats) == 0
        assert total_stats["files"] == 0
    
    def test_generate_summary_with_files(self):
        """Test generating summary with actual files"""
        # Create test files first
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3")
        
        file_stats, total_stats, file_types, error = self.analyzer.analyze_directory(self.temp_dir)
        summary = self.analyzer.generate_summary(total_stats, file_types)
        
        assert "fichiers" in summary
        assert "lignes" in summary
        assert "mots" in summary
    
    def test_generate_summary_empty(self):
        """Test generating summary with no files"""
        summary = self.analyzer.generate_summary({}, {})
        assert "Aucun fichier texte trouvé" in summary
    
    def test_get_detailed_report(self):
        """Test generating detailed report"""
        # Create multiple files with different sizes
        large_content = "x" * 1000
        small_content = "x" * 100
        
        large_file = Path(self.temp_dir) / "large.txt"
        small_file = Path(self.temp_dir) / "small.txt"
        
        large_file.write_text(large_content)
        small_file.write_text(small_content)
        
        file_stats, total_stats, file_types, error = self.analyzer.analyze_directory(self.temp_dir)
        report = self.analyzer.get_detailed_report(file_stats, total_stats, file_types)
        
        assert "summary" in report
        assert "file_types" in report
        assert "largest_files" in report
        assert "error_files" in report
        assert len(report["largest_files"]) == 2
        assert report["largest_files"][0]["metadata"]["size_bytes"] == 1000
    
    def test_analyze_file_unsupported_encoding(self):
        """Test analyzing file with encoding issues"""
        # Create a binary file that will cause encoding errors
        binary_file = Path(self.temp_dir) / "binary.dat"
        binary_file.write_bytes(b'\x80\x81\x82')
        
        result = self.analyzer.analyze_file(str(binary_file))
        assert result["error"] is False  # Should handle with errors='ignore'
    
    def test_supported_extensions(self):
        """Test that supported extensions are correctly set"""
        expected_extensions = {'.txt', '.py', '.md', '.json', '.xml', '.html', '.css', '.js', '.java', '.c', '.cpp', '.h'}
        assert self.analyzer.supported_extensions == expected_extensions
