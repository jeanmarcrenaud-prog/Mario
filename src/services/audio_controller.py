"""audio_controller
====================
This module provides a small, well‑typed wrapper around :mod:`pyaudio`.  
The original implementation was functional but had a few issues that made it
impractical for long‑running applications:

* The :class:`AudioController` instance terminated the underlying
  :class:`pyaudio.PyAudio` object in :meth:`get_default_microphone` and
  :meth:`get_all_audio_devices`.  This meant that subsequent calls would
  raise ``AttributeError`` because the internal ``_pa`` attribute was
  ``None``.
* The API was missing a clean shutdown method and a few convenience
  helpers that are useful when working with audio devices.
* Type hints and docstrings were sparse, making it harder for static
  analysers and IDEs to provide useful feedback.

The updated implementation addresses these problems while keeping the public
surface area small and easy to use.

Typical usage::

    from audio_controller import AudioController

    ac = AudioController()
    print("Microphones:", ac.get_microphones())
    print("Default mic:", ac.get_default_microphone())
    print("All devices:", ac.get_all_audio_devices())
    ac.close()  # Clean up when finished

The class is intentionally lightweight – it does not open any streams – so
it can be instantiated in a background thread or a GUI event loop
without blocking.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pyaudio

__all__ = ["AudioController", "AudioDeviceInfo"]


@dataclass(frozen=True)
class AudioDeviceInfo:
    """A lightweight representation of a PyAudio device.

    The dataclass is *frozen* to make instances hashable and immutable.
    It mirrors the dictionary returned by :meth:`pyaudio.PyAudio.get_device_info_by_index`.
    """

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    host_api: int
    is_default_input: bool = False
    is_default_output: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "AudioDeviceInfo":
        return cls(
            index=data["index"],
            name=data["name"],
            max_input_channels=data["maxInputChannels"],
            max_output_channels=data["maxOutputChannels"],
            default_sample_rate=data["defaultSampleRate"],
            host_api=data["hostApi"],
            is_default_input=data.get("defaultInput", False),
            is_default_output=data.get("defaultOutput", False),
        )


class AudioController:
    """Thin wrapper around :class:`pyaudio.PyAudio`."""

    def __init__(self) -> None:
        self._pa: pyaudio.PyAudio = pyaudio.PyAudio()
        self._device_cache: Optional[List[AudioDeviceInfo]] = None

    # ------------------------------------------------------------------
    # Device enumeration helpers
    # ------------------------------------------------------------------
    def _refresh_cache(self) -> None:
        """Populate :attr:`_device_cache` with the current device list."""
        device_count = self._pa.get_device_count()
        devices = [
            AudioDeviceInfo.from_dict(self._pa.get_device_info_by_index(i))
            for i in range(device_count)
        ]
        self._device_cache = devices

    def get_all_audio_devices(self) -> List[AudioDeviceInfo]:
        """Return a list of :class:`AudioDeviceInfo` for every device."""
        self._refresh_cache()
        assert self._device_cache is not None
        return list(self._device_cache)

    def get_microphones(self) -> List[AudioDeviceInfo]:
        """Return all devices that support input channels."""
        return [d for d in self.get_all_audio_devices() if d.max_input_channels > 0]

    def get_output_devices(self) -> List[AudioDeviceInfo]:
        """Return all devices that support output channels."""
        return [d for d in self.get_all_audio_devices() if d.max_output_channels > 0]

    # ------------------------------------------------------------------
    # Default device helpers
    # ------------------------------------------------------------------
    def get_default_microphone(self) -> Optional[AudioDeviceInfo]:
        """Return the default input device or ``None`` if unavailable."""
        try:
            info = self._pa.get_default_input_device_info()
        except OSError:
            return None
        return AudioDeviceInfo.from_dict(info)

    def get_default_output_device_info(self) -> Optional[AudioDeviceInfo]:
        """Return the default output device or ``None`` if unavailable."""
        try:
            info = self._pa.get_default_output_device_info()
        except OSError:
            return None
        return AudioDeviceInfo.from_dict(info)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get_device_info(self, index: int) -> AudioDeviceInfo:
        """Return :class:`AudioDeviceInfo` for the given *index*."""
        try:
            info = self._pa.get_device_info_by_index(index)
        except IOError as exc:  # PyAudio uses IOError for out‑of‑range
            raise IndexError(f"Device index {index} out of range") from exc
        return AudioDeviceInfo.from_dict(info)

    def get_device_count(self) -> int:
        """Return the number of devices reported by PyAudio."""
        return self._pa.get_device_count()

    def get_microphone_names(self) -> List[str]:
        """Return a list of names of all input devices."""
        return [d.name for d in self.get_microphones()]

    def get_output_device_names(self) -> List[str]:
        """Return a list of names of all output devices."""
        return [d.name for d in self.get_output_devices()]

    def get_all_device_names(self) -> List[str]:
        """Return a list of names of all devices."""
        return [d.name for d in self.get_all_audio_devices()]
    
    def get_default_speaker(self) -> Optional[AudioDeviceInfo]:
        """Compatibility alias for :meth:`get_default_output_device_info`."""
        return self.get_default_output_device_info()

    
    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Terminate the underlying :class:`pyaudio.PyAudio` instance."""
        if self._pa is not None:
            try:
                self._pa.terminate()
            finally:
                self._pa = None  # type: ignore[assignment]

    # Context manager support
    def __enter__(self) -> "AudioController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()
