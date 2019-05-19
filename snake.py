import math
import threading
import numpy as np
import pygame

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
EATEN_NUM = 2

class Snake():
    def __init__(self, screen=None, screen_lock=None, game_board=None, weights=None):
        """Initialize snake with screen and game_board."""
        self.board = game_board
        self.screen = screen
        self.screen_lock = screen_lock
        snek_rect, apple_rect = self.init_board()
        self.body = [snek_rect]
        self.apple = apple_rect
        self.weights_one = np.multiply(np.random.rand(weights[1], weights[0]), 2) - np.ones((weights[1], weights[0]))
        self.weights_two = np.random.rand(weights[2], weights[1]) - np.ones((weights[2], weights[1]))
        self.weights_three = np.random.rand(weights[3], weights[2]) - np.ones((weights[3], weights[2]))
        self.direction = np.random.choice(['Up', 'Left', 'Right', 'Down'])
        self.score = 0
        # print(self.weights_three)

    def restart(self):
        snek_rect, apple_rect = self.init_board()
        self.body = [snek_rect]
        self.apple = apple_rect
        self.direction = np.random.choice(['Up', 'Left', 'Right', 'Down'])
        self.score = 0

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

        return (snek_x, snek_y), (apple_x, apple_y)

    def check_bounds(self, next_rect):
        """Check to see if the next rect breaks the bounds."""
        if next_rect == self.apple:
            # print('Body')
            return 1

        if next_rect[0] < 0 or next_rect[1] < 0 or next_rect[0] >= 35 or next_rect[1] >= 30 or next_rect in self.body:
            return -1

        return 0

    def create_input_vector(self):
        # [Front?, Left?, Right?, Angle-Norm, Distance]
        input_vec = [0 for _ in range(29)]
        angle = (self.apple[0] - self.body[-1][0], self.apple[1] - self.body[-1][1])
        angle = (math.atan2(angle[0], angle[1]) + 2 * math.pi) % (2 * math.pi)
        if self.direction == 'Up':
            # 3 in front
            input_vec[0] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[1] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 2)) # Up
            input_vec[2] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 3)) # Up

            # 3 in left front
            input_vec[3] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] - 1)) # Left Up
            input_vec[4] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] - 2)) # Left Up
            input_vec[5] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] - 3)) # Left Up

            # 3 in left
            input_vec[6] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[7] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1])) # Left
            input_vec[8] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1])) # Left

            # 3 in left back
            input_vec[9] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] + 1)) # Left Down
            input_vec[10] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] + 2)) # Left Down
            input_vec[11] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] + 3)) # Left Down

            # 3 in back
            input_vec[12] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
            input_vec[13] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 2)) # Down
            input_vec[14] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 3)) # Down

            # 3 in back right
            input_vec[15] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] + 1)) # Right Down
            input_vec[16] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] + 2)) # Right Down
            input_vec[17] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] + 3)) # Right Down

            # 3 in right
            input_vec[18] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
            input_vec[19] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1])) # Right
            input_vec[20] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1])) # Right

            # 3 in right front
            input_vec[21] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] - 1)) # Right Up
            input_vec[22] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] - 2)) # Right Up
            input_vec[23] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] - 3)) # Right Up

            angle -= math.pi
        elif self.direction == 'Left':
            # 3 in left
            input_vec[0] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[1] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1])) # Left
            input_vec[2] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1])) # Left

            # 3 in left back
            input_vec[3] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] + 1)) # Left Down
            input_vec[4] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] + 2)) # Left Down
            input_vec[5] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] + 3)) # Left Down

            # 3 in back
            input_vec[6] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
            input_vec[7] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 2)) # Down
            input_vec[8] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 3)) # Down

            # 3 in back right
            input_vec[9] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] + 1)) # Right Down
            input_vec[10] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] + 2)) # Right Down
            input_vec[11] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] + 3)) # Right Down

            # 3 in right
            input_vec[12] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
            input_vec[13] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1])) # Right
            input_vec[14] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1])) # Right

            # 3 in right front
            input_vec[15] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] - 1)) # Right Up
            input_vec[16] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] - 2)) # Right Up
            input_vec[17] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] - 3)) # Right Up

            # 3 in front
            input_vec[18] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[19] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 2)) # Up
            input_vec[20] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 3)) # Up

            # 3 in left front
            input_vec[21] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] - 1)) # Left Up
            input_vec[22] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] - 2)) # Left Up
            input_vec[23] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] - 3)) # Left Up

            angle -= 3 * math.pi / 2
        elif self.direction == 'Right':
            # 3 in right
            input_vec[0] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
            input_vec[1] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1])) # Right
            input_vec[2] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1])) # Right

            # 3 in right front
            input_vec[3] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] - 1)) # Right Up
            input_vec[4] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] - 2)) # Right Up
            input_vec[5] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] - 3)) # Right Up

            # 3 in front
            input_vec[6] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[7] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 2)) # Up
            input_vec[8] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 3)) # Up

            # 3 in left front
            input_vec[9] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] - 1)) # Left Up
            input_vec[10] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] - 2)) # Left Up
            input_vec[11] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] - 3)) # Left Up

            # 3 in left
            input_vec[12] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[13] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1])) # Left
            input_vec[14] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1])) # Left

            # 3 in left back
            input_vec[15] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] + 1)) # Left Down
            input_vec[16] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] + 2)) # Left Down
            input_vec[17] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] + 3)) # Left Down

            # 3 in back
            input_vec[18] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
            input_vec[19] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 2)) # Down
            input_vec[20] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 3)) # Down

            # 3 in back right
            input_vec[21] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] + 1)) # Right Down
            input_vec[22] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] + 2)) # Right Down
            input_vec[23] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] + 3)) # Right Down

            angle -= math.pi / 2
        elif self.direction == 'Down':
            # 3 in back
            input_vec[0] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 1)) # Down
            input_vec[1] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 2)) # Down
            input_vec[2] = self.check_bounds((self.body[-1][0], self.body[-1][1] + 3)) # Down

            # 3 in back right
            input_vec[3] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] + 1)) # Right Down
            input_vec[4] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] + 2)) # Right Down
            input_vec[5] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] + 3)) # Right Down

            # 3 in right
            input_vec[6] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1])) # Right
            input_vec[7] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1])) # Right
            input_vec[8] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1])) # Right

            # 3 in right front
            input_vec[9] = self.check_bounds((self.body[-1][0] + 1, self.body[-1][1] - 1)) # Right Up
            input_vec[10] = self.check_bounds((self.body[-1][0] + 2, self.body[-1][1] - 2)) # Right Up
            input_vec[11] = self.check_bounds((self.body[-1][0] + 3, self.body[-1][1] - 3)) # Right Up

            # 3 in front
            input_vec[12] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 1)) # Up
            input_vec[13] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 2)) # Up
            input_vec[14] = self.check_bounds((self.body[-1][0], self.body[-1][1] - 3)) # Up

            # 3 in left front
            input_vec[15] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] - 1)) # Left Up
            input_vec[16] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] - 2)) # Left Up
            input_vec[17] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] - 3)) # Left Up

            # 3 in left
            input_vec[18] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1])) # Left
            input_vec[19] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1])) # Left
            input_vec[20] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1])) # Left

            # 3 in left back
            input_vec[21] = self.check_bounds((self.body[-1][0] - 1, self.body[-1][1] + 1)) # Left Down
            input_vec[22] = self.check_bounds((self.body[-1][0] - 2, self.body[-1][1] + 2)) # Left Down
            input_vec[23] = self.check_bounds((self.body[-1][0] - 3, self.body[-1][1] + 3)) # Left Down

        if angle < 0:
            angle += 2 * math.pi

        input_vec[24] = self.body[-1][0] / 35
        input_vec[25] = self.body[-1][1] / 30

        input_vec[26] = (self.apple[0] - self.body[-1][0]) / 35
        input_vec[27] = (self.apple[1] - self.body[-1][1]) / 30

        input_vec[28] = angle / (2 * math.pi)

        return input_vec

    def run_weights(self, input_vec):
        layer_one = [0 for _ in range(9)]
        layer_two = [0 for _ in range(15)]
        output = [0 for _ in range(3)]

        layer_one = np.matmul(self.weights_one, input_vec)
        for idx in range(len(layer_one)):
            if layer_one[idx] < 0:
                layer_one[idx] = 0

        layer_two = np.matmul(self.weights_two, layer_one)
        for idx in range(len(layer_two)):
            if layer_two[idx] < 0:
                layer_two[idx] = 0

        output = np.matmul(self.weights_three, layer_two)
        max_index = np.argmax(output)
        return max_index

    def get_dir_num(self):
        input_vec = self.create_input_vector()
        return self.run_weights(input_vec)

    def determine_direction(self, input_vec, num):
        max_index = self.run_weights(input_vec)

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
        eaten_count = 0
        non_used = [(x, y) for x in range(35) for y in range(30)]
        non_used.remove(self.body[-1])
        self.score = 0
        lifetime = 0
        closer = 0
        farther = 0
        timeout = 200

        while True:
            # if num == 0:
            #     import pdb;pdb.set_trace()
            timeout -= 1
            lifetime += 1

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

            if self.check_bounds(next_rect) < 0 or timeout == 0:
                counter_lock.acquire()
                counter['dead'] += 1
                finished_cv.notifyAll()
                # self.score -= (200 - counter['iterations']) * 100
                # self.score = (closer * 100 - farther * 150) + lifetime * lifetime * len(self.body)
                if (len(self.body) - 1) // 4 < 10:
                    self.score = (10 * closer - 15 * farther) * lifetime * lifetime * 2 ** ((len(self.body) - 1) // (EATEN_NUM + 1))
                else:
                    self.score = (10 * closer - 15 * farther) * lifetime * lifetime * 2 ** 10 * ((len(self.body) - 1) // (EATEN_NUM + 1))
                
                counter_lock.release()
                # print(self.score)
                return

            if np.linalg.norm(np.array(next_rect) - np.array(self.apple)) < np.linalg.norm(np.array(self.body[-1]) - np.array(self.apple)):
                closer += 1
            else:
                farther += 1

            if not eaten:
                self.screen_lock.acquire()
                pygame.draw.rect(self.screen, BLACK, self.board[self.body[0]])
                self.screen_lock.release()
                non_used.append(self.body[0])
                self.body.pop(0)
            elif eaten_count == EATEN_NUM:
                eaten = False
                eaten_count = 0
            else:
                eaten_count += 1

            self.screen_lock.acquire()
            pygame.draw.rect(self.screen, GREEN, self.board[next_rect])
            self.screen_lock.release()

            self.body.append(next_rect)
            non_used.remove(next_rect)

            if next_rect == self.apple:
                # print("ATE", num)
                eaten = True
                timeout += 100 * ((len(self.body) - 1) // (EATEN_NUM + 1))
                self.apple = self.find_new_apple(non_used)
                # self.score += 50000

            counter_lock.acquire()
            counter['moved'] += 1
            counter['pass'][num] = 1
            finished_cv.notifyAll()
            # print(counter, num)
            while counter['pass'][num] == 1:
                finished_cv.wait()

            counter_lock.release()

    def combine(self, parent1, parent2):
        for x in range(self.weights_one.shape[0]):
            for y in range(self.weights_one.shape[1]):
                if np.random.random() < 0.5:
                    self.weights_one[x][y] = parent1.weights_one[x][y]
                else:
                    self.weights_one[x][y] = parent2.weights_one[x][y]

        for x in range(self.weights_two.shape[0]):
            for y in range(self.weights_two.shape[1]):
                if np.random.random() < 0.5:
                    self.weights_two[x][y] = parent1.weights_two[x][y]
                else:
                    self.weights_two[x][y] = parent2.weights_two[x][y]

        for x in range(self.weights_three.shape[0]):
            for y in range(self.weights_three.shape[1]):
                if np.random.random() < 0.5:
                    self.weights_three[x][y] = parent1.weights_three[x][y]
                else:
                    self.weights_three[x][y] = parent2.weights_three[x][y]

    def mutate(self):
        for x in range(self.weights_one.shape[0]):
            for y in range(self.weights_one.shape[1]):
                if np.random.random() < 0.01:
                    self.weights_one[x][y] = np.random.random() * 2 - 1

        for x in range(self.weights_two.shape[0]):
            for y in range(self.weights_two.shape[1]):
                if np.random.random() < 0.01:
                    self.weights_two[x][y] = np.random.random() * 2 - 1

        for x in range(self.weights_three.shape[0]):
            for y in range(self.weights_three.shape[1]):
                if np.random.random() < 0.01:
                    self.weights_three[x][y] = np.random.random() * 2 - 1
