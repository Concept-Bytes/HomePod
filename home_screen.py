import pygame
import math
import sys
import os
import time
from dotenv import load_dotenv
from multiprocessing import Process

# Load environment variables from .env file
load_dotenv()

class AppCircle:
    def __init__(self, center, app_index, screen_size):
        self.center = center
        self.radius = min(screen_size) // 10  # Example radius
        self.app_index = app_index
        self.image = self.load_image(app_index)
        self.text = f'App {app_index}'

    def load_image(self, app_index):
        path = f'./apps/app_{app_index}/app_{app_index}.png'
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (2 * self.radius, 2 * self.radius))
            return img
        except FileNotFoundError:
            print(f"Image file not found: {path}")
            return None

    def draw(self, screen):
        if self.image:
            top_left = (self.center[0] - self.radius, self.center[1] - self.radius)
            screen.blit(self.image, top_left)
        else:
            pygame.draw.circle(screen, (255, 255, 255), self.center, self.radius)
            font = pygame.font.Font(None, 32)
            text_surface = font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return math.hypot(pos[0] - self.center[0], pos[1] - self.center[1]) <= self.radius

def create_circles(screen_size):
    circles = []
    num_circles = 8
    angle_step = 360 / num_circles
    center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
    radius = min(screen_size) // 2.6

    for i in range(num_circles):
        angle = math.radians(angle_step * i)
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        circles.append(AppCircle((x, y), i + 1, screen_size))
    return circles

def fade_text_in(screen, text_surfaces, text_rects, background, circles, duration=1.0):
    """Fade the text in."""
    for alpha in range(0, 256, int(256 / (duration * 60))):
        screen.blit(background, (0, 0))
        for circle in circles:
            circle.draw(screen)
        for text_surface, text_rect in zip(text_surfaces, text_rects):
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(int(1000 / 60))

def fade_text_out(screen, text_surfaces, text_rects, background, circles, duration=1.0):
    """Fade the text out."""
    for alpha in range(255, -1, -int(256 / (duration * 60))):
        screen.blit(background, (0, 0))
        for circle in circles:
            circle.draw(screen)
        for text_surface, text_rect in zip(text_surfaces, text_rects):
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(int(1000 / 60))

def create_text_surfaces(response, font, screen_width, margin):
    words = response.split()
    lines = []
    current_line = []
    for word in words:
        test_line = current_line + [word]
        test_surface = font.render(' '.join(test_line), True, (255, 255, 255))
        if test_surface.get_width() <= screen_width - 2 * margin:
            current_line = test_line
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))  # Add the last line

    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
    total_height = sum(surface.get_height() for surface in text_surfaces)
    start_y = (screen.get_height() - total_height) // 2

    text_rects = [surface.get_rect(center=(screen_width // 2, start_y + i * surface.get_height())) for i, surface in enumerate(text_surfaces)]

    return text_surfaces, text_rects

def display_response(screen, response, background, circles):
    font = pygame.font.Font(None, 36)  # Adjust font size to fit better
    margin = screen.get_width() // 4  # Increase the margin to narrow the text area
    text_surfaces, text_rects = create_text_surfaces(response, font, screen.get_width(), margin)
    fade_text_in(screen, text_surfaces, text_rects, background, circles)
    pygame.time.delay(15000)  # Display for 15 seconds
    fade_text_out(screen, text_surfaces, text_rects, background, circles)

def run_home_screen(screen):
    screen_size = screen.get_size()
    background = pygame.image.load('./resources/background.jpg')
    background = pygame.transform.scale(background, screen_size)
    
    circles = create_circles(screen_size)
    
    voice_assistant_process = Process(target=start_voice_assistant)
    voice_assistant_process.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for circle in circles:
                    if circle.is_clicked(event.pos):
                        app_index = circles.index(circle) + 1
                        app_module_name = f'apps.app_{app_index}.app_{app_index}'
                        mod = __import__(app_module_name, fromlist=[''])
                        mod.run(screen)

        screen.blit(background, (0, 0))

        for circle in circles:
            circle.draw(screen)
        pygame.display.flip()

        # Check response.txt for any response
        if os.path.exists("response.txt"):
            with open("response.txt", "r") as file:
                response = file.read().strip()
            if response:
                display_response(screen, response, background, circles)
                # Clear the response from the file
                open("response.txt", "w").close()

        pygame.time.delay(1)

def start_voice_assistant():
    import jarvis
    jarvis.run_voice_assistant()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))
    run_home_screen(screen)
