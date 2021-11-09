from os import write
import pygame
from pygame.locals import *

score_screen = True
font = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()
FRAMERATE = 10


def text_objects(text):
    """Function that returns data of text"""
    textSurface = font.render(text, True, (255, 255, 255))
    return textSurface, textSurface.get_rect()


def write_to_screen(screen, msg, y_displacement=0):
    """Function to write text on screen"""
    textSurface, textRect = text_objects(msg)
    textRect.center = (screen.get_rect().center[0], screen.get_rect().center[1] + y_displacement)
    screen.blit(textSurface, textRect)


def display_screen(screen, score, won):
    # Handle events for quit and return to game
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # Return values for score_screen and running variables in main file
            return (False, False, False)

        if event.type == KEYDOWN and event.key == K_RETURN:
            return (False, True, False)

    # Fill screen with black
    screen.fill((0, 0, 0))

    if won:
        write_to_screen(screen, "YOU WIN", -50)
    else:
        write_to_screen(screen, "GAME OVER", -50)
    write_to_screen(screen, f'Score: {score}', 50)
    write_to_screen(screen, "Press enter to continue", screen.get_height()/2 - font.get_linesize())

    pygame.display.flip()
    clock.tick(FRAMERATE)

    return (True, True, won)
