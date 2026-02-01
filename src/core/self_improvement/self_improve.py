from analyzer import analyze_logs
from generator import generate_code
from integrator import integrate_code
from tests import run_tests

def self_improve():
    # 1. Analyser les logs
    improvements = analyze_logs("data/conversation_history.json")
    print("Améliorations proposées :", improvements)

    # 2. Générer le code pour chaque amélioration
    for improvement in improvements.split("\n"):
        if "Génère le code pour" in improvement:
            module_name = improvement.split(" ")[-1].strip(".")
            prompt = f"Génère le code pour {improvement} dans le projet Mario (architecture MVC)."
            code = generate_code(prompt)
            integrate_code(module_name, code)

    # 3. Exécuter les tests
    test_output, test_errors = run_tests()
    print("Résultats des tests :", test_output)
    if test_errors:
        print("Erreurs à corriger :", test_errors)
    else:
        print("Toutes les améliorations ont été validées !")

if __name__ == "__main__":
    self_improve()
