#!/usr/bin/env python3
"""
Demonstration complete du systeme de monitoring LLM.
Teste le rafraichissement automatique et l'affichage dans le menu d'information systeme.
"""

import sys
import os

# Ajouter le repertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.system_monitor import SystemMonitor
from services.llm_service import LLMService

def demo_complete_llm_monitoring():
    """Demonstration complete du monitoring LLM."""
    print("=" * 80)
    print("DEMONSTRATION - MONITORING LLM AUTOMATIQUE")
    print("=" * 80)
    
    # 1. Test detection automatique LLM
    print("\n1. TEST DETECTION AUTOMATIQUE LLM:")
    print("-" * 40)
    llm_service = LLMService.detect_and_create()
    service_info = llm_service.get_service_info()
    
    print(f"Service detecte: {service_info['service_type']}")
    print(f"Modele actif: {service_info['model']}")
    print(f"Connexion: {'OK' if service_info['connection_test'] else 'ECHEC'}")
    
    # 2. Test rafraichissement via SystemMonitor
    print("\n2. TEST RAFRAICHISSEMENT VIA SYSTEMMONITOR:")
    print("-" * 50)
    monitor = SystemMonitor()
    llm_info = monitor.refresh_llm_models()
    
    print(f"Service: {llm_info['service_type']}")
    print(f"Modele actif: {llm_info['active_model']}")
    print(f"Total modeles: {llm_info['total_models']}")
    
    if llm_info.get('available_models'):
        print("Modeles disponibles:")
        for i, model in enumerate(llm_info['available_models'], 1):
            is_active = model == llm_info.get('active_model')
            marker = " [ACTIF]" if is_active else ""
            print(f"   {i}. {model}{marker}")
    
    # 3. Test integration dans les infos systeme
    print("\n3. TEST INTEGRATION DANS INFOS SYSTEME:")
    print("-" * 45)
    detailed_info = monitor.get_detailed_system_info()
    llm_section = detailed_info.get('llm', {})
    
    print("Section LLM dans les informations systeme detaillees:")
    print(f"   Service: {llm_section.get('service_type', 'N/A')}")
    print(f"   Modele actif: {llm_section.get('active_model', 'N/A')}")
    print(f"   Modeles disponibles: {llm_section.get('total_models', 0)}")
    print(f"   Timestamp: {llm_section.get('timestamp', 'N/A')}")
    
    # 4. Test simulation de demarrage d'application
    print("\n4. SIMULATION DEMARRAGE APPLICATION:")
    print("-" * 45)
    print("Initialisation des services...")
    print("Detection automatique des modeles LLM...")
    
    startup_llm_info = monitor.refresh_llm_models()
    
    if startup_llm_info.get('service_type') not in ['error', 'none']:
        print(f"Service LLM detecte: {startup_llm_info['service_type']}")
        print(f"Modele configure: {startup_llm_info['active_model']}")
        print(f"{startup_llm_info['total_models']} modele(s) disponible(s)")
        print("Application prete avec LLM fonctionnel!")
    else:
        print("Aucun service LLM detecte")
        print("L'application utilisera le mode simulation")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION TERMINEE")
    print("Le systeme LLM est correctement configure et monitore!")
    print("=" * 80)

if __name__ == "__main__":
    demo_complete_llm_monitoring()