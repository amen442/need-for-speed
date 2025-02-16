import pygame
from pygame.locals import *
import socket
import json
import random

# Server settings
HOST = '10.10.6.241'  # Replace with your IP address
PORT = 9999

# Initialize Pygame
pygame.init()

# Screen settings
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game - Client')

# Colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# Load images
player_car_img = pygame.image.load("car.png")  # Replace with your car image file

# Define vehicle types and their corresponding images
vehicle_imgs = {
    "taxi": pygame.image.load("taxi.png"),  # Replace with your taxi image file
    "van": pygame.image.load("van.png"),    # Replace with your van image file
    "semi_trailer": pygame.image.load("semi_trailer.png") # Replace with your truck image file
}

# Resize images (optional)
player_car_img = pygame.transform.scale(player_car_img, (50, 50))
for key in vehicle_imgs:
    vehicle_imgs[key] = pygame.transform.scale(vehicle_imgs[key], (50, 50))

# Player settings
player_id = None

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall("JOIN".encode())

# Wait for server to send player ID
response = sock.recv(1024).decode()
if response.startswith("ID:"):
    try:
        player_id = int(response.split(":")[1])
        print(f"Joined the game as Player {player_id}")
    except (IndexError, ValueError):
        print("Invalid player ID received from server.")
        exit()
else:
    print("Failed to join the game.")
    exit()

# Game loop
running = True
game_over = False
clock = pygame.time.Clock()

# Track score changes
last_score = 0
current_vehicle_type = random.choice(list(vehicle_imgs.keys()))

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if not game_over:
                if event.key == K_LEFT:
                    sock.sendall(f"MOVE:{player_id}:LEFT".encode())
                elif event.key == K_RIGHT:
                    sock.sendall(f"MOVE:{player_id}:RIGHT".encode())
            else:
                if event.key == K_y:  # Restart game
                    sock.sendall("RESTART".encode())
                    game_over = False
                elif event.key == K_n:  # Quit game
                    running = False

    # Get game state from server
    try:
        sock.sendall("GET_STATE".encode())
        game_state = json.loads(sock.recv(4096).decode())
    except (socket.error, json.JSONDecodeError) as e:
        print(f"Error receiving game state: {e}")
        break

    # Check if player is alive
    if str(player_id) in game_state["players"]:
        if not game_state["players"][str(player_id)]["alive"]:
            game_over = True
    else:
        print("Player not found in game state.")
        break

    # Update vehicle type if score increases
    player_score = game_state["players"][str(player_id)]["score"]
    if player_score > last_score:
        current_vehicle_type = random.choice(list(vehicle_imgs.keys()))
        last_score = player_score
    
    # Draw game
    screen.fill(green)
    pygame.draw.rect(screen, gray, (100, 0, 300, 500))

    # Draw players
    for player_id_str, player in game_state["players"].items():
        if player["alive"]:
            screen.blit(player_car_img, (player["x"], player["y"]))

    # Draw vehicles and check for collisions
    for vehicle in game_state["vehicles"]:
        vehicle["y"] += game_state["speed"]

        if current_vehicle_type in vehicle_imgs:
            screen.blit(vehicle_imgs[current_vehicle_type], (vehicle["x"], vehicle["y"]))

        # Collision detection
        player_x = game_state["players"][str(player_id)]["x"]
        player_y = game_state["players"][str(player_id)]["y"]
        player_rect = pygame.Rect(player_x, player_y, 50, 50)
        vehicle_rect = pygame.Rect(vehicle["x"], vehicle["y"], 50, 50)
        if player_rect.colliderect(vehicle_rect):
            game_over = True
            sock.sendall(f"CRASH:{player_id}".encode())  # Notify server of crash

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {player_score}", True, white)
    screen.blit(score_text, (10, 10))

    # Display game over message
    if game_over:
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, red)
        screen.blit(game_over_text, (width // 2 - 140, height // 2 - 120))
        restart_text = font.render("Restart? (Y/N)", True, white)
        screen.blit(restart_text, (width // 2 - 160, height // 2 + 50))

    pygame.display.update()
    clock.tick(30)  # Limit to 30 FPS

pygame.quit()
