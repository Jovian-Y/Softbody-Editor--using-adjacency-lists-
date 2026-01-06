import pygame

def collidePoint(rect, point):
    if(
            point[0] <= rect.x + rect.width   #right
        and point[0] >= rect.x                #left
        and point[1] <= rect.y + rect.height  #top
        and point[1] >= rect.y                #bottom
        ):   
            return True
    return False