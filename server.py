import socket
import threading
import pygame

# Server configuration
HOST = "127.0.0.1"
PORT = 5555

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Car Race")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Car settings
car_width, car_height = 50, 100
players = {}  # Store player positions

def handle_client(conn, addr, player_id):
    global players
    conn.send(str(player_id).encode())  # Send player ID to client
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            x, y = map(int, data.split(","))
            players[player_id] = (x, y)
            conn.sendall(str(players).encode())  # Send updated positions
        except:
            break
    conn.close()
    del players[player_id]

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)  # Allow up to 2 players
print("Server started...")

player_count = 0

while True:
    conn, addr = server.accept()
    print(f"New connection: {addr}")
    threading.Thread(target=handle_client, args=(conn, addr, player_count)).start()
    players[player_count] = (WIDTH//2, HEIGHT - car_height - 10)
    player_count += 1
