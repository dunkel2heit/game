import pygame

WHITE = (255, 255, 255)
BLUE = (70, 130, 255)
DARK_BLUE = (15, 20, 50)
RED = (220, 70, 70)

class Button:
    def __init__(self, x, y, w, h, text, color, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.font = font

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=20)
        pygame.draw.rect(screen, WHITE, self.rect, 4, border_radius=20)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

def run_menu(screen, clock, font, WIDTH, HEIGHT):
    button_width = 340
    button_height = 80
    center_x = WIDTH // 2 - button_width // 2

    play_button = Button(center_x, HEIGHT // 2 - 40, button_width, button_height, "PLAY GAME", BLUE, font)
    exit_button = Button(center_x, HEIGHT // 2 + 80, button_width, button_height, "EXIT TO DESKTOP", RED, font)

    while True:
        clock.tick(60)
        screen.fill(DARK_BLUE)

        title = font.render("SPACESHIPS VS SPACE ROCKS", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
        screen.blit(title, title_rect)

        play_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button.clicked(mouse_pos):
                    try:
                        pygame.mixer.music.play(-1)
                    except pygame.error:
                        pass
                    return "play"
                if exit_button.clicked(mouse_pos):
                    return "exit"
