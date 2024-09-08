import pygame
import math
import sys
import os
import assist
import time
import tools
from RealtimeSTT import AudioToTextRecorder

class AppCircle:
    def __init__(self, center, app_index, screen_size):
        self.center = center
        self.radius = min(screen_size) // 10
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
    lines.append(' '.join(current_line))

    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
    total_height = sum(surface.get_height() for surface in text_surfaces)
    start_y = (screen.get_height() - total_height) // 2

    text_rects = [surface.get_rect(center=(screen_width // 2, start_y + i * surface.get_height())) for i, surface in enumerate(text_surfaces)]

    return text_surfaces, text_rects

def display_response(screen, response, background, circles):
    font = pygame.font.Font(None, 36)
    margin = screen.get_width() // 4
    text_surfaces, text_rects = create_text_surfaces(response, font, screen.get_width(), margin)
    fade_text_in(screen, text_surfaces, text_rects, background, circles)
    pygame.time.delay(15000)
    fade_text_out(screen, text_surfaces, text_rects, background, circles)

def apply_blur_and_ring(screen, blue_ring_thickness=100):
    """Apply a blur effect to the whole screen and a subtle transparent blue ring."""
    # Create a blurred screen copy
    screen_copy = pygame.Surface(screen.get_size())
    screen_copy.blit(screen, (0, 0))

    for _ in range(10):  # Simulate blur by scaling down and back up
        screen_copy = pygame.transform.smoothscale(screen_copy, (screen.get_width() // 2, screen.get_height() // 2))
        screen_copy = pygame.transform.smoothscale(screen_copy, screen.get_size())

    # Draw the blurred screen
    screen.blit(screen_copy, (0, 0))

    # Create a transparent surface for the gradient ring effect
    ring_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # Define the gradient effect
    center = (screen.get_width() // 2, screen.get_height() // 2)
    outer_radius = screen.get_width() // 2
    inner_radius = outer_radius - blue_ring_thickness

    for i in range(outer_radius, inner_radius, -1):
        # Calculate the alpha value for transparency that fades towards the center
        alpha = int(128 * (i - inner_radius) / blue_ring_thickness)
        pygame.draw.circle(ring_surface, (173, 216, 230, alpha), center, i)

    screen.blit(ring_surface, (0, 0))

def fade_text_with_blur(screen, text_surfaces, text_rects, circles, background, blur=True, duration=0.2, fade_in=True):
    """Fade in or out the text with optional blur effect."""
    step = int(256 / (duration * 60))
    if not fade_in:
        step = -step

    alpha_values = range(0, 256, step) if fade_in else range(255, -1, step)
    for alpha in alpha_values:
        screen.blit(background, (0, 0))  # Draw the background first

        # Draw circles (apps) on top of the background
        for circle in circles:
            circle.draw(screen)

        # Apply blur and ring effect if needed
        if blur:
            apply_blur_and_ring(screen, blue_ring_thickness=100)

        # Fade in or out text surfaces
        for text_surface, text_rect in zip(text_surfaces, text_rects):
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.delay(int(1000 / 60))

def display_query(screen, query, circles, background):
    """Display the query with blur and ring effect, and fade-in the text."""
    font = pygame.font.Font(None, 36)
    margin = screen.get_width() // 4
    text_surfaces, text_rects = create_text_surfaces(query, font, screen.get_width(), margin)

    # Fade in the text with the blur effect
    fade_text_with_blur(screen, text_surfaces, text_rects, circles, background, blur=True, fade_in=True)
    return text_surfaces, text_rects

def display_response(screen, response, circles, background):
    """Display the response with blur and ring effect, and fade-in the text."""
    font = pygame.font.Font(None, 36)
    margin = screen.get_width() // 4
    text_surfaces, text_rects = create_text_surfaces(response, font, screen.get_width(), margin)

    # Fade in the response with the blur effect
    fade_text_with_blur(screen, text_surfaces, text_rects, circles, background, blur=True, fade_in=True)
    return text_surfaces, text_rects

def run_home_screen(screen,):
    screen_size = screen.get_size()
    background = pygame.image.load('./resources/background.jpg')
    background = pygame.transform.scale(background, screen_size)
    
    circles = create_circles(screen_size)
    
    running = True
    query_displayed = False
    response_displayed = False
    query_surfaces = []
    query_rects = []
    response_surfaces = []
    response_rects = []


    recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.4)
    hot_words = ["jarvis", "alexa"]
    skip_hot_word_check = False
    print("Say something...")


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

        current_text = recorder.text()
        print(current_text)
        if any(hot_word in current_text.lower() for hot_word in hot_words) or skip_hot_word_check:
            if current_text:
                print("User: " + current_text)

                # Start the blur effect and display the query
                query_surfaces, query_rects = display_query(screen, current_text, circles, background)
                query_displayed = True

                recorder.stop()
                current_text = current_text + " " + time.strftime("%Y-%m-%d %H-%M-%S")
                response = assist.ask_question_memory(current_text)
                print(response)
                speech = response.split('#')[0]
                

                if query_displayed:
                    # Immediately fade out the query much faster
                    fade_text_with_blur(screen, query_surfaces, query_rects, circles, background, blur=True, duration=0.1, fade_in=False)
                    query_displayed = False

                response_surfaces, response_rects = display_response(screen, response, circles, background)
                response_displayed = True

                done = assist.TTS(speech)
                # skip_hot_word_check = True if "?" in response else False
                if len(response.split('#')) > 1:
                    command = response.split('#')[1]
                    tools.parse_command(command)
                recorder.start()


            

        # After the response has been displayed for some time, fade everything out
        if response_displayed:
            pygame.time.delay(3000)  # Shorter delay to speed up transition
            # Fade out the response and blur effect
            fade_text_with_blur(screen, response_surfaces, response_rects, circles, background, blur=True, duration=0.5, fade_in=False)
            response_displayed = False

        # Draw the normal screen when there is no query or response to show
        if not query_displayed and not response_displayed:
            screen.blit(background, (0, 0))  # Draw background first
            for circle in circles:  # Then draw apps (circles)
                circle.draw(screen)

        pygame.display.flip()
        pygame.time.delay(1)






if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))

    # Run the home screen
    run_home_screen(screen,)
