class BaseScene:
    def __init__(self, game):
        self.game = game  # access assets, screen, etc.

    def enter(self): pass
    def exit(self): pass

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, screen): pass
