#!/usr/bin/env python3
"""
Script de test pour vérifier les informations LLM dans le système de monitoring.
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.system_monitor import SystemMonitor

def test_llm_system_info():
    """Test des informations LLM dans le système de monitoring."""
    print("Test des informations LLM dans le système de monitoring...")
    print("=" * 70)
    
    monitor = SystemMonitor()
    
    # Test refresh et info LLM
    print("1. Rafraîchissement des modèles LLM:")
    llm_info = monitor.refresh_llm_models()
    
    print(f"   Service actif: {llm_info.get('service_type', 'N/A')}")
    print(f"   Modèle actif: {llm_info.get('active_model', 'N/A')}")
    print(f"   Nombre de modèles: {llm_info.get('total_models', 0)}")
    print(f"   Test de connexion: {'OK' if llm_info.get('connection_test') else 'Échoué'}")
    
    if llm_info.get('available_models'):
        print("   Modèles disponibles:")
        for i, model in enumerate(llm_info['available_models'], 1):
            is_active = model == llm_info.get('active_model')
            marker = " [ACTIF]" if is_active else ""
            print(f"      {i}. {model}{marker}")
    
    print("\n2. Informations système détaillées avec LLM:")
    detailed_info = monitor.get_detailed_system_info()
    llm_section = detailed_info.get('llm', {})
    
    print(f"   Section LLM dans les infos système:")
    print(f"   Service: {llm_section.get('service_type', 'N/A')}")
    print(f"   Modèle actif: {llm_section.get('active_model', 'N/A')}")
    print(f"   Total modèles: {llm_section.get('total_models', 0)}")
    
    if llm_section.get('error'):
        print(f"   Erreur: {llm_section['error']}")
    
    print("=" * 70)

if __name__ == "__main__":
    test_llm_system_info()