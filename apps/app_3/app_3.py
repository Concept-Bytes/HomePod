import pygame
import math
import samsung

def run(screen):
    NUM_DEVICES = 12
    RADIUS = 100
    DEVICE_NAMES = ["lamp", "lamp2"] + ["Device " + str(i) for i in range(3, NUM_DEVICES+1)]
    device_states = {name: False for name in DEVICE_NAMES}
    CENTER = (screen.get_width() // 2, screen.get_height() // 2)
    DEVICE_CIRCLE_RADIUS = 425  # Radius of the circle on which device circles are placed
    BACK_BUTTON_RADIUS = 50  # Radius for the back button
    BACK_BUTTON_POS = CENTER
    FONT_SIZE = 24
    font = pygame.font.Font(None, FONT_SIZE)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    background_image_path = './apps/app_2/background.jpg'
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    back_button_image_path = './resources/back.png'
    back_button_image = pygame.image.load(back_button_image_path)
    back_button_image = pygame.transform.scale(back_button_image, (2 * BACK_BUTTON_RADIUS, 2 * BACK_BUTTON_RADIUS))

    def draw_device_circle(angle, name, on):
        angle = math.radians(angle)
        x = CENTER[0] + DEVICE_CIRCLE_RADIUS * math.cos(angle)
        y = CENTER[1] + DEVICE_CIRCLE_RADIUS * math.sin(angle)
        circle_inner_color = (255, 255, 255, 128) if on else (0, 0, 0, 128)  # Semi-transparent white if on, semi-transparent black if off
        text_color = BLACK if on else WHITE  # Black text if on, white if off

        # Create a surface for the circle with per-pixel alpha
        circle_surface = pygame.Surface((RADIUS * 2, RADIUS * 2), pygame.SRCALPHA)
        circle_surface = circle_surface.convert_alpha()

        # Draw the semi-transparent circle
        pygame.draw.circle(circle_surface, circle_inner_color, (RADIUS, RADIUS), RADIUS - 4, 0)  # Smaller inner circle with transparency
        screen.blit(circle_surface, (x - RADIUS, y - RADIUS))

        # Draw the white border around the circle
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), RADIUS, 4)  # White border for visibility

        text = font.render(name, True, text_color)
        text_rect = text.get_rect(center=(int(x), int(y)))
        screen.blit(text, text_rect)

    def draw_back_button():
        top_left = (BACK_BUTTON_POS[0] - BACK_BUTTON_RADIUS, BACK_BUTTON_POS[1] - BACK_BUTTON_RADIUS)
        screen.blit(back_button_image, top_left)

    def toggle_device(name):
        current_state = device_states[name]
        new_state = not current_state
        device_states[name] = new_state
        samsung.command_device_sync(name, new_state)
        print(f"Command sent to {name}: {'On' if new_state else 'Off'}")  # Mocking command

    def check_click(pos):
        # Check back button click
        if math.hypot(pos[0] - BACK_BUTTON_POS[0], pos[1] - BACK_BUTTON_POS[1]) <= BACK_BUTTON_RADIUS:
            return False  # Return False to indicate that the app should close
        # Check device circle clicks
        for i, name in enumerate(DEVICE_NAMES):
            angle = 360 / NUM_DEVICES * i
            angle = math.radians(angle)
            x = CENTER[0] + DEVICE_CIRCLE_RADIUS * math.cos(angle)
            y = CENTER[1] + DEVICE_CIRCLE_RADIUS * math.sin(angle)
            if math.sqrt((pos[0] - x) ** 2 + (pos[1] - y) ** 2) <= RADIUS:
                toggle_device(name)
                break
        return True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = check_click(pygame.mouse.get_pos())
        
        screen.blit(background_image, (0, 0))
        for i, name in enumerate(DEVICE_NAMES):
            draw_device_circle(360 / NUM_DEVICES * i, name, device_states[name])
        draw_back_button()
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))
    pygame.display.set_caption("Smart Home Control")
    run(screen)
    pygame.quit()
