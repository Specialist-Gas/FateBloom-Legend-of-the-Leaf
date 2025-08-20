# scenes/debug_menu.py
import pygame
from core import settings as S

class DebugMenu:
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(0, 0, S.DEBUG_MENU_WIDTH, S.HEIGHT)
        self.font = self.game.assets.fonts["ui"]
        pad = 16
        y0 = 70
        h  = 32
        gap = 12

        # Keep original items and add a new one directly under it
        self.item_rects = {
            "god_mode":   pygame.Rect(pad, y0, self.rect.w - pad*2, h),
            "kill_all":   pygame.Rect(pad, y0 + h + gap, self.rect.w - pad*2, h),
        }

    def draw(self, screen):
        panel = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        panel.fill((20, 20, 24, S.DEBUG_MENU_ALPHA))
        pygame.draw.rect(panel, (0, 0, 0), panel.get_rect(), 2)

        title = self.font.render("DEBUG", True, (230, 230, 230))
        panel.blit(title, (16, 20))

        # --- God Mode toggle (unchanged styling) ---
        gm = "ON" if getattr(self.game.world.player, "god_mode", False) else "OFF"
        r = self.item_rects["god_mode"]
        pygame.draw.rect(panel, (50, 50, 60), r, border_radius=6)
        pygame.draw.rect(panel, (0, 0, 0), r, 1, border_radius=6)
        panel.blit(self.font.render(f"God Mode: {gm}", True, (220, 220, 180)), (r.x + 10, r.y + 6))

        # --- Kill All Enemies button (matches the look) ---
        rk = self.item_rects["kill_all"]
        pygame.draw.rect(panel, (50, 50, 60), rk, border_radius=6)
        pygame.draw.rect(panel, (0, 0, 0), rk, 1, border_radius=6)
        panel.blit(self.font.render("Kill all enemies", True, (220, 220, 180)), (rk.x + 10, rk.y + 6))

        panel.blit(self.font.render("~ to close", True, (170, 170, 170)), (16, self.rect.h - 28))
        screen.blit(panel, (0, 0))

    def _kill_all_enemies(self):
        """Clear all enemies robustly, regardless of Group vs list implementation."""
        world = self.game.world
        enemies = getattr(world, "enemy_sprites", None)
        if enemies is None:
            enemies = getattr(world, "enemies", None)

        if enemies is None:
            # Nothing to do; keep behavior silent but log for clarity
            self.game.log("Debug: No enemies container found")
            return

        # pygame.sprite.Group-like
        if hasattr(enemies, "sprites"):
            try:
                for e in list(enemies):
                    try:
                        if hasattr(e, "kill"):
                            e.kill()
                    except Exception:
                        pass
                if hasattr(enemies, "empty"):
                    enemies.empty()
            except Exception:
                pass
        else:
            # list-like
            try:
                for e in list(enemies):
                    try:
                        if hasattr(e, "kill"):
                            e.kill()
                    except Exception:
                        pass
                if hasattr(enemies, "clear"):
                    enemies.clear()
                else:
                    while enemies:
                        enemies.pop()
            except Exception:
                pass

        if hasattr(self.game, "log"):
            self.game.log("Debug: Killed all enemies")

    def handle_event(self, event):
        # Clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toggle God Mode
            if self.item_rects["god_mode"].collidepoint(event.pos):
                p = self.game.world.player
                p.god_mode = not getattr(p, "god_mode", False)
                if p.god_mode:
                    p.hp = p.max_hp  # heal on enable so you don't insta-die after closing
                self.game.log(f"God Mode {'ON' if p.god_mode else 'OFF'}")
                return True

            # Kill all enemies
            if self.item_rects["kill_all"].collidepoint(event.pos):
                self._kill_all_enemies()
                return True

        # Optional keyboard toggle inside menu (kept from your original)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            p = self.game.world.player
            p.god_mode = not getattr(p, "god_mode", False)
            if p.god_mode:
                p.hp = p.max_hp
            self.game.log(f"God Mode {'ON' if p.god_mode else 'OFF'}")
            return True

        return False
