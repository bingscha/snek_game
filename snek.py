"""Game of snake to be solved using ML."""
import sys
import threading
import numpy as np
import pygame
from snake import Snake

WIDTH = 750
HEIGHT = 650
STATE = None
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BUTTONS = []

def init_game():
    """Initialize the game of snek, returns screen."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    title_screen(screen)
    return screen

def create_button(screen, left, top, width, height, text, font):
    """Create button for the main screen."""
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
    screen.fill(BLACK)
    pygame.display.set_caption("Start")
    global STATE
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

def create_rects(left, top, tile_dim, color_dim):
    """Create the rects for the game board."""
    board = np.empty((35, 30), dtype=pygame.Rect)
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            board[x, y] = pygame.Rect(left + x * tile_dim, top + y * tile_dim, color_dim, color_dim)
    return board

def init_board(screen, game_board):
    """Init the board with snek x and y position and apple."""
    snek_x = np.random.randint(0, 35)
    snek_y = np.random.randint(0, 30)
    apple_x = np.random.randint(0, 35)
    apple_y = np.random.randint(0, 30)

    # Should not initially share the same coords.
    while (snek_x, snek_y) == (apple_x, apple_y):
        apple_x = np.random.randint(0, 35)
        apple_y = np.random.randint(0, 30)

    snek = game_board[snek_x, snek_y]
    apple = game_board[apple_x, apple_y]
    pygame.draw.rect(screen, RED, apple)
    pygame.draw.rect(screen, GREEN, snek)
    return (snek_x, snek_y), (apple_x, apple_y)

def check_bounds(next_rect, snek):
    """Check to see if the next rect breaks the bounds."""
    if next_rect[0] < 0 or next_rect[1] < 0 or next_rect[0] >= 35 or next_rect[1] >= 30 or next_rect in snek:
        return False
    return True

def find_new_apple(screen, game_board, non_used):
    """Find new location to insert apple."""
    new_apple = non_used[np.random.randint(0, len(non_used))]
    pygame.draw.rect(screen, RED, game_board[new_apple])
    return new_apple

def run_game_loop(screen, game_board):
    """Run the snek game loop."""
    snek_rect, apple_rect = init_board(screen, game_board)
    snek = [snek_rect]
    direction = "None"
    eaten = False

    non_used = [(x, y) for x in range(35) for y in range(30)]
    non_used.remove(snek_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == 273 and direction != 'Down': # UP
                    direction = 'Up'
                    break
                if event.key == 276 and direction != 'Right': # LEFT
                    direction = 'Left'
                    break
                if event.key == 274 and direction != 'Up': # DOWN
                    direction = 'Down'
                    break
                if event.key == 275 and direction != 'Left': # RIGHT
                    direction = 'Right'
                    break

        next_rect = None
        if direction == 'Left':
            next_rect = (snek[-1][0] - 1, snek[-1][1])
        elif direction == 'Up':
            next_rect = (snek[-1][0], snek[-1][1] - 1)
        elif direction == 'Right':
            next_rect = (snek[-1][0] + 1, snek[-1][1])
        elif direction == 'Down':
            next_rect = (snek[-1][0], snek[-1][1] + 1)

        if next_rect:
            if not check_bounds(next_rect, snek):
                return

            if not eaten:
                pygame.draw.rect(screen, BLACK, game_board[snek[0]])
                non_used.append(snek[0])
                snek.pop(0)
            else:
                eaten = False

            pygame.draw.rect(screen, GREEN, game_board[next_rect])
            snek.append(next_rect)
            non_used.remove(next_rect)

            if next_rect == apple_rect:
                eaten = True
                apple_rect = find_new_apple(screen, game_board, non_used)

        pygame.time.wait(75) # Maybe do not need maybe change later.
        pygame.display.flip()


def create_game_borders(screen, border_corner, border_dim, game_corner, game_dim):
    """Create the border where the game is going to be played."""
    border = pygame.Rect(border_corner, border_dim)
    pygame.draw.rect(screen, WHITE, border)
    board = pygame.Rect(game_corner, game_dim)
    pygame.draw.rect(screen, BLACK, board)


def game_screen(screen, button_idx):
    """Change to the main game screen."""
    screen.fill(BLACK)

    # Regular game with input from user
    if button_idx == 0:
        # Create the game board
        create_game_borders(screen, (20, 20), (710, 610), (25, 25), (700, 600))

        # Creates the rects of the game board
        game_board = create_rects(25, 25, 20, 20)
        run_game_loop(screen, game_board)
        title_screen(screen)

        # Update screen
        pygame.display.flip()

    elif button_idx == 1: # Train the model
        # game_boards = np.empty((5, 5), dtype=np.ndarray)
        screen_lock = threading.Lock()
        snakes = []
        for x in range(5):
            for y in range(5):
                left_border = 5 + x * 140 + 10 * x - 1
                top_border = 5 + y * 120 + 10 * y - 1
                create_game_borders(screen, (left_border, top_border),
                                    (142, 122), (left_border + 1, top_border + 1), (140, 120))
                game_board = create_rects(left_border + 1, top_border + 1, 4, 4)

                # 5 input layer, 9 first hidden, 7 second hidden, 3 output
                snakes.append(Snake(screen, screen_lock, game_board, (45, 63, 21)))
        pygame.display.flip()
        start_training(screen, snakes)

def restart_borders(screen):
    for x in range(5):
            for y in range(5):
                left_border = 5 + x * 140 + 10 * x - 1
                top_border = 5 + y * 120 + 10 * y - 1
                create_game_borders(screen, (left_border, top_border),
                                    (142, 122), (left_border + 1, top_border + 1), (140, 120))

def start_training(screen, snakes):
    """Start training the snakes."""
    counter = {'moved': 0, 'dead': 0, 'pass': []}
    counter['pass'] = [0 for _ in range(25)]
    counter_lock = threading.Lock()
    finished_cv = threading.Condition(counter_lock)
    # Start threads
    counter_lock.acquire()
    # Acquire lock
    # import pdb;pdb.set_trace()
    for _ in range(10):
        num = 0
        for snake in snakes:
            snek_thread = threading.Thread(target=snake.run_game, args=(counter, counter_lock, finished_cv, num))
            snek_thread.daemon = True
            snek_thread.start()
            num += 1
        iterations = 0
        while True:
            finished_cv.notifyAll()
            while counter['moved'] + counter['dead'] != 25:
                finished_cv.wait()
            iterations += 1

            counter['moved'] = 0
            if iterations == 100:
                counter['pass'] = [2 for _ in range(25)]
                finished_cv.notifyAll()
                break
            else:
                counter['pass'] = [0 for _ in range(25)]

            if counter['dead'] == 25:
                break

            pygame.display.flip()
        counter['moved'] = 0
        counter['dead'] = 0
        iterations = 0
        restart_borders(screen)
        for snake in snakes:
            snake.restart()
    counter_lock.release()
    print('finished')

def run_start_screen_loop(screen):
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
    MAIN_SCREEN = init_game()
    run_start_screen_loop(MAIN_SCREEN)
