import sys
import time
import pygame

try:
    import settings as S
except Exception:
    class S:
        WIDTH, HEIGHT = 1280, 720
        FPS = 60
        TITLE = "Floral Foundations"
        WORLD_RECT = (0, 0, 960, 720)
        PANEL_RECT = (960, 0, 320, 720)
        STATE_PLAYING   = "PLAYING"
        STATE_PAUSED    = "PAUSED"
        STATE_GAME_OVER = "GAME_OVER"
        STATE_WIN       = "WIN"
        BLACK = (0, 0, 0)
        # Audio fallbacks
        MUSIC_ENABLED     = True
        MUSIC_VOLUME      = 0.60
        MUSIC_FADE_MS     = 600
        MUSIC_PATH_LEVEL1 = "music/test_level.mp3"
        SFX_FILES         = {}

# ----- imports you already have -----
try:
    from scenes.hud import HUD
    from scenes.spells import SpellsWindow
    from scenes.radar import Radar
    from scenes.debug_menu import DebugMenu
    from scenes.pause_menu import PauseMenu
    from world.test_level import TestLevel
    from .assets import Assets
except Exception:
    HUD = type("HUD", (), {"__init__": lambda self, g: None, "draw": lambda self, s: None, "handle_event": lambda self, e: False})
    SpellsWindow = type("SpellsWindow", (), {"__init__": lambda self, g: None, "draw": lambda self, s: None, "handle_event": lambda self, e: False})
    Radar = type("Radar", (), {"__init__": lambda self, g: None, "draw": lambda self, s: None})
    DebugMenu = type("DebugMenu", (), {"__init__": lambda self, g: None, "draw": lambda self, s: None, "handle_event": lambda self, e: None})
    PauseMenu = type("PauseMenu", (), {
        "__init__": lambda self, g: setattr(self, "confirm_open", False) or setattr(self, "quit_confirmed", False),
        "reset": lambda self: (setattr(self, "confirm_open", False), setattr(self, "quit_confirmed", False)),
        "handle_event": lambda self, e: None,
        "draw": lambda self, s: None,
    })
    class _DummyWorld:
        def __init__(self, game):
            self.player = type("P", (), {"hp": 10, "max_hp": 10, "dead": False})()
            self.enemy_sprites = [object(), object(), object()]
        def handle_event(self, e): pass
        def handle_world_click(self, pos, spell):
            if self.enemy_sprites: self.enemy_sprites.pop()
        def update(self, dt): pass
        def draw(self, screen): screen.fill((28, 30, 34))
        def reset_world(self): self.__init__(None)
    TestLevel = _DummyWorld
    class Assets:
        def __init__(self):
            self.images = {"btn_spell": object(), "spark": object()}
            self.fonts = {"ui": pygame.font.SysFont("consolas", 18)}
        def load(self): pass

# NEW: central audio manager
from core.audio import AudioManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(0)
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(getattr(S, "TITLE", "Game"))

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.win = False
        self.paused = False

        # Assets
        self.assets = Assets()
        self.assets.load()
        required = {"btn_spell", "spark"}
        missing = required - set(getattr(self.assets, "images", {}).keys())
        if missing:
            raise RuntimeError(f"Missing asset keys: {sorted(missing)}")

        # World & UI
        self.world = TestLevel(self)
        self.radar = Radar(self)
        self.hud = HUD(self)
        self.windows = {"spells": SpellsWindow(self)}
        self.active_window = self.windows["spells"]

        # Debug menu
        self.debug_menu_open = False
        self.debug_menu = DebugMenu(self)
        self._menu_toggle_cooldown = 0.18
        self._menu_toggle_timer = 0.0

        # Pause menu
        self.pause_menu = PauseMenu(self)

        # Misc
        self.selected_spell = None
        self.msg = ""
        self.font = getattr(self.assets, "fonts", {}).get("ui") or pygame.font.SysFont("consolas", 18)

        # Win overlay clickable buttons
        self._win_buttons = {}
        self._win_awaiting_confirm = False

        # ---- AudioManager setup ----
        self.audio = AudioManager()
        # Pre-register SFX from settings if you have any listed
        for key, path in getattr(S, "SFX_FILES", {}).items():
            self.audio.register_sfx(key, path)
        # Set + start level BGM
        self.audio.set_music(getattr(S, "MUSIC_PATH_LEVEL1", None))
        self.audio.play_music()

    # ---------------- Utilities ----------------
    def set_window(self, name: str):
        if name in self.windows:
            self.active_window = self.windows[name]

    def log(self, text: str):
        self.msg = text
        print(text)

    def _is_backquote(self, event: pygame.event.Event) -> bool:
        return (
            getattr(pygame, "K_BACKQUOTE", None) is not None and event.key == pygame.K_BACKQUOTE
        ) or (hasattr(event, "unicode") and event.unicode in ("`", "~"))

    def _draw_hp_bar(self):
        vx, vy, vw, _ = S.WORLD_RECT
        pct = getattr(self.world.player, "hp", 1) / max(1, getattr(self.world.player, "max_hp", 1))
        w, h = 180, 16
        x, y = vx + 12, vy + 12
        back = pygame.Rect(x, y, w, h)
        fill = pygame.Rect(x, y, int(w * pct), h)
        pygame.draw.rect(self.screen, (40, 0, 0), back, border_radius=4)
        pygame.draw.rect(self.screen, (200, 40, 40), fill, border_radius=4)
        pygame.draw.rect(self.screen, (0, 0, 0), back, 2, border_radius=4)
        txt = self.font.render(f"HP {getattr(self.world.player,'hp',0)}/{getattr(self.world.player,'max_hp',0)}", True, (255, 255, 255))
        self.screen.blit(txt, (x + 6, y - 18))

    # ---------------- Overlays ----------------
    def _draw_game_over(self):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        big = pygame.font.SysFont("consolas", 42)
        t1 = big.render("GAME OVER", True, (255, 220, 220))
        t2 = self.font.render("Press Esc to quit", True, (220, 220, 220))
        self.screen.blit(t1, (S.WIDTH // 2 - t1.get_width() // 2, S.HEIGHT // 2 - 40))
        self.screen.blit(t2, (S.WIDTH // 2 - t2.get_width() // 2, S.HEIGHT // 2 + 10))

    def _draw_win(self):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        w, h = 520, 300
        panel = pygame.Rect((S.WIDTH - w)//2, (S.HEIGHT - h)//2, w, h)
        pygame.draw.rect(self.screen, (18, 18, 20), panel, border_radius=16)
        pygame.draw.rect(self.screen, (80, 80, 90), panel, 2, border_radius=16)

        big = pygame.font.SysFont("consolas", 42)
        t1 = big.render("YOU WIN!", True, (220, 255, 220))
        t2 = self.font.render("All enemies defeated", True, (220, 220, 220))
        self.screen.blit(t1, (panel.centerx - t1.get_width()//2, panel.y + 34))
        self.screen.blit(t2, (panel.centerx - t2.get_width()//2, panel.y + 92))

        btn_w, btn_h, gap = 190, 54, 24
        y = panel.y + h - 90
        total = btn_w * 2 + gap
        x = panel.centerx - total // 2
        play_rect = pygame.Rect(x, y, btn_w, btn_h)
        quit_rect = pygame.Rect(x + btn_w + gap, y, btn_w, btn_h)

        self._win_buttons = {"Play Again": play_rect, "Quit": quit_rect}
        for rect, label in [(play_rect, "Play Again"), (quit_rect, "Quit")]:
            pygame.draw.rect(self.screen, (36, 36, 42), rect, border_radius=10)
            pygame.draw.rect(self.screen, (110, 110, 120), rect, 2, border_radius=10)
            t = self.font.render(label, True, (235, 235, 245))
            self.screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

        if self._win_awaiting_confirm or getattr(self.pause_menu, "confirm_open", False):
            self.pause_menu.confirm_open = True
            self.pause_menu.draw(self.screen)

    # ---------------- Restart ----------------
    def _restart(self):
        if hasattr(self.world, "reset_world"):
            self.world.reset_world()
        else:
            self.world = TestLevel(self)
        self.selected_spell = None
        self.game_over = False
        self.win = False
        self.paused = False
        self.msg = ""
        if hasattr(self.pause_menu, "reset"):
            self.pause_menu.reset()
        self.debug_menu_open = False
        self._win_buttons = {}
        self._win_awaiting_confirm = False

        # Restart level music
        self.audio.set_music(getattr(S, "MUSIC_PATH_LEVEL1", None))
        self.audio.play_music()

    # ---------------- Main Loop ----------------
    def run(self):
        FIXED_UPS = 120
        FIXED_DT = 1.0 / FIXED_UPS
        MAX_FRAME = 0.25

        prev = time.perf_counter()
        accum = 0.0

        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])

        while self.running:
            now = time.perf_counter()
            frame = now - prev
            prev = now
            if frame > MAX_FRAME:
                frame = MAX_FRAME
            accum += frame

            if self._menu_toggle_timer > 0.0:
                self._menu_toggle_timer = max(0.0, self._menu_toggle_timer - frame)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    # Toggle debug
                    if self._is_backquote(event) and self._menu_toggle_timer == 0.0 and not (self.game_over or self.win):
                        self.debug_menu_open = not self.debug_menu_open
                        self._menu_toggle_timer = self._menu_toggle_cooldown
                        self.log("Debug menu " + ("OPEN" if self.debug_menu_open else "CLOSED"))
                        continue

                    # Pause/Resume
                    if event.key == pygame.K_ESCAPE and not (self.game_over or self.win) and not self.debug_menu_open:
                        if self.paused:
                            if getattr(self.pause_menu, "confirm_open", False):
                                self.pause_menu.confirm_open = False
                            else:
                                self.paused = False
                                self.audio.resume_music()
                        else:
                            self.paused = True
                            if hasattr(self.pause_menu, "reset"):
                                self.pause_menu.reset()
                            self.audio.pause_music()
                        continue

                    # Game Over → only Esc to quit
                    if self.game_over:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        continue

                    # Win state
                    if self.win:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self._restart()
                        elif event.key == pygame.K_ESCAPE:
                            self._win_awaiting_confirm = True
                            if hasattr(self.pause_menu, "reset"):
                                self.pause_menu.reset()
                            self.pause_menu.confirm_open = True
                        continue

                    # Normal flow
                    if self.paused:
                        self.pause_menu.handle_event(event)
                    elif self.debug_menu_open:
                        self.debug_menu.handle_event(event)
                    else:
                        self.world.handle_event(event)

                elif event.type == pygame.KEYUP:
                    if not (self.game_over or self.win or self.debug_menu_open or self.paused):
                        self.world.handle_event(event)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_over:
                        pass
                    elif self.win:
                        if self._win_buttons:
                            pos = event.pos
                            play = self._win_buttons.get("Play Again")
                            quitb = self._win_buttons.get("Quit")
                            if play and play.collidepoint(pos):
                                self._restart(); continue
                            if quitb and quitb.collidepoint(pos):
                                self._win_awaiting_confirm = True
                                if hasattr(self.pause_menu, "reset"): self.pause_menu.reset()
                                self.pause_menu.confirm_open = True
                                continue
                        if getattr(self.pause_menu, "confirm_open", False):
                            self.pause_menu.handle_event(event); continue
                    elif self.debug_menu_open:
                        self.debug_menu.handle_event(event)
                    elif self.paused:
                        self.pause_menu.handle_event(event)
                    else:
                        if self.hud.handle_event(event) or self.active_window.handle_event(event):
                            pass
                        else:
                            if pygame.Rect(S.WORLD_RECT).collidepoint(event.pos):
                                self.world.handle_world_click(event.pos, self.selected_spell)

            # Quit confirmed (Pause or Win confirm)
            if (self.paused or self.win) and getattr(self.pause_menu, "quit_confirmed", False):
                self.running = False

            # Fixed updates (play only)
            while not (self.game_over or self.win or self.debug_menu_open or self.paused) and accum >= (1.0 / 120):
                self.world.update(1.0 / 120)
                accum -= (1.0 / 120)

            # Transitions
            if getattr(self.world.player, "dead", False) and not self.game_over:
                self.game_over = True
                self.audio.fadeout_music()
            if not self.win and not getattr(self.world, "enemy_sprites", []):
                self.win = True
                self.audio.fadeout_music()

            # Render
            self.screen.fill(S.BLACK)
            self.world.draw(self.screen)

            divider_x = S.WORLD_RECT[2]
            pygame.draw.line(self.screen, (50, 50, 50), (divider_x, 0), (divider_x, S.HEIGHT), 2)
            px, py, pw, ph = S.PANEL_RECT
            pygame.draw.line(self.screen, (50, 50, 50), (px, py + ph), (px + pw, py + ph), 2)

            self.radar.draw(self.screen)
            self.active_window.draw(self.screen)
            self.hud.draw(self.screen)
            self._draw_hp_bar()

            if self.msg:
                self.screen.blit(self.font.render(self.msg, True, (255, 255, 0)), (20, S.HEIGHT - 26))

            if self.game_over: self._draw_game_over()
            if self.win:       self._draw_win()
            if self.debug_menu_open: self.debug_menu.draw(self.screen)
            if self.paused and not (self.game_over or self.win): self.pause_menu.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(S.FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
