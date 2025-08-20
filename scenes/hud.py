from ui.button import Button
from core import settings as S

class HUD:
    def __init__(self, game):
        self.game = game
        A = game.assets
        px, py, pw, ph = S.PANEL_RECT

        x = px + 12
        y = py + 12
        self.tab_buttons = [
            Button((x, y), A.images["btn_spell"], lambda: game.set_window("spells"), "Spells"),
        ]

    def draw(self, screen):
        for b in self.tab_buttons:
            b.draw(screen)

    def handle_event(self, event):
        for b in self.tab_buttons:
            if b.handle_event(event):
                return True
        return False
