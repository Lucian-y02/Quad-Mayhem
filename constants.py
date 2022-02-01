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
wasd = Table('images').get_image(18)[18].convert()
arrows = Table('images').get_image(19)[19].convert()
gamepad1 = Table('images').get_image(20)[20].convert()
gamepad2 = Table('images').get_image(21)[21].convert()
wasd_light = Table('images').get_image(22)[22].convert()
arrows_light = Table('images').get_image(23)[23].convert()
gamepad1_light = Table('images').get_image(24)[24].convert()
gamepad2_light = Table('images').get_image(25)[25].convert()
control_choice = Table('images').get_image(26)[26].convert()
continue_but = Table('images').get_image(27)[27].convert()
hero_choicing2 = Table('images').get_image(28)[28].convert()
in_but = Table('images').get_image(29)[29].convert()
in_but_light = Table('images').get_image(30)[30].convert()
machine_gun = Table('images').get_image(31)[31].convert()
sub_machine_gun = Table('images').get_image(32)[32].convert()
semi_automatic_sniper_rifle = Table('images').get_image(33)[33].convert()
sniper_rifle = Table('images').get_image(58)[58].convert()

jasper_animation = list()
adam_animation = list()
vincent_animation = list()
guido_animation = list()

for i in range(35, 40):
    a = Table('images').get_image(i)[i].convert()
    a.set_colorkey('black')
    jasper_animation.append(a)

for i in range(41, 46):
    a = Table('images').get_image(i)[i].convert()
    a.set_colorkey('black')
    adam_animation.append(a)

for i in range(47, 52):
    a = Table('images').get_image(i)[i].convert()
    a.set_colorkey('black')
    vincent_animation.append(a)

for i in range(53, 58):
    a = Table('images').get_image(i)[i].convert()
    a.set_colorkey('black')
    guido_animation.append(a)

normal_gas.set_colorkey('white')
toxic_gas.set_colorkey('white')
pause_btn.set_colorkey('white')
machine_gun.set_colorkey('black')
sub_machine_gun.set_colorkey('black')
semi_automatic_sniper_rifle.set_colorkey('black')
sniper_rifle.set_colorkey('black')

images = [normal_gas, toxic_gas]

btn1_coords = (418, 347)
btn2_coords = (756, 347)
btn3_coords = (418, 448)
btn4_coords = (754, 448)
