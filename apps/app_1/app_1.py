import pygame
import math
import sys
import requests
import time
from io import BytesIO
import os
from dotenv import load_dotenv
import assist

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('WEATHER_API_KEY')
url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={os.getenv('WEATHER_CITY')}"
themes_dir = './apps/app_1/themes'
font_path = './apps/app_1/JetBrainsMono.ttf'
font_path_extra_bold = './apps/app_1/BebasNeue-Regular.ttf'

icon_cache = {}

def get_weather():
    print("GETTING WEATHER")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to retrieve data: {response.status_code}"}

def get_icon(url):
    if url not in icon_cache:
        response = requests.get(url)
        if response.status_code == 200:
            icon_image = pygame.image.load(BytesIO(response.content))
            icon_cache[url] = pygame.transform.scale(icon_image, (64, 64))
        else:
            print(f"Failed to download icon: {url}")
            return None
    return icon_cache[url]

# Load custom font
def load_custom_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Failed to load font: {e}")
        return pygame.font.Font(None, size)  # Default font if custom font fails

def load_theme(theme):
    print(theme)
    theme_path = os.path.join(themes_dir, theme)
    if not os.path.exists(theme_path):
        if "rain" in theme:
            theme_path = os.path.join(themes_dir, 'stormy')
        else:
            theme_path = os.path.join(themes_dir, 'sunny')
    background_image_path = os.path.join(theme_path, 'background.png')
    back_button_image_path = os.path.join(theme_path, 'back.png')
    return background_image_path, back_button_image_path

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
    pygame.font.init()  # Initialize font module
    FONT_SIZE_SMALL = 30
    FONT_SIZE_MEDIUM = 50
    FONT_SIZE_LARGE = 350
    FONT_SIZE_DESCRIPTION = 35
    font_small = load_custom_font(font_path, FONT_SIZE_SMALL)  # Load JetBrains Mono font
    font_medium = load_custom_font(font_path, FONT_SIZE_MEDIUM)
    font_large = load_custom_font(font_path_extra_bold, FONT_SIZE_LARGE)  # Load JetBrains Mono Extra Bold font
    font_description = load_custom_font(font_path, FONT_SIZE_DESCRIPTION)
    WHITE = (255, 255, 255)
    BLUE = (50, 50, 100)  # Dark blue for aesthetic background

    CENTER = (screen.get_width() // 2, screen.get_height() // 2)
    INFO_RADIUS = 350  # Radius to place text elements
    BACK_BUTTON_RADIUS = 60  # Radius for the back button
    BACK_BUTTON_POS = (CENTER[0], screen.get_height() - 100)  # Position for the back button

    update_interval = 300  # 5 minutes in seconds
    next_update_time = time.time()

    weather_data = get_weather()  # Fetch initial data

    def draw_text(screen, text, font, color, position):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

    def draw_back_button(back_button_image):
        top_left = (BACK_BUTTON_POS[0] - BACK_BUTTON_RADIUS, BACK_BUTTON_POS[1] - BACK_BUTTON_RADIUS)
        screen.blit(back_button_image, top_left)

    def check_click(pos):
        if math.hypot(pos[0] - BACK_BUTTON_POS[0], pos[1] - BACK_BUTTON_POS[1]) <= BACK_BUTTON_RADIUS:
            return False
        return True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not check_click(pygame.mouse.get_pos()):
                    running = False

        current_time = time.time()
        if current_time >= next_update_time:
            weather_data = get_weather()
            query = "Give a brief description of what I should wear based on this weather data: " + str(weather_data)
            response = assist.ask_question_memory(query)
            print(response)
            next_update_time = current_time + update_interval

        screen.fill(BLUE)

        if weather_data and 'current' in weather_data:
            condition = weather_data['current']['condition']['text'].replace(" ", "").lower()
            background_image_path, back_button_image_path = load_theme(condition)

            if os.path.exists(background_image_path):
                background_image = pygame.image.load(background_image_path)
                background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))
                screen.blit(background_image, (0, 0))
            else:
                print(f"No background image found for {condition}")

            if os.path.exists(back_button_image_path):
                back_button_image = pygame.image.load(back_button_image_path)
                back_button_image = pygame.transform.scale(back_button_image, (2 * BACK_BUTTON_RADIUS, 2 * BACK_BUTTON_RADIUS))
                draw_back_button(back_button_image)
            else:
                print(f"No back button image found for {condition}")

        if 'current' in weather_data:
            location_text = f"{weather_data['location']['name']}, {weather_data['location']['region']}"
            condition_text = weather_data['current']['condition']['text']
            temp_text = f"{int(weather_data['current']['temp_f'])}°F"
            humidity_text = f"Humidity: {weather_data['current']['humidity']}%"
            wind_text = f"Wind: {int(weather_data['current']['wind_mph'])} mph"
            description_text = response

            # Move the temperature text down
            draw_text(screen, temp_text, font_large, WHITE, (CENTER[0], CENTER[1] - 50))

            # Commented out the display of other weather details
            # draw_text(screen, condition_text, font_medium, WHITE, (CENTER[0], CENTER[1] - 50))
            # draw_text(screen, location_text, font_medium, WHITE, (CENTER[0], CENTER[1] + 50))
            # draw_text(screen, wind_text, font_small, WHITE, (CENTER[0], CENTER[1] + 100))
            # draw_text(screen, humidity_text, font_small, WHITE, (CENTER[0], CENTER[1] + 130))

            # Wrap description text with adjusted bounds
            description_lines = wrap_text(description_text, font_description, screen.get_width() - 200)
            line_height = font_description.get_linesize()
            for i, line in enumerate(description_lines):
                draw_text(screen, line, font_description, WHITE, (CENTER[0], CENTER[1] + 100 + i * line_height))

        pygame.display.flip()



#to add
#partlycloudy
#add sunny swap with partly cloudy 
#Check for rainy 
 
