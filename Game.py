import sys

from functions import create_field, load_level

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
            "walls": pygame.sprite.Group(),
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
        if player.draw_teleport:
            group = pygame.sprite.Group()
            group.add(player.teleport1, player.teleport2)
            group.draw(self.screen)
        else:
            player.teleport1.timer -= 1
            if player.teleport1.timer == 0:
                player.teleport1.timer = player.teleport1.timer2
                player.draw_teleport = True

    # Основная функция сцены
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()

            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    prototype = Scene(title="Prototype")
    players = create_field(load_level('level.txt'), prototype.groups_data)
    player = players[0]
    prototype.play()
