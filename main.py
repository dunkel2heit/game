import pygame
import sys
import random
import menu

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Spaceships VS Space Rocks")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 40)

WHITE = (255, 255, 255)
GRAY = (160, 160, 160)
BLACK = (0, 0, 0)
BLUE = (70, 130, 255)
RED = (220, 70, 70)

try:
    pygame.mixer.music.load("assets/sound.mp3")
    pygame.mixer.music.set_volume(0.8)
except pygame.error:
    print("Warning: Audio asset 'sound.mp3' not found.")

try:
    rock_img = pygame.image.load("assets/rock.png").convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (120, 120))
except pygame.error:
    rock_img = pygame.Surface((120, 120))
    rock_img.fill(RED)

try:
    ship_img = pygame.image.load("assets/spaceship.png").convert_alpha()
    ship_img = pygame.transform.scale(ship_img, (80, 80))
except pygame.error:
    ship_img = None

def new_game():
    return {
        "player_x": WIDTH // 2 - 40,
        "player_y": HEIGHT - 120,
        "bullets": [],
        "rocks": [],
        "score": 0,
        "game_over": False
    }

def spawn_rock(state):
    x = random.randint(0, WIDTH - 120)
    y = random.randint(-600, -120)
    speed = random.randint(3, 7)
    state["rocks"].append([x, y, speed])

pause_button_rect = pygame.Rect(WIDTH - 80, 20, 60, 60)
center_x = WIDTH // 2 - 150
continue_button = menu.Button(center_x, HEIGHT // 2 - 40, 300, 80, "CONTINUE", BLUE, font)
pause_exit_button = menu.Button(center_x, HEIGHT // 2 + 60, 300, 80, "MAIN MENU", RED, font)

state = new_game()
player_speed = 7
is_paused = False
current_state = "MENU"

while True:
    if current_state == "MENU":
        action = menu.run_menu(screen, clock, font, WIDTH, HEIGHT)
        if action == "play":
            state = new_game()
            is_paused = False
            current_state = "GAME"
        elif action == "exit":
            break

    elif current_state == "GAME":
        clock.tick(60)
        screen.fill((15, 20, 50))

        if not state["game_over"] and not is_paused:
            if random.randint(1, 30) == 1:
                spawn_rock(state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = "MENU"
                    pygame.mixer.music.stop()
                
                if event.key == pygame.K_SPACE and not state["game_over"] and not is_paused:
                    state["bullets"].append([state["player_x"] + 38, state["player_y"]])

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if state["game_over"]:
                    current_state = "MENU"
                    pygame.mixer.music.stop()
                else:
                    if not is_paused:
                        if pause_button_rect.collidepoint(mouse_pos):
                            is_paused = True
                    else:
                        if continue_button.clicked(mouse_pos):
                            is_paused = False
                        elif pause_exit_button.clicked(mouse_pos):
                            current_state = "MENU"
                            pygame.mixer.music.stop()

        if not state["game_over"] and not is_paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                state["player_x"] -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                state["player_x"] += player_speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                state["player_y"] -= player_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                state["player_y"] += player_speed

            state["player_x"] = max(0, min(WIDTH - 80, state["player_x"]))
            state["player_y"] = max(0, min(HEIGHT - 80, state["player_y"]))

        if not state["game_over"] and not is_paused:
            for b in state["bullets"]:
                b[1] -= 10
            state["bullets"] = [b for b in state["bullets"] if b[1] > -20]

            for r in state["rocks"]:
                r[1] += r[2]
            state["rocks"] = [r for r in state["rocks"] if r[1] < HEIGHT + 150]

            for b in state["bullets"][:]:
                for r in state["rocks"][:]:
                    if pygame.Rect(r[0], r[1], 120, 120).collidepoint(b[0], b[1]):
                        try:
                            state["bullets"].remove(b)
                            state["rocks"].remove(r)
                            state["score"] += 1
                        except ValueError:
                            pass

            player_rect = pygame.Rect(state["player_x"], state["player_y"], 80, 80)
            for r in state["rocks"]:
                if player_rect.colliderect(pygame.Rect(r[0], r[1], 120, 120)):
                    state["game_over"] = True

        if not state["game_over"]:
            score_text = font.render(f"Score: {state['score']}", True, WHITE)
            screen.blit(score_text, (20, 20))

            if ship_img:
                screen.blit(ship_img, (state["player_x"], state["player_y"]))
            else:
                pygame.draw.rect(screen, BLUE, (state["player_x"], state["player_y"], 80, 80))

            for b in state["bullets"]:
                pygame.draw.rect(screen, WHITE, (b[0], b[1], 5, 15))

            for r in state["rocks"]:
                screen.blit(rock_img, (r[0], r[1]))

            pygame.draw.rect(screen, GRAY, pause_button_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, (WIDTH - 65, 30, 8, 35))
            pygame.draw.rect(screen, WHITE, (WIDTH - 45, 30, 8, 35))

            if is_paused:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))

                pause_text = font.render("PAUSED", True, WHITE)
                screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140)))
                continue_button.draw(screen)
                pause_exit_button.draw(screen)

        else:
            over = font.render("GAME OVER", True, RED)
            screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

            restart = font.render("CLICK TO RETURN TO MAIN MENU", True, WHITE)
            screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        pygame.display.update()

pygame.quit()
sys.exit()
