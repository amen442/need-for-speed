import pygame
from pygame.locals import *
import socket
import json

HOST = '192.168.226.37'
PORT = 6666

pygame.init()
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game - Client')


gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

player_car_img = pygame.image.load("car.png")
player_car_img = pygame.transform.scale(player_car_img, (50, 50))

vehicle_imgs = {
    "taxi": pygame.transform.scale(pygame.image.load("taxi.png"), (50, 50)),
    "van": pygame.transform.scale(pygame.image.load("van.png"), (50, 50)),
    "semi_trailer": pygame.transform.scale(pygame.image.load("semi_trailer.png"), (50, 50))
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))


font = pygame.font.Font(None, 36)
mode_selected = False
game_mode = "HUMAN"

while not mode_selected:
    screen.fill(green)
    mode_text1 = font.render("1 - Play vs Human", True, white)
    mode_text2 = font.render("2 - Play vs AI", True, white)
    note_text = font.render("Click inside then press 1 or 2", True, white)
    screen.blit(mode_text1, (150, 200))
    screen.blit(mode_text2, (150, 250))
    screen.blit(note_text, (100, 300))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            key_name = pygame.key.name(event.key)
            print("Pressed:", key_name)
            if key_name in ['1', 'kp 1']:
                game_mode = "HUMAN"
                mode_selected = True
            elif key_name in ['2', 'kp 2']:
                game_mode = "AI"
                mode_selected = True
        elif event.type == QUIT:
            pygame.quit()
            exit()


sock.sendall(f"JOIN:{game_mode}".encode())
response = sock.recv(1024).decode()
player_id = int(response.split(":")[1]) if response.startswith("ID:") else None

running = True
game_over = False
clock = pygame.time.Clock()
last_score = 0

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
                if event.key == K_y:
                    sock.sendall("RESTART".encode())
                    game_over = False
                elif event.key == K_n:
                    running = False

    try:
        sock.sendall("GET_STATE".encode())
        game_state = json.loads(sock.recv(4096).decode())
    except:
        break

    if str(player_id) not in game_state["players"]:
        break

    player_data = game_state["players"][str(player_id)]
    game_over = not player_data["alive"]
    player_score = player_data["score"]

    screen.fill(green)
    pygame.draw.rect(screen, gray, (100, 0, 300, 500))


    for pid, p in game_state["players"].items():
        if p["alive"]:
            screen.blit(player_car_img, (p["x"], p["y"]))


    for v in game_state["vehicles"]:
        if v["type"] in vehicle_imgs:
            screen.blit(vehicle_imgs[v["type"]], (v["x"], v["y"]))


    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {player_score}", True, white)
    screen.blit(score_text, (10, 10))

    if game_over:
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, red)
        screen.blit(game_over_text, (width//2 - 140, height//2 - 120))
        restart_text = font.render("Restart? (Y/N)", True, white)
        screen.blit(restart_text, (width//2 - 160, height//2 + 50))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
