import socket
import threading
import random
import json

# Server settings
HOST = '10.10.6.241'  # Listen on all network interfaces
PORT = 9999

# Game state
players = {}
vehicles = []
speed = 10
lock = threading.Lock()

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            if message.startswith("JOIN"):
                player_id = len(players) + 1
                players[player_id] = {"x": 250, "y": 400, "score": 0, "alive": True}
                print(f"Player {player_id} joined the game.")
                conn.sendall(f"ID:{player_id}".encode())
            elif message.startswith("MOVE"):
                _, player_id, direction = message.split(":")
                player_id = int(player_id)
                with lock:
                    if player_id in players and players[player_id]["alive"]:
                        if direction == "LEFT" and players[player_id]["x"] > 150:
                            players[player_id]["x"] -= 100
                        elif direction == "RIGHT" and players[player_id]["x"] < 350:
                            players[player_id]["x"] += 100
            elif message == "GET_STATE":
                with lock:
                    game_state = {
                        "players": players,
                        "vehicles": vehicles,
                        "speed": speed
                    }
                    conn.sendall(json.dumps(game_state).encode())
            elif message == "RESTART":
                with lock:
                    if player_id in players:
                        players[player_id]["alive"] = True
                        players[player_id]["x"] = 250
                        players[player_id]["y"] = 400
                        players[player_id]["score"] = 0

def spawn_vehicles():
    global vehicles, speed
    lanes = [150, 250, 350]
    while True:
        if len(vehicles) < 2:
            vehicle = {
                "x": random.choice(lanes),
                "y": -50
            }
            with lock:
                vehicles.append(vehicle)
        for vehicle in vehicles:
            vehicle["y"] += speed
            if vehicle["y"] > 500:
                vehicles.remove(vehicle)
                for player in players.values():
                    if player["alive"]:
                        player["score"] += 1
                        if player["score"] % 5 == 0:
                            speed += 3
            # Check collision
            for player in players.values():
                if player["alive"] and abs(player["x"] - vehicle["x"]) < 50 and abs(player["y"] - vehicle["y"]) < 50:
                    player["alive"] = False
        threading.Event().wait(0.1)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        # Start vehicle spawning thread
        threading.Thread(target=spawn_vehicles, daemon=True).start()

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
