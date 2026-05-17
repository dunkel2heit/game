"""
SHOOTER: top-down dodger/shooter. Survive and rack up score.

Controls:
    Arrow keys / WASD  - move
    Space              - shoot
    R                  - restart after game over
    ESC                - quit

How to run:
    python examples/shooter/shooter.py
"""

import pygame
import random


# ----------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 700, 800
FPS = 60

PLAYER_SIZE = 36
PLAYER_SPEED = 6

BULLET_W, BULLET_H = 5, 14
BULLET_SPEED = 10
SHOOT_COOLDOWN_MS = 220       # how often you can fire

ENEMY_SIZE = 34
ENEMY_BASE_SPEED = 3
INITIAL_SPAWN_INTERVAL = 900  # milliseconds between spawns at the start
MIN_SPAWN_INTERVAL = 220      # the spawning never gets faster than this
SPAWN_RAMP_MS = 6000          # every N ms, spawn interval shrinks

BG = (10, 10, 25)
PLAYER_COLOR = (90, 220, 220)
BULLET_COLOR = (255, 240, 120)
ENEMY_COLOR = (230, 80, 80)
WHITE = (240, 240, 240)
GREEN = (80, 200, 120)


# ----------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 72)


def new_game():
    return {
        "player_x": WIDTH // 2 - PLAYER_SIZE // 2,
        "player_y": HEIGHT - PLAYER_SIZE - 30,
        "bullets": [],          # list of pygame.Rect
        "enemies": [],          # list of dicts: {"rect":..., "speed":...}
        "score": 0,
        "last_shot_ms": 0,
        "last_spawn_ms": 0,
        "start_ms": pygame.time.get_ticks(),
        "game_over": False,
    }


def draw_text(text, font_to_use, color, center):
    surface = font_to_use.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


def current_spawn_interval(elapsed_ms):
    """Spawn faster as time goes on. Never faster than MIN_SPAWN_INTERVAL."""
    steps = elapsed_ms // SPAWN_RAMP_MS
    interval = INITIAL_SPAWN_INTERVAL - steps * 80
    return max(MIN_SPAWN_INTERVAL, interval)


state = new_game()
running = True

while running:
    now = pygame.time.get_ticks()

    # --- EVENTS -------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and state["game_over"]:
                state = new_game()

    # --- UPDATE -------------------------------------------------------
    if not state["game_over"]:
        keys = pygame.key.get_pressed()

        # Movement: arrow keys OR wasd.
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            state["player_x"] -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            state["player_x"] += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            state["player_y"] -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            state["player_y"] += PLAYER_SPEED

        # Clamp inside the window.
        if state["player_x"] < 0:
            state["player_x"] = 0
        if state["player_x"] > WIDTH - PLAYER_SIZE:
            state["player_x"] = WIDTH - PLAYER_SIZE
        if state["player_y"] < 0:
            state["player_y"] = 0
        if state["player_y"] > HEIGHT - PLAYER_SIZE:
            state["player_y"] = HEIGHT - PLAYER_SIZE

        # Shooting (with a cooldown, so holding space doesn't fire 60/sec).
        if keys[pygame.K_SPACE] and now - state["last_shot_ms"] > SHOOT_COOLDOWN_MS:
            bullet_x = state["player_x"] + PLAYER_SIZE // 2 - BULLET_W // 2
            bullet_y = state["player_y"] - BULLET_H
            state["bullets"].append(pygame.Rect(bullet_x, bullet_y, BULLET_W, BULLET_H))
            state["last_shot_ms"] = now

        # Move bullets up, drop the ones that left the screen.
        new_bullets = []
        for b in state["bullets"]:
            b.y -= BULLET_SPEED
            if b.bottom > 0:
                new_bullets.append(b)
        state["bullets"] = new_bullets

        # Spawn enemies on a timer that gets faster over time.
        elapsed = now - state["start_ms"]
        if now - state["last_spawn_ms"] > current_spawn_interval(elapsed):
            ex = random.randint(0, WIDTH - ENEMY_SIZE)
            speed = ENEMY_BASE_SPEED + random.random() * 2
            state["enemies"].append(
                {
                    "rect": pygame.Rect(ex, -ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE),
                    "speed": speed,
                }
            )
            state["last_spawn_ms"] = now

        # Move enemies down, drop the ones that escaped past the bottom.
        new_enemies = []
        for e in state["enemies"]:
            e["rect"].y += e["speed"]
            if e["rect"].top < HEIGHT:
                new_enemies.append(e)
        state["enemies"] = new_enemies

        # Bullet vs enemy collisions.
        # Build a fresh list of survivors each frame. We can't modify the
        # lists we're iterating over without confusing Python, hence the
        # 'surviving_*' lists below.
        surviving_bullets = []
        for b in state["bullets"]:
            hit = False
            for e in state["enemies"]:
                if b.colliderect(e["rect"]):
                    hit = True
                    state["enemies"].remove(e)   # remove this enemy
                    state["score"] += 1
                    break
            if not hit:
                surviving_bullets.append(b)
        state["bullets"] = surviving_bullets

        # Enemy vs player collision -> game over.
        player_rect = pygame.Rect(
            state["player_x"], state["player_y"], PLAYER_SIZE, PLAYER_SIZE
        )
        for e in state["enemies"]:
            if e["rect"].colliderect(player_rect):
                state["game_over"] = True
                break

    # --- DRAW ---------------------------------------------------------
    screen.fill(BG)

    # Player drawn as a chunky triangle (just looks cooler than a square).
    px, py = state["player_x"], state["player_y"]
    triangle = [
        (px + PLAYER_SIZE // 2, py),                       # top point
        (px, py + PLAYER_SIZE),                            # bottom-left
        (px + PLAYER_SIZE, py + PLAYER_SIZE),              # bottom-right
    ]
    pygame.draw.polygon(screen, PLAYER_COLOR, triangle)

    # Bullets
    for b in state["bullets"]:
        pygame.draw.rect(screen, BULLET_COLOR, b)

    # Enemies
    for e in state["enemies"]:
        pygame.draw.rect(screen, ENEMY_COLOR, e["rect"])

    # HUD
    hud = font.render(f"Score: {state['score']}", True, WHITE)
    screen.blit(hud, (10, 10))

    # Game over screen
    if state["game_over"]:
        draw_text("GAME OVER", big_font, ENEMY_COLOR, (WIDTH // 2, HEIGHT // 2 - 30))
        draw_text(
            f"Final score: {state['score']}",
            font,
            WHITE,
            (WIDTH // 2, HEIGHT // 2 + 30),
        )
        draw_text(
            "Press R to play again", font, GREEN, (WIDTH // 2, HEIGHT // 2 + 70)
        )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()