import pygame

class Camera:
    def __init__(self, viewport_rect, world_size, zoom=2.0, lerp=0.15):
        self.viewport = pygame.Rect(viewport_rect)         # screen area to draw into
        self.world_w, self.world_h = world_size
        self.zoom = float(zoom)
        self.lerp = float(lerp)
        self.pos = None            # world center
        self.target = None         # sprite with .rect.center

    def set_target(self, sprite):
        self.target = sprite
        if self.pos is None:
            self.pos = pygame.Vector2(sprite.rect.center)

    def set_zoom(self, zoom):
        self.zoom = max(0.5, float(zoom))

    def update(self, dt):
        if not self.target:
            return
        desired = pygame.Vector2(self.target.rect.center)
        if self.pos is None:
            self.pos = desired
        # framerate-independent smoothing (convert lerp to per-frame alpha)
        alpha = 1 - (1 - self.lerp) ** (dt * 60.0)
        self.pos += (desired - self.pos) * alpha
        self._clamp()

    def _clamp(self):
        half_w = (self.viewport.w / self.zoom) / 2
        half_h = (self.viewport.h / self.zoom) / 2
        self.pos.x = max(half_w, min(self.world_w - half_w, self.pos.x))
        self.pos.y = max(half_h, min(self.world_h - half_h, self.pos.y))

    def view_rect(self):
        w = int(self.viewport.w / self.zoom)
        h = int(self.viewport.h / self.zoom)
        left = int(self.pos.x - w // 2)
        top  = int(self.pos.y - h // 2)
        return pygame.Rect(left, top, w, h)
