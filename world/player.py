import pygame
from core import settings as S

# --- speeds ---
WALK_SPEED = 160
RUN_MULT   = 1.75  # hold Shift to run

# --- sprite sheet config ---
SHEET_ORDER_TOP_TO_BOTTOM = ("up", "left", "down", "right")
FRAMES_PER_DIR = 8
FRAME_W = 64
FRAME_H = 64

# On perfect diagonals, which axis decides the facing?
DIAGONAL_PREF = "horizontal"  # W+E => RIGHT, W+Q => LEFT, S+D => RIGHT, S+A => LEFT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Load & slice animations using explicit row order
        sheet = pygame.image.load("assets/tilesets/walk.png").convert_alpha()
        self.animations = self._slice_4dir_sheet(sheet)

        self.facing = "down"
        self.frame_index = 0
        self.image = self.animations[self.facing][0]
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 0)

        # animation timing (base is for walking; running scales it)
        self.anim_timer = 0.0
        self.anim_base = 0.12  # seconds per frame at WALK speed

        # runtime state
        self.run_mult = 1.0  # updated each frame based on Shift

        # --- combat / health ---
        self.max_hp = S.PLAYER_MAX_HP
        self.hp = self.max_hp
        self.invuln_t = 0.0   # >0 means can't take damage
        self.dead = False

    def _slice_4dir_sheet(self, sheet: pygame.Surface):
        anims = {d: [] for d in ("up", "down", "left", "right")}
        for row, direction in enumerate(SHEET_ORDER_TOP_TO_BOTTOM):
            for col in range(FRAMES_PER_DIR):
                rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
                frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                anims[direction].append(frame)
        return anims

    # ---------------- Input ----------------
    def handle_event(self, event):
        # Reserved for future hooks
        pass

    def _read_inputs(self):
        keys = pygame.key.get_pressed()

        # Cardinals
        right_down = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])
        left_down  = bool(keys[pygame.K_LEFT]  or keys[pygame.K_a])
        down_down  = bool(keys[pygame.K_DOWN]  or keys[pygame.K_s])
        up_down    = bool(keys[pygame.K_UP]    or keys[pygame.K_w])

        # Diagonal modifiers (ONLY with W)
        q_down = bool(keys[pygame.K_q])  # up-left with W
        e_down = bool(keys[pygame.K_e])  # up-right with W

        # Shift-to-run
        running = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.run_mult = RUN_MULT if running else 1.0

        # WASD/Arrows
        x = (1 if right_down else 0) - (1 if left_down else 0)
        y = (1 if down_down else 0)  - (1 if up_down else 0)

        # W+Q / W+E modifiers only when W is held and no horizontal cardinal is deciding
        if up_down and not left_down and not right_down:
            if e_down and x == 0 and y == -1:
                x = 1   # W+E => up-right
            elif q_down and x == 0 and y == -1:
                x = -1  # W+Q => up-left

        # Clamp to -1..0..1
        x = 1 if x > 0 else (-1 if x < 0 else 0)
        y = 1 if y > 0 else (-1 if y < 0 else 0)
        return x, y

    def _update_facing_from_vector(self, x, y):
        if x == 0 and y == 0:
            return
        ax, ay = abs(x), abs(y)
        if ax > ay:
            self.facing = "right" if x > 0 else "left"
        elif ay > ax:
            self.facing = "down" if y > 0 else "up"
        else:
            self.facing = ("right" if x > 0 else "left") if DIAGONAL_PREF == "horizontal" \
                          else ("down" if y > 0 else "up")

    # ---------------- Health ----------------
    def take_damage(self, amount: int):
        if self.invuln_t > 0.0 or self.dead:
            return
        self.hp = max(0, self.hp - int(amount))
        self.invuln_t = S.PLAYER_INVULNERABLE_TIME
        if self.hp <= 0:
            self.dead = True

    # ---------------- Tick ----------------
    def handle_input(self):
        x, y = self._read_inputs()
        self.velocity.update(x, y)
        self._update_facing_from_vector(x, y)

    def update(self, dt):
        # invulnerability countdown
        if self.invuln_t > 0.0:
            self.invuln_t = max(0.0, self.invuln_t - dt)

        self.handle_input()

        if self.velocity.length_squared() > 0:
            move_dir = self.velocity.normalize()
            speed = WALK_SPEED * self.run_mult
            self.pos += move_dir * speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))

            # animation rate scales with speed
            effective_anim = self.anim_base / self.run_mult
            self.anim_timer += dt
            if self.anim_timer >= effective_anim:
                self.anim_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.facing])
                self.image = self.animations[self.facing][self.frame_index]
        else:
            # idle
            self.frame_index = 0
            self.image = self.animations[self.facing][0]
            self.anim_timer = 0.0

        # keep pos in sync with rect (TestLevel clamps world bounds)
        self.pos.update(self.rect.center)
