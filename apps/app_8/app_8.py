import pygame
import requests
from bs4 import BeautifulSoup
import os
import time
from io import BytesIO
from dotenv import load_dotenv
import math

# Load environment variables from .env file
load_dotenv()

# Read sports from environment variables
sports_to_scrape = os.getenv('SPORTS').split(',')

# Initialize Pygame
pygame.init()
pygame.display.set_caption('Sports Scores App')
clock = pygame.time.Clock()

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Custom fonts
font_path = './resources/fonts/good-times/good_times_rg.otf'
font_small = pygame.font.Font(font_path, 30)
font_large = pygame.font.Font(font_path, 60)
font_sport = pygame.font.Font(font_path, 80)
font_score = pygame.font.Font(font_path, 100)

def get_scores(sports):
    url = 'https://www.foxsports.com/scores'
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    scores_data = []
    
    for sport in sports:
        div_id = f"sport_{sport}"
        sport_div = soup.find('div', id=div_id)
        
        if sport_div:
            games = sport_div.find_all('a', class_='score-chip')
            
            for game in games:
                teams = game.find_all('div', class_='score-team-row')
                
                if len(teams) == 2:
                    team1_name = teams[0].find('span', class_='scores-text').text.strip()
                    team2_name = teams[1].find('span', class_='scores-text').text.strip()
                    
                    team1_score = teams[0].find('div', class_='score-team-score').find('span', class_='scores-text').text.strip()
                    team2_score = teams[1].find('div', class_='score-team-score').find('span', class_='scores-text').text.strip()
                    
                    team1_logo = teams[0].find('img', class_='team-logo')['src'].replace('80.80', '300.300')
                    team2_logo = teams[1].find('img', class_='team-logo')['src'].replace('80.80', '300.300')
                    
                    scores_data.append({
                        'sport': sport,
                        'team1_name': team1_name,
                        'team2_name': team2_name,
                        'team1_score': team1_score,
                        'team2_score': team2_score,
                        'team1_logo': team1_logo,
                        'team2_logo': team2_logo
                    })
    
    return scores_data

def load_image_from_url(url):
    response = requests.get(url)
    image = pygame.image.load(BytesIO(response.content))
    return image

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

    scores = get_scores(sports_to_scrape)
    score_index = 0
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

        if scores:
            score = scores[score_index]
            try:
                team1_logo = load_image_from_url(score['team1_logo'])
                team2_logo = load_image_from_url(score['team2_logo'])
                team1_name = score['team1_name']
                team2_name = score['team2_name']
                team1_score = score['team1_score']
                team2_score = score['team2_score']
                sport_name = score['sport']
            except Exception as e:
                print(f"Error loading score data: {e}")
                team1_logo = team2_logo = None
                team1_name = team2_name = ""
                team1_score = team2_score = ""
                sport_name = ""

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
                    score_index = (score_index + 1) % len(scores)

            if team1_logo and team2_logo:
                team1_logo = pygame.transform.scale(team1_logo, (300, 300))
                team2_logo = pygame.transform.scale(team2_logo, (300, 300))
                team1_logo.set_alpha(alpha)
                team2_logo.set_alpha(alpha)

                screen.blit(team1_logo, (CENTER[0] - 400, CENTER[1] - 100))
                screen.blit(team2_logo, (CENTER[0] + 100, CENTER[1] - 100))

            sport_text_surface = font_sport.render(sport_name, True, WHITE)
            sport_text_surface.set_alpha(alpha)
            sport_text_rect = sport_text_surface.get_rect(center=(CENTER[0], CENTER[1] - 400))
            screen.blit(sport_text_surface, sport_text_rect)

            team1_text_surface = font_large.render(team1_name, True, WHITE)
            team1_text_surface.set_alpha(alpha)
            team1_text_rect = team1_text_surface.get_rect(center=(CENTER[0] - 250, CENTER[1] - 250))
            screen.blit(team1_text_surface, team1_text_rect)

            team2_text_surface = font_large.render(team2_name, True, WHITE)
            team2_text_surface.set_alpha(alpha)
            team2_text_rect = team2_text_surface.get_rect(center=(CENTER[0] + 250, CENTER[1] - 250))
            screen.blit(team2_text_surface, team2_text_rect)

            score_text = f"{team1_score} - {team2_score}"
            score_surface = font_score.render(score_text, True, WHITE)
            score_surface.set_alpha(alpha)
            score_rect = score_surface.get_rect(center=(CENTER[0], CENTER[1] + 300))
            screen.blit(score_surface, score_rect)
        else:
            print("No scores to display.")

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
    pygame.display.set_caption("Sports Scores App")
    run(screen)
    pygame.quit()
