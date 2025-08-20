# NEW: top-right radar area (same width as panel, top half)
# scenes/radar.py
import pygame
from core import settings as S

class Radar:
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(S.RADAR_RECT)
        # inner padding so dots/border don’t crowd
        self.pad = 8

        # colors
        self.bg = (22, 22, 24)
        self.border = (0, 0, 0)
        self.grid = (36, 36, 40)
        self.player_col = (90, 220, 255)   # cyan
        self.enemy_col = (230, 70, 70)     # red
        self.cam_col = (180, 180, 180)     # camera view outline

    def _map_xy(self, x, y, world_w, world_h):
        """World (x,y) -> radar pixel inside padded rect."""
        r = self.rect
        inner = pygame.Rect(r.x + self.pad, r.y + self.pad,
                            r.w - 2*self.pad, r.h - 2*self.pad)
        # world coords grow downwards like screen, so linear map is fine
        rx = inner.x + (x / max(1, world_w)) * inner.w
        ry = inner.y + (y / max(1, world_h)) * inner.h
        return int(rx), int(ry)

    def draw(self, screen):
        world = self.game.world
        world_w, world_h = world.world_size

        # background + border
        pygame.draw.rect(screen, self.bg, self.rect)
        pygame.draw.rect(screen, self.border, self.rect, 2)

        # optional minimal grid
        gx = self.rect.x + self.pad
        gy = self.rect.y + self.pad
        gw = self.rect.w - 2*self.pad
        gh = self.rect.h - 2*self.pad

        # light crosshairs
        pygame.draw.line(screen, self.grid, (gx, gy + gh//2), (gx + gw, gy + gh//2), 1)
        pygame.draw.line(screen, self.grid, (gx + gw//2, gy), (gx + gw//2, gy + gh), 1)

        # camera view rectangle (map the camera’s world rect corners into radar)
        cam_rect = world.camera.view_rect()
        tl = self._map_xy(cam_rect.left,  cam_rect.top,    world_w, world_h)
        br = self._map_xy(cam_rect.right, cam_rect.bottom, world_w, world_h)
        cam_px = pygame.Rect(min(tl[0], br[0]), min(tl[1], br[1]),
                             abs(br[0]-tl[0]), abs(br[1]-tl[1]))
        pygame.draw.rect(screen, self.cam_col, cam_px, 1)

        # player dot
        px, py = self._map_xy(world.player.pos.x, world.player.pos.y, world_w, world_h)
        pygame.draw.circle(screen, self.player_col, (px, py), 3)

        # enemy dots
        for e in world.enemies:
            ex, ey = self._map_xy(e.pos.x, e.pos.y, world_w, world_h)
            pygame.draw.circle(screen, self.enemy_col, (ex, ey), 3)
