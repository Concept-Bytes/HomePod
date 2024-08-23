import pygame
import os
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

def scale_text_to_fit(surface, text, font_path, max_width, initial_size):
    font_size = initial_size
    font = pygame.font.Font(font_path, font_size)
    while font.size(text)[0] > max_width and font_size > 10:  # Ensure the font size does not go below 10
        font_size -= 1
        font = pygame.font.Font(font_path, font_size)
    return font

def run(screen):
    pygame.init()
    running = True

    banner_image_path = './apps/app_4/banner.png'
    banner_image = pygame.transform.scale(pygame.image.load(banner_image_path), (700, 250))

    menu_image_path = './resources/spotify/menu.png'
    menu_image = pygame.transform.scale(pygame.image.load(menu_image_path), (700, 250))

    # Load control button images
    play_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/play.png'), (100, 100))
    pause_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/pause.png'), (100, 100))
    skip_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/skip.png'), (100, 100))
    previous_button_image = pygame.transform.scale(pygame.image.load('./resources/spotify/previous.png'), (100, 100))

    # Load back button image
    back_button_image_path = './apps/app_4/back.png'
    back_button_image = pygame.transform.scale(pygame.image.load(back_button_image_path), (100, 100))

    # Button positions
    back_button_center = (screen.get_width() // 2, screen.get_height() - 50)
    control_buttons_y = back_button_center[1] - 170  # Position below the artist name
    play_pause_center = (screen.get_width() // 2, control_buttons_y)
    skip_button_center = (screen.get_width() // 2 + 150, control_buttons_y)
    previous_button_center = (screen.get_width() // 2 - 150, control_buttons_y)

    # Load custom fonts
    song_font_path = './apps/app_4/JetBrainsMono-ExtraBold.ttf'
    artist_font_path = './apps/app_4/JetBrainsMono.ttf'
    initial_song_font_size = 48  # Initial font size for song title
    artist_font_size = 36

    last_check = 0
    spotify_details = None
    is_playing = True  # Assume music is playing initially

    while running:
        current_time = time.time()
        if current_time - last_check > 5:
            spotify_details = get_current_playing_info()
            last_check = current_time
            if spotify_details:
                response = requests.get(spotify_details['album_cover'])
                album_cover_image = pygame.transform.scale(pygame.image.load(BytesIO(response.content)), (screen.get_width(), screen.get_height()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if math.hypot(event.pos[0] - back_button_center[0], event.pos[1] - back_button_center[1]) <= 50:
                    return
                if math.hypot(event.pos[0] - play_pause_center[0], event.pos[1] - play_pause_center[1]) <= 50:
                    if is_playing:
                        print("Pause")
                        stop_music()
                        is_playing = False
                    else:
                        print("Play")
                        start_music()
                        is_playing = True
                elif math.hypot(event.pos[0] - skip_button_center[0], event.pos[1] - skip_button_center[1]) <= 50:
                    print("Skip")
                    skip_to_next()
                elif math.hypot(event.pos[0] - previous_button_center[0], event.pos[1] - previous_button_center[1]) <= 50:
                    print("Previous")
                    skip_to_previous()

        if spotify_details:
            screen.blit(album_cover_image, (0, 0))  # Set album cover as background
            screen.blit(banner_image, (screen.get_width() // 2 - 350, back_button_center[1] - 350))
            screen.blit(menu_image, (screen.get_width() // 2 - 350, back_button_center[1] - 350))

            # Display music control buttons
            screen.blit(previous_button_image, (previous_button_center[0] - previous_button_image.get_width() // 2, previous_button_center[1] - previous_button_image.get_height() // 2))
            if is_playing:
                screen.blit(pause_button_image, (play_pause_center[0] - pause_button_image.get_width() // 2, play_pause_center[1] - pause_button_image.get_height() // 2))
            else:
                screen.blit(play_button_image, (play_pause_center[0] - play_button_image.get_width() // 2, play_pause_center[1] - play_button_image.get_height() // 2))
            screen.blit(skip_button_image, (skip_button_center[0] - skip_button_image.get_width() // 2, skip_button_center[1] - skip_button_image.get_height() // 2))

            song = f"{spotify_details['title']}"
            artist = f"{spotify_details['artist']}"

            # Scale the song title text to fit within the banner
            max_width = 700 - 20  # Banner width minus some padding
            song_font = scale_text_to_fit(screen, song, song_font_path, max_width, initial_song_font_size)
            song_surface = song_font.render(song, True, (255, 255, 255))
            artist_font = pygame.font.Font(artist_font_path, artist_font_size)
            artist_surface = artist_font.render(artist, True, (255, 255, 255))

            # Calculate positions to place the text inside the banner
            banner_rect = banner_image.get_rect(center=(screen.get_width() // 2, back_button_center[1] - 325))
            total_text_height = song_surface.get_height() + artist_surface.get_height() + 10  # 10 pixels for spacing
            song_y = banner_rect.top + (banner_rect.height - total_text_height) // 2 + 40
            artist_y = song_y + song_surface.get_height() + 10

            song_x = banner_rect.left + (banner_rect.width - song_surface.get_width()) // 2
            artist_x = banner_rect.left + (banner_rect.width - artist_surface.get_width()) // 2

            screen.blit(song_surface, (song_x, song_y))
            screen.blit(artist_surface, (artist_x, artist_y))

        # Display the back button
        screen.blit(back_button_image, (back_button_center[0] - back_button_image.get_width() // 2, back_button_center[1] - back_button_image.get_height() // 2))

        pygame.display.flip()
