# src/controllers/settings_controller.py
```
"""Controller to manage settings (stub)."""
class SettingsController:
    def __init__(self, settings_model):
        self.settings = settings_model

    def get(self):
        return self.settings

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.settings, k, v)
```

---
# src/models/user_profile.py
```
class UserProfile:
    def __init__(self, name: str = "Utilisateur"):
        self.name = name