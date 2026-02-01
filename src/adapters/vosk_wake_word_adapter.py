import json
import logging
import queue
import threading
from typing import Callable, Optional

import pyaudio
from vosk import KaldiRecognizer, Model

from src.interfaces.microphone_checker import Microphone_Checker
from src.interfaces.wake_word import IWakeWordAdapter

logger = logging.getLogger(__name__)


class VoskWakeWordAdapter(IWakeWordAdapter):
    """Adaptateur de detection de mot-cle utilisant Vosk.
    
    Ecoute en continu l'audio du microphone et declenche une detection
    quand le mot-cle "mario" est detecte dans le texte reconnu.
    """

    SAMPLE_RATE = 16000
    CHUNK = 4000
    WAKE_WORD = "mario"

    def __init__(
        self,
        model_path: str,
        microphone_checker: Optional[Microphone_Checker] = None,
    ) -> None:
        """Initialise l'adaptateur Vosk.
        
        Args:
            model_path: Chemin vers le dossier du modele Vosk
            microphone_checker: Instance de Microphone_Checker
        """
        try:
            self._model = Model(model_path)
        except Exception as e:
            logger.error(f"Impossible de charger le modele Vosk: {e}")
            raise

        self._mic_checker = microphone_checker or Microphone_Checker()
        self._pyaudio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None

        self._queue: queue.Queue[bytes] = queue.Queue()
        self._recognizer: Optional[KaldiRecognizer] = None

        self._on_detect: Optional[Callable[[], None]] = None
        self._on_audio: Optional[Callable[[bytes], None]] = None

        self._device_index: Optional[int] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(
        self,
        device_index: Optional[int],
        on_detect: Callable[[], None],
        on_audio: Callable[[bytes], None],
    ) -> bool:
        """Demarre l'ecoute du microphone."""
        self._device_index = device_index
        self._on_detect = on_detect
        self._on_audio = on_audio

        if not self._mic_checker.is_microphone_available(device_index):
            logger.error(f"Microphone non disponible (indice: {device_index})")
            return False

        try:
            self._recognizer = KaldiRecognizer(self._model, self.SAMPLE_RATE)
            logger.info("KaldiRecognizer cree")
        except Exception as e:
            logger.error(f"Impossible de creer KaldiRecognizer: {e}")
            return False

        try:
            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.CHUNK,
                stream_callback=self._pyaudio_callback,
            )
            self._stream.start_stream()
            logger.info(f"Flux PyAudio ouvert (device {device_index})")
        except Exception as e:
            logger.error(f"Impossible d'ouvrir le flux PyAudio: {e}")
            return False

        self._running = True
        self._thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self._thread.start()
        logger.info("Thread de reconnaissance Vosk demarre")
        return True

    def stop(self) -> None:
        """Arrete l'ecoute et libere les ressources."""
        logger.info("Arret de VoskWakeWordAdapter...")
        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture du flux: {e}")

        if self._pyaudio is not None:
            try:
                self._pyaudio.terminate()
            except Exception as e:
                logger.warning(f"Erreur lors de la terminaison de PyAudio: {e}")

        logger.info("VoskWakeWordAdapter arrete")

    def get_audio_devices(self) -> list[str]:
        """Recupere la liste des peripheriques audio disponibles."""
        devices = []
        try:
            for i in range(self._pyaudio.get_device_count()):
                info = self._pyaudio.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    devices.append(info.get("name", f"Device {i}"))
        except Exception as e:
            logger.warning(f"Erreur lors de l'enumeration des devices: {e}")
        return devices

    def _pyaudio_callback(
        self,
        in_data: bytes,
        frame_count: int,
        time_info: object,
        status_flags: int,
    ) -> tuple:
        """Callback appele par PyAudio."""
        if self._running and in_data:
            self._queue.put(in_data)
        return (None, pyaudio.paContinue)

    def _recognition_loop(self) -> None:
        """Boucle de reconnaissance continue via Vosk."""
        assert self._recognizer is not None
        logger.debug("Boucle de reconnaissance demarree")

        while self._running:
            try:
                data = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if not data:
                continue

            if self._on_audio is not None:
                try:
                    self._on_audio(data)
                except Exception as e:
                    logger.warning(f"Erreur dans on_audio callback: {e}")

            try:
                if self._recognizer.AcceptWaveform(data):
                    result = json.loads(self._recognizer.Result())
                    self._handle_result(result, is_final=True)
                else:
                    partial = json.loads(self._recognizer.PartialResult())
                    self._handle_result(partial, is_final=False)
            except Exception as e:
                logger.warning(f"Erreur lors de la reconnaissance Vosk: {e}")

        logger.debug("Boucle de reconnaissance arretee")

    def _handle_result(self, result: dict, is_final: bool) -> None:
        """Traite un resultat de reconnaissance Vosk."""
        text = ""
        if is_final:
            text = result.get("text", "")
        else:
            text = result.get("partial", "")

        if not text:
            return

        normalized = text.lower().strip()
        logger.debug(f"Texte reconnu ({'final' if is_final else 'partiel'}): {normalized}")

        words = normalized.split()
        if self.WAKE_WORD in words:
            logger.info(f"Mot-cle '{self.WAKE_WORD}' detecte!")
            if self._on_detect is not None:
                try:
                    self._on_detect()
                except Exception as e:
                    logger.error(f"Erreur dans on_detect callback: {e}")
