# Debug menu UI
DEBUG_MENU_WIDTH = 280
DEBUG_MENU_ALPHA = 180  # 0..255 translucency


# ===== Window / UI / Camera (your existing settings stay the same) =====
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Floral Foundations – RS-style UI + Camera"

PANEL_WIDTH = 320
PANEL_RECT = (WIDTH - PANEL_WIDTH, HEIGHT // 2, PANEL_WIDTH, HEIGHT // 2)
WORLD_RECT = (0, 0, WIDTH - PANEL_WIDTH, HEIGHT)
RADAR_RECT = (WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT // 2)

TILE_SIZE = 64
TILESET_PATH = "assets/tilesets/grass.png"
GROUND_TILE_COORDS = (1, 1)
DEBUG_TILES = True

WORLD_W, WORLD_H = 3072, 2048

CAMERA_ZOOM = 2.0
CAMERA_LERP = 0.15

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
DARK   = (32, 32, 36)
LIGHT  = (200, 200, 210)
ACCENT = (120, 220, 230)

# --- Audio ---
MUSIC_ENABLED    = True
MUSIC_VOLUME     = 0.60          # 0.0 - 1.0
MUSIC_FADE_MS    = 600           # fade in/out ms
MUSIC_PATH_LEVEL1 = "music/test_level.mp3"   # put your file here


# ===== Debug =====
DEBUG_COMBAT = False  # set True to see melee hitboxes etc.

# ===== Player Combat =====
PLAYER_MAX_HP      = 100
PLAYER_INVULNERABLE_TIME = 0.60   # seconds of invulnerability after being hit

# ===== Enemy AI/Combat =====
ENEMY_SPEED            = 120    # px/s
ENEMY_DETECT_RADIUS    = 900    # start chasing within this distance
ENEMY_ATTACK_DAMAGE    = 12
ENEMY_ATTACK_COOLDOWN  = 0.60   # seconds between hits per enemy
ENEMY_ATTACK_RANGE     = 28     # if closer than this OR rect-colliding -> damage

# Game states
STATE_PLAYING = "PLAYING"
STATE_PAUSED  = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"
STATE_WIN = "WIN"           # <-- add this

