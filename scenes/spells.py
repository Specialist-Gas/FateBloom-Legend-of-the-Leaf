# scenes/spells.py
from ui.window import Window
from ui.button import Button

class SpellsWindow(Window):
    def __init__(self, game):
        super().__init__("spells")
        self.game = game
        A = game.assets
        ox, oy, _, _ = self.rect

        self.spark_btn = Button((ox + 20, oy + 60), A.images["spark"], on_click=self.select_spark, hint="Spark")
        self.children += [self.spark_btn]

    def select_spark(self):
        # Set the currently selected spell on the Game
        self.game.selected_spell = "spark"
        self.game.log("Spark selected")

    def draw(self, surf):
        super().draw(surf)
        # simple selection outline
        if getattr(self.game, "selected_spell", None) == "spark":
            r = self.spark_btn.rect.inflate(6, 6)
            import pygame
            pygame.draw.rect(surf, (255, 255, 120), r, 2)
