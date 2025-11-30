from ..utils.logger import logger

class ConsoleView:
    """Vue console pour l'assistant vocal."""
    
    def __init__(self, controller):
        self.controller = controller
        if controller is None:
            logger.warning("⚠️ ConsoleView running without controller")
        logger.info("ConsoleView initialisée")

    def display_message(self, message):
        """Affiche un message dans la console."""
        print(f"🤖 {message}")

    def get_user_input(self, prompt="Vous> "):
        """Récupère une entrée utilisateur."""
        try:
            return input(prompt)
        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Erreur lecture entrée: {e}")
            return None

    def show_help(self):
        """Affiche l'aide de la console."""
        help_text = """
Commandes disponibles:
  help    - Affiche cette aide
  clear   - Efface l'historique de conversation
  status  - Affiche le statut de l'assistant
  exit    - Quitte l'application
        """
        self.display_message(help_text)

    def show_status(self):
        """Affiche le statut de l'assistant."""
        try:
            status = self.controller.get_performance_status()
            status_text = f"""
Statut de l'assistant:
  CPU: {status.get('cpu_percent', 'N/A')}%
  Mémoire: {status.get('memory_percent', 'N/A')}%
  Disque: {status.get('disk_percent', 'N/A')}%
            """
            self.display_message(status_text)
        except Exception as e:
            error_msg = f"[ERREUR] Impossible d'obtenir le statut: {e}"
            self.display_message(error_msg)

    def clear_conversation(self):
        """Efface la conversation."""
        self.controller.clear_conversation()
        self.display_message("Conversation effacée")

    def process_message(self, user_input):
        """Traite un message utilisateur."""
        if not user_input or not user_input.strip():
            return
            
        response = self.controller.process_user_message(user_input)
        self.controller.play_tts_response(response)
        return response

    def loop(self):
        """Boucle principale de l'interface console."""
        try:
            self.display_message("=== Assistant Vocal Mario ===")
            self.display_message("Tapez 'help' pour la liste des commandes")
            
            while True:
                user_input = self.get_user_input("Vous> ")
                
                if user_input is None:  # KeyboardInterrupt
                    break
                    
                if not user_input:
                    continue
                    
                cmd = user_input.lower().strip()
                if cmd in ['exit', 'quit', 'q']:
                    break
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'clear':
                    self.clear_conversation()
                elif cmd == 'status':
                    self.show_status()
                else:
                    self.process_message(user_input)
                    
        except Exception as e:
            logger.error(f"Erreur dans la boucle console: {e}")
            self.display_message(f"[ERREUR] {e}")
        finally:
            logger.info("Interface console terminée")
