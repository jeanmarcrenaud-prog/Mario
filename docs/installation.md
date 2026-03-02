# Guide d'installation

## Prérequis

- Python 3.10+
- Conda (recommandé) ou pip
- Microphone
- Haut-parleurs

## Étape 1: Cloner le projet

```bash
git clone https://github.com/jeanmarcrenaud-prog/Mario.git
cd Mario
```

## Étape 2: Créer un environnement virtuel

### Avec Conda (recommandé)

```bash
conda create -n mario python=3.13
conda activate mario
```

### Avec venv

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

## Étape 3: Installer les dépendances

```bash
pip install -r requirements.txt
```

## Étape 4: Installer Ollama (pour le LLM)

### Windows
Téléchargez et installez Ollama depuis [ollama.com](https://ollama.com)

### Linux/Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Télécharger un modèle
```bash
ollama pull qwen3-coder:latest
```

## Étape 5: Configuration

Copiez le fichier de configuration exemple:

```bash
cp config.yaml.example config.yaml
```

Modifiez les paramètres dans `config.yaml`:
- `DEFAULT_MICROPHONE_INDEX`: Index du microphone (0 par défaut)
- `DEFAULT_VOICE`: Voix TTS (fr_FR-siwis-medium)
- `DEFAULT_MODEL`: Modèle LLM (qwen3-coder:latest)

## Étape 6: Lancer l'application

### Interface Web (Gradio)
```bash
python run.py
```

L'interface sera disponible sur `http://localhost:7860`

### Interface Console
```bash
python -m src.core.app_runner
```

## Dépannage

### Erreur: "Aucun microphone détecté"
- Vérifiez que votre microphone est connecté
- Vérifiez les permissions microphone dans Windows/macOS/Linux

### Erreur: "Ollama non disponible"
- Assurez-vous qu'Ollama est installé et démarré
- Lancez `ollama serve` dans un terminal séparé

### Erreur d'import de torch
- Réinstallez torch avec CUDA:
```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Problèmes de performance
- Activez le mode faible latence dans settings
- Vérifiez les statistiques avec `get_latency_stats()`

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `MARIO_PORT` | Port de l'interface web | 7860 |
| `MARIO_MODEL` | Modèle LLM | qwen3-coder:latest |
| `MARIO_VOICE` | Voix TTS | fr_FR-siwis-medium |

## Mise à jour

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```
