import pygame
import yfinance as yf
import os
import time
from dotenv import load_dotenv
import math

# Load environment variables from .env file
load_dotenv()

# Read stock symbols from environment variables
stock_symbols = os.getenv('STOCK_SYMBOLS').split(',')

# Initialize Pygame
pygame.init()
pygame.display.set_caption('Stock Ticker App')
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

def load_custom_font(path, size):
    """Loads a custom font."""
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Failed to load font: {e}")
        return pygame.font.Font(None, size)  # Default font if custom font fails

# Path to the custom font
font_path = './resources/fonts/good-times/good_times_rg.otf'
font_small = load_custom_font(font_path, 30)
font_large = load_custom_font(font_path, 200)
font_symbol = load_custom_font(font_path, 120)

def get_stock_data(symbol):
    """Fetches stock data using the yfinance library."""
    stock = yf.Ticker(symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    previous_price = stock.history(period="2d")['Close'].iloc[0]
    increase_dollars = current_price - previous_price
    return current_price, increase_dollars

def run(screen):
    screen_width, screen_height = screen.get_size()
    CENTER = (screen_width // 2, screen_height // 2)
    BACK_BUTTON_POS = (screen_width // 2, screen_height * 9 // 10)
    BACK_BUTTON_RADIUS = 40
    rotate_interval = 10  # seconds
    fade_speed = 5

    background_image_path = './apps/app_2/background.jpg'
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    back_button_image_path = './resources/back.png'
    back_button_image = pygame.image.load(back_button_image_path)
    back_button_image = pygame.transform.scale(back_button_image, (2 * BACK_BUTTON_RADIUS, 2 * BACK_BUTTON_RADIUS))

    stock_index = 0
    alpha = 255
    fade_in = True
    fade_out = False
    start_time = time.time()

    def draw_back_button():
        top_left = (BACK_BUTTON_POS[0] - BACK_BUTTON_RADIUS, BACK_BUTTON_POS[1] - BACK_BUTTON_RADIUS)
        screen.blit(back_button_image, top_left)

    running = True
    while running:
        screen.blit(background_image, (0, 0))
        draw_back_button()

        current_time = time.time()
        if current_time - start_time > rotate_interval:
            fade_out = True
            fade_in = False

        symbol = stock_symbols[stock_index]
        try:
            price, gain_dollars = get_stock_data(symbol)
            color = GREEN if gain_dollars > 0 else RED
            price_text = f"${price:.2f}"
            symbol_text = symbol
        except Exception as e:
            color = BLACK
            price_text = f"Error fetching data"
            symbol_text = symbol

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
                stock_index = (stock_index + 1) % len(stock_symbols)

        # Render and display symbol text
        symbol_surface = font_symbol.render(symbol_text, True, WHITE)
        symbol_surface.set_alpha(alpha)
        symbol_rect = symbol_surface.get_rect(center=(CENTER[0], CENTER[1] - 150))
        screen.blit(symbol_surface, symbol_rect)

        # Render and display price text
        price_surface = font_large.render(price_text, True, color)
        price_surface.set_alpha(alpha)
        price_rect = price_surface.get_rect(center=CENTER)
        screen.blit(price_surface, price_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(event.pos[0] - BACK_BUTTON_POS[0], event.pos[1] - BACK_BUTTON_POS[1]) <= BACK_BUTTON_RADIUS:
                    running = False  # Exit the loop if back button is pressed

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1080, 1080))
    pygame.display.set_caption("Stock Ticker App")
    run(screen)
    pygame.quit()
