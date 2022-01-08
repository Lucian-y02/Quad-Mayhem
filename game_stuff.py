from random import randint
from math import asin, degrees

import pygame


pygame.init()


class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups: dict, **kwargs):
        super(Weapon, self).__init__(groups["weapons"])
        self.image = pygame.Surface(kwargs.get("size", (65, 16)))
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.mirror = kwargs.get("mirror", False)

        self.walls = groups["walls_horizontal"]
        self.bullet_group = groups["bullets"]

        # Кем используется
        self.user = kwargs.get("user", None)

        self.recoil = kwargs.get("recoil", 1)  # Отдача

        # Гравитация
        self.gravity_force = kwargs.get("gravity", 8)  # Ускорение свободного падения
        self.gravity_count = 0
        self.gravity = 0  # Скорость падения

        self.shot_timer = 0

    def update(self):
        if not self.user:
            self.shot_timer = 0
            move_y = self.gravity

            # Столкновение
            for wall in self.walls:
                if self.rect.colliderect(wall.rect):
                    self.gravity = 0
                    self.gravity_count = 0
                    self.rect.y = wall.rect.y - self.rect.height + 1
                    move_y = 0

            # Смещение
            self.rect.move_ip(0, move_y)

            # Влияния ускорения свободного падения
            self.gravity_count += 1
            if self.gravity_count % 6 == 0:
                self.gravity += self.gravity_force if self.gravity <= self.gravity_force * 3 else 0
                self.gravity_count = 0
        else:
            self.shot_timer -= 1 if self.shot_timer > 0 else 0
            if not self.mirror:
                self.rect.x = self.user.rect.x - 7
            else:
                self.rect.x = self.user.rect.x - (self.rect.width - 7 - self.user.rect.width)
            self.rect.y = self.user.rect.y + 20

    def shot(self):
        if self.shot_timer == 0:
            if not self.mirror:
                Bullet(self.bullet_group, x=self.rect.x + self.rect.width,
                       y=self.rect.y + self.rect.height // 2, mirror=False)
                self.user.recoil(-self.recoil)
            else:
                Bullet(self.bullet_group, x=self.rect.x - 32,
                       y=self.rect.y + self.rect.height // 2, mirror=True)
                self.user.recoil(self.recoil)
            self.shot_timer = 20


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Bullet, self).__init__(group)
        self.image = pygame.Surface(kwargs.get("size", (32, 2)))
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)

        self.scatter_write = kwargs.get("scatter", (-2, 2))
        self.scatter = randint(self.scatter_write[0], self.scatter_write[1])
        self.speed = kwargs.get("speed", 32) * (-1 if kwargs.get("mirror", False) else 1)

        # self.image = pygame.transform.rotate(self.image,
        #                                      degrees(asin(self.scatter /
        #                                                   ((self.speed ** 2 +
        #                                                     self.scatter ** 2) ** (1 / 2)))))

    def update(self):
        self.rect.move_ip(self.speed, self.scatter)
