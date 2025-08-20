import pygame
from core import settings as S

class Window:
    def __init__(self, name):
        self.name = name
        self.rect = pygame.Rect(S.PANEL_RECT)  # right sidebar area (bottom half)
        self.children = []

    def draw_bg(self, surf):
        pygame.draw.rect(surf, S.DARK, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)

    def draw(self, surf):
        self.draw_bg(surf)
        for c in self.children:
            if hasattr(c, "draw"):
                c.draw(surf)

    def handle_event(self, event):
        for c in self.children:
            if hasattr(c, "handle_event") and c.handle_event(event):
                return True
        return False
