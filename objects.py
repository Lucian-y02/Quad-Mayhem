import pygame


pygame.init()


class Wall(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Wall, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("wall_size", (32, 32)))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)


class Teleport1(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Teleport1, self).__init__()
        self.image = pygame.Surface(kwargs.get("teleport_size", (32, 64)))
        self.image.fill('blue')
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


class Teleport2(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Teleport2, self).__init__()
        self.image = pygame.Surface(kwargs.get("teleport_size", (32, 64)))
        self.image.fill('blue')
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.teleports = list()
        self.timer2 = self.timer = kwargs.get("cooldown", 120)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player, self).__init__(groups["players"])
        self.image = pygame.Surface((40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.groups = groups
        self.speed = kwargs.get("speed", 5)  # Скорость персонажа
        self.gravity = kwargs.get("gravity", 10)  # Значение гравитации
        self.resistance = 0  # Значение реакции опоры
        self.jump_force_count = kwargs.get("jump_force", 10)  # Начальное значение jump_force
        self.jump_force = 0  # Сила прыжка
        self.save_place = (self.rect.x, self.rect.y)
        self.mask = pygame.mask.from_surface(self.image)  # Маска игрока

    def update(self):
        key = pygame.key.get_pressed()
        move_x = 0
        # Проверка на столкновение
        for wall in self.groups["walls"]:
            if self.rect.colliderect(wall):
                self.resistance = -self.gravity
        if not pygame.sprite.spritecollideany(self, self.groups["walls"]):
            self.resistance = 0
        # Прыжок
        self.jump_force -= 1 if self.jump_force > 0 else 0
        if key[pygame.K_w] and self.resistance:
            self.jump_force = self.jump_force_count
        # Передвижение вправо и влево
        if key[pygame.K_a]:
            move_x -= self.speed
            self.save_place = (self.rect.x, self.rect.y)
        if key[pygame.K_d]:
            move_x += self.speed
            self.save_place = (self.rect.x, self.rect.y)
        # Смещение персонажа
        self.rect.move_ip(move_x,
                          self.resistance + self.gravity - (self.jump_force ** 1.2))


class Player2(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player2, self).__init__(groups["players"])
        self.image = pygame.Surface((40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.groups = groups
        self.speed = kwargs.get("speed", 5)  # Скорость персонажа
        self.gravity = kwargs.get("gravity", 10)  # Значение гравитации
        self.resistance = 0  # Значение реакции опоры
        self.jump_force_count = kwargs.get("jump_force", 10)  # Начальное значение jump_force
        self.jump_force = 0  # Сила прыжка
        self.save_place = (self.rect.x, self.rect.y)
        self.mask = pygame.mask.from_surface(self.image)  # Маска игрока

    def update(self):
        key = pygame.key.get_pressed()
        move_x = 0
        # Проверка на столкновение
        for wall in self.groups["walls"]:
            if self.rect.colliderect(wall):
                self.resistance = -self.gravity
        if not pygame.sprite.spritecollideany(self, self.groups["walls"]):
            self.resistance = 0
        # Прыжок
        self.jump_force -= 1 if self.jump_force > 0 else 0
        if key[pygame.K_UP] and self.resistance:
            self.jump_force = self.jump_force_count
        # Передвижение вправо и влево
        if key[pygame.K_LEFT]:
            move_x -= self.speed
            self.save_place = (self.rect.x, self.rect.y)
        if key[pygame.K_RIGHT]:
            move_x += self.speed
            self.save_place = (self.rect.x, self.rect.y)
        # Смещение персонажа
        self.rect.move_ip(move_x,
                          self.resistance + self.gravity - (self.jump_force ** 1.2))
