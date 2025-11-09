# src/adapters/display_epaper.py

class DisplayEPaper:
    def __init__(self, driver=None):
        self.driver = driver  # Peut être un objet dépendant du matériel réel

    def display_text(self, text: str):
        # Appel le driver e-paper pour afficher texte
        if self.driver:
            self.driver.display(text)
        else:
            print(f"Affichage e-Paper: {text}")

    def clear(self):
        if self.driver:
            self.driver.clear()
        else:
            print("Nettoyage e-Paper")

class DisplayEPaperMock:
    def __init__(self):
        pass

    def display_text(self, text: str):
        print(f"[Mock] Texte à afficher sur e-Paper : {text}")

    def clear(self):
        print("[Mock] Nettoyage e-Paper (mock)")
