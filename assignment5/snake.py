# Snake and Snake App
# Author: Yuanjie Yuanjie
# Date: 11/20/19

import pygame
import random
import time
import config

class Snake:
    # pos = (x, y), where x is the col offset, and y is the row offset.
    def __init__(self, pos, rows, cols):
        self.rows, self.cols = rows, cols
        self.body = [pos]
        self.dc, self.dr = 0, 1
        self.direction = config.DOWN

    # Update snake's direction according to the given direction
    def _update_dir(self, direction):
        if direction == config.UP:
            self.dc, self.dr = 0, -1
        elif direction == config.RIGHT:
            self.dc, self.dr = 1, 0
        elif direction == config.DOWN:
            self.dc, self.dr = 0, 1
        elif direction == config.LEFT:
            self.dc, self.dr = -1, 0

    # Return true if move is okay, false otherwise.
    def move(self, opponent_snake, apple, direction):
        self._update_dir(direction)
        c, r = self.head()
        nc, nr = (c + self.dc) % self.cols, (r + self.dr) % self.rows

        # hit his own body, lose
        if (nc, nr) in self.body: 
            return config.LOSE
        # two snake run at heads, tie
        if (nc, nr) == opponent_snake.head():
            return config.TIE
        # hit opponent snake body, lose
        if (nc, nr) in opponent_snake.body:
            return config.LOSE
        self.body.insert(0, (nc, nr))
        if not (nc, nr) == apple:
            self.body.pop()
        return config.CONTINUE

    # Return the head of the snake.
    def head(self):
        return self.body[0]

class SnakeApp:
    def __init__(self):
        # Initialize surface
        self.rows, self.cols = config.HEIGHT, config.WIDTH
        self.snake_size = 20
        self.surface = pygame.display.set_mode((self.cols * self.snake_size, self.rows * self.snake_size))
        pygame.display.set_caption('Snake Game')
        self.game_status = config.CREATE
        self.snake = []
        self.opponent_snake = []
        self.apple = None

        pygame.display.update()

    def _draw_rect(self, pos, color):
        c, r = pos
        pygame.draw.rect(self.surface, color,
                         (c*self.snake_size+1, r*self.snake_size+1, self.snake_size-2 , self.snake_size-2))

    # redraw the game window
    def _redraw_window(self):
        self.surface.fill(config.BLACK)
        self._draw_rect(self.apple, config.RED)
        for pos in self.snake:
            self._draw_rect(pos, config.GREEN)
        for pos in self.opponent_snake:
            self._draw_rect(pos, config.ORANGE)
        pygame.display.flip()

    # run the game for one time
    def run_once(self):
        if self.game_status == config.OVER: return
        if self.game_status == config.CREATE:
            self._draw_msg('Wait for component')
        elif self.game_status == config.READY:
            self._draw_msg('Wait game start')
        elif self.game_status == config.START:
            self._redraw_window()

    # show wait for opponent and wait for game start
    def _draw_msg(self, msg):
        self.surface.fill(config.BLACK)
        assert pygame.font.get_init()
        font = pygame.font.Font(None, 60)
        text = font.render(msg, True, config.BLUE)
        text_rect = text.get_rect()
        text_x = self.surface.get_width() / 2 - text_rect.width / 2
        text_y = self.surface.get_height() / 2 - text_rect.height / 2
        self.surface.blit(text, [text_x, text_y])
        pygame.display.flip()   

    # Update the status of the game to the given status
    def _update_game_status(self, status):
        self.game_status = status

    # Update snakes and apple with the given snakes and apple
    def _update_snakes_and_apple(self, snake, opponent_snake, apple):
        self.snake, self.opponent_snake = [], []
        self.snake.extend(snake)
        self.opponent_snake.extend(opponent_snake)
        self.apple = apple

# if __name__ == "__main__":
#     clock = pygame.time.Clock()
#     FPS = 10  # frames-per-second
#     game = SnakeApp()
#     while True:
#         clock.tick(FPS)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()   
#         game.run_once()

