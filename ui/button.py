import pygame

class Button:
    def __init__(self, pos, image, on_click=None, hint=""):
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.on_click = on_click
        self.hint = hint
        self.enabled = True

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False
