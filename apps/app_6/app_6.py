import pygame
import math
import sys
from datetime import timedelta

def run(screen):
    RING_THICKNESS = 20
    CENTER = (screen.get_width() // 2, screen.get_height() // 2)
    RING_RADIUS = screen.get_width() // 2 - RING_THICKNESS // 2
    BUTTON_POS = (CENTER[0], CENTER[1] + 200)
    BUTTON_RADIUS = 50
    BACK_BUTTON_POS = (CENTER[0], screen.get_height() - 100)
    BACK_BUTTON_RADIUS = 40
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    FONT_SIZE = 144  # Increased font size for the time display
    font = pygame.font.Font(None, FONT_SIZE)
    button_images = {
        'start': pygame.image.load('./apps/app_6/start_button.png'),
        'pause': pygame.image.load('./apps/app_6/pause_button.png'),
        'stop': pygame.image.load('./apps/app_6/stop_button.png')
    }
    for key in button_images:
        button_images[key] = pygame.transform.scale(button_images[key], (2 * BUTTON_RADIUS, 2 * BUTTON_RADIUS))
    back_button_image = pygame.image.load('./resources/back.png')
    back_button_image = pygame.transform.scale(back_button_image, (2 * BACK_BUTTON_RADIUS, 2 * BACK_BUTTON_RADIUS))
    current_button = 'start'
    timer_running = False
    timer_paused = False
    timer_duration = timedelta()
    remaining_time = timedelta()

    background_image_path = './apps/app_2/background.jpg'
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    def draw_ring(angle, color):
        pygame.draw.arc(screen, color, 
                        (RING_THICKNESS // 2, RING_THICKNESS // 2, screen.get_width() - RING_THICKNESS, screen.get_height() - RING_THICKNESS), 
                        math.radians(90), math.radians(90 - angle), RING_THICKNESS)

    def draw_time():
        time_left = str(remaining_time).split('.')[0]
        color = RED if timer_running and remaining_time <= timedelta(seconds=timer_duration.total_seconds() * 0.1) else WHITE
        text = font.render(time_left, True, color)
        text_rect = text.get_rect(center=CENTER)
        screen.blit(text, text_rect)

    def draw_button():
        screen.blit(button_images[current_button], (BUTTON_POS[0] - BUTTON_RADIUS, BUTTON_POS[1] - BUTTON_RADIUS))

    def draw_back_button():
        top_left = (BACK_BUTTON_POS[0] - BACK_BUTTON_RADIUS, BACK_BUTTON_POS[1] - BACK_BUTTON_RADIUS)
        screen.blit(back_button_image, top_left)

    def update_time():
        nonlocal remaining_time, timer_running
        if timer_running:
            remaining_time -= timedelta(seconds=1)
            if remaining_time <= timedelta():
                remaining_time = timedelta()
                timer_running = False

    def get_angle_from_position(pos):
        x, y = pos
        angle = (math.degrees(math.atan2(y - CENTER[1], x - CENTER[0])) + 90) % 360
        return angle

    running = True
    dragging = False
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Return to the home screen if the window is closed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(event.pos[0] - BUTTON_POS[0], event.pos[1] - BUTTON_POS[1]) <= BUTTON_RADIUS:
                    if current_button == 'start':
                        timer_running = True
                        timer_paused = False
                        current_button = 'pause'
                        timer_duration = remaining_time if remaining_time else timedelta(hours=1)
                        remaining_time = timer_duration
                    elif current_button == 'pause':
                        timer_running = False
                        timer_paused = True
                        current_button = 'start'
                    elif current_button == 'stop':
                        timer_running = False
                        timer_paused = False
                        current_button = 'start'
                        remaining_time = timedelta()
                elif math.hypot(event.pos[0] - BACK_BUTTON_POS[0], event.pos[1] - BACK_BUTTON_POS[1]) <= BACK_BUTTON_RADIUS:
                    return  # Return to the home screen if the back button is clicked
                else:
                    dragging = True
                    angle = get_angle_from_position(event.pos)
                    timer_duration = timedelta(seconds=((360 - angle) / 360) * 3600)
                    timer_duration -= timedelta(seconds=timer_duration.seconds % 60)  # Round to the nearest minute
                    remaining_time = timer_duration
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging and not timer_running:
                angle = get_angle_from_position(event.pos)
                timer_duration = timedelta(seconds=((360 - angle) / 360) * 3600)
                timer_duration -= timedelta(seconds=timer_duration.seconds % 60)  # Round to the nearest minute
                remaining_time = timer_duration
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to the home screen on ESC key

        screen.blit(background_image, (0, 0))
        angle = (360 * (1 - remaining_time.total_seconds() / 3600)) if timer_running else (360 * (1 - timer_duration.total_seconds() / 3600))
        ring_color = RED if timer_running and remaining_time <= timedelta(seconds=timer_duration.total_seconds() * 0.1) else BLUE
        draw_ring(angle, ring_color)
        draw_time()
        draw_button()
        draw_back_button()
        pygame.display.flip()

        if timer_running:
            update_time()
        clock.tick(1)
