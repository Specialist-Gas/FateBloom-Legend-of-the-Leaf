import pygame
from typing import Dict, Optional
from core import settings as S

class AudioManager:
    """Centralized audio controller for music + SFX."""
    def __init__(self):
        # Safe init (don’t crash if device missing)
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except Exception:
            pass

        self._sfx: Dict[str, pygame.mixer.Sound] = {}
        self._music_path: Optional[str] = None
        self._music_volume = getattr(S, "MUSIC_VOLUME", 0.6)
        self._fade_ms = getattr(S, "MUSIC_FADE_MS", 600)
        self._enabled = getattr(S, "MUSIC_ENABLED", True)
        self._muted = False

        # Optional: reserve a channel for UI sounds (clicks, popups, etc.)
        try:
            pygame.mixer.set_num_channels(max(8, pygame.mixer.get_num_channels()))
            self.ui_channel = pygame.mixer.Channel(1)
        except Exception:
            self.ui_channel = None

    # ---------- Music ----------
    def play_music(self, path: Optional[str] = None, *, loop=True, fade_ms: Optional[int] = None):
        if not self._enabled or not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.stop()
            if path is None:
                path = self._music_path
            else:
                self._music_path = path
            if not path:
                return
            pygame.mixer.music.load(path)
            vol = 0.0 if self._muted else self._music_volume
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms if fade_ms is not None else self._fade_ms)
        except Exception:
            # Silent fail for prototype
            pass

    def set_music(self, path: str):
        """Just set the track without starting."""
        self._music_path = path

    def pause_music(self):
        if pygame.mixer.get_init():
            try: pygame.mixer.music.pause()
            except Exception: pass

    def resume_music(self):
        if pygame.mixer.get_init():
            try: pygame.mixer.music.unpause()
            except Exception: pass

    def fadeout_music(self, ms: Optional[int] = None):
        if pygame.mixer.get_init():
            try: pygame.mixer.music.fadeout(ms if ms is not None else self._fade_ms)
            except Exception: pass

    def music_volume(self, volume: float):
        """0..1"""
        self._music_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.get_init():
            try: pygame.mixer.music.set_volume(0.0 if self._muted else self._music_volume)
            except Exception: pass

    def mute(self, muted: bool):
        self._muted = muted
        if pygame.mixer.get_init():
            try: pygame.mixer.music.set_volume(0.0 if muted else self._music_volume)
            except Exception: pass

    # ---------- SFX ----------
    def register_sfx(self, key: str, path: str, volume: float = 1.0):
        """Load and register a sound by key."""
        if not pygame.mixer.get_init():
            return
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(max(0.0, min(1.0, volume)))
            self._sfx[key] = snd
        except Exception:
            pass

    def play_sfx(self, key: str, *, channel: Optional[int] = None):
        """Play a registered sound once."""
        if not pygame.mixer.get_init():
            return
        snd = self._sfx.get(key)
        if not snd:
            return
        try:
            if channel is None:
                snd.play()
            elif channel == "ui" and self.ui_channel is not None:
                self.ui_channel.play(snd)
            else:
                pygame.mixer.Channel(int(channel)).play(snd)
        except Exception:
            pass
