"""Game of snake to be solved using ML."""
import random
import sys
import pygame

WIDTH = 750
HEIGHT = 650
STATE = None
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
BUTTONS = []

def init_game():
    """Initialize the game of snek, returns screen."""

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    title_screen(screen)
    return screen

def create_button(screen, left, top, width, height, text, font):
    # Create button rect
    button = pygame.Rect(left, top, width, height)
    pygame.draw.rect(screen, RED, button)

    # Draw text on button
    text = font.render(text, True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = button.center
    screen.blit(text, text_rect)

    return button

def title_screen(screen):
    """Display title screen."""

    # Reset Screen and init title
    screen.fill(BLACK)
    pygame.display.set_caption("Start")
    STATE = "title"

    # Set Fonts
    title_font = pygame.font.Font('fonts/pixel.otf', 128)
    button_font = pygame.font.Font('fonts/pixel.otf', 64)

    # Create the title
    title = title_font.render('Snek', True, WHITE)
    title_rect = title.get_rect()
    title_rect.center = (375, 125)
    screen.blit(title, title_rect) 

    # Menu Buttons
    global BUTTONS
    BUTTONS = []
    BUTTONS.append(create_button(screen, 100, 250, 550, 100, 'Start', button_font))
    BUTTONS.append(create_button(screen, 100, 375, 550, 100, 'Train', button_font))
    BUTTONS.append(create_button(screen, 100, 500, 550, 100, 'Run', button_font))
    
    # Re-render screen
    pygame.display.flip()

def game_screen(screen, button_idx):
    """Change to the main game screen."""
    screen.fill(BLACK)
    border = pygame.Rect(20, 20, 710, 610)
    pygame.draw.rect(screen, WHITE, border)
    board = pygame.Rect(25, 25, 700, 600)
    pygame.draw.rect(screen, BLACK, board)

    pygame.display.flip()

def run_game_loop(screen):
    """Run game loop."""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # print('EVENT')
                mouse_pos = pygame.mouse.get_pos()
                # print(BUTTONS)
                for idx, button in enumerate(BUTTONS):
                    # print(button)
                    if button.collidepoint(mouse_pos):
                        game_screen(screen, idx)


if __name__ == '__main__':
    screen = init_game()
    run_game_loop(screen)