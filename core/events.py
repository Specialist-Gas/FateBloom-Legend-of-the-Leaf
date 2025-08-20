import pygame

def is_left_click(event):
    return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
