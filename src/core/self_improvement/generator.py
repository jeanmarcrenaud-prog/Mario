import requests

def generate_code(prompt: str, model: str = "codellama"):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    return response.json()["response"]

# Exemple d'utilisation
improvement_plan = "Génère un adapter pour la météo utilisant OpenWeatherMap, compatible avec l'architecture MVC de Mario."
generated_code = generate_code(improvement_plan)
print(generated_code)
