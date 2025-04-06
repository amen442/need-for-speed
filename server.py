import socket
import threading
import random
import json
import time

HOST = '192.168.150.37'
PORT = 9999

players = {}
vehicles = []
speed = 10
lock = threading.Lock()
ai_thread_started = False

def ai_controller():
    global speed
    while True:
        with lock:
            for pid, player in players.items():
                if player.get('type') == 'AI' and player['alive']:
                    dangers = {150: False, 250: False, 350: False}
                    for v in vehicles:
                        if v['y'] < player['y'] + 150:
                            dangers[v['x']] = True

                    safe_lanes = [lane for lane, danger in dangers.items() if not danger]
                    if safe_lanes:
                        target_x = random.choice(safe_lanes)
                        if target_x < player['x'] and player['x'] > 150:
                            player['x'] -= 100
                        elif target_x > player['x'] and player['x'] < 350:
                            player['x'] += 100
                    else:
                        if player['x'] != 250:
                            player['x'] = 250
        time.sleep(0.5)

def handle_client(conn, addr):
    global ai_thread_started
    print(f"Connected by {addr}")
    player_id = None
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()

            if message.startswith("JOIN"):
                _, mode = message.split(":")
                with lock:
                    player_id = len(players) + 1
                    players[player_id] = {
                        "x": 250,
                        "y": 400,
                        "score": 0,
                        "alive": True,
                        "type": "HUMAN"
                    }


                    if mode.strip() == "AI" and not ai_thread_started:
                        ai_player_id = player_id + 1
                        players[ai_player_id] = {
                            "x": 150,
                            "y": 400,
                            "score": 0,
                            "alive": True,
                            "type": "AI"
                        }
                        threading.Thread(target=ai_controller, daemon=True).start()
                        ai_thread_started = True

                print(f"Player {player_id} ({mode.strip()}) joined the game.")
                conn.sendall(f"ID:{player_id}".encode())

            elif message.startswith("MOVE"):
                _, pid, direction = message.split(":")
                pid = int(pid)
                with lock:
                    if pid in players and players[pid]["alive"]:
                        if direction == "LEFT" and players[pid]["x"] > 150:
                            players[pid]["x"] -= 100
                        elif direction == "RIGHT" and players[pid]["x"] < 350:
                            players[pid]["x"] += 100

            elif message == "GET_STATE":
                with lock:
                    game_state = {
                        "players": players,
                        "vehicles": vehicles,
                        "speed": speed
                    }
                    conn.sendall(json.dumps(game_state).encode())

            elif message == "RESTART" and player_id:
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
        if len(vehicles) < 2 + len(players) // 2:
            vehicle = {
                "x": random.choice(lanes),
                "y": -50,
                "type": random.choice(["taxi", "van", "semi_trailer"])
            }
            with lock:
                vehicles.append(vehicle)

        with lock:
            for vehicle in list(vehicles):
                vehicle["y"] += speed
                if vehicle["y"] > 500:
                    vehicles.remove(vehicle)
                    for pid, player in players.items():
                        if player["alive"] and player["type"] == "HUMAN":
                            player["score"] += 1
                            if player["score"] % 5 == 0:
                                speed += 1

                for pid, player in players.items():
                    if (player["alive"] and 
                        abs(player["x"] - vehicle["x"]) < 50 and 
                        abs(player["y"] - vehicle["y"]) < 50):
                        player["alive"] = False
        time.sleep(0.1)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        threading.Thread(target=spawn_vehicles, daemon=True).start()

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
