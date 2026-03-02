# Tests de Performance pour Assistant Vocal Mario

## Objectifs

1. Benchmarker les temps de réponse des modules audio (STT, TTS, Wake Word)
2. Mesurer la charge mémoire et CPU lors de sessions prolongées
3. Évaluer la concurrence entre modules audio
4. Validater l'utilisation GPU optimisée

## Benchmarks Temps Réel

### Structure de test recommandée

#### 1. Test de transcription (STT)

```python
# test_real_time_transcription.py
import time
import tempfile
import os

class RealTimeTranscriptionTest:
    def __init__(self, adapter):
        self.adapter = adapter
        
    def test_average_transcription_time(self, iterations=5):
        """Benchmark le temps moyen de transcription"""
        times = []
        for i in range(iterations):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                # Créer fichier audio Test (5s)
                pass
            
            start = time.time()
            result = self.adapter.transcribe(f.name)
            elapsed = time.time() - start
            
            times.append(elapsed)
            os.unlink(f.name)
            
        avg_time = sum(times) / len(times)
        print(f"Temps moyen de transcription: {avg_time:.2f}s")
        return avg_time
```

#### 2. Test de synthèse vocale (TTS)

```python
# test_real_time_tts.py
import time

class RealTimeTTSTest:
    def __init__(self, tts_service):
        self.tts_service = tts_service
        
    def test_generation_speed(self, text="Bonjour comment allez-vous", repetitions=3):
        """Benchmark la vitesse de génération TTS"""
        times = []
        for _ in range(repetitions):
            start = time.time()
            self.tts_service.speak(text)
            elapsed = time.time() - start
            times.append(elapsed)
            
        avg_time = sum(times) / len(times)
        print(f"Temps moyen TTS: {avg_time:.2f}s")
        return avg_time
```

#### 3. Test de détection mot-clé (Wake Word)

```python
# test_real_time_wake_word.py
import time
from unittest.mock import MagicMock

class RealTimeWakeWordTest:
    def __init__(self, wake_word_service):
        self.wake_word_service = wake_word_service
        
    def test_detection_latency(self, audio_clips, repetitions=5):
        """Benchmark la latence de détection wake word"""
        latencies = []
        for clip in audio_clips:
            for _ in range(repetitions):
                mock_audio = MagicMock()
                mock_audio.get_wave_data.return_value = clip
                
                start = time.time()
                detected = self.wake_word_service.detect_wake_word(mock_audio)
                elapsed = time.time() - start
                
                latencies.append(elapsed)
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"Latence moyenne de détection: {avg_latency:.2f}s")
        return avg_latency
```

## Tests de Charge Mémoire

### Configuration recommandée

```python
# test_memory_usage.py
import tracemalloc
import psutil
import gc

class MemoryUsageTest:
    def __init__(self):
        tracemalloc.start()
        
    def test_memory_after_transcription(self, adapter, audio_file):
        """Test de consommation mémoire après transcription"""
        gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        initial_memory = peak / 1024 / 1024  # MB
        
        result = adapter.transcribe(audio_file)
        
        gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        final_memory = peak / 1024 / 1024
        
        memory_used = final_memory - initial_memory
        print(f"Mémoire utilisée: {memory_used:.2f}MB")
        return memory_used
        
    def test_system_memory_stability(self, service, iterations=10):
        """Test de stabilité mémoire système"""
        memory_readings = []
        for _ in range(iterations):
            # Exécuter service
            service.process("test")
            # Lire mémoire utilisée
            memory = psutil.virtual_memory().percent
            memory_readings.append(memory)
        
        print(f"Mémoire système - Min: {min(memory_readings)}%, Max: {max(memory_readings)}%")
        return memory_readings
```

## Tests de Concurrence Audio

### Tests recommandés

```python
# test_audio_concurrency.py
import threading
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

class AudioConcurrencyTest:
    def __init__(self, audio_pipeline):
        self.audio_pipeline = audio_pipeline
        
    def test_parallel_processing(self, clips_count=3):
        """Test de traitement parallèle"""
        results = Queue()
        threads = []
        
        def process_clip(clip):
            result = self.audio_pipeline.process_clip(clip)
            results.put(result)
        
        clips = ["clip1.wav", "clip2.wav", "clip3.wav"]
        
        for clip in clips:
            t = threading.Thread(target=process_clip, args=(clip,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print(f"Temps total: {time.time() - start:.2f}s")
        return results.qsize()
        
    def test_thread_safety(self, iterations=10):
        """Test de sécurité des threads"""
        exceptions = []
        
        def safe_process():
            try:
                result = self.audio_pipeline.process_clip("test.wav")
                return True
            except Exception as e:
                exceptions.append(e)
                return False
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(safe_process) for _ in range(iterations)]
        
        successful = sum(1 for f in futures if f.result())
        print(f"Succès: {successful}/{iterations} ({successful/iterations*100:.1f}%)")
        return len(exceptions) == 0
```

## Validation GPU

### Utilisation GPU avec PyTorch

```python
# test_gpu_usage.py
import torch

class GPUUsageTest:
    def __init__(self, service):
        self.service = service
        
    def test_gpu_utilization(self, audio_file):
        """Test d'utilisation GPU"""
        if not torch.cuda.is_available():
            print("GPU non disponible")
            return
        
        gpu_memory_before = torch.cuda.memory_allocated()
        self.service.process(audio_file)
        gpu_memory_after = torch.cuda.memory_allocated()
        
        memory_used = (gpu_memory_after - gpu_memory_before) / 1024 / 1024
        print(f"Mémoire GPU utilisée: {memory_used:.2f}MB")
        return memory_used
```

## Exécution des Tests

```python
# run_performance_tests.py
import unittest
from test_real_time_transcription import RealTimeTranscriptionTest
from test_gpu_usage import GPUUsageTest

if __name__ == "__main__":
    # Initialiser les services
    from src.adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter
    adapter = WhisperSpeechRecognitionAdapter()
    
    # Exécuter benchmarks
    trans_test = RealTimeTranscriptionTest(adapter)
    gpu_test = GPUUsageTest(adapter)
    
    print("=== BENCHMARKS TEMPS RÉEL ===")
    trans_test.test_average_transcription_time()
    gpu_test.test_gpu_utilization("test_audio.wav")
    
    # Lancer tests unitaires
    unittest.main()
```

## Métriques Clés à Mesurer

1. **Temps de réponse** (s)
   - Transcription: <10s recommended
   - TTS: <3s recommended  
   - Wake Word: <0.5s recommended

2. **Consommation mémoire**
   - Mémoire GPU: <2GB recommended
   - Mémoire RAM peak: <1GB recommended

3. **Utilisation CPU**
   - CPU < 70% during processing
   - CPU return < 30% after processing

4. **Concurence**
   - Pas de deadlocks dans 10 tests parallèles
   - Latence constante sous charge

5. **Stabilité**
   - Pas de fuites mémoire après 50 Itérations
   - Temps de réponse stable sur 100 requêtes

## Configuration de Test

```yaml
# test_config.yaml
benchmark:
  iterations: 10
  audio_clips: 
    - short.wav: 5s
    - medium.wav: 30s
    - long.wav: 2min
  tts:
    - short: "Bonjour"
    - medium: "Bonjour comment allez-vous"
    - long: "Cecis un texte long pour le benchmark TTS"
```

## Priorités d'Implémentation

1. [ ] Ajouter test benchmark transcription
2. [ ] Ajouter test benchmark TTS
3. [ ] Ajouter test benchmark wake word
4. [ ] Ajouter tests mémoire
5. [ ] Ajouter tests concurrence
6. [ ] Ajouter validation GPU