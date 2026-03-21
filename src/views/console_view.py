from ..utils.logger import logger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt
RICH_AVAILABLE = True

class ConsoleView:
    """Vue console améliorée avec Rich pour l'assistant vocal."""
    
    def __init__(self, controller):
        self.controller = controller
        if controller is None:
            logger.warning("⚠️ ConsoleView running without controller")
        
        # Initialiser Rich si disponible
        if RICH_AVAILABLE:
            self.console = Console()
            self.use_rich = True
        else:
            self.use_rich = False
            
        logger.info("ConsoleView initialisée")

    def display_message(self, message):
        """Affiche un message dans la console."""
        if self.use_rich:
            # Messages de l'assistant avec mise en forme
            if message.startswith("Assistant:"):
                content = message.replace("Assistant:", "").strip()
                panel = Panel(
                    Markdown(content) if content.startswith("#") or "**" in content else content,
                    title="🤖 Assistant",
                    border_style="blue",
                    expand=False
                )
                self.console.print(panel)
            # Messages d'erreur
            elif message.startswith("[ERREUR]"):
                self.console.print(f"❌ {message}", style="bold red")
            # Messages d'information
            elif message.startswith("📝"):
                self.console.print(message, style="green")
            elif message.startswith("🎯"):
                self.console.print(message, style="yellow")
            elif message.startswith("🎤"):
                self.console.print(message, style="cyan")
            else:
                self.console.print(f"💬 {message}")
        else:
            print(f"🤖 {message}")

    def display_system_message(self, message):
        """Affiche un message système."""
        if self.use_rich:
            self.console.print(f"🔧 {message}", style="dim")
        else:
            print(f"🔧 {message}")

    def display_success(self, message):
        """Affiche un message de succès."""
        if self.use_rich:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")

    def display_warning(self, message):
        """Affiche un message d'avertissement."""
        if self.use_rich:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"⚠️  {message}")

    def display_error(self, message):
        """Affiche un message d'erreur."""
        if self.use_rich:
            self.console.print(f"❌ {message}", style="bold red")
        else:
            print(f"❌ {message}")

    def get_user_input(self, prompt="Vous> "):
        """Récupère une entrée utilisateur."""
        try:
            if self.use_rich:
                return Prompt.ask(prompt.rstrip())
            else:
                return input(prompt)
        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Erreur lecture entrée: {e}")
            return None

    def show_help(self):
        """Affiche l'aide de la console avec mise en forme améliorée."""
        if self.use_rich:
            help_text = """
# 🎮 Commandes de l'Assistant Vocal

## 📋 Commandes de base
- **help** : Affiche cette aide
- **clear** : Efface l'historique de conversation
- **status** : Affiche le statut de l'assistant
- **exit** : Quitte l'application

## 💬 Interaction
Tapez simplement votre message pour discuter avec l'assistant.
L'assistant répondra vocalement et textuellement.

## 🛠️ Fonctionnalités avancées
- **analyze <chemin>** : Analyse un projet complet
- **test** : Exécute un test de fonctionnalité
- **optimize** : Optimise les performances

## 🎯 Astuces
- L'assistant détecte automatiquement le mot-clé "Mario"
- La synthèse vocale est automatique pour les réponses
- Les conversations sont sauvegardées pendant la session
            """
            self.console.print(Markdown(help_text))
        else:
            help_text = """
Commandes disponibles:
  help    - Affiche cette aide
  clear   - Efface l'historique de conversation
  status  - Affiche le statut de l'assistant
  exit    - Quitte l'application
            """
            self.display_message(help_text)

    def show_status(self):
        """Affiche le statut de l'assistant avec mise en forme."""
        try:
            status = self.controller.get_performance_status()
            
            if self.use_rich:
                table = Table(title="📊 Statut de l'Assistant", show_header=True)
                table.add_column("Ressource", style="cyan")
                table.add_column("Valeur", style="green")
                
                cpu = status.get('cpu', 'N/A')
                memory = status.get('memory', 'N/A')
                memory_used = status.get('memory_used', 'N/A')
                
                table.add_row("CPU", cpu)
                table.add_row("Mémoire", memory)
                table.add_row("Mémoire utilisée", memory_used)
                
                # Ajouter GPU si disponible
                if 'gpu' in status:
                    table.add_row("GPU", status['gpu'])
                if 'gpu_utilization' in status:
                    table.add_row("GPU Utilisation", status['gpu_utilization'])
                
                self.console.print(table)
            else:
                status_text = f"""
Statut de l'assistant:
  CPU: {status.get('cpu_percent', 'N/A')}%
  Mémoire: {status.get('memory_percent', 'N/A')}%
  Disque: {status.get('disk_percent', 'N/A')}%
                """
                self.display_message(status_text)
                
        except Exception as e:
            error_msg = f"[ERREUR] Impossible d'obtenir le statut: {e}"
            self.display_error(error_msg)

    def show_conversation_history(self):
        """Affiche l'historique de conversation avec mise en forme."""
        try:
            history = self.controller.get_history()
            
            if self.use_rich:
                if not history:
                    self.console.print("📝 Aucun historique de conversation", style="dim")
                    return
                    
                table = Table(title="📜 Historique de Conversation")
                table.add_column("Rôle", style="bold")
                table.add_column("Message", style="white")
                
                for msg in history[-10:]:  # Afficher seulement les 10 derniers messages
                    role_style = "blue" if msg['role'] == 'user' else "green"
                    table.add_row(msg['role'].title(), msg['content'], style=role_style)
                
                self.console.print(table)
            else:
                self.display_message("📜 Historique de conversation:")
                for msg in history:
                    role = "Vous" if msg['role'] == 'user' else "Assistant"
                    print(f"  {role}: {msg['content']}")
                    
        except Exception as e:
            self.display_error(f"Erreur affichage historique: {e}")

    def clear_conversation(self):
        """Efface la conversation."""
        self.controller.clear_conversation()
        if self.use_rich:
            self.console.print("🗑️  Conversation effacée", style="yellow")
        else:
            self.display_message("Conversation effacée")

    def show_welcome(self):
        """Affiche le message de bienvenue avec mise en forme."""
        if self.use_rich:
            welcome_text = """
# 🎤 Assistant Vocal Mario

Bienvenue dans votre assistant vocal intelligent !

## 🚀 Fonctionnalités
- 🔊 Reconnaissance et synthèse vocale
- 🧠 Intelligence artificielle avancée
- 📁 Analyse de projets et de code
- 🎯 Détection de mot-clé "Mario"

## 📝 Commandes
Tapez `help` pour voir toutes les commandes disponibles.
            """
            self.console.print(Markdown(welcome_text))
        else:
            self.display_message("=== Assistant Vocal Mario ===")
            self.display_message("Tapez 'help' pour la liste des commandes")

    def process_message(self, user_input):
        """Traite un message utilisateur."""
        if not user_input or not user_input.strip():
            return
            
        # Commandes spéciales
        if user_input.lower().startswith('analyze '):
            path = user_input[8:].strip()
            return self._analyze_project(path)
        elif user_input.lower() == 'test':
            return self._run_test()
        elif user_input.lower() == 'optimize':
            return self._optimize_performance()
        elif user_input.lower() == 'history':
            self.show_conversation_history()
            return
            
        # Traitement normal
        if self.use_rich:
            with self.console.status("[bold green]Traitement en cours...", spinner="dots"):
                response = self.controller.process_user_message(user_input)
        else:
            print("⏳ Traitement en cours...")
            response = self.controller.process_user_message(user_input)
            
        self.controller.play_tts_response(response)
        return response

    def _analyze_project(self, project_path):
        """Analyse un projet."""
        try:
            if self.use_rich:
                with self.console.status("[bold blue]Analyse du projet en cours...", spinner="clock"):
                    report = self.controller.analyze_project(project_path)
            else:
                print("🔍 Analyse du projet en cours...")
                report = self.controller.analyze_project(project_path)
                
            if 'error' in report:
                self.display_error(f"Erreur analyse: {report['error']}")
            else:
                summary = report.get('summary', 'Analyse terminée')
                self.display_success(f"Analyse terminée: {summary}")
                
        except Exception as e:
            self.display_error(f"Erreur analyse projet: {e}")

    def _run_test(self):
        """Exécute un test de fonctionnalité."""
        try:
            if self.use_rich:
                with self.console.status("[bold yellow]Test en cours...", spinner="star"):
                    # Test TTS
                    tts_success = self.controller.tts_service.test_synthesis()
                    # Test LLM
                    llm_success = self.controller.llm_service.test_service()
            else:
                print("🧪 Test en cours...")
                tts_success = self.controller.tts_service.test_synthesis()
                llm_success = self.controller.llm_service.test_service()
                
            if self.use_rich:
                table = Table(title="📊 Résultats des Tests")
                table.add_column("Service", style="cyan")
                table.add_column("Statut", style="green")
                table.add_row("TTS", "✅ OK" if tts_success else "❌ KO")
                table.add_row("LLM", "✅ OK" if llm_success else "❌ KO")
                self.console.print(table)
            else:
                self.display_success("Test TTS: " + ("OK" if tts_success else "KO"))
                self.display_success("Test LLM: " + ("OK" if llm_success else "KO"))
                
        except Exception as e:
            self.display_error(f"Erreur test: {e}")

    def _optimize_performance(self):
        """Optimise les performances."""
        try:
            if self.use_rich:
                with self.console.status("[bold magenta]Optimisation en cours...", spinner="clock"):
                    success = self.controller.optimize_performance()
            else:
                print("⚡ Optimisation en cours...")
                success = self.controller.optimize_performance()
                
            if success:
                self.display_success("Optimisation terminée avec succès")
            else:
                self.display_warning("Pas d'optimisations nécessaires")
                
        except Exception as e:
            self.display_error(f"Erreur optimisation: {e}")

    def loop(self):
        """Boucle principale de l'interface console."""
        try:
            self.show_welcome()
            
            while True:
                user_input = self.get_user_input()
                
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
                elif cmd == 'history':
                    self.show_conversation_history()
                else:
                    self.process_message(user_input)
                    
        except Exception as e:
            logger.error(f"Erreur dans la boucle console: {e}")
            self.display_error(f"Erreur dans la console: {e}")
        finally:
            if self.use_rich:
                self.console.print("\nAu revoir !", style="bold blue")
            else:
                print("\nAu revoir !")
            logger.info("Interface console terminee")
