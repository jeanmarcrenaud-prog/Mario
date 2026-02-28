# src/core/interface_manager.py
import socket
import threading
from typing import Optional

from src.utils.logger import logger
from src.views.web_interface_gradio import GradioWebInterface


class InterfaceManager:
    """Gère les interfaces: console et web"""

    def __init__(self, assistant, settings):
        self.assistant = assistant
        self.settings = settings
        self.console_view: Optional[object] = None
        self.web_interface: Optional[GradioWebInterface] = None

    def start_console(self) -> bool:
        """Démarre l'interface console"""
        try:
            from src.views.console_view import ConsoleView

            self.console_view = ConsoleView(self.assistant)
            console_thread = threading.Thread(target=self.console_view.loop, daemon=True)
            console_thread.start()
            logger.info("Interface console démarrée")
            return True
        except Exception as e:
            logger.warning(f"ConsoleView non disponible: {e}")
            return False

    def start_web(self) -> bool:
        """Démarre l'interface web Gradio"""
        try:
            self.web_interface = GradioWebInterface(self.assistant)

            def launch():
                try:
                    local_ip = socket.gethostbyname(socket.gethostname())
                    logger.info(f"Interface web: http://localhost:{self.settings.web_port}")
                    logger.info(f"Accès réseau: http://{local_ip}:{self.settings.web_port}")
                    self.web_interface.launch(
                        server_name="0.0.0.0",
                        server_port=self.settings.web_port,
                        share=False,
                        inbrowser=True,
                        prevent_thread_lock=True,
                    )
                except Exception as e:
                    logger.error(f"Erreur lancement web: {e}")

            web_thread = threading.Thread(target=launch, daemon=True)
            web_thread.start()
            logger.info("Interface web démarrée")
            return True
        except Exception as e:
            logger.error(f"Erreur démarrage web: {e}")
            return False

    def display_message(self, text: str):
        """Affiche un message dans l'interface console si disponible"""
        if self.console_view:
            try:
                self.console_view.display_message(text)
            except Exception:
                logger.info(f"Assistant: {text}")
        else:
            logger.info(f"Assistant: {text}")
