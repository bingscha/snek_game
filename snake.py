import threading
import numpy as np
import pygame

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]

class Snake():
    def __init__(self, screen, screen_lock, game_board, weights):
        """Initialize snake with screen and game_board."""
        self.board = game_board
        self.screen = screen
        self.screen_lock = screen_lock
        snek_rect, apple_rect = self.init_board()
        self.body = [snek_rect]
        self.apple = apple_rect
        self.weights_one = np.random.choice(np.arange(-1, 1, step=0.01), size=weights[0], replace=True)
        self.weights_two = np.random.choice(np.arange(-1, 1, step=0.01), size=weights[1], replace=True)
        self.weights_three = np.random.choice(np.arange(-1, 1, step=0.01), size=weights[2], replace=True)
        self.direction = np.random.choice(['Up', 'Left', 'Right', 'Down'])
        self.score = 0
        # print(self.weights_three)

    def restart(self):
        snek_rect, apple_rect = self.init_board()
        self.body = [snek_rect]
        self.apple = apple_rect
        self.direction = np.random.choice(['Up', 'Left', 'Right', 'Down'])

    def init_board(self):
        """Init the board with snek x and y position and apple."""
        snek_x = np.random.randint(0, 35)
        snek_y = np.random.randint(0, 30)
        apple_x = np.random.randint(0, 35)
        apple_y = np.random.randint(0, 30)

        # Should not initially share the same coords.
        while (snek_x, snek_y) == (apple_x, apple_y):
            apple_x = np.random.randint(0, 35)
            apple_y = np.random.randint(0, 30)

        snek = self.board[snek_x, snek_y]
        apple = self.board[apple_x, apple_y]
        self.screen_lock.acquire()
        pygame.draw.rect(self.screen, RED, apple)
        pygame.draw.rect(self.screen, GREEN, snek)
        self.screen_lock.release()
        return (snek_x, snek_y), (apple_x, apple_y)

    def check_bounds(self, next_rect):
        """Check to see if the next rect breaks the bounds."""
        if next_rect[0] < 0 or next_rect[1] < 0 or next_rect[0] >= 35 or next_rect[1] >= 30 or next_rect in self.body:
            return 1

        return 0

    def create_input_vector(self):
        # [Front?, Left?, Right?, Angle-Norm, Distance]
        input_vec = [0 for _ in range(5)]
        if self.direction == 'Up':
            input_vec[0] = not self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[1] = not self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[2] = not self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
        elif self.direction == 'Left':
            input_vec[0] = not self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[1] = not self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[2] = not self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
        elif self.direction == 'Right':
            input_vec[0] = not self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Left
            input_vec[1] = not self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
            input_vec[2] = not self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
        elif self.direction == 'Down':
            input_vec[0] = not self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Up
            input_vec[1] = not self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
            input_vec[2] = not self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
        input_vec[3] = ((np.arctan2(*self.body[-1][::-1]) - np.arctan2(*self.apple[::-1])) % (2 * np.pi)) / (2 * np.pi)
        input_vec[4] = np.linalg.norm(np.array(self.body[-1]) - np.array(self.apple))

        return input_vec


    def determine_direction(self, input_vec, num):
        layer_one = [0 for _ in range(9)]
        layer_two = [0 for _ in range(7)]
        output = [0 for _ in range(3)]

        for input_idx in range(5):
            for layer_idx in range(9):
                layer_one[layer_idx] += input_vec[input_idx] * self.weights_one[input_idx * 9 + layer_idx]

        for idx in range(9):
            if layer_one[idx] < 0:
                layer_one[idx] = 0

        for input_idx in range(9):
            for layer_idx in range(7):
                layer_two[layer_idx] += layer_one[input_idx] * self.weights_two[input_idx * 7 + layer_idx]

        for idx in range(7):
            if layer_two[idx] < 0:
                layer_two[idx] = 0

        for input_idx in range(7):
            for layer_idx in range(3):
                output[layer_idx] += layer_two[input_idx] * self.weights_three[input_idx * 3 + layer_idx]
        
        max_index = output.index(max(output))

        if max_index == 1:
            # print('Changed!', num, self.direction)
            if self.direction == 'Up':
                self.direction = 'Left'
            elif self.direction == 'Left':
                self.direction = 'Down'
            elif self.direction == 'Right':
                self.direction = 'Up'
            elif self.direction == 'Down':
                self.direction = 'Right'
            # print('Changed!', num, self.direction)
        elif max_index == 2:
            # print('Changed!', num, self.direction)
            if self.direction == 'Up':
                self.direction = 'Right'
            elif self.direction == 'Left':
                self.direction = 'Up'
            elif self.direction == 'Right':
                self.direction = 'Down'
            elif self.direction == 'Down':
                self.direction = 'Left'
            # print('Changed!', num, self.direction)

    def find_new_apple(self, non_used):
        """Find new location to insert apple."""
        new_apple = non_used[np.random.randint(0, len(non_used))]
        self.screen_lock.acquire()
        pygame.draw.rect(self.screen, RED, self.board[new_apple])
        self.screen_lock.release()
        return new_apple

    def run_game(self, counter, counter_lock, finished_cv, num):
        """Start running the game."""
        eaten = False
        non_used = [(x, y) for x in range(35) for y in range(30)]
        non_used.remove(self.body[-1])
        self.score = 0

        while True:
            input_vec = self.create_input_vector()
            self.determine_direction(input_vec, num)
            
            if self.direction == 'Left':
                next_rect = (self.body[-1][0] - 1, self.body[-1][1])
            elif self.direction == 'Up':
                next_rect = (self.body[-1][0], self.body[-1][1] - 1)
            elif self.direction == 'Right':
                next_rect = (self.body[-1][0] + 1, self.body[-1][1])
            elif self.direction == 'Down':
                next_rect = (self.body[-1][0], self.body[-1][1] + 1)

            if self.check_bounds(next_rect):
                counter_lock.acquire()
                counter['dead'] += 1
                finished_cv.notifyAll()
                counter_lock.release()
                print(self.score)
                return

            if not eaten:
                self.screen_lock.acquire()
                pygame.draw.rect(self.screen, BLACK, self.board[self.body[0]])
                self.screen_lock.release()
                non_used.append(self.body[0])
                self.body.pop(0)
            else:
                eaten = False

            self.screen_lock.acquire()
            pygame.draw.rect(self.screen, GREEN, self.board[next_rect])
            self.screen_lock.release()

            self.body.append(next_rect)
            non_used.remove(next_rect)

            if np.linalg.norm(np.array(next_rect) - np.array(self.apple)) < input_vec[4]:
                self.score += 20
            else:
                self.score -= 30

            if next_rect == self.apple:
                eaten = True
                self.apple = self.find_new_apple(non_used)
                self.score += 500

            counter_lock.acquire()
            counter['moved'] += 1
            counter['pass'][num] = 1
            finished_cv.notifyAll()
            while counter['pass'][num] == 1:
                finished_cv.wait()

            exit = False
            if counter['pass'][num] == 2:
                exit = True
            counter_lock.release()
            if exit:
                print(self.score)
                return
