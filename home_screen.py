import pygame
import math
import sys
import os
import assist
import time
import tools
from RealtimeSTT import AudioToTextRecorder
import threading

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

def apply_blur_ring_and_text(screen, text, blue_ring_thickness=100):
    """Apply a simplified blur effect to the screen, draw a subtle transparent blue ring, and overlay text."""
    
    # Create a semi-transparent surface for the blur effect
    blur_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    blur_surface.fill((0, 0, 0, 128))  # Fill with semi-transparent black (adjust alpha for blur intensity)

    # Draw the blurred screen back onto the main screen
    screen.blit(blur_surface, (0, 0))

    # Create a transparent surface for the gradient ring effect
    ring_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # Define the gradient effect
    center = (screen.get_width() // 2, screen.get_height() // 2)
    outer_radius = screen.get_width() // 2
    inner_radius = outer_radius - blue_ring_thickness

    # Draw a gradient ring from outer to inner radius
    for i in range(outer_radius, inner_radius, -1):
        alpha = int(128 * (i - inner_radius) / blue_ring_thickness)
        pygame.draw.circle(ring_surface, (173, 216, 230, alpha), center, i)

    # Overlay the ring surface onto the screen
    screen.blit(ring_surface, (0, 0))

    # Create text surfaces
    font = pygame.font.Font(None, 36)
    margin = screen.get_width() // 4
    text_surfaces, text_rects = create_text_surfaces(text, font, screen.get_width(), margin)

    # Draw the text surfaces on top of the blurred background and ring
    for text_surface, text_rect in zip(text_surfaces, text_rects):
        screen.blit(text_surface, text_rect)

    # Update the display to show changes
    pygame.display.update()

def run_voice_assistant(circles, screen, background, draw_event, idle_event):
    recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.4)
    query_displayed = False
    response_displayed = False
    query_surfaces = []
    query_rects = []
    response_surfaces = []
    response_rects = []
    hot_words = ["jarvis", "alexa"]
    skip_hot_word_check = False
    print("Say something...")
    
    while True:
        current_text = recorder.text()
        if any(hot_word in current_text.lower() for hot_word in hot_words) or skip_hot_word_check:
            if current_text:
                print("User: " + current_text)

                # Indicate that voice assistant is drawing
                draw_event.set()
                idle_event.clear()

                # Start the blur effect and display the query
                apply_blur_ring_and_text(screen, current_text, blue_ring_thickness=100)
                # query_surfaces, query_rects = display_query(screen, current_text, circles, background)
                query_displayed = True

                recorder.stop()
                current_text = current_text + " " + time.strftime("%Y-%m-%d %H-%M-%S")
                response = assist.ask_question_memory(current_text)
                print(response)
                speech = response.split('#')[0]

                if query_displayed:
                    screen.blit(background, (0, 0))  # Draw background first
                    for circle in circles:  # Then draw apps (circles)
                        circle.draw(screen)
                    # Immediately fade out the query much faster
                    apply_blur_ring_and_text(screen, response, blue_ring_thickness=100)
                    query_displayed = False
                    response_displayed = True

                # if response_displayed:
                #     apply_blur_ring_and_text(screen, response, blue_ring_thickness=100)

                done = assist.TTS(speech)
                if len(response.split('#')) > 1:
                    command = response.split('#')[1]
                    tools.parse_command(command)
                recorder.start()

        # After the response has been displayed for some time, fade everything out
        if response_displayed:
            pygame.time.delay(3000)  # Shorter delay to speed up transition
            # Fade out the response and blur effect
            response_displayed = False

            # Indicate that the voice assistant is done drawing
            idle_event.set()
            draw_event.clear()

        # Draw the normal screen when there is no query or response to show
        if not query_displayed and not response_displayed and idle_event.is_set():
            screen.blit(background, (0, 0))  # Draw background first
            for circle in circles:  # Then draw apps (circles)
                circle.draw(screen)

def run_home_screen(screen):
    screen_size = screen.get_size()
    background = pygame.image.load('./resources/background.jpg')
    background = pygame.transform.scale(background, screen_size)
    
    circles = create_circles(screen_size)
    
    running = True
    draw_event = threading.Event()
    idle_event = threading.Event()
    idle_event.set()  # Initially set the idle event to allow drawing

    print("Here")
    voice_thread = threading.Thread(target=run_voice_assistant, args=(circles, screen, background, draw_event, idle_event))
    voice_thread.daemon = True
    voice_thread.start()
    print("Here2")
    
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

        # Draw home screen only if the voice assistant is idle
        if idle_event.is_set():
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
