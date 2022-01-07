import sys

from tools_for_creating_maps import *
from player import Player
from game_stuff import *

import pygame


pygame.init()


class Scene:
    def __init__(self, **kwargs):
        self.size = self.width, self.height = kwargs.get("size", (1280, 800))
        self.FPS = kwargs.get("FPS", 60)
        self.bg_color = kwargs.get("bg_color", (200, 200, 200))

        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        pygame.display.set_caption(kwargs.get("title", "New game"))
        self.clock = pygame.time.Clock()
        self.game_run = True

        self.grid = False

        # Игровые объекты
        self.groups_data = {
            "players": pygame.sprite.Group(),
            "walls_horizontal": pygame.sprite.Group(),
            "walls_vertical": pygame.sprite.Group(),
            "weapons": pygame.sprite.Group(),
            "bullets": pygame.sprite.Group()
        }

    # Добавление новой группы спрайтов
    def add_group(self, name):
        self.groups_data[name] = pygame.sprite.Group()

    def check_event(self):
        for key in self.groups_data:
            self.groups_data[key].update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.game_run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_g:
                    self.grid = not self.grid

    def render(self):
        self.screen.fill(self.bg_color)
        for key in self.groups_data:
            self.groups_data[key].draw(self.screen)
        if self.grid:
            self.draw_grid()

    # Основная функция сцена
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()

            pygame.display.flip()
            self.clock.tick(self.FPS)
        pygame.quit()
        sys.exit()

    def draw_grid(self):
        for j in range(self.width // 32 + 3):
            pygame.draw.line(self.screen, (0, 0, 200), (32 * j, 0), (32 * j, self.height))
        for g in range(self.height // 32):
            pygame.draw.line(self.screen, (0, 0, 200), (0, 32 * g), (self.width + 64, 32 * g))


if __name__ == '__main__':
    prototype = Scene(title="Prototype", FPS=60)
    player1 = Player(prototype.groups_data, x=800, y=400, controller="keyboard_2", color="green")
    player2 = Player(prototype.groups_data, x=550, y=150, controller="joystick", color="blue")
    player3 = Player(prototype.groups_data, x=200, y=100, controller="keyboard_1", color="red")

    platform_left(prototype.groups_data, x=32 * 17, y=32 * 15)
    for i in range(18, 27):
        platform(prototype.groups_data, x=32 * i, y=32 * 15)
    platform_right(prototype.groups_data, x=32 * 27, y=32 * 15)

    box(prototype.groups_data, x=640, y=352)
    box(prototype.groups_data, x=608, y=320)
    box(prototype.groups_data, x=672, y=384)

    platform_left(prototype.groups_data, x=32 * 20, y=32 * 19)
    for i in range(21, 30):
        platform(prototype.groups_data, x=32 * i, y=32 * 19)
    platform_right(prototype.groups_data, x=32 * 30, y=32 * 19)

    platform_top_left(prototype.groups_data, x=32 * 10, y=32 * 8)
    for i in range(11, 17):
        floor(prototype.groups_data, x=32 * i, y=32 * 8)
        ceiling(prototype.groups_data, x=32 * i, y=32 * 10)
    platform_top_right(prototype.groups_data, x=32 * 17, y=32 * 8)
    right_wall(prototype.groups_data, x=32 * 10, y=32 * 9)
    left_wall(prototype.groups_data, x=32 * 17, y=32 * 9)
    platform_bottom_left(prototype.groups_data, x=32 * 10, y=32 * 10)
    platform_bottom_right(prototype.groups_data, x=32 * 17, y=32 * 10)
    box(prototype.groups_data, x=32 * 6, y=32 * 6)

    Weapon(prototype.groups_data, x=32 * 13, y=32 * 5)
    Weapon(prototype.groups_data, x=32 * 23, y=32 * 5)
    Weapon(prototype.groups_data, x=32 * 26, y=32 * 5)

    prototype.play()
