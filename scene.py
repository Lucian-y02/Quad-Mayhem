import sys

from database import DBase, Table
from objects import VerticalPlatform, HorizontalPlatform, Weapon, Pause
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
        self.gas = list()

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
            "walls_vertical": pygame.sprite.Group(),
            "barrels": pygame.sprite.Group(),
            "toxic_barrels": pygame.sprite.Group(),
            "gas": pygame.sprite.Group(),
            "platforms": pygame.sprite.Group(),
            "weapons": pygame.sprite.Group(),
            "bullets": pygame.sprite.Group(),
            "health_indicators": pygame.sprite.Group(),
            "healing_boxes": pygame.sprite.Group(),
            "game_stuff": pygame.sprite.Group(),
            "pause": pygame.sprite.Group()
        }

        DBase('images.db')
        self.normal_gas = Table('images').get_image(1)[1].convert()
        self.toxic_gas = Table('images').get_image(2)[2].convert()
        self.play_btn = Table('images').get_image(3)[3].convert()
        self.quit_btn = Table('images').get_image(4)[4].convert()
        self.ffa_btn = Table('images').get_image(5)[5].convert()
        self.ctf_btn = Table('images').get_image(6)[6].convert()
        self.tdm_btn = Table('images').get_image(7)[7].convert()
        self.pause_btn = Table('images').get_image(8)[8].convert()
        self.normal_gas.set_colorkey('white')
        self.toxic_gas.set_colorkey('white')
        self.pause_btn.set_colorkey('white')
        self.images = [self.normal_gas, self.toxic_gas]

        self.pause = None
        self.stop = False

    def add_players(self, players):  # Создание списка игроков
        self.players = players

    # Добавление новой группы спрайтов
    def add_group(self, name):
        self.groups_data[name] = pygame.sprite.Group()

    def check_event(self):
        if not self.stop:
            for key in self.groups_data:
                self.groups_data[key].update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE):
                self.game_run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                self.grid = not self.grid
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stop = not self.stop

    def update(self):
        if not self.stop:
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
        if not self.stop:
            self.screen.fill(self.bg_color)
            for key in self.groups_data:
                if key != 'platforms':
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
            for gas in self.gas:
                gas.duration -= 1
                if gas.duration == 0:
                    gas.kill()

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

    def set_pause(self, pause):
        self.pause = pause


def menu(game):
    game.screen.fill('white')
    play_btn_coords = (400, 200)
    quit_btn_coords = (800, 200)
    game.screen.blit(game.play_btn, play_btn_coords)
    game.screen.blit(game.quit_btn, quit_btn_coords)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit(pygame.quit())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = event.pos
                if play_btn_coords[0] < coords[0] < play_btn_coords[0] + 200 and \
                        play_btn_coords[1] < coords[1] < play_btn_coords[1] + 60:
                    return 0
                elif quit_btn_coords[0] < coords[0] < quit_btn_coords[0] + 200 and \
                        quit_btn_coords[1] < coords[1] < quit_btn_coords[1] + 60:
                    sys.exit(pygame.quit())
        pygame.display.flip()
        clock.tick(60)


def mode_choice(game):
    game.screen.fill('white')
    ffa_btn_coords = (400, 200)
    ctf_btn_coords = (800, 200)
    tdm_btn_coords = (600, 400)
    game.screen.blit(game.ffa_btn, ffa_btn_coords)
    game.screen.blit(game.ctf_btn, ctf_btn_coords)
    game.screen.blit(game.tdm_btn, tdm_btn_coords)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit(pygame.quit())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = event.pos
                if ffa_btn_coords[0] < coords[0] < ffa_btn_coords[0] + 200 and \
                        ffa_btn_coords[1] < coords[1] < ffa_btn_coords[1] + 60:
                    return 'FFA'
                elif ctf_btn_coords[0] < coords[0] < ctf_btn_coords[0] + 200 and \
                        ctf_btn_coords[1] < coords[1] < ctf_btn_coords[1] + 60:
                    return 'CTF'
                elif tdm_btn_coords[0] < coords[0] < tdm_btn_coords[0] + 200 and \
                        tdm_btn_coords[1] < coords[1] < tdm_btn_coords[1] + 60:
                    return 'TDM'
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    prototype = Scene(title="Prototype", FPS=60, size=(1920, 1080))
    menu(prototype)
    mode_choice(prototype)
    list_of_players = create_field(load_level('level.txt'), prototype)
    prototype.add_players(list_of_players)
    prototype.set_pause(Pause(prototype, x=1280, y=0, size=(50, 50)))
    VerticalPlatform(prototype.groups_data, prototype.screen, x=250, y=200, y2=400, speed=1)
    HorizontalPlatform(prototype.groups_data, prototype.screen, x=1020, y=230, x2=1210, speed=1)
    Weapon(prototype.groups_data, x=32 * 13, y=32 * 5)
    Weapon(prototype.groups_data, x=32 * 23, y=32 * 5)
    Weapon(prototype.groups_data, x=32 * 26, y=32 * 5)
    prototype.play()
