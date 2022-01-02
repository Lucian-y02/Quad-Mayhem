import sys

from tools_for_creating_maps import *
from player import Player
import wall

import pygame


pygame.init()


class Scene:
    def __init__(self, **kwargs):
        # Входные параметры
        self.size = self.width, self.height = kwargs.get("size", (1280, 800))
        self.FPS = kwargs.get("FPS", 60)
        self.bg_color = kwargs.get("bg_color", (200, 200, 200))

        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        pygame.display.set_caption(kwargs.get("title", "New game"))
        self.clock = pygame.time.Clock()
        self.game_run = True

        # Игровые объекты
        self.groups_data = {
            "players": pygame.sprite.Group(),
            "walls_horizontal": pygame.sprite.Group(),
            "walls_vertical": pygame.sprite.Group()
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

    def render(self):
        self.screen.fill(self.bg_color)
        for key in self.groups_data:
            self.groups_data[key].draw(self.screen)

    # Основная функция сцена
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()

            pygame.display.flip()
            self.clock.tick(self.FPS)
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    prototype = Scene(title="Prototype", FPS=60)
    player = Player(prototype.groups_data, x=800, y=400)

    for i in range(10):
        wall.WallHorizontal(x=550 + (i * 32), y=450,
                            group=prototype.groups_data["walls_horizontal"])
        wall.WallHorizontal(x=550 + (i * 32), y=482,
                            group=prototype.groups_data["walls_horizontal"])
    wall.WallVertical(x=550, y=450,
                      group=prototype.groups_data["walls_vertical"])
    wall.WallVertical(x=870, y=450,
                      group=prototype.groups_data["walls_vertical"])

    for i in range(10):
        wall.WallHorizontal(x=750 + (i * 32), y=550,
                            group=prototype.groups_data["walls_horizontal"])
        wall.WallHorizontal(x=750 + (i * 32), y=582,
                            group=prototype.groups_data["walls_horizontal"])
    wall.WallVertical(x=750, y=550,
                      group=prototype.groups_data["walls_vertical"])
    wall.WallVertical(x=1070, y=550,
                      group=prototype.groups_data["walls_vertical"])

    # Как надо делать стены
    wall.WallVertical(x=710, y=391,
                      group=prototype.groups_data["walls_vertical"],
                      size=(1, 31))
    wall.WallVertical(x=742, y=391,
                      group=prototype.groups_data["walls_vertical"],
                      size=(1, 31))
    wall.WallHorizontal(x=716, y=390,
                        group=prototype.groups_data["walls_horizontal"],
                        size=(21, 1))
    wall.WallHorizontal(x=716, y=422,
                        group=prototype.groups_data["walls_horizontal"],
                        size=(21, 1))

    box(prototype.groups_data, x=650, y=350)

    prototype.play()
