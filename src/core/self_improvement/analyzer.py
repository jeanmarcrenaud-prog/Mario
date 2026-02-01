import json
import requests

def analyze_logs(log_path: str, model: str = "codellama"):
    with open(log_path, "r") as f:
        logs = [json.loads(line) for line in f]

    prompt = f"""
    Analyse les logs suivants pour identifier :
    1. Les réponses incorrectes ou incomplètes de Mario.
    2. Les modules manquants ou défaillants.
    3. Les suggestions pour de nouvelles fonctionnalités.
    4. Les optimisations possibles pour le processeur AMD Ryzen 9 9800X3D.

    Logs :
    {logs}

    Propose un plan d'action détaillé pour chaque point, en tenant compte de l'architecture MVC de Mario.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    return response.json()["response"]
