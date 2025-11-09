# src/ui/console_view.py
class ConsoleView:
    def __init__(self, controller):
        self.controller = controller

    def loop(self):
        print("Assistant Mario (console) — Entrer 'exit' pour arrêter.")
        while True:
            user_input = input("Vous : ")
            if user_input.lower() == 'exit':
                break
            # Ici, mise en forme comme dans le chat Gradio (historique dict role-content)
            self.controller.add_user_message(user_input)
            response = self.controller.generate_response()
            print("Assistant :", response)
            self.controller.play_tts_response(response)  # TTS automatique comme l'interface web

            # Affichage historique récapitulatif (optionnel)
            for msg in self.controller.get_history():
                print(f"{msg['role']} : {msg['content']}")
