import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Player, self).__init__(groups["players"])
        self.image = pygame.Surface((40, 60))
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        self.speed = kwargs.get("speed", 5)  # Скорость персонажа
        self.groups = groups  # Словарь групп српайтов

        # Столкновение
        self.stay = False  # Определяет находится ли игрок на какой-либо опоре

        # Падение
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        # Прыжок
        self.jump_force = kwargs.get("jump", 12)

    def update(self):
        # Показатели смещения
        move_x = 0
        move_y = self.gravity - (self.jump_force if not self.stay else 0)

        # Столкновения
        for wall in self.groups["walls_horizontal"]:
            if self.rect.colliderect(wall):
                if self.rect.y < wall.rect.y:
                    self.stay = True
                    self.gravity = 0
                    self.gravity_count = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1
                    move_y = 0

        # Нажатия
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            move_x -= self.speed
        if key[pygame.K_d]:
            move_x += self.speed
        if key[pygame.K_SPACE] and self.stay:
            move_y -= self.jump_force
            self.stay = False

        # Смещение персонажа
        self.rect.move_ip(move_x, move_y)

        # Влияния ускорения свободного падения
        self.gravity_count += 1
        if self.gravity_count % 8 == 0:
            self.gravity += self.gravity_force if self.gravity <= self.gravity * 3 else 0
            self.gravity_count = 0
