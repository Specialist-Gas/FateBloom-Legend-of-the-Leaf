# scenes/pause_menu.py
import pygame
from core import settings as S

class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.font = self.game.assets.fonts["ui"]
        self.big  = pygame.font.SysFont("consolas", 42)

        # Main "Quit" button (centered under the PAUSED title)
        bw, bh = 220, 42
        cx, cy = S.WIDTH // 2, S.HEIGHT // 2 + 30
        self.quit_btn = pygame.Rect(0, 0, bw, bh)
        self.quit_btn.center = (cx, cy)

        # Modal confirm ("Quit to Desktop?")
        mw, mh = 420, 180
        self.modal_rect = pygame.Rect(0, 0, mw, mh)
        self.modal_rect.center = (S.WIDTH // 2, S.HEIGHT // 2)

        # Yes / No buttons inside modal
        mbw, mbh = 120, 36
        pad = 20
        y_btn = self.modal_rect.centery + 34
        self.yes_btn = pygame.Rect(0, 0, mbw, mbh)
        self.no_btn  = pygame.Rect(0, 0, mbw, mbh)
        self.yes_btn.center = (self.modal_rect.centerx - (mbw//2 + pad), y_btn)
        self.no_btn.center  = (self.modal_rect.centerx + (mbw//2 + pad), y_btn)

        # State
        self.confirm_open = False
        self.quit_confirmed = False

    def reset(self):
        self.confirm_open = False
        self.quit_confirmed = False

    def handle_event(self, event) -> bool:
        """Return True if the menu consumed the event."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.confirm_open:
                if self.yes_btn.collidepoint(mx, my):
                    self.quit_confirmed = True
                    return True
                if self.no_btn.collidepoint(mx, my):
                    self.confirm_open = False
                    return True
                # clicks elsewhere on modal layer do nothing
                return True
            else:
                if self.quit_btn.collidepoint(mx, my):
                    self.confirm_open = True
                    return True
                return True  # swallow clicks while paused

        if event.type == pygame.KEYDOWN:
            if self.confirm_open:
                if event.key in (pygame.K_y, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.quit_confirmed = True
                    return True
                if event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.confirm_open = False
                    return True
            return True  # swallow other keys while paused

    def draw(self, screen):
        # Dim world
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Title
        t1 = self.big.render("PAUSED", True, (220, 240, 255))
        screen.blit(t1, (S.WIDTH//2 - t1.get_width()//2, S.HEIGHT//2 - 80))

        # Quit button
        pygame.draw.rect(screen, (50, 50, 60), self.quit_btn, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.quit_btn, 2, border_radius=8)
        qtxt = self.font.render("Quit", True, (230, 230, 230))
        screen.blit(qtxt, (self.quit_btn.centerx - qtxt.get_width()//2,
                           self.quit_btn.centery - qtxt.get_height()//2))

        # Modal confirm
        if self.confirm_open:
            modal = pygame.Surface(self.modal_rect.size, pygame.SRCALPHA)
            modal.fill((24, 24, 28, 235))
            pygame.draw.rect(modal, (0, 0, 0), modal.get_rect(), 2)

            prompt = self.font.render("Quit to Desktop?", True, (235, 235, 235))
            modal.blit(prompt, (modal.get_width()//2 - prompt.get_width()//2, 28))

            # buttons
            # compute local-space rects for blitting
            y_local = self.yes_btn.y - self.modal_rect.y
            x_yes_local = self.yes_btn.x - self.modal_rect.x
            x_no_local  = self.no_btn.x - self.modal_rect.x

            yes_r = pygame.Rect(x_yes_local, y_local, self.yes_btn.w, self.yes_btn.h)
            no_r  = pygame.Rect(x_no_local,  y_local, self.no_btn.w,  self.no_btn.h)

            pygame.draw.rect(modal, (60, 60, 72), yes_r, border_radius=6)
            pygame.draw.rect(modal, (0, 0, 0),   yes_r, 1, border_radius=6)
            pygame.draw.rect(modal, (60, 60, 72), no_r,  border_radius=6)
            pygame.draw.rect(modal, (0, 0, 0),   no_r,  1, border_radius=6)

            ytxt = self.font.render("Yes", True, (230, 230, 230))
            ntxt = self.font.render("No",  True, (230, 230, 230))
            modal.blit(ytxt, (yes_r.centerx - ytxt.get_width()//2, yes_r.centery - ytxt.get_height()//2))
            modal.blit(ntxt, (no_r.centerx - ntxt.get_width()//2,  no_r.centery - ntxt.get_height()//2))

            screen.blit(modal, self.modal_rect.topleft)
