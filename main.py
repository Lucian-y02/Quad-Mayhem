import sys
from random import shuffle

from functions import create_field, load_level
from constants import *
from game_stuff import Mouse, Button
from player import Jasper, Guido, Adam, Vincent

import pygame


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

        self.result = ''

        self.clock = pygame.time.Clock()
        self.game_run = True

        self.grid = False
        self.teleports1 = list()  # Хранение данных о телепортах
        self.teleports2 = list()
        self.teleport1 = None
        self.teleport2 = None
        self.draw_teleport = True  # Рисовать ли телепорт
        self.players = None
        self.horizontal_platforms = list()

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
            "doors": pygame.sprite.Group()
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
                elif event.key == pygame.K_o:
                    self.end_of_game_session("The end")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.stop:
                    coords = event.pos
                    if btn1_coords[0] < coords[0] < btn1_coords[0] + 200 and \
                            btn1_coords[1] < coords[1] < btn1_coords[1] + 60:
                        self.result = 'МЕНЮ'
                        self.game_run = False
                    elif btn2_coords[0] < coords[0] < btn2_coords[0] + 200 and \
                            btn2_coords[1] < coords[1] < btn2_coords[1] + 60:
                        self.result = 'ЗАНОВО'
                        self.game_run = False
                    elif btn3_coords[0] < coords[0] < btn3_coords[0] + 200 and \
                            btn3_coords[1] < coords[1] < btn3_coords[1] + 60:
                        self.stop = False
                    elif btn4_coords[0] < coords[0] < btn4_coords[0] + 200 and \
                            btn4_coords[1] < coords[1] < btn4_coords[1] + 60:
                        sys.exit(pygame.quit())

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
                for platform in self.horizontal_platforms:
                    if pygame.sprite.collide_mask(gamer, platform):
                        gamer.rect.x += platform.speed

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
            if self.draw_final_text:
                self.screen.blit(self.pixel_font.render(self.final_text, False, (10, 10, 10)),
                                 (self.width // 2 - 96, self.height // 2))
        elif self.stop:
            self.screen.blit(pause, (384, 184))

    # Основная функция сцена
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()
            if self.teleports1 and self.teleports2:
                self.update()
            pygame.display.flip()
            self.clock.tick(self.FPS)

    # Рисование сетки
    def draw_grid(self):
        for j in range(self.width // 32 + 3):
            pygame.draw.line(self.screen, (0, 0, 200), (32 * j, 0), (32 * j, self.height))
        for g in range(self.height // 32):
            pygame.draw.line(self.screen, (0, 0, 200), (0, 32 * g), (self.width + 64, 32 * g))

    def end_of_game_session(self, final_text):
        for key in self.groups_data:
            for game_obj in self.groups_data[key]:
                game_obj.kill()
        self.final_text = final_text
        self.draw_final_text = True

    def add_players(self, list_players):  # Создание списка игроков
        self.players = list_players


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
        self.horizontal_platforms = list()

        self.result = ''

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
            "doors": pygame.sprite.Group()
        }
        self.stop = False

    def add_players(self, list_players):  # Создание списка игроков
        self.players = list_players

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.stop:
                    coords = event.pos
                    if btn1_coords[0] < coords[0] < btn1_coords[0] + 200 and \
                            btn1_coords[1] < coords[1] < btn1_coords[1] + 60:
                        self.result = 'МЕНЮ'
                        self.game_run = False
                    elif btn2_coords[0] < coords[0] < btn2_coords[0] + 200 and \
                            btn2_coords[1] < coords[1] < btn2_coords[1] + 60:
                        self.result = 'ЗАНОВО'
                        self.game_run = False
                    elif btn3_coords[0] < coords[0] < btn3_coords[0] + 200 and \
                            btn3_coords[1] < coords[1] < btn3_coords[1] + 60:
                        self.stop = False
                    elif btn4_coords[0] < coords[0] < btn4_coords[0] + 200 and \
                            btn4_coords[1] < coords[1] < btn4_coords[1] + 60:
                        sys.exit(pygame.quit())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                self.grid = not self.grid
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.stop = not self.stop
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_g:
                    self.grid = not self.grid
                elif event.key == pygame.K_h:
                    for pl in self.groups_data["players"]:
                        pl.health_points = 100

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
                for platform in self.horizontal_platforms:
                    if pygame.sprite.collide_mask(gamer, platform):
                        gamer.rect.x += platform.speed

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
        elif self.stop:
            self.screen.blit(pause, (384, 184))

    # Основная функция сцены
    def play(self):
        while self.game_run:
            self.check_event()
            self.render()
            if self.teleports1 and self.teleports2:
                self.update()
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def draw_grid(self):
        for j in range(self.width // 32 + 3):
            pygame.draw.line(self.screen, (0, 0, 200), (32 * j, 0), (32 * j, self.height))
        for g in range(self.height // 32):
            pygame.draw.line(self.screen, (0, 0, 200), (0, 32 * g), (self.width + 64, 32 * g))


def menu():
    screen.fill((200, 200, 200))
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
    screen.fill((200, 200, 200))
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


def hero_choice_ctf():
    screen.fill((200, 200, 200))
    group = pygame.sprite.Group()
    draw_group = pygame.sprite.Group()
    mouse = Mouse(group)
    first_row_coords = [(209, 346), (453, 346), (702, 346), (951, 346)]
    second_row_coords = [(209, 419), (454, 419), (702, 419), (953, 419)]
    third_row_coords = [(209, 500), (454, 500), (701, 500), (951, 500)]

    btn_attack = Button(attack_btn, draw_group, x=first_row_coords[0][0], y=first_row_coords[0][1])
    btn_attack2 = Button(attack_btn, draw_group, x=first_row_coords[1][0], y=first_row_coords[1][1])
    btn_attack3 = Button(attack_btn, draw_group, x=first_row_coords[2][0], y=first_row_coords[2][1])
    btn_attack4 = Button(attack_btn, draw_group, x=first_row_coords[3][0], y=first_row_coords[3][1])

    attack_buttons = [btn_attack, btn_attack2, btn_attack3, btn_attack4]

    btn_def = Button(def_btn, draw_group, x=second_row_coords[0][0], y=second_row_coords[0][1])
    btn_def2 = Button(def_btn, draw_group, x=second_row_coords[1][0], y=second_row_coords[1][1])
    btn_def3 = Button(def_btn, draw_group, x=second_row_coords[2][0], y=second_row_coords[2][1])
    btn_def4 = Button(def_btn, draw_group, x=second_row_coords[3][0], y=second_row_coords[3][1])

    defence_buttons = [btn_def, btn_def2, btn_def3, btn_def4]

    btn_not = Button(not_in_btn, draw_group, x=third_row_coords[0][0], y=third_row_coords[0][1])
    btn_not2 = Button(not_in_btn, draw_group, x=third_row_coords[1][0], y=third_row_coords[1][1])
    btn_not3 = Button(not_in_btn, draw_group, x=third_row_coords[2][0], y=third_row_coords[2][1])
    btn_not4 = Button(not_in_btn, draw_group, x=third_row_coords[3][0], y=third_row_coords[3][1])

    not_in_buttons = [btn_not, btn_not2, btn_not3, btn_not4]

    result = {0: None, 1: None, 2: None, 3: None}
    chosen_btns = {0: None, 1: None, 2: None, 3: None}

    flag = True

    clock = pygame.time.Clock()
    running = True

    start = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit(pygame.quit())
            if event.type == pygame.MOUSEBUTTONDOWN:
                for u in range(0, 4):
                    if pygame.sprite.collide_mask(mouse, not_in_buttons[u]):
                        result[u] = '3'
                        chosen_btns[u] = not_in_buttons[u]
                    elif pygame.sprite.collide_mask(mouse, defence_buttons[u]):
                        result[u] = '2'
                        chosen_btns[u] = defence_buttons[u]
                    if pygame.sprite.collide_mask(mouse, attack_buttons[u]):
                        result[u] = '1'
                        chosen_btns[u] = attack_buttons[u]
                if start:
                    if pygame.sprite.collide_mask(mouse, start):
                        return result
            if event.type == pygame.MOUSEMOTION:
                mouse.update(event.pos[0], event.pos[1])
        if all(result.values()) and flag:
            flag = False
            start = Button(continue_but, draw_group, x=534, y=585)
        for u in not_in_buttons:
            if u not in chosen_btns.values():
                u.set_image(not_in_btn)
            else:
                u.set_image(not_in_btn_light)
        for u in defence_buttons:
            if u not in chosen_btns.values():
                u.set_image(def_btn)
            else:
                u.set_image(def_btn_light)
        for u in attack_buttons:
            if u not in chosen_btns.values():
                u.set_image(attack_btn)
            else:
                u.set_image(attack_btn_light)
        screen.blit(hero_choicing, (184, 84))
        draw_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def hero_choice_ffa():
    screen.fill((200, 200, 200))
    group = pygame.sprite.Group()
    draw_group = pygame.sprite.Group()
    mouse = Mouse(group)
    first_row_coords = [(206, 355), (459, 355), (708, 355), (959, 355)]
    second_row_coords = [(207, 432), (460, 432), (710, 432), (959, 432)]

    btn_in1 = Button(in_but, draw_group, x=first_row_coords[0][0], y=first_row_coords[0][1])
    btn_in2 = Button(in_but, draw_group, x=first_row_coords[1][0], y=first_row_coords[1][1])
    btn_in3 = Button(in_but, draw_group, x=first_row_coords[2][0], y=first_row_coords[2][1])
    btn_in4 = Button(in_but, draw_group, x=first_row_coords[3][0], y=first_row_coords[3][1])

    in_buttons = [btn_in1, btn_in2, btn_in3, btn_in4]

    btn_notin1 = Button(not_in_btn, draw_group, x=second_row_coords[0][0], y=second_row_coords[0][1])
    btn_notin2 = Button(not_in_btn, draw_group, x=second_row_coords[1][0], y=second_row_coords[1][1])
    btn_notin3 = Button(not_in_btn, draw_group, x=second_row_coords[2][0], y=second_row_coords[2][1])
    btn_notin4 = Button(not_in_btn, draw_group, x=second_row_coords[3][0], y=second_row_coords[3][1])

    notin_buttons = [btn_notin1, btn_notin2, btn_notin3, btn_notin4]

    result = {0: None, 1: None, 2: None, 3: None}
    chosen_btns = {0: None, 1: None, 2: None, 3: None}

    flag = True

    clock = pygame.time.Clock()
    running = True

    start = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit(pygame.quit())
            if event.type == pygame.MOUSEBUTTONDOWN:
                for t in range(0, 4):
                    if pygame.sprite.collide_mask(mouse, notin_buttons[t]):
                        result[t] = '3'
                        chosen_btns[t] = notin_buttons[t]
                    elif pygame.sprite.collide_mask(mouse, in_buttons[t]):
                        result[t] = '1'
                        chosen_btns[t] = in_buttons[t]
                if start:
                    if pygame.sprite.collide_mask(mouse, start):
                        return result
            if event.type == pygame.MOUSEMOTION:
                mouse.update(event.pos[0], event.pos[1])
        if all(result.values()) and flag:
            flag = False
            start = Button(continue_but, draw_group, x=534, y=585)
        for t in notin_buttons:
            if t not in chosen_btns.values():
                t.set_image(not_in_btn)
            else:
                t.set_image(not_in_btn_light)
        for t in in_buttons:
            if t not in chosen_btns.values():
                t.set_image(in_but)
            else:
                t.set_image(in_but_light)
        screen.blit(hero_choicing2, (184, 84))
        draw_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def controls_choice(result):
    screen.fill((200, 200, 200))
    group = pygame.sprite.Group()
    draw_group = pygame.sprite.Group()
    mouse = Mouse(group)
    first_row_coords = [(208, 341), (458, 341), (708, 341), (958, 341)]
    second_row_coords = [(208, 401), (458, 401), (708, 401), (958, 401)]
    third_row_coords = [(208, 461), (458, 461), (708, 461), (958, 461)]
    fourth_row_coords = [(208, 521), (458, 521), (708, 521), (958, 521)]
    wasd1, arrows1, gp1_1, gp2_1, wasd2, arrows2, gp1_2, gp2_2, gp1_3, wasd3, arrows3, gp2_3, \
        gp2_4, gp1_4, arrows4, wasd4 = [None for _ in range(16)]
    chosen_btns = {0: None, 1: None, 2: None, 3: None}
    ret = {0: None, 1: None, 2: None, 3: None}
    if result[0] != '3':
        wasd1 = Button(wasd, draw_group, x=first_row_coords[0][0], y=first_row_coords[0][1])
        arrows1 = Button(arrows, draw_group, x=second_row_coords[0][0], y=second_row_coords[0][1])
        gp1_1 = Button(gamepad1, draw_group, x=third_row_coords[0][0], y=third_row_coords[0][1])
        gp2_1 = Button(gamepad2, draw_group, x=fourth_row_coords[0][0], y=fourth_row_coords[0][1])
    else:
        ret[0] = 'NOT'
    if result[1] != '3':
        wasd2 = Button(wasd, draw_group, x=first_row_coords[1][0], y=first_row_coords[1][1])
        arrows2 = Button(arrows, draw_group, x=second_row_coords[1][0], y=second_row_coords[1][1])
        gp1_2 = Button(gamepad1, draw_group, x=third_row_coords[1][0], y=third_row_coords[1][1])
        gp2_2 = Button(gamepad2, draw_group, x=fourth_row_coords[1][0], y=fourth_row_coords[1][1])
    else:
        ret[1] = 'NOT'
    if result[2] != '3':
        gp1_3 = Button(gamepad1, draw_group, x=third_row_coords[2][0], y=third_row_coords[2][1])
        wasd3 = Button(wasd, draw_group, x=first_row_coords[2][0], y=first_row_coords[2][1])
        arrows3 = Button(arrows, draw_group, x=second_row_coords[2][0], y=second_row_coords[2][1])
        gp2_3 = Button(gamepad2, draw_group, x=fourth_row_coords[2][0], y=fourth_row_coords[2][1])
    else:
        ret[2] = 'NOT'
    if result[3] != '3':
        gp2_4 = Button(gamepad2, draw_group, x=fourth_row_coords[3][0], y=fourth_row_coords[3][1])
        gp1_4 = Button(gamepad1, draw_group, x=third_row_coords[3][0], y=third_row_coords[3][1])
        arrows4 = Button(arrows, draw_group, x=second_row_coords[3][0], y=second_row_coords[3][1])
        wasd4 = Button(wasd, draw_group, x=first_row_coords[3][0], y=first_row_coords[3][1])
    else:
        ret[3] = 'NOT'
    wasd_btns = [wasd1, wasd2, wasd3, wasd4]
    gp2_btns = [gp2_1, gp2_2, gp2_3, gp2_4]
    gp1_btns = [gp1_1, gp1_2, gp1_3, gp1_4]
    arrows_btns = [arrows1, arrows2, arrows3, arrows4]
    flag = True
    clock = pygame.time.Clock()
    running = True
    start = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit(pygame.quit())
            if event.type == pygame.MOUSEBUTTONDOWN:
                for e in range(0, 4):
                    if wasd_btns[e]:
                        if pygame.sprite.collide_mask(mouse, wasd_btns[e]):
                            ret[e] = 'keyboard_1'
                            chosen_btns[e] = wasd_btns[e]
                    if arrows_btns[e]:
                        if pygame.sprite.collide_mask(mouse, arrows_btns[e]):
                            ret[e] = 'keyboard_2'
                            chosen_btns[e] = arrows_btns[e]
                    if gp1_btns[e]:
                        if pygame.sprite.collide_mask(mouse, gp1_btns[e]):
                            ret[e] = 'joystick'
                            chosen_btns[e] = gp1_btns[e]
                    if gp2_btns[e]:
                        if pygame.sprite.collide_mask(mouse, gp2_btns[e]):
                            ret[e] = 'joystick_2'
                            chosen_btns[e] = gp2_btns[e]
                    if start:
                        if pygame.sprite.collide_mask(mouse, start):
                            return ret
            if event.type == pygame.MOUSEMOTION:
                mouse.update(event.pos[0], event.pos[1])
        if all(ret.values()) and flag:
            flag = False
            start = Button(start_btn, draw_group, x=534, y=585)
        for e in wasd_btns:
            if e:
                if e not in chosen_btns.values():
                    e.set_image(wasd)
                else:
                    e.set_image(wasd_light)
        for e in arrows_btns:
            if e:
                if e not in chosen_btns.values():
                    e.set_image(arrows)
                else:
                    e.set_image(arrows_light)
        for e in gp1_btns:
            if e:
                if e not in chosen_btns.values():
                    e.set_image(gamepad1)
                else:
                    e.set_image(gamepad1_light)
        for e in gp2_btns:
            if e:
                if e not in chosen_btns.values():
                    e.set_image(gamepad2)
                else:
                    e.set_image(gamepad2_light)
        screen.blit(control_choice, (184, 84))
        draw_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def add_players_ctf(players, controls, first_team, second_team):
    print(first_team[0][0], first_team[0][1])
    players_list = list()
    if players[0] == '1':
        players_list.append(Jasper(prototype.groups_data, x=100, y=100,
                            controller=controls[0], color="red", team='2', screen=prototype.screen,
                            cool_down=2000, recovery_places=first_team))
    elif players[0] == '2':
        players_list.append(Jasper(prototype.groups_data, x=100, y=100,
                            controller=controls[0], color="red", team='1', screen=prototype.screen,
                            cool_down=2000, recovery_places=second_team))

    if players[1] == '1':
        players_list.append(Vincent(prototype.groups_data, x=first_team[0][0], y=first_team[0][1],
                            controller=controls[1], color="blue", team='2', screen=prototype.screen,
                            cool_down=3000, recovery_places=first_team))
    elif players[1] == '2':
        players_list.append(Vincent(prototype.groups_data, x=second_team[0][0], y=second_team[0][1],
                            controller=controls[1], color="blue", team='1', screen=prototype.screen,
                            cool_down=3000, recovery_places=second_team))

    if players[2] == '1':
        players_list.append(Adam(prototype.groups_data, x=first_team[0][0], y=first_team[0][1],
                            controller=controls[2], color="yellow", team='2', screen=prototype.screen,
                            cool_down=1000, recovery_places=first_team))
    elif players[2] == '2':
        players_list.append(Adam(prototype.groups_data, x=second_team[0][0], y=second_team[0][1],
                            controller=controls[2], color="yellow", team='1', screen=prototype.screen,
                            cool_down=1000, recovery_places=second_team))

    if players[3] == '1':
        players_list.append(Guido(prototype.groups_data, x=first_team[0][0], y=first_team[0][1],
                            controller=controls[3], color="green", team='2', screen=prototype.screen,
                            cool_down=4000, recovery_places=first_team))
    elif players[3] == '2':
        players_list.append(Guido(prototype.groups_data, x=second_team[0][0], y=second_team[0][1],
                            controller=controls[3], color="green", team='1', screen=prototype.screen,
                            cool_down=4000, recovery_places=second_team))
    return players_list


def add_players_ffa(players, controls, places):
    players_list = list()
    shuffle(places)
    if players[0] != '3':
        players_list.append(Jasper(prototype.groups_data, x=places[0][0], y=places[0][1],
                            controller=controls[0], color="red", lives=5, screen=prototype.screen,
                            cool_down=2000, recovery_places=places))
    shuffle(places)
    if players[1] != '3':
        players_list.append(Vincent(prototype.groups_data, x=places[0][0], y=places[0][1],
                            controller=controls[1], color="blue", lives=5, screen=prototype.screen,
                            cool_down=3000, recovery_places=places))
    shuffle(places)
    if players[2] != '3':
        players_list.append(Adam(prototype.groups_data, x=places[0][0], y=places[0][1],
                            controller=controls[2], color="yellow", lives=5, screen=prototype.screen,
                            cool_down=1000, recovery_places=places))
    shuffle(places)
    if players[3] != '3':
        players_list.append(Guido(prototype.groups_data, x=places[0][0], y=places[0][1],
                            controller=controls[3], color="green", lives=5, screen=prototype.screen,
                            cool_down=4000, recovery_places=places))
    return players_list


if __name__ == '__main__':
    menu()
    mode = mode_choice()
    while 1:
        if mode == 'FFA':
            heroes = hero_choice_ffa()
            control = controls_choice(heroes)
            prototype = FFA()
            spots = create_field(load_level('levelffa.txt'), prototype, 'FFA')
            player = add_players_ffa(heroes, control, spots)
            prototype.add_players(player)
            prototype.play()
        else:
            heroes = hero_choice_ctf()
            control = controls_choice(heroes)
            prototype = CTF()
            team1, team2 = create_field(load_level('levelctf.txt'), prototype, 'CTF')
            player = add_players_ctf(heroes, control, team1, team2)
            prototype.add_players(player)
            for game_object in prototype.groups_data["game_stuff"]:
                if game_object.__class__.__name__ == "TeamFlag":
                    game_object.end_function = prototype.end_of_game_session
            prototype.play()
        if prototype.result == 'МЕНЮ':
            menu()
            mode = mode_choice()
        elif prototype.result == 'ЗАНОВО':
            if mode == 'FFA':
                prototype = FFA()
                list_of_players = create_field(load_level('levelffa.txt'), prototype, 'FFA')
                prototype.add_players(list_of_players)
                prototype.play()
            else:
                prototype = CTF()
                list_of_players = create_field(load_level('levelctf.txt'), prototype, 'CTF')
                prototype.add_players(list_of_players)
                for game_object in prototype.groups_data["game_stuff"]:
                    if game_object.__class__.__name__ == "TeamFlag":
                        game_object.end_function = prototype.end_of_game_session
