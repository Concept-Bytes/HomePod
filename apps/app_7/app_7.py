import pygame
import requests
import time
import math
import sys

def get_news():
    query_params = {
        "source": "bbc-news",
        "sortBy": "top",
        "apiKey": "4dbc17e007ab436fb66416009dfb59a8"
    }
    main_url = "https://newsapi.org/v1/articles"
    res = requests.get(main_url, params=query_params)
    open_bbc_page = res.json()
    article = open_bbc_page["articles"]
    headlines = [ar["title"] for ar in article]
    return headlines[:10]  # Get only the top 10 headlines

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    lines.append(current_line.strip())
    return lines

def run(screen):
    pygame.font.init()
    FONT_SIZE = 64
    font = pygame.font.Font(None, FONT_SIZE)
    fade_speed = 5  # Speed of fade in and fade out

    CENTER = (screen.get_width() // 2, screen.get_height() // 2)
    BACK_BUTTON_POS = (CENTER[0], screen.get_height() - 100)
    BACK_BUTTON_RADIUS = 40

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    back_button_image_path = './resources/back.png'
    back_button_image = pygame.image.load(back_button_image_path)
    back_button_image = pygame.transform.scale(back_button_image, (2 * BACK_BUTTON_RADIUS, 2 * BACK_BUTTON_RADIUS))

    background_image_path = './apps/app_2/background.jpg'
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    callout_image_path = './apps/app_7/callout.png'
    callout_image = pygame.image.load(callout_image_path)

    app_image_path = './apps/app_7/app_7.png'
    app_image = pygame.image.load(app_image_path)
    app_image = pygame.transform.scale(app_image, (200, 200))

    headlines = get_news()
    headline_index = 0
    alpha = 255
    fade_in = True
    fade_out = False
    display_time = 20  # seconds
    start_time = time.time()

    def draw_back_button():
        top_left = (BACK_BUTTON_POS[0] - BACK_BUTTON_RADIUS, BACK_BUTTON_POS[1] - BACK_BUTTON_RADIUS)
        screen.blit(back_button_image, top_left)

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(event.pos[0] - BACK_BUTTON_POS[0], event.pos[1] - BACK_BUTTON_POS[1]) <= BACK_BUTTON_RADIUS:
                    return  # Return to the home screen if the back button is clicked
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to the home screen on ESC key

        current_time = time.time()
        if current_time - start_time > display_time:
            fade_out = True
            fade_in = False

        screen.blit(background_image, (0, 0))
        screen.blit(app_image, (CENTER[0] - 100, 50))  # Position the app image at the top center
        draw_back_button()

        headline_text = headlines[headline_index]
        wrapped_text = wrap_text(headline_text, font, screen.get_width() - 100)
        line_height = font.size('Tg')[1]
        total_text_height = line_height * len(wrapped_text)

        if fade_in:
            alpha += fade_speed
            if alpha >= 255:
                alpha = 255
                fade_in = False
        elif fade_out:
            alpha -= fade_speed
            if alpha <= 0:
                alpha = 0
                fade_out = False
                fade_in = True
                start_time = current_time
                headline_index = (headline_index + 1) % len(headlines)

        callout_image.set_alpha(alpha)
        screen.blit(callout_image, (0, 0))

        for i, line in enumerate(wrapped_text):
            text_surface = font.render(line, True, WHITE)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(CENTER[0], CENTER[1] - total_text_height // 2 + i * line_height))
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))
    pygame.display.set_caption("News App")
    run(screen)
    pygame.quit()
