import socket
import json
from threading import Thread

class TicTacToeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = []
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = 0  # Player 0 (X) starts first
        self.game_over = False
        print(f"Server started on {host}:{port}. Waiting for players...")

    def broadcast(self, message):
        """Send message to all connected clients"""
        for client in self.clients:
            try:
                client.send(json.dumps(message).encode())
                print(f"[SERVER] Broadcast: {message}")  # Debug
            except Exception as e:
                print(f"[SERVER] Broadcast failed: {e}")
                self.remove_client(client)

    def remove_client(self, client):
        """Clean up disconnected clients"""
        if client in self.clients:
            print(f"[SERVER] Removing disconnected client")
            self.clients.remove(client)
            if len(self.clients) < 2:
                self.reset_game()

    def reset_game(self):
        """Reset game state when players disconnect"""
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = 0
        self.game_over = False
        print("[SERVER] Game reset - waiting for players")

    def check_winner(self):
        """Check for a winner or draw. Returns 'X', 'O', 'draw', or None."""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return self.board[0][col]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return self.board[0][2]
        
        # Check draw
        if all(cell != " " for row in self.board for cell in row):
            return "draw"
        return None

    def handle_client(self, client, player_id):
        """Handle communication with a client (Player 0 or 1)"""
        try:
            # Send player their assigned ID
            assign_msg = {
                "action": "assign_id", 
                "player": player_id,
                "symbol": "X" if player_id == 0 else "O"
            }
            client.send(json.dumps(assign_msg).encode())
            print(f"[SERVER] Assigned Player {player_id} as {'X' if player_id == 0 else 'O'}")

            # Start game when both players connect
            if len(self.clients) == 2:
                start_msg = {
                    "action": "game_start",
                    "board": self.board,
                    "current_player": self.current_player
                }
                self.broadcast(start_msg)
                print("[SERVER] Game started")

            # Main game loop for this client
            while True:
                data = client.recv(1024).decode()
                if not data:
                    break

                message = json.loads(data)
                print(f"[SERVER] Received from Player {player_id}: {message}")

                if message["action"] == "make_move":
                    row, col = message["row"], message["col"]

                    # Validate move
                    if (player_id == self.current_player and
                        0 <= row < 3 and 0 <= col < 3 and
                        self.board[row][col] == " " and
                        not self.game_over):
                        
                        # Update board
                        self.board[row][col] = "X" if player_id == 0 else "O"
                        print(f"[SERVER] Player {player_id} moved to ({row}, {col})")

                        # Check for winner
                        winner = self.check_winner()
                        if winner:
                            self.game_over = True
                            self.broadcast({
                                "action": "game_over",
                                "winner": winner,
                                "board": self.board
                            })
                            print(f"[SERVER] Game over! Winner: {winner}")
                        else:
                            # Switch turns
                            self.current_player = 1 - self.current_player
                            self.broadcast({
                                "action": "move_made",
                                "board": self.board,
                                "current_player": self.current_player,
                                "last_move": {"row": row, "col": col, "player": player_id}
                            })
                            print(f"[SERVER] Turn switched to Player {self.current_player}")
                    else:
                        print(f"[SERVER] Invalid move from Player {player_id}")
                        client.send(json.dumps({
                            "action": "invalid_move",
                            "message": "Not your turn or invalid cell"
                        }).encode())

        except json.JSONDecodeError:
            print(f"[SERVER ERROR] Player {player_id} sent invalid data")
        except Exception as e:
            print(f"[SERVER ERROR] Player {player_id} error: {e}")
        finally:
            self.remove_client(client)
            client.close()
            print(f"[SERVER] Player {player_id} disconnected")

    def start(self):
        """Main server loop to accept connections"""
        while True:
            client, addr = self.server.accept()
            if len(self.clients) < 2:
                player_id = len(self.clients)
                self.clients.append(client)
                Thread(target=self.handle_client, args=(client, player_id)).start()
                print(f"[SERVER] Player {player_id} connected from {addr}")
            else:
                client.send(json.dumps({"action": "server_full"}).encode())
                client.close()
                print("[SERVER] Rejected connection (server full)")

if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()