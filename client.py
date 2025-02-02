import pygame
import socket
import threading

# Configuration
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Chargement des voitures
car_image = pygame.image.load(r"C:\Users\amenb\OneDrive\Desktop\SPEEDCODE\vecteezy_red-sport-car-design-transparent-background_23524637.png")
car_rect = car_image.get_rect(center=(400, 500))

# Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.31.220", 9999))


def receive_data():
    while True:
        try:
            data = client.recv(1024).decode()
            if data:
                print("Données reçues :", data)
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

running = True
while running:
    screen.fill(WHITE)
# Contrôles du joueur
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        car_rect.x += 5
    if keys[pygame.K_UP]:
        car_rect.y -= 5
    if keys[pygame.K_DOWN]:
        car_rect.y += 5

    # Envoyer la position au serveur
    data = f"{car_rect.x},{car_rect.y}"
    client.sendall(data.encode())

    # Afficher la voiture
    screen.blit(car_image, car_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.close()