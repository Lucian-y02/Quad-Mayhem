from os import path

import pygame


pygame.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, group, **kwargs):
        super(Player, self).__init__(group)
        self.image = pygame.Surface((40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = kwargs.get("x", 0)
        self.rect.y = kwargs.get("y", 0)
        self.speed = kwargs.get("speed", 5)

    def update(self):
        key = pygame.key.get_pressed()
        move_x = move_y = 0

        if key[pygame.K_a]:
            move_x -= self.speed
        if key[pygame.K_d]:
            move_x += self.speed

        self.rect.move_ip(move_x, move_y)
