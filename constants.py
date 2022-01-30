import pygame
from database import DBase, Table


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
pause = Table('images').get_image(9)[9].convert()
hero_choicing = Table('images').get_image(10)[10].convert()
start_btn = Table('images').get_image(11)[11].convert()
not_in_btn = Table('images').get_image(12)[12].convert()
def_btn = Table('images').get_image(13)[13].convert()
attack_btn = Table('images').get_image(14)[14].convert()
not_in_btn_light = Table('images').get_image(15)[15].convert()
def_btn_light = Table('images').get_image(16)[16].convert()
attack_btn_light = Table('images').get_image(17)[17].convert()
normal_gas.set_colorkey('white')
toxic_gas.set_colorkey('white')
pause_btn.set_colorkey('white')
images = [normal_gas, toxic_gas]

btn1_coords = (418, 347)
btn2_coords = (756, 347)
btn3_coords = (418, 448)
btn4_coords = (754, 448)
