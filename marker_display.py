import pygame
from pygame.locals import *
from time import time
import os

WIDTH = 1920
HEIGHT = 1080
SCALE = 125

def set_x(x):
        return(x*WIDTH - SCALE*0.5)

def set_y(y):
        return(HEIGHT - (y*HEIGHT + SCALE*0.5))

def start(accuracy = False):
        position = 1920, 0
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])
        pygame.display.init()
        windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME, 32)
        windowSurface.fill((70,70,70))

        #pygame.display.toggle_fullscreen()
        img = pygame.image.load("marker.png")
        img = pygame.transform.smoothscale(img, (SCALE,SCALE))
        end = False
        pygame.mouse.set_visible(False)

        x = 10000
        y = 10000
        windowSurface.blit(img, (set_x(x), set_y(y)))

        show_time = 2.75
        intermission = 0.25

        sites = [(.3, 0.90), (.5, 0.90), (.7, .90),
                (.1,.7),(.3, .7),(.5, .7),(.7, .7),(0.9,.7),
                (.1,.5),(.3, .5),(.5,.5),(.7,.5),(.9,.5),
                (.1,.3),(.3,.3),(.5,.3),(.7,.3),(.9,.3),
                (.1,.10),(.3, .10),(.5,.10),(.7,.10),(.9,.10)]
        if accuracy:
                sites = [(.5, .8),
                        (.25,.5), (.5,.5), (.75,.5),
                        (.35,.3),(.65,.3)]
        set_time = -100
        while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        end = True
                t = time()

                if t > set_time + show_time + intermission and sites:
                        loc = sites.pop(0)
                        x = loc[0]
                        y = loc[1]
                        set_time = t
                elif t > set_time + show_time + intermission:
                        pygame.quit()
                        end = True
                if end:
                        break
                windowSurface.fill((70,70,70))
                if t > set_time + intermission:
                    windowSurface.blit(img, (set_x(x), set_y(y)))
                pygame.display.flip()
                pygame.time.wait(10)
        return

if __name__ == '__main__':
    start()
