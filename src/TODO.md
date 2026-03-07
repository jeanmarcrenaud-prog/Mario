# 🔧 TODO - src/ Mario Assistant Vocal

## En Cours ✅ (Mar 2026)

### Priorité: HAUT
- [ ] Adapter `src/services/` aux besoins GPU
- [ ] Optimiser `src/controllers/` pour faible latence
- [ ] Vérifier `src/adapters/` pour toutes plateformes

### Priorité: MOYEN
- [ ] Tests unitaires pour `src/services/*`
- [ ] Tests intégration `src/controllers/main.py`
- [ ] Coverage `src/models/*` à atteindre

### Priorité: BAS
- [ ] Documentation API `src/services/`
- [ ] Documentation API `src/controllers/`
- [ ] Javadoc/Docstrings pour toutes classes

---

## Terminées ✅

### Architecture
- [x] Structure MVC complète
- [x] Factory pattern implémenté
- [x] Architecture modulaire

### Services (`src/services/`)
- [x] `LLMService` - Communication Ollama
- [x] `AudioPipeline` - Traitement audio basique
- [x] `SystemMonitor` - Monitoring CPU/GPU/mémoire
- [x] `ErrorHandler` - Gestion d'erreurs centralisée

### Controllers (`src/controllers/`)
- [x] `main.py` - Point d'entrée principal
- [x] Gestion des événements audio
- [x] Orchestration des services

### Config (`src/config/`)
- [x] `__init__.py` - Configuration système
- [x] `settings.py` - Configuration audio

### Models (`src/models/`)
- [x] `ConversationState` - Gestion état conversation
- [x] `WakeWordDetection` - Détection mot activateur

### Adapters (`src/adapters/`)
- [x] Interfaces standardisées
- [x] Drivers audio supportés

### Events (`src/events/`)
- [x] Système de publications d'événements
- [x]: Événements audio et LLM

### Interfaces (`src/interfaces/`)
- [x] Web (Gradio)
- [x] Console
- [x] ePaper

### Views (`src/views/`)
- [x] HTML/CSS/JS templates
- [x] Styling responsive

---

## Architecture src/

```
src/
├── adapters/       # Adaptateurs (audio, LLM, wake word)
├── config/         # Configuration système
├── controllers/    # Contrôleurs (main.py, gestion flux)
├── core/           # Cœur (gestion d'état, événements)
├── events/         # Système d'événements
├── factory.py      # Factory pattern
├── interfaces/     # Interfaces utilisateur (Web, Console, ePaper)
├── main.py         # Point d'entrée principal
├── models/         # Modèles (ConversationState, WakeWord)
├── services/       # Services (LLM, Audio, Monitor, Error)
├── utils/          # Utilitaires
├── views/          # Templates HTML/CSS
└── __init__.py
```

## Coverage Actuelle

| Module | Couverture | Status |
|--------|------------|--------|
| settings | 100% | ✅ |
| conversation_state | 100% | ✅ |
| error_guard | 100% | ✅ |
| config | 100% | ✅ |
| **Moyenne** | **27%** | 🔄 50% cible |

## Prochaines Actions

1. **Adapter PyTorch** pour utiliser CUDA sur RTX 5080
2. **Augmenter tests** pour atteindre 50% de couverture
3. **Documenter** toutes les APIs exposed
4. **Optimiser** latence audio avec chunking intelligent