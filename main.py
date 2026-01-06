import sys
import pygame
from pygame.locals import *

from softbody import SoftBody

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
softbodies.append(SoftBody(display, (20,20), 7,(100,20,255), "softbody_data/goal.json"))
softbodies.append(SoftBody(display, (100,20), 10,(255,0,100), "softbody_data/flag.json"))
softbodies.append(SoftBody(display, (200,20), 10,(200,100,100), "softbody_data/ball.json"))
softbodies.append(SoftBody(display, (300,20), 10,(255,255,255), "softbody_data/mobile.json"))
softbodies.append(SoftBody(display, (200,100), 5,(50,0,200), "softbody_data/randomplacementtest.json"))


# external forces
wind = 0
force = {"x": 0, "y": 0}

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

    # rendering
    display.fill((10,10,20))

    wind += 0.01

    # update all softbodies
    for s in softbodies:
        s.update(wind, force['x'], force['y'])
        # toggle these three on/off for fun
        # ----------
        s.fill()
        s.render_spring()
        #s.render_node()
        # ----------

    #
    screen.blit(pygame.transform.scale(display, (screen.get_width(), screen.get_height())), (0,0))
    pygame.display.update()
    clock.tick(FPS)