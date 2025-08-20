from ui.window import Window
from ui.button import Button

class InventoryWindow(Window):
    def __init__(self, game):
        super().__init__("inventory")
        A = game.assets
        # Place a few example item buttons inside the panel
        ox, oy, _, _ = self.rect

