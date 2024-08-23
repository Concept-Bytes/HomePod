import pygame
from home_screen import run_home_screen

def main():
    pygame.init()
    # Use the current screen resolution for fullscreen mode
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption('Home Screen with App Circles')
    run_home_screen(screen)

if __name__ == '__main__':
    main()
