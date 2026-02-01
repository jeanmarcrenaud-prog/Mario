# src/controllers/self_improvement_controller.py
from src.core.self_improvement.self_improve import self_improve

class SelfImprovementController:
    def __init__(self):
        pass

    def trigger_self_improvement(self):
        print("Début de l'auto-amélioration...")
        self_improve()
        print("Auto-amélioration terminée.")
