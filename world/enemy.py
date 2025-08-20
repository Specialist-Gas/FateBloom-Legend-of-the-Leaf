# world/enemy.py
import pygame
from core import settings as S

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, size=22, hp=100):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.hp = int(hp)
        self.player = player

        # simple red box
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill((200, 60, 60))
        pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 2)
        self.rect = self.image.get_rect(center=(round(x), round(y)))

        # AI / combat
        self.speed = float(S.ENEMY_SPEED)
        self.detect_radius = float(S.ENEMY_DETECT_RADIUS)
        self.attack_range = float(S.ENEMY_ATTACK_RANGE)
        self.attack_cooldown = float(S.ENEMY_ATTACK_COOLDOWN)
        self._atk_cd = 0.0

    def damage(self, amount: int) -> bool:
        self.hp -= int(amount)
        return self.hp <= 0

    def update(self, dt: float):
        # cooldown tick
        if self._atk_cd > 0.0:
            self._atk_cd = max(0.0, self._atk_cd - dt)

        # chase player if within detection radius
        to_p = self.player.pos - self.pos
        dist2 = to_p.length_squared()
        if dist2 > 1e-6 and dist2 <= (self.detect_radius * self.detect_radius):
            dir_vec = to_p.normalize()
            self.pos += dir_vec * self.speed * dt

        # sync rect
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # ---- DAMAGE PHASE (respect God Mode) ----
        if self.player.dead:
            return

        # Don’t deal damage if player is invulnerable via God Mode
        if getattr(self.player, "god_mode", False):
            return

        close = (to_p.length() <= self.attack_range) or self.rect.colliderect(self.player.rect)
        if close and self._atk_cd <= 0.0:
            # Only ever damage through the Player API
            self.player.take_damage(S.ENEMY_ATTACK_DAMAGE)
            self._atk_cd = self.attack_cooldown
