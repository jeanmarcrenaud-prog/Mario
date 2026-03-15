#!/usr/bin/env python3
"""
Script de test pour vérifier la détection automatique des services LLM.
Teste Ollama et LM Studio et affiche les informations du service utilisé.
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
from services.llm_service import LLMService, OllamaLLMAdapter, LMStudioLLMAdapter

def test_service_endpoints():
    """Test des endpoints des services LLM."""
    print("Test des endpoints des services LLM...")
    print("=" * 60)
    
    services = [
        ("Ollama", "http://localhost:11434", "/api/tags"),
        ("LM Studio", "http://localhost:1234", "/v1/models")
    ]
    
    for name, base_url, endpoint in services:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"{name}: {response.status_code} - {response.reason}")
            
            if name == "Ollama":
                models = [model['name'] for model in response.json().get('models', [])]
                print(f"  Modeles disponibles: {models}")
            elif name == "LM Studio":
                models = [model['id'] for model in response.json().get('data', [])]
                print(f"  Modeles disponibles: {models}")
                
        except Exception as e:
            print(f"{name}: Erreur - {str(e)}")
    
    print("=" * 60)

def test_with_actual_models():
    """Test avec les modèles réellement disponibles."""
    print("\nTest avec les modeles reels disponibles...")
    print("=" * 60)
    
    # Test Ollama avec le modèle disponible
    print("1. Test Ollama avec minimax-m2:cloud:")
    try:
        ollama_adapter = OllamaLLMAdapter(model_name="minimax-m2:cloud")
        if ollama_adapter.test_connection():
            messages = [
                {"role": "system", "content": "Tu es un assistant utile."},
                {"role": "user", "content": "Dis-moi bonjour."}
            ]
            response = ollama_adapter.generate_response(messages)
            print(f"   Reponse: {response}")
        else:
            print("   Connexion echouee")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test LM Studio avec qwen3.5-9b
    print("\n2. Test LM Studio avec qwen3.5-9b:")
    try:
        lmstudio_adapter = LMStudioLLMAdapter(model_name="qwen/qwen3.5-9b")
        if lmstudio_adapter.test_connection():
            messages = [
                {"role": "system", "content": "Tu es un assistant utile."},
                {"role": "user", "content": "Dis-moi bonjour."}
            ]
            response = lmstudio_adapter.generate_response(messages)
            print(f"   Reponse: {response}")
        else:
            print("   Connexion echouee")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    print("=" * 60)

def test_llm_detection():
    """Teste la détection automatique des services LLM."""
    print("\nDetection automatique des services LLM...")
    print("=" * 60)
    
    # Test de détection automatique
    llm_service = LLMService.detect_and_create()
    
    # Informations du service
    info = llm_service.get_service_info()
    
    print(f"Service detecte: {info['service_type']}")
    print(f"Disponibilite: {'Disponible' if info['available'] else 'Non disponible'}")
    print(f"Modele: {info['model'] or 'N/A'}")
    print(f"Test de connexion: {'Reussi' if info['connection_test'] else 'Echoue'}")
    print()
    
    if info['service_type'] != 'simulation':
        print("Test de generation de reponse:")
        messages = [
            {"role": "system", "content": "Tu es un assistant utile."},
            {"role": "user", "content": "Dis-moi bonjour et explique ce que tu peux faire."}
        ]
        
        response = llm_service.generate_response(messages)
        print(f"Reponse: {response}")
    else:
        print("Mode simulation active - Aucun service LLM reel detecte")
        print("Assurez-vous qu'Ollama ou LM Studio est en cours d'execution")
    
    print("=" * 60)

if __name__ == "__main__":
    test_service_endpoints()
    test_with_actual_models()
    test_llm_detection()