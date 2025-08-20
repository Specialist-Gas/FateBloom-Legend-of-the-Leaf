# world/test_level.py
import math
from pathlib import Path
import random
import pygame

from core import settings as S
from world.player import Player
from world.camera import Camera
from world.enemy import Enemy
from world.projectile import Projectile

def _slice_tile(tileset: pygame.Surface, tile_size: int, col: int, row: int) -> pygame.Surface:
    x = col * tile_size; y = row * tile_size
    rect = pygame.Rect(x, y, tile_size, tile_size)
    tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    tile.blit(tileset, (0, 0), rect)
    return tile

def _load_ground_tile() -> pygame.Surface:
    path = Path(S.TILESET_PATH)
    try:
        tileset = pygame.image.load(str(path)).convert()
    except Exception:
        t = pygame.Surface((S.TILE_SIZE, S.TILE_SIZE)).convert()
        t.fill((78, 161, 72)); pygame.draw.rect(t, (72, 149, 66), t.get_rect(), 3)
        return t

    ts_w, ts_h = tileset.get_size()
    T = S.TILE_SIZE
    if ts_w == T and ts_h == T:
        return tileset.copy()
    col, row = S.GROUND_TILE_COORDS
    x, y = col * T, row * T
    if (x + T) <= ts_w and (y + T) <= ts_h:
        return _slice_tile(tileset, T, col, row).convert()
    t = pygame.Surface((T, T)).convert()
    t.fill((78, 161, 72)); pygame.draw.rect(t, (72, 149, 66), t.get_rect(), 3)
    return t

def _build_tiled_surface(tile: pygame.Surface, width: int, height: int) -> pygame.Surface:
    cols = math.ceil(width / tile.get_width())
    rows = math.ceil(height / tile.get_height())
    surf = pygame.Surface((width, height)).convert()
    for r in range(rows):
        for c in range(cols):
            surf.blit(tile, (c * tile.get_width(), r * tile.get_height()))
    return surf

class TestLevel:
    # --- add this new method anywhere in TestLevel class ---
    def reset_world(self):
        """Hard reset: restore player, clear projectiles/target, and respawn enemies."""
        # Player
        self.player.dead = False
        self.player.hp = self.player.max_hp
        self.player.invuln_t = 0.0
        self.player.pos.update(self.spawn_pos)
        self.player.rect.center = (round(self.spawn_pos[0]), round(self.spawn_pos[1]))

        # Projectiles & target
        self.projectiles.clear()
        self.current_target = None
        self.cast_timer = 0.0

        # Enemies
        self.enemy_sprites.empty()
        self.enemies.clear()
        self._spawn_enemies(n=20, margin=128)

        # Camera will naturally lerp back to the player; if you want a hard snap,
        # and your Camera has such a method, you could call:
        #   self.camera.set_target(self.player)
        #   self.camera.update(0)  # or self.camera.snap_to_target() if you add one

    def __init__(self, game):
        self.game = game

        # --- world surface (bigger than viewport)
        self.world_size = (S.WORLD_W, S.WORLD_H)
        ground = _load_ground_tile()
        self.world_bg = _build_tiled_surface(ground, *self.world_size)

        # --- player
        self.spawn_pos = (self.world_size[0] // 2, self.world_size[1] // 2)
        self.player = Player(pos=self.spawn_pos)

        # --- enemies
        self.enemy_sprites = pygame.sprite.Group()
        self.enemies = []  # for radar dots
        self._spawn_enemies(n=20, margin=128)

        # --- projectiles
        self.projectiles = []
        self.cast_cooldown = 0.10
        self.cast_timer = 0.0

        # --- targeting
        self.current_target: Enemy | None = None

        # --- camera
        self.camera = Camera(S.WORLD_RECT, self.world_size, zoom=S.CAMERA_ZOOM, lerp=S.CAMERA_LERP)
        self.camera.set_target(self.player)

    def _spawn_enemies(self, n=15, margin=128):
        rnd = random.Random(1337)
        W, H = self.world_size
        for _ in range(n):
            x = rnd.randint(margin, W - margin)
            y = rnd.randint(margin, H - margin)
            e = Enemy(x, y, player=self.player)
            self.enemies.append(e)
            self.enemy_sprites.add(e)

    # ========= Input from Game =========
    def handle_event(self, event):
        self.player.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                self.camera.set_zoom(self.camera.zoom + 0.25)
            elif event.key == pygame.K_MINUS:
                self.camera.set_zoom(self.camera.zoom - 0.25)

    def handle_world_click(self, screen_pos, selected_spell):
        """Left-click in world: click-to-target; cast only if cursor is on the current target."""
        if not selected_spell or self.player.dead:
            return
        world_xy = self.screen_to_world(screen_pos)
        if world_xy is None:
            return
        wx, wy = world_xy

        # click-to-target
        clicked_enemy = self._enemy_at_world_point(wx, wy)
        if clicked_enemy is not None:
            self.current_target = clicked_enemy

        # cast only if cursor is on the current target
        if self.current_target and self.current_target.rect.collidepoint((int(wx), int(wy))):
            if self.cast_timer <= 0.0 and selected_spell == "spark":
                start = self.player.rect.center
                self.projectiles.append(
                    Projectile(start_xy=start, target_xy=self.current_target.rect.center,
                               speed=800, radius=4, damage=28,
                               color=(170, 120, 255), max_dist=1400)
                )
                self.cast_timer = self.cast_cooldown
                self.game.log("Cast Spark")

    # ========= Helpers =========
    def _enemy_at_world_point(self, wx: float, wy: float) -> Enemy | None:
        point = (int(wx), int(wy))
        for e in self.enemy_sprites:
            if e.rect.collidepoint(point):
                return e
        return None

    def screen_to_world(self, screen_xy):
        sx, sy = screen_xy
        vx, vy, vw, vh = self.camera.viewport
        if not (vx <= sx < vx + vw and vy <= sy < vy + vh):
            return None
        cam = self.camera.view_rect()
        fx = (sx - vx) / vw
        fy = (sy - vy) / vh
        wx = cam.left + fx * cam.width
        wy = cam.top  + fy * cam.height
        return (wx, wy)

    # ========= Update / Draw =========
    def update(self, dt):
        # cooldowns
        if self.cast_timer > 0:
            self.cast_timer = max(0.0, self.cast_timer - dt)

        # player
        self.player.update(dt)

        # clamp player center to world bounds
        half_w = self.player.rect.width  * 0.5
        half_h = self.player.rect.height * 0.5
        W, H = self.world_size
        px = max(half_w, min(W - half_w, self.player.pos.x))
        py = max(half_h, min(H - half_h, self.player.pos.y))
        self.player.pos.update((px, py))
        self.player.rect.center = (round(px), round(py))

        # enemies (chase + damage)
        self.enemy_sprites.update(dt)

        # projectiles (hits)
        for p in list(self.projectiles):
            p.update(dt)
            hit_any = False
            for enemy in list(self.enemy_sprites):
                if p.rect.colliderect(enemy.rect):
                    enemy.hp -= p.damage
                    hit_any = True
                    if enemy.hp <= 0:
                        self.enemy_sprites.remove(enemy)
                        if enemy in self.enemies: self.enemies.remove(enemy)
                        if self.current_target is enemy:
                            self.current_target = None
                    break
            if hit_any or not p.alive():
                self.projectiles.remove(p)

        # clear target that died elsewhere
        if self.current_target and (self.current_target not in self.enemy_sprites):
            self.current_target = None

        # camera last
        self.camera.update(dt)

    def draw(self, screen):
        cam_rect = self.camera.view_rect()

        # camera layer (world chunk)
        layer = pygame.Surface(cam_rect.size, pygame.SRCALPHA)
        layer.blit(self.world_bg, (-cam_rect.x, -cam_rect.y))

        # enemies
        for e in self.enemy_sprites:
            layer.blit(e.image, (e.rect.x - cam_rect.x, e.rect.y - cam_rect.y))

        # target highlight
        if self.current_target:
            r = self.current_target.rect.copy()
            r.x -= cam_rect.x; r.y -= cam_rect.y
            pygame.draw.rect(layer, (255, 240, 120), r, 2)

        # projectiles
        for p in self.projectiles:
            p.draw_on_layer(layer, cam_rect)

        # player (ALWAYS draw; tint while invulnerable)
        px = self.player.rect.x - cam_rect.x
        py = self.player.rect.y - cam_rect.y
        if self.player.invuln_t > 0.0:
            img = self.player.image.copy()
            img.set_alpha(180)  # 0..255
            layer.blit(img, (px, py))

        else:
            layer.blit(self.player.image, (px, py))

        # scale to viewport and blit
        view_w, view_h = self.camera.viewport.size
        scaled = pygame.transform.scale(layer, (view_w, view_h))
        screen.blit(scaled, self.camera.viewport.topleft)
