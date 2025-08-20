# world/projectile.py
import pygame
import math

class Projectile:
    def __init__(self, start_xy, target_xy, speed=700, radius=4, damage=25, color=(170, 120, 255), max_dist=1200):
        self.pos = pygame.Vector2(start_xy)
        to = pygame.Vector2(target_xy) - self.pos
        if to.length_squared() == 0:
            to = pygame.Vector2(1, 0)
        self.dir = to.normalize()
        self.speed = float(speed)
        self.radius = int(radius)
        self.damage = int(damage)
        self.color = color
        self.traveled = 0.0
        self.max_dist = float(max_dist)

        # a small rect for cheap collision with enemy.rect
        d = self.radius * 2
        self.rect = pygame.Rect(0, 0, d, d)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self, dt):
        step = self.dir * self.speed * dt
        self.pos += step
        self.traveled += step.length()
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def alive(self):
        return self.traveled <= self.max_dist

    def draw_on_layer(self, layer, cam_rect):
        # draw as a filled circle in screen space (layer coordinates)
        sx = int(self.pos.x - cam_rect.x)
        sy = int(self.pos.y - cam_rect.y)
        pygame.draw.circle(layer, self.color, (sx, sy), self.radius)
        # optional: a tiny outline
        pygame.draw.circle(layer, (40, 20, 60), (sx, sy), self.radius, 2)
