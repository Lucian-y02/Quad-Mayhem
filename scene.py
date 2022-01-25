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

        self.pixel_font = pygame.font.Font("PixelFont.ttf", 56)
        self.final_text = "The end"
        self.draw_final_text = False

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
            "bullets": pygame.sprite.Group(),
            "healing_boxes": pygame.sprite.Group(),
            "game_stuff": pygame.sprite.Group()
        }

    # Добавление новой группы спрайтов
    def add_group(self, name):
        self.groups_data[name] = pygame.sprite.Group()

    # События
    def check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.game_run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_g:
                    self.grid = not self.grid
                elif event.key == pygame.K_h:
                    for pl in self.groups_data["players"]:
                        pl.health_points = 100
                elif event.key == pygame.K_f:
                    self.FPS = 3 if self.FPS == 60 else 60
                elif event.key == pygame.K_o:
                    self.end_of_game_session("The end")
        for key in self.groups_data:
            self.groups_data[key].update()

    # Отрисовка
    def render(self):
        self.screen.fill(self.bg_color)
        for key in self.groups_data:
            self.groups_data[key].draw(self.screen)
        if self.grid:
            self.draw_grid()
        if self.draw_final_text:
            self.screen.blit(self.pixel_font.render(self.final_text, False, (10, 10, 10)),
                             (self.width // 2 - 96, self.height // 2))

    # Основная функция сцена
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()

            pygame.display.flip()
            self.clock.tick(self.FPS)
        pygame.quit()
        sys.exit()

    # Рисование сетки
    def draw_grid(self):
        for j in range(self.width // 32 + 3):
            pygame.draw.line(self.screen, (0, 0, 200), (32 * j, 0), (32 * j, self.height))
        for g in range(self.height // 32):
            pygame.draw.line(self.screen, (0, 0, 200), (0, 32 * g), (self.width + 64, 32 * g))

    def end_of_game_session(self, final_text):
        for key in self.groups_data:
            for game_object in self.groups_data[key]:
                game_object.kill()
        self.final_text = final_text
        self.draw_final_text = True


if __name__ == '__main__':
    prototype = Scene(title="Prototype", FPS=60)
    player2 = Player(prototype.groups_data, x=550, y=150, controller="joystick", color="blue",
                     team="2")
    player3 = Player(prototype.groups_data, x=32 * 7, y=100, controller="keyboard_1", color="red",
                     team="1")

    platform_left(prototype.groups_data, x=32 * 17, y=32 * 15)
    for i in range(18, 27):
        platform(prototype.groups_data, x=32 * i, y=32 * 15)
    platform_right(prototype.groups_data, x=32 * 27, y=32 * 15)

    box(prototype.groups_data, x=640, y=352)
    box(prototype.groups_data, x=608, y=320)
    box(prototype.groups_data, x=672, y=384)
    box(prototype.groups_data, x=768, y=416)
    Beam(prototype.groups_data, x=32 * 25, y=32 * 13)
    Beam(prototype.groups_data, x=32 * 26, y=32 * 13)

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

    Beam(prototype.groups_data, x=32 * 6, y=32 * 6)
    Beam(prototype.groups_data, x=32 * 5, y=32 * 6)

    box(prototype.groups_data, x=32 * 7, y=32 * 6)
    Beam(prototype.groups_data, x=32 * 8, y=32 * 6)

    Weapon(prototype.groups_data, x=32 * 10, y=32 * 5)
    Ammo(prototype.groups_data, x=32 * 12, y=32 * 5)
    Spikes(prototype.groups_data["game_stuff"], x=32 * 29, y=32 * 18)
    ItemsSpawner(prototype.groups_data, x=32 * 25, y=32 * 18, cool_down=2)

    TeamFlag(prototype.groups_data, x=32 * 16, y=32 * 5, team="1",
             end_function=prototype.end_of_game_session)

    prototype.play()
