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

        self.grid = False

        self.game_run = True
        self.teleports1 = list()  # Хранение данных о телепортах
        self.teleports2 = list()
        self.teleport1 = None
        self.teleport2 = None
        self.draw_teleport = True  # Рисовать ли телепорт
        self.players = None

        self.teleport_timer2 = self.teleport_timer = kwargs.get("teleport_cooldown", 120)
        # Игровые объекты
        self.groups_data = {
            "players": pygame.sprite.Group(),
            "walls_horizontal": pygame.sprite.Group(),
            "walls_vertical": pygame.sprite.Group()
        }

    def add_players(self, players):
        self.players = players

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                self.grid = not self.grid

    def update(self):
        self.teleport1 = self.teleports1[0]
        self.teleport2 = self.teleports2[0]
        for gamer in self.players:
            if pygame.sprite.collide_mask(gamer, self.teleport1) and self.draw_teleport:
                gamer.rect.x = self.teleport2.rect.x  # Провернка на столкновение с
                gamer.rect.y = self.teleport2.rect.y  # телепортами
                self.draw_teleport = False
                self.teleports1.remove(self.teleport1)
                self.teleports1.append(self.teleport1)
                self.teleports2.remove(self.teleport2)
                self.teleports2.append(self.teleport2)
            elif pygame.sprite.collide_mask(gamer, self.teleport2) and self.draw_teleport:
                gamer.rect.x = self.teleport1.rect.x
                gamer.rect.y = self.teleport1.rect.y
                self.draw_teleport = False
                self.teleports1.remove(self.teleport1)
                self.teleports1.append(self.teleport1)
                self.teleports2.remove(self.teleport2)
                self.teleports2.append(self.teleport2)

    def render(self):
        self.screen.fill(self.bg_color)
        for key in self.groups_data:
            self.groups_data[key].draw(self.screen)
        if self.draw_teleport:
            if self.teleport1 and self.teleport2:
                group = pygame.sprite.Group()
                group.add(self.teleport1, self.teleport2)
                group.draw(self.screen)
        else:
            self.teleport_timer -= 1
            if self.teleport_timer == 0:
                self.teleport_timer = self.teleport_timer2
                self.draw_teleport = True
        if self.grid:
            self.draw_grid()

    # Основная функция сцена
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()
            if self.teleports1 and self.teleports2:
                self.update()
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
    prototype = Scene(title="Prototype", FPS=60, size=(1920, 1080))
    list_of_players = create_field(load_level('level.txt'), prototype)
    prototype.add_players(list_of_players)
    prototype.play()
