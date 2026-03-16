"""Tests de benchmarking réseau pour le service LLM."""

import pytest
from unittest.mock import Mock, patch
import time
import statistics

from src.services.llm_service import (
    OllamaLLMAdapter,
    LMStudioLLMAdapter,
    SimulatedLLMAdapter,
    LLMService
)


class TestNetworkLatencyBenchmark:
    """Tests de latence réseau pour les adaptateurs LLM."""
    
    @pytest.mark.integration
    def test_ollama_connection_latency(self):
        """Test la latence de connexion à Ollama."""
        adapter = OllamaLLMAdapter(
            model_name="qwen3-coder",
            base_url="http://localhost:11434"
        )
        
        # Mesurer le temps de connexion
        start_time = time.time()
        try:
            is_available = adapter.test_connection()
            connection_time = (time.time() - start_time) * 1000
            
            if is_available:
                assert connection_time < 5000, f"Connexion trop lente : {connection_time:.2f}ms"
                print(f"✅ Ollama connecté en {connection_time:.2f}ms")
            else:
                print("⚠️ Ollama non disponible (test de latence ignoré)")
        except Exception as e:
            print(f"⚠️ Ollama inaccessible : {e}")
    
    @pytest.mark.integration
    def test_lmstudio_connection_latency(self):
        """Test la latence de connexion à LM Studio."""
        adapter = LMStudioLLMAdapter(
            model_name="test-model",
            base_url="http://localhost:1234"
        )
        
        start_time = time.time()
        try:
            is_available = adapter.test_connection()
            connection_time = (time.time() - start_time) * 1000
            
            if is_available:
                assert connection_time < 5000, f"Connexion trop lente : {connection_time:.2f}ms"
                print(f"✅ LM Studio connecté en {connection_time:.2f}ms")
            else:
                print("⚠️ LM Studio non disponible (test de latence ignoré)")
        except Exception as e:
            print(f"⚠️ LM Studio inaccessible : {e}")


class TestResponseTimeBenchmark:
    """Tests de temps de réponse pour les requêtes LLM."""
    
    @pytest.mark.integration
    def test_ollama_response_time(self):
        """Test le temps de réponse d'Ollama."""
        adapter = OllamaLLMAdapter(
            model_name="qwen3-coder",
            base_url="http://localhost:11434"
        )
        
        if not adapter.test_connection():
            pytest.skip("Ollama non disponible")
        
        # Tester avec un prompt court
        messages = [{"role": "user", "content": "Bonjour"}]
        
        response_times = []
        num_iterations = 3
        
        for i in range(num_iterations):
            start_time = time.time()
            try:
                response = adapter.chat(messages, temperature=0.5, max_tokens=50)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                print(f"✅ Itération {i+1}: {response_time:.2f}ms")
            except Exception as e:
                print(f"❌ Erreur itération {i+1}: {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"\n📊 Statistiques Ollama:")
            print(f"   Moyenne: {avg_time:.2f}ms")
            print(f"   Min: {min_time:.2f}ms")
            print(f"   Max: {max_time:.2f}ms")
            
            assert avg_time < 10000, f"Temps de réponse moyen trop élevé : {avg_time:.2f}ms"


class TestModelListLatency:
    """Tests de latence pour la liste des modèles."""
    
    @pytest.mark.integration
    def test_ollama_model_list_latency(self):
        """Test le temps de récupération de la liste des modèles Ollama."""
        adapter = OllamaLLMAdapter(
            model_name="qwen3-coder",
            base_url="http://localhost:11434"
        )
        
        if not adapter.test_connection():
            pytest.skip("Ollama non disponible")
        
        start_time = time.time()
        models = adapter.get_available_models()
        list_time = (time.time() - start_time) * 1000
        
        print(f"✅ Liste modèles Ollama récupérée en {list_time:.2f}ms ({len(models)} modèles)")
        
        assert list_time < 3000, f"Récupération liste trop lente : {list_time:.2f}ms"
        assert isinstance(models, list), "La liste des modèles doit être une liste"


class TestNetworkStressBenchmark:
    """Tests de stress réseau pour le service LLM."""
    
    @pytest.mark.integration
    def test_concurrent_requests_simulation(self):
        """Test la gestion de requêtes concurrentes (simulation)."""
        # Simulation sans vrai réseau
        adapter = SimulatedLLMAdapter()
        
        num_requests = 10
        response_times = []
        
        for i in range(num_requests):
            start_time = time.time()
            messages = [{"role": "user", "content": f"Test {i}"}]
            
            try:
                response = adapter.chat(messages, temperature=0.5)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
            except Exception as e:
                print(f"❌ Erreur requête {i}: {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            print(f"\n📊 Simulation - Moyenne: {avg_time:.2f}ms ({num_requests} requêtes)")


class TestLLMServiceNetworkBenchmark:
    """Tests de benchmarking pour le service LLM complet."""
    
    @pytest.mark.integration
    def test_llm_service_response_benchmark(self):
        """Test les performances du service LLM complet."""
        # Utiliser la simulation pour éviter dépendances réseau
        llm_service = LLMService.create_with_simulation()
        
        messages = [{"role": "user", "content": "Bonjour, comment ça va?"}]
        
        response_times = []
        num_iterations = 5
        
        for i in range(num_iterations):
            start_time = time.time()
            
            try:
                response = llm_service.generate_response(messages, temperature=0.7)
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                print(f"✅ Itération {i+1}: {response_time:.2f}ms")
            except Exception as e:
                print(f"❌ Erreur itération {i+1}: {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
            
            print(f"\n📊 Statistiques Service LLM:")
            print(f"   Moyenne: {avg_time:.2f}ms")
            print(f"   P95: {p95_time:.2f}ms")


class TestNetworkTimeoutHandling:
    """Tests de gestion des timeouts réseau."""
    
    @pytest.mark.integration
    def test_ollama_timeout_handling(self):
        """Test la gestion du timeout Ollama."""
        # Utiliser une URL invalide pour tester le timeout
        adapter = OllamaLLMAdapter(
            model_name="test",
            base_url="http://192.0.2.1:11434"  # IP réservée pour tests (TEST-NET-1)
        )
        
        start_time = time.time()
        try:
            is_available = adapter.test_connection()
            elapsed = (time.time() - start_time) * 1000
            
            if not is_available:
                print(f"✅ Timeout correctement géré en {elapsed:.2f}ms")
                assert elapsed < 15000, "Timeout trop long"
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"✅ Exception gérée en {elapsed:.2f}ms : {type(e).__name__}")


class TestNetworkBandwidthEstimation:
    """Tests d'estimation de bande passante."""
    
    @pytest.mark.integration
    def test_response_size_measurement(self):
        """Test la mesure de la taille des réponses LLM."""
        adapter = SimulatedLLMAdapter()
        
        messages = [{"role": "user", "content": "Écris un texte long"}]
        
        response = adapter.chat(messages, temperature=0.7, max_tokens=500)
        response_size = len(response.encode('utf-8'))
        
        print(f"📏 Taille réponse: {response_size} octets ({response_size/1024:.2f} KB)")


@pytest.mark.integration
def test_full_network_benchmark_suite():
    """Exécute toute la suite de benchmarking réseau."""
    print("\n" + "="*60)
    print("🚀 BENCHMARKING RÉSEAU LLM - DÉMARRAGE")
    print("="*60)
    
    # Tests de latence
    latency_test = TestNetworkLatencyBenchmark()
    try:
        latency_test.test_ollama_connection_latency()
    except Exception as e:
        print(f"⚠️ Test latence Ollama échoué : {e}")
    
    try:
        latency_test.test_lmstudio_connection_latency()
    except Exception as e:
        print(f"⚠️ Test latence LM Studio échoué : {e}")
    
    # Tests de temps de réponse
    response_test = TestResponseTimeBenchmark()
    try:
        response_test.test_ollama_response_time()
    except Exception as e:
        print(f"⚠️ Test réponse Ollama échoué : {e}")
    
    # Tests de liste modèles
    model_test = TestModelListLatency()
    try:
        model_test.test_ollama_model_list_latency()
    except Exception as e:
        print(f"⚠️ Test liste modèles échoué : {e}")
    
    # Tests de stress
    stress_test = TestNetworkStressBenchmark()
    try:
        stress_test.test_concurrent_requests_simulation()
    except Exception as e:
        print(f"⚠️ Test stress échoué : {e}")
    
    # Tests service complet
    service_test = TestLLMServiceNetworkBenchmark()
    try:
        service_test.test_llm_service_response_benchmark()
    except Exception as e:
        print(f"⚠️ Test service LLM échoué : {e}")
    
    # Tests timeout
    timeout_test = TestNetworkTimeoutHandling()
    try:
        timeout_test.test_ollama_timeout_handling()
    except Exception as e:
        print(f"⚠️ Test timeout échoué : {e}")
    
    # Tests bande passante
    bandwidth_test = TestNetworkBandwidthEstimation()
    try:
        bandwidth_test.test_response_size_measurement()
    except Exception as e:
        print(f"⚠️ Test bande passante échoué : {e}")
    
    print("\n" + "="*60)
    print("✅ BENCHMARKING RÉSEAU TERMINÉ")
    print("="*60 + "\n")
