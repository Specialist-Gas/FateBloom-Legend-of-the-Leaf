import pygame

class Assets:
    def __init__(self):
        self.images = {}
        self.fonts  = {}

    def load(self):
        # Only spells UI + spell icon
        self.images["btn_spell"] = self._rect_icon((120, 120, 180))  # tab button
        self.images["spark"]     = self._rect_icon((120, 120, 200))  # spell icon

        self.fonts["ui"] = pygame.font.SysFont("consolas", 18)

    def _rect_icon(self, color, w=40, h=40):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(color)
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
        return surf
