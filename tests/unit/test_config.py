"""
Tests complets pour le module de configuration
"""
import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestConfigManager:
    """Tests pour le gestionnaire de configuration."""
    
    @pytest.fixture
    def config_manager_tmp(self, tmp_path):
        """Crée un ConfigManager avec chemins tmp."""
        config_file = tmp_path / "config_test.yaml"
        content = """
default_microphone_index: 1
default_voice: "fr_FR-siwis-medium"
default_model: "qwen3-coder:latest"
web_port: 7860
sample_rate: 16000
"""
        config_file.write_text(content)
        return config_file
    
    def test_config_load(tmp_path, config_manager_tmp):
        """Test de chargement de configuration."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_manager_tmp))
        
        assert cfg.default_microphone_index == 1
        assert cfg.default_voice == "fr_FR-siwis-medium"
        assert cfg.default_model == "qwen3-coder:latest"
        assert cfg.web_port == 7860
        assert cfg.sample_rate == 16000
    
    def test_config_load_defaults(tmp_path):
        """Test de chargement avec valeurs par défaut."""
        from src.config.config import ConfigManager
        
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")  # Fichier vide
        
        cfg = ConfigManager(str(config_file))
        
        # Vérifie que les valeurs par défaut sont utilisées
        assert hasattr(cfg, 'voice_name')
        assert hasattr(cfg, 'llm_model')
        assert hasattr(cfg, 'web_port')
    
    def test_config_update(self, tmp_path, config_manager_tmp):
        """Test de mise à jour de configuration."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_manager_tmp))
        
        cfg.default_voice = "new_voice"
        cfg.web_port = 8888
        
        # Vérifie que les mises à jour sont appliquées
        assert cfg.default_voice == "new_voice"
        assert cfg.web_port == 8888
    
    def test_config_save(self, tmp_path, config_manager_tmp):
        """Test de sauvegarde de configuration."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_manager_tmp))
        
        # Sauvegarde vers un nouveau fichier
        new_config = tmp_path / "new_config.yaml"
        cfg.save(str(new_config))
        
        assert new_config.exists()
        assert cfg.default_voice in new_config.read_text()


class TestSettings:
    """Tests pour les settings audio."""
    
    def test_settings_default_values(self):
        """Test des valeurs par défaut des settings audio."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        assert settings.chunk_size == 1024
        assert settings.audio_buffer_size == 3
        assert settings.enable_low_latency is False
    
    def test_settings_from_config(self):
        """Test de la création des settings depuis la config."""
        from src.models.settings import Settings
        
        mock_config = MagicMock()
        mock_config.DEFAULT_MICROPHONE_INDEX = 1
        mock_config.DEFAULT_VOICE = "test-voice"
        mock_config.DEFAULT_MODEL = "test-model"
        mock_config.WEB_PORT = 8080
        mock_config.SAMPLE_RATE = 44100
        mock_config.CHUNK_SIZE = 512
        mock_config.AUDIO_BUFFER_SIZE = 2
        mock_config.ENABLE_LOW_LATENCY = True
        
        settings = Settings.from_config(mock_config)
        
        assert settings.microphone_index == 1
        assert settings.voice_name == "test-voice"
        assert settings.chunk_size == 512
        assert settings.audio_buffer_size == 2
        assert settings.enable_low_latency is True
    
    def test_settings_voice_names(self):
        """Test des noms de voix valides."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        assert "fr_FR-siwis-medium" not in settings.invalid_voice_names
    
    def test_settings_llm_models(self):
        """Test des modèles LLM valides."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        assert "qwen3-coder" not in settings.invalid_llm_models


class TestConfigParser:
    """Tests pour le parser YAML."""
    
    @pytest.fixture
    def sample_config(self, tmp_path):
        """Fournit une config YAML d'échantillon."""
        config_content = """
sample_rate: 16000
default_microphone_index: 0
default_voice: "fr_FR-siwis-medium"
default_model: "qwen3-coder:latest"
web_port: 7860
log_level: "INFO"
performance:
  auto_optimize: true
  monitoring_interval: 5
  alert_thresholds:
    cpu_max: 80.0
    memory_max: 85.0
    gpu_memory_max: 85.0
"""
        return tmp_path / "config.yaml"
    
    def test_parse_audio_settings(self, sample_config):
        """Test du parsing des paramètres audio."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(sample_config))
        
        assert cfg.sample_rate == 16000
        assert cfg.default_microphone_index == 0
    
    def test_parse_performance_settings(self, sample_config):
        """Test du parsing des paramètres de performance."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(sample_config))
        
        assert cfg.performance.auto_optimize is True
        assert cfg.performance.monitoring_interval == 5
    
    def test_parse_thresholds(self, sample_config):
        """Test du parsing des seuils d'alerte."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(sample_config))
        
        assert cfg.performance.alert_thresholds.cpu_max == 80.0
        assert cfg.performance.alert_thresholds.memory_max == 85.0


def test_config_environment_override(tmp_path, config_manager_tmp):
    """Test de l'override par variables d'environnement."""
    from src.config.config import ConfigManager
    import os
    
    cfg = ConfigManager(str(config_manager_tmp))
    
    # Test d'override par environment
    os.environ["WEB_PORT"] = "9999"
    
    # Relève la class pour réinitialiser
    ConfigManager.__module__ = "src.config.config"
    
    del os.environ["WEB_PORT"]


# Tests edge cases
class TestConfigEdgeCases:
    """Tests cas limites de configuration."""
    
    def test_empty_config(self, tmp_path):
        """Test avec configuration vide."""
        from src.config.config import ConfigManager
        
        config_file = tmp_path / "empty_config.yaml"
        config_file.write_text("")
        
        with pytest.warns():
            cfg = ConfigManager(str(config_file))
            
            assert hasattr(cfg, 'voice_name')
    
    def test_invalid_yaml(self, tmp_path):
        """Test avec YAML invalide."""
        from src.config.config import ConfigManager
        
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")
        
        with pytest.raises(Exception) as exc:
            cfg = ConfigManager(str(config_file))
            
        assert "invalid" in str(exc.value).lower()
    
    def test_missing_file(self, tmp_path):
        """Test avec fichier manquant."""
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(None)
        
        # Fallback à la configuration par défaut
        assert hasattr(cfg, 'voice_name')


class TestConfigManagerValidation:
    """Tests de validation de configuration."""
    
    def test_valid_audio_sample_rate(self):
        """Test du taux d'échantillonnage valide."""
        from src.config.config import ConfigManager
        
        sample_rates = [8000, 16000, 22050, 44100, 48000]
        for rate in sample_rates:
            config_file = Path(None)
            content = f"""
sample_rate: {rate}
"""
            config_file.write_text("")
            cfg = ConfigManager(str(config_file))
            
            assert cfg.sample_rate is not None
    
    def test_invalid_audio_sample_rate(self):
        """Test du taux d'échantillonnage invalide."""
        from src.config.config import ConfigManager
        
        sample_rates = [0, -1000, 100000]
        for rate in sample_rates:
            config_content = f"""
sample_rate: {rate}
"""
            
            config_file = Path(None)
            cfg = ConfigManager(str(config_file))
            
            assert cfg.sample_rate is not None


class TestPerformanceConfig:
    """Tests de configuration de performance."""
    
    def test_performance_auto_optimize_true(self, tmp_path):
        """Test de l'auto_optimize activé."""
        config_content = """
performance:
  auto_optimize: true
  monitoring_interval: 5
"""
        config_file = tmp_path / "perf.yaml"
        config_file.write_text(config_content)
        
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_file))
        
        assert cfg.performance.auto_optimize is True
        assert cfg.performance.monitoring_interval == 5
    
    def test_performance_thresholds_cpu(self, tmp_path):
        """Test des seuils CPU."""
        config_content = """
performance:
  alert_thresholds:
    cpu_max: 75.0
    memory_max: 80.0
    gpu_memory_max: 70.0
"""
        config_file = tmp_path / "thresh.yaml"
        config_file.write_text(config_content)
        
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_file))
        
        assert cfg.performance.alert_thresholds.cpu_max == 75.0
        assert cfg.performance.alert_thresholds.memory_max == 80.0
        assert cfg.performance.alert_thresholds.gpu_memory_max == 70.0


class TestConfigLogging:
    """Tests de configuration de logging."""
    
    def test_logging_levels(self, tmp_path):
        """Test des niveaux de logging valides."""
        from src.config.config import ConfigManager
        
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            config_content = f"""
log_level: "{level}"
"""
            
            config_file = tmp_path / "log.yaml"
            config_file.write_text(config_content)
            
            cfg = ConfigManager(str(config_file))
            
            assert cfg.log_level == level
    
    def test_logging_level_default(self, tmp_path):
        """Test du niveau de logging par défaut."""
        config_content = """
log_level: "INFO"
"""
        
        config_file = tmp_path / "default.yaml"
        config_file.write_text(config_content)
        
        from src.config.config import ConfigManager
        
        cfg = ConfigManager(str(config_file))
        
        assert cfg.log_level == "INFO"
