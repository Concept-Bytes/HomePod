import pygame
import os
import random
import sys
import requests
from io import BytesIO
import time
import math
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env file
load_dotenv()

# Spotify configuration from .env
username = os.getenv('SPOTIFY_USERNAME')
clientID = os.getenv('SPOTIFY_CLIENT_ID')
clientSecret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

def get_current_playing_info():
    global spotify
    
    current_track = spotify.current_user_playing_track()
    if current_track is None:
        return None  # Return None if no track is playing

    # Extracting necessary details
    artist_name = current_track['item']['artists'][0]['name']
    album_name = current_track['item']['album']['name']
    album_cover_url = current_track['item']['album']['images'][0]['url']
    track_title = current_track['item']['name']  # Get the track name

    return {
        "artist": artist_name,
        "album": album_name,
        "album_cover": album_cover_url,
        "title": track_title
    }

def spotify_authenticate(client_id, client_secret, redirect_uri, username):
    # OAuth with the required scopes for playback control and reading currently playing track
    scope = "user-read-currently-playing user-modify-playback-state"
    auth_manager = SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, username=username)
    return spotipy.Spotify(auth_manager=auth_manager)

spotify = spotify_authenticate(clientID, clientSecret, redirect_uri, username)

def start_music():
    global spotify
    try:
        spotify.start_playback()
    except spotipy.SpotifyException as e:
        return f"Error in starting playback: {str(e)}"

def stop_music():
    global spotify
    try:
        spotify.pause_playback()
    except spotipy.SpotifyException as e:
        return f"Error in stopping playback: {str(e)}"

def skip_to_next():
    global spotify
    try:
        spotify.next_track()
        return "Skipped to next track."
    except spotipy.SpotifyException as e:
        return f"Error in skipping to next track: {str(e)}"

def skip_to_previous():
    global spotify
    try:
        spotify.previous_track()
        return "Skipped to previous track."
    except spotipy.SpotifyException as e:
        return f"Error in skipping to previous track: {str(e)}"

def run(screen):
    pygame.init()
    running = True
    image_directory = './apps/app_4/records/'
    image_files = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]
    random_image_path = random.choice(image_files)
    image = pygame.image.load(random_image_path)
    image = pygame.transform.scale(image, (1080, 1080))
    banner_image_path = './resources/spotify/banner.png'
    banner_image = pygame.transform.scale(pygame.image.load(banner_image_path), (700, 250))

    # Load control button images
    play_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/play.png'), (100, 100))
    pause_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/pause.png'), (100, 100))
    skip_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/skip.png'), (100, 100))
    previous_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/previous.png'), (100, 100))

    # Button positions
    back_button_center = (screen.get_width() // 2, screen.get_height() - 50)
    back_button_radius = 50
    control_buttons_y = back_button_center[1] - 170  # Position below the artist name
    play_pause_center = (screen.get_width() // 2 + 60, control_buttons_y)
    skip_button_center = (screen.get_width() // 2 + 190, control_buttons_y)
    previous_button_center = (screen.get_width() // 2 - 70, control_buttons_y)

    font = pygame.font.Font(None, 36)
    angle = 0
    angle_increment = -0.5
    last_check = 0
    spotify_details = None
    is_playing = True  # Assume music is playing initially

    # Spinning variables
    center_of_image = (screen.get_width() // 2, screen.get_height() // 2)
    dragging = False
    last_mouse_pos = None

    while running:
        current_time = time.time()
        if current_time - last_check > 5:
            spotify_details = get_current_playing_info()
            last_check = current_time
            if spotify_details:
                response = requests.get(spotify_details['album_cover'])
                album_cover_image = pygame.transform.scale(pygame.image.load(BytesIO(response.content)), (200, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if math.hypot(event.pos[0] - back_button_center[0], event.pos[1] - back_button_center[1]) <= back_button_radius:
                    return
                if math.hypot(event.pos[0] - play_pause_center[0]- 50, event.pos[1] - play_pause_center[1]- 50) <= 50:
                    if is_playing:
                        print("Pause")
                        stop_music()
                        is_playing = False
                        angle_increment = 0
                    else:
                        print("Play")
                        start_music()
                        is_playing = True
                        angle_increment = -0.5
                elif math.hypot(event.pos[0] - skip_button_center[0]- 50, event.pos[1] - skip_button_center[1]-50) <= 50:
                    print("Skip")
                    skip_to_next()
                elif math.hypot(event.pos[0] - previous_button_center[0]- 50, event.pos[1] - previous_button_center[1]- 50) <= 50:
                    print("Previous")
                    skip_to_previous()
                # Check if the click is within the image radius to start dragging
                elif math.hypot(event.pos[0] - center_of_image[0], event.pos[1] - center_of_image[1]) <= 540:
                    dragging = True
                    last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_pos = pygame.mouse.get_pos()
                if last_mouse_pos:
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    angle -= dx * 0.1  # Adjust rotation sensitivity as needed
                    angle %= 360  # Keep the angle within 0-360 degrees
                last_mouse_pos = mouse_pos

        screen.fill((50, 50, 100))
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=center_of_image)
        screen.blit(rotated_image, rotated_rect)
        angle = (angle + angle_increment) % 360
        screen.blit(banner_image, (screen.get_width() // 2 - 350, back_button_center[1] - 300))

        # Display music control buttons
        screen.blit(skip_button_image, skip_button_center)
        screen.blit(previous_button_image, previous_button_center)
        if is_playing:
            screen.blit(pause_button_image, play_pause_center)
        else:
            screen.blit(play_button_image, play_pause_center)

        if spotify_details:
            screen.blit(album_cover_image, (220, 750))  # Position for album cover
            song = f"{spotify_details['title']}"
            artist = f"{spotify_details['artist']}"
            song_surface = font.render(song, True, (255, 255, 255))
            artist_surface = font.render(artist, True, (255, 255, 255))
            song_x = (420 + 900 - song_surface.get_width()) // 2
            screen.blit(song_surface, (song_x, 750))  # Position for track info
            artist_x = (420 + 900 - artist_surface.get_width()) // 2
            screen.blit(artist_surface, (artist_x, 800))

        pygame.draw.circle(screen, (255, 255, 255), back_button_center, back_button_radius, 2)
        text_surface = font.render('Back', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(back_button_center[0], back_button_center[1]))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
