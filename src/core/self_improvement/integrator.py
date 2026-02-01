import os

def integrate_code(module_name: str, code: str, module_type: str = "adapter"):
    base_path = f"src/{module_type}s"
    os.makedirs(base_path, exist_ok=True)
    module_path = os.path.join(base_path, f"{module_name}.py")

    with open(module_path, "w") as f:
        f.write(code)

    return f"Module {module_name} intégré dans {module_path}."

# Exemple d'utilisation
integrate_code("weather_adapter", generated_code, "adapter")
