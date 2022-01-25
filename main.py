import sys

from database import DBase, Table
from functions import create_field, load_level

import pygame


pygame.init()
size = width, height = (1280, 800)
FPS = 60
bg_color = 200, 200, 200
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Quad Mayhem")
DBase('images.db')
normal_gas = Table('images').get_image(1)[1].convert()
toxic_gas = Table('images').get_image(2)[2].convert()
play_btn = Table('images').get_image(3)[3].convert()
quit_btn = Table('images').get_image(4)[4].convert()
ffa_btn = Table('images').get_image(5)[5].convert()
ctf_btn = Table('images').get_image(6)[6].convert()
tdm_btn = Table('images').get_image(7)[7].convert()
pause_btn = Table('images').get_image(8)[8].convert()
normal_gas.set_colorkey('white')
toxic_gas.set_colorkey('white')
pause_btn.set_colorkey('white')
images = [normal_gas, toxic_gas]


class CTF:
    def __init__(self, **kwargs):
        self.size = size
        self.width, self.height = width, height
        self.FPS = FPS
        self.bg_color = bg_color
        self.screen = screen

        self.pixel_font = pygame.font.Font("PixelFont.ttf", 56)
        self.final_text = "The end"
        self.draw_final_text = False

        self.clock = pygame.time.Clock()
        self.game_run = True

        self.grid = False
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
            "game_stuff": pygame.sprite.Group()
        }
        self.stop = False
        self.gas = list()

    # Добавление новой группы спрайтов
    def add_group(self, name):
        self.groups_data[name] = pygame.sprite.Group()

    # События
    def check_event(self):
        if not self.stop:
            for key in self.groups_data:
                self.groups_data[key].update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE):
                self.game_run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stop = not self.stop
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

    def add_players(self, players):  # Создание списка игроков
        self.players = players


class FFA:
    def __init__(self, **kwargs):
        # Входные параметры
        self.size = size
        self.width, self.height = width, height
        self.FPS = FPS
        self.bg_color = bg_color
        self.screen = screen
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
            "game_stuff": pygame.sprite.Group()
        }
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


def menu():
    screen.fill('white')
    play_btn_coords = (400, 200)
    quit_btn_coords = (800, 200)
    screen.blit(play_btn, play_btn_coords)
    screen.blit(quit_btn, quit_btn_coords)
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


def mode_choice():
    screen.fill('white')
    ffa_btn_coords = (400, 200)
    ctf_btn_coords = (800, 200)
    screen.blit(ffa_btn, ffa_btn_coords)
    screen.blit(ctf_btn, ctf_btn_coords)
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
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    menu()
    mode = mode_choice()
    if mode == 'FFA':
        prototype = FFA()
        list_of_players = create_field(load_level('levelffa.txt'), prototype, 'FFA')
        prototype.add_players(list_of_players)
        prototype.play()
    elif mode == 'CTF':
        prototype = CTF()
        list_of_players = create_field(load_level('levelctf.txt'), prototype, 'CTF')
        prototype.add_players(list_of_players)
        prototype.play()
