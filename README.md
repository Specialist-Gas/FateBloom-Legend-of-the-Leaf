# Floral Foundations — Top-Down Action Prototype

A fast-paced, RuneScape-inspired top-down prototype built with **Pygame**. Move with WASD, select a spell in the right-side panel, and click enemies to sling projectiles. Includes camera zoom, a radar/minimap panel, a pause menu with a quit modal, and a handy debug menu (God Mode).

---

## Quick Start

### Requirements
- **Python** 3.10+ (tested on 3.13.2)
- **Pygame** 2.6.1+

```bash
# from project root
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -U pygame
```

### Run
```bash
# if your entry is main_1.py
python main_1.py
# (or python main.py if you use that filename)
```

If you get asset errors, check the **Assets** section below.

---

## Project Structure

```
FloralFoundations/
├─ assets/
│  └─ tilesets/
│     ├─ grass.png         # ground tileset or single tile
│     └─ walk.png          # 4-dir, 8 frames per row player sheet
├─ core/
│  ├─ game.py              # main game loop, menus, routing
│  ├─ settings.py          # window/UI/camera & tuning knobs
│  └─ assets.py            # placeholder images/fonts
├─ scenes/
│  ├─ hud.py               # top/bottom tab strip, etc.
│  ├─ spells.py            # spell window (Spark)
│  ├─ radar.py             # top-right radar/minimap
│  ├─ debug_menu.py        # ~ toggle, God Mode
│  └─ pause_menu.py        # Esc pause + Quit modal
├─ ui/
│  ├─ button.py            # simple image button
│  └─ window.py            # basic clamped window frame
└─ world/
   ├─ test_level.py        # level, spawns, click-to-target casting
   ├─ player.py            # animation, movement, HP, God Mode
   ├─ enemy.py             # chase AI, contact damage, respects God Mode
   ├─ projectile.py        # Spark projectile
   └─ camera.py            # view rect + zoom, scales to viewport
```

---

## Controls

- **Move:** `W A S D` or Arrow keys  
- **Run:** Hold **Shift**
- **Diagonals:**  
  - **Up-Right:** `W + E`  
  - **Up-Left:** `W + Q`  
  - **Down-Right:** `S + D`  
  - **Down-Left:** `S + A`
- **Spell Select:** Click **Spark** in the right panel (Spells)
- **Cast:** **Left-click** an enemy (click-to-target; casts when cursor is over the target)
- **Zoom:** `+` / `-` (plus/minus)
- **Pause Menu:** **Esc**  
  - Esc (main pause) → **Unpause**  
  - Esc (quit modal open) → **Close modal** (back to pause)
- **Quit (from Pause):** Click **Quit**, then **Yes** in the modal (or **No** to return)
- **Debug Menu:** **~** (tilde/backquote) — toggle God Mode
- **Game Over:** **R** to restart, **Esc** to quit

---

## Gameplay Features

- **Camera zoom & viewport:** World is larger than the window; camera renders to the left viewport and scales.
- **Right-side UI:** Top radar/minimap; bottom spells window (Spark button).
- **Click-to-target casting:** Click an enemy to set it as target; subsequent clicks while your cursor is on that enemy fire **Spark** (with a short cooldown).
- **Enemies:** Chase AI; they seek the player in a detection radius and deal contact damage on a cooldown.
- **Player health & i-frames:** HP bar at top-left of the world; brief invulnerability on hit; visual tint instead of flicker.
- **God Mode:** Toggle via Debug menu; damage is ignored (enemies also explicitly check this).
- **Pause menu + modal:** Esc opens pause, click **Quit** to confirm **Yes/No**.

---

## Configuration (edit `core/settings.py`)

Common knobs:
- **Window & Layout**
  - `WIDTH`, `HEIGHT` (default 1280×720)
  - `PANEL_WIDTH`, `WORLD_RECT`, `RADAR_RECT`, `PANEL_RECT`
- **Camera**
  - `CAMERA_ZOOM` (default 2.0), `CAMERA_LERP`
- **World**
  - `WORLD_W`, `WORLD_H`
  - `TILE_SIZE`, `TILESET_PATH`, `GROUND_TILE_COORDS`
- **Combat**
  - `PLAYER_MAX_HP`, `PLAYER_INVULN_TIME`
  - `ENEMY_SPEED`, `ENEMY_DETECT_RADIUS`
  - `ENEMY_ATTACK_DAMAGE`, `ENEMY_ATTACK_COOLDOWN`, `ENEMY_ATTACK_RANGE`
- **Debug**
  - `DEBUG_TILES`, `DEBUG_INVULN` (starts player in God Mode if True)

---

## Assets

- **Player sheet:** `assets/tilesets/walk.png`  
  - 4 rows (top→bottom order: **down**, **left**, **right**, **up**)  
  - 8 frames per row, each **64×64**
- **Ground:** `assets/tilesets/grass.png`  
  - Either a single **64×64** tile **or** a tileset; `GROUND_TILE_COORDS` picks the tile.
- **UI icons:** `spark` and button placeholders are generated in `core/assets.py`. Replace with real images if desired (keep the keys `"btn_spell"` and `"spark"`).

---

## Restart Flow

On **Game Over**:
- Press **R** to call `Game._restart()`, which uses `TestLevel.reset_world()` to:
  - Restore player HP, clear death state, and move back to **spawn**
  - Clear projectiles and target
  - **Respawn enemies**
  - Reset timers

---

## Extending

### Add a new spell
1. Add an icon image (or placeholder) to `Assets.load()` with a unique key.
2. In `scenes/spells.py`, add a `Button` to select your new spell (set `game.selected_spell = "my_spell"`).
3. In `world/test_level.py → handle_world_click`, branch on `selected_spell == "my_spell"` and spawn a new `Projectile` or custom behavior.

### Add an enemy type
- Create a new class in `world/` (e.g., `enemy_fast.py`) with unique stats/AI.
- Spawn it in `TestLevel._spawn_enemies`.
- Keep damage via `player.take_damage(...)` and respect `player.god_mode`.

---

## Troubleshooting

- **ImportError: cannot import name 'Game' from core.game**  
  Ensure `core/game.py` defines `class Game` and you run `from core.game import Game`.

- **KeyError for images (e.g., `'spark'`)**  
  Confirm `Assets.load()` sets `self.images["spark"]` and any UI keys you use.

- **Tilde doesn’t toggle debug menu**  
  Layouts vary; we also check the printable char. Try the backquote key (under Esc). We debounce toggles and `pygame.key.set_repeat(0)` to avoid rapid repeats.

- **God Mode but still taking damage**  
  - `Player.take_damage` early-returns if `god_mode` is True.  
  - Enemies call `player.take_damage(...)` and also check `player.god_mode` before applying hits.  
  - Verify no direct writes to HP (search for `player.hp -=` etc.).

- **Map not drawing correctly**  
  - Check `TILE_SIZE`, `TILESET_PATH`, and `GROUND_TILE_COORDS`.  
  - Set `DEBUG_TILES = True` to print diagnostics.

---

## Roadmap

- Multiple spells & hotbar (keybinds)
- Enemy variety & telegraphed attacks
- Loot/XP & equipment
- Proper inventory window (separate from spells)
- Save/load
- Audio & VFX polish

---

## License

Add your preferred license (MIT is common for prototypes).

---

## Credits

- Built with **Pygame**  
- Sprite sheet & tiles are placeholders; replace with your own or properly licensed art.
