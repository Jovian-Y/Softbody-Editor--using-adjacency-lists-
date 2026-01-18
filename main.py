import sys
import pygame
from pygame.locals import *

# switch between force based springs and distance based spring physics here.
#from softbody_force_based import SoftBody
from softbody_position_based import SoftBody

# initialize, clock
pygame.init()
clock = pygame.time.Clock()
FPS = 60

# screen dimensions/aspect ratios
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h
aspect_ratio = display_width / display_height

screen_mode = (int(aspect_ratio * display_height / 2), int(display_height / 2))
screen = pygame.display.set_mode(screen_mode, pygame.RESIZABLE)

# internal game resolution
display_mode = (int(aspect_ratio * 312), 312)
display = pygame.Surface(display_mode)
pygame.display.set_caption("SOFTBODY EDITOR")

# collection of SoftBody objects
softbodies = []

# cloth-like SoftBodies
softbodies.append(SoftBody(display, (10,10), 7, (100,20,255), "softbody_data/cloth1.json"))
softbodies.append(SoftBody(display, (70,10), 7, (255,255,200), "softbody_data/cloth2.json"))
softbodies.append(SoftBody(display, (140,10), 7, (0,255,200), "softbody_data/cloth3.json"))
softbodies.append(SoftBody(display, (190,10), 7, (255,100,150), "softbody_data/cloth4.json"))
# rope-like Softbodies
softbodies.append(SoftBody(display, (220,10), 7, (30,100,100), "softbody_data/rope1.json"))
softbodies.append(SoftBody(display, (270,10), 7, (0,150,150), "softbody_data/rope2.json"))
softbodies.append(SoftBody(display, (290,10), 7, (255,150,100), "softbody_data/rope3.json"))
softbodies.append(SoftBody(display, (310,10), 7, (255,150,150), "softbody_data/rope4.json"))
# spider web, net, bridge, mobile, chandelier: other
softbodies.append(SoftBody(display, (10,100), 7, (255,255,255), "softbody_data/web.json"))
softbodies.append(SoftBody(display, (135,100), 7, (150,75,100), "softbody_data/net.json"))
softbodies.append(SoftBody(display, (240,100), 7, (150,75,200), "softbody_data/bridge.json"))
softbodies.append(SoftBody(display, (430,100), 7, (25,55,200), "softbody_data/mobile.json"))
# 4th row
softbodies.append(SoftBody(display, (10,230), 7,(53,74,43), "softbody_data/rag.json"))
softbodies.append(SoftBody(display, (60,230), 5,(200,100,100), "softbody_data/hang.json"))
softbodies.append(SoftBody(display, (150,200), 7,(114,116,255), "softbody_data/chandelier.json"))
softbodies.append(SoftBody(display, (210,200), 5,(0,100,200), "softbody_data/centered.json"))
softbodies.append(SoftBody(display, (255,200), 3,(50,0,200), "softbody_data/components1.json"))
softbodies.append(SoftBody(display, (320,200), 3,(200,0,200), "softbody_data/components2.json"))

# external forces, universal gravity
wind = 0    
gravity = 0.1
force = {"x": 0, "y": 0}

# text
font = pygame.font.Font(None, 25)
do_render = {'node': True, 'spring': True, 'fill': True}

# main loop
while True:
    # render ratio
    window_width, window_height = pygame.display.get_window_size()
    screen_display_ratio_x = display.get_width()/window_width
    screen_display_ratio_y = display.get_height()/window_height
            
    # mouse pos
    mouse_coords = pygame.mouse.get_pos()
    mouse_coords = (list(mouse_coords))

    mouse_coords[0] *= screen_display_ratio_x
    mouse_coords[1] *= screen_display_ratio_y

    # eventhandler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                force['x'] = -0.1
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                force['y'] = -0.1
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                force['y'] = 0.1
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                force['x'] = 0.1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                force['x'] = 0
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                force['y'] = 0
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                force['y'] = 0
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                force['x'] = 0

            if event.key == pygame.K_1:
                do_render['node'] = not do_render['node']
            if event.key == pygame.K_2:
                do_render['spring'] = not do_render['spring']
            if event.key == pygame.K_3:
                do_render['fill'] = not do_render['fill']


    # rendering
    display.fill((10,10,20))

    # update all softbodies
    for s in softbodies:
        s.apply_force(force['x'], force['y'])
        s.update(wind, gravity)
        # toggle these three on/off for fun
        # ----------
        if do_render['fill'] == True:
            s.fill()
        if do_render['spring'] == True:
            s.render_spring()
        if do_render['node'] == True:
            s.render_node()
        # ----------

    # wind
    wind += 0.01

    # text
    display.blit(font.render(f"1: node: {do_render['node']}", False, (255,150,100)), (10,10))
    display.blit(font.render(f"2: spring: {do_render['spring']}", False, (255,150,100)), (10,30))
    display.blit(font.render(f"3: fill: {do_render['fill']}", False, (255,150,100)), (10,50))

    # ---
    screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
    pygame.display.update()
    clock.tick(FPS)