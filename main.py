import pygame as p
import os
import sys
import random
from enum import Enum
import pickle
import socket
import json
from threading import Thread



p.init()

screen_width = 500
screen_height = 700
font_path = "C:\\Windows\\Fonts\\segoesc.ttf"

BG_COLOR = (252, 243, 227)
LINE_COLOR = (50, 50, 50)
WIDTH, HEIGHT = screen_width, screen_height
screen = p.display.set_mode((screen_width, screen_height))
win = screen

overlay = p.image.load("texture_overlay.png").convert_alpha()
font1 = p.font.Font(font_path, 36)
text = font1.render("Tic Tac Toe", True, (0, 0, 0))

shape = p.image.load("shape.png")  
shape_width, shape_height = shape.get_size()

font = p.font.Font(font_path, 24)
text1 = font.render("user vs user ", True, (255, 255, 255))
text2 = font.render("user vs machine", True, (255, 255, 255))
text3 = font.render("user vs user(online)", True, (255, 255, 255))

text_rect = text.get_rect(center=(screen_width // 2, screen_height // 4))
text1_rect = text1.get_rect(center=(screen_width // 2, 370))
text2_rect = text2.get_rect(center=(screen_width // 2, 370 + shape_height + 10))
text3_rect = text3.get_rect(center=(screen_width // 2, 370 + 2 * (shape_height + 10)))

GRID_COLOR = (50, 50, 50)
LINE_THICKNESS = 5  

GRID_SIZE = 450  
GRID_X = (screen_width - GRID_SIZE) // 2  
GRID_Y = (screen_height - GRID_SIZE) // 2  
CELL_SIZE = GRID_SIZE // 3


O_img = p.image.load("O.png")
X_img = p.image.load("X.png")

O_img = p.transform.scale(O_img, (CELL_SIZE, CELL_SIZE))
X_img = p.transform.scale(X_img, (CELL_SIZE, CELL_SIZE))

# Initialize game state
current_page = "menu"
markers = [[0 for _ in range(3)] for _ in range(3)]
player = 1  
clicked = False
pos=[]
player = 1
winner = 0
game_over= False

# Button-related variables
button_text = "Restart"  # Text on the button
button_rect = p.Rect(screen_width // 2 - 100, GRID_Y + GRID_SIZE + 20, 200, 50)  # Position and size of the button
button_font = p.font.SysFont("Arial", 30)  # Font for the button text
button_color = (255, 255, 255)  # Color of the text (white for visibility)
button_image = p.image.load("rectangle 1.png")  # Background image for the button





class RLAgent:
    def __init__(self):
        self.model_loaded = False
        self.qtable = None
        self.load_q_agent()
        
        # Strategic fallbacks when Q-table fails
        self.fallback_rules = [
            self._win_if_possible,
            self._block_opponent,
            self._take_center,
            self._take_corner,
            self._take_side
        ]

    def load_q_agent(self):
        try:
            with open('q_agent.pkl', 'rb') as f:
                agent = pickle.load(f)
                if len(agent.Q) < 5000:
                    raise ValueError("Q-table too small - retrain with more episodes")
                self.qtable = agent.Q
                self.model_loaded = True
                print(f"Loaded Q-agent with {len(self.qtable)} states")
        except Exception as e:
            print(f"Using fallback rules - {e}")

    def act(self, board):
        # Try Q-table first
        if self.model_loaded:
            try:
                state = self._convert_state(board)
                if state in self.qtable:
                    action = max(self.qtable[state].items(), key=lambda x: x[1])[0]
                    return (action // 3, action % 3)
            except Exception as e:
                print(f"Q-table error: {e}")
        
        # Strategic fallbacks
        for strategy in self.fallback_rules:
            move = strategy(board)
            if move: return move
            
        return self._random_move(board)

    # Strategic fallback methods
    def _win_if_possible(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = -1
                    if self._check_win(board) == -1:
                        board[i][j] = 0
                        return (i, j)
                    board[i][j] = 0
        return None

    def _block_opponent(self, board):
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = 1
                    if self._check_win(board) == 1:
                        board[i][j] = 0
                        return (i, j)
                    board[i][j] = 0
        return None

    def _take_center(self, board):
        return (1, 1) if board[1][1] == 0 else None

    def _take_corner(self, board):
        corners = [(0,0), (0,2), (2,0), (2,2)]
        random.shuffle(corners)
        for i,j in corners:
            if board[i][j] == 0:
                return (i, j)
        return None

    def _take_side(self, board):
        sides = [(0,1), (1,0), (1,2), (2,1)]
        random.shuffle(sides)
        for i,j in sides:
            if board[i][j] == 0:
                return (i, j)
        return None

    def _random_move(self, board):
        valid = [(i,j) for i in range(3) for j in range(3) if board[i][j] == 0]
        return random.choice(valid) if valid else None

    def _convert_state(self, board):
        return ''.join('2' if x == -1 else str(x) for row in board for x in row)

    def _check_win(self, board):
        # Check rows, columns, and diagonals
        lines = (
            *[(board[i][0], board[i][1], board[i][2]) for i in range(3)],  # rows
            *[(board[0][i], board[1][i], board[2][i]) for i in range(3)],  # cols
            (board[0][0], board[1][1], board[2][2]),  # diagonal
            (board[0][2], board[1][1], board[2][0])   # anti-diagonal
        )
        for line in lines:
            if all(c == -1 for c in line): return -1
            if all(c == 1 for c in line): return 1
        return 0
    
    

ai_agent = RLAgent()


online_game = {
    "socket": None,
    "player_id": None,
    "current_player": 0,
    "board": [[" " for _ in range(3)] for _ in range(3)],
    "game_over": False,
    "waiting": True
}


def connect_to_server(host='localhost', port=5555):
    try:
        online_game["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        online_game["socket"].connect((host, port))
        return True
    except Exception as e:
        print(f"Connection error: {e}")
        online_game["waiting"] = False
        return False
    
    
def draw_board():
    # Draw grid lines
    for i in range(1, 3):
        p.draw.line(win, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH)
        p.draw.line(win, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_WIDTH)
    
    # Draw X's and O's from the online_game["board"]
    for row in range(3):
        for col in range(3):
            if online_game["board"][row][col] == "X":
                draw_x(row, col)
            elif online_game["board"][row][col] == "O":
                draw_o(row, col)
    
    p.display.update()

def receive_updates():
    while True:
        try:
            data = online_game["socket"].recv(1024).decode()
            if not data:
                break
                
            message = json.loads(data)
            print(f"CLIENT RECEIVED: {message}")  # Debug print

            if message["action"] == "assign_id":
                online_game["player_id"] = message["player"]
                online_game["current_player"] = 0  # X goes first
                online_game["waiting"] = False
                print(f"Assigned as Player {online_game['player_id']}")

            elif message["action"] == "game_start":
                online_game["board"] = message["board"]
                online_game["current_player"] = message["current_player"]
                online_game["waiting"] = False
                print("Game started! Current player:", online_game["current_player"])

            elif message["action"] == "move_made":
                online_game["board"] = message["board"]
                online_game["current_player"] = message["current_player"]
                print(f"Player {message.get('player')} moved. Now it's Player {online_game['current_player']}'s turn")

            elif message["action"] == "game_over":
                online_game["board"] = message["board"]
                online_game["game_over"] = True
                online_game["winner"] = message["winner"]

        except Exception as e:
            print(f"Error in receive_updates: {e}")
            break
        
def draw_x(row, col):
    x_pos = GRID_X + col * CELL_SIZE
    y_pos = GRID_Y + row * CELL_SIZE
    screen.blit(X_img, (x_pos, y_pos))

def draw_o(row, col):
    x_pos = GRID_X + col * CELL_SIZE
    y_pos = GRID_Y + row * CELL_SIZE
    screen.blit(O_img, (x_pos, y_pos))

def get_clicked_position(pos):
    """Convert screen position to grid coordinates."""
    x, y = pos
    col = (x - GRID_X) // CELL_SIZE
    row = (y - GRID_Y) // CELL_SIZE
    return row, col

def is_board_full(board):
    return all(cell != " " for row in board for cell in row)


def send_move(row, col):
    if online_game["socket"] and online_game["board"][row][col] == " ":
        online_game["socket"].send(json.dumps({
            "row": row, 
            "col": col
        }).encode())



def draw_grid():
    """Draw the Tic-Tac-Toe grid centered on the screen."""
    for i in range(1, 3):
        p.draw.line(screen, GRID_COLOR, 
                    (GRID_X, GRID_Y + i * CELL_SIZE), 
                    (GRID_X + GRID_SIZE, GRID_Y + i * CELL_SIZE), 
                    LINE_THICKNESS)

        p.draw.line(screen, GRID_COLOR, 
                    (GRID_X + i * CELL_SIZE, GRID_Y), 
                    (GRID_X + i * CELL_SIZE, GRID_Y + GRID_SIZE), 
                    LINE_THICKNESS)


def draw_button(text, rect, font, font_color, background_image, screen):
    # to draw the restart button
    button_scaled = p.transform.scale(background_image, (rect.width, rect.height))  # Scale the image
    screen.blit(button_scaled, (rect.x, rect.y))
    rendered_text = font.render(text, True, font_color)
    text_rect = rendered_text.get_rect(center=rect.center)
    screen.blit(rendered_text, text_rect)

def handle_button_click(button_rect, mouse_pos, action_function):
    """Detects button click and calls the associated function."""
    if button_rect.collidepoint(mouse_pos):
        action_function()


def restart_game():
    # Action for the restart button
    global markers, player, game_over, winner
    markers = [[0 for _ in range(3)] for _ in range(3)]  # Reset the grid
    player = 1  # Set player 1 to start
    game_over = False  # Reset game over flag
    winner = 0  # No winner initially




def draw_markers():
    """Draw X and O based on the markers array."""
    for row in range(3):
        for col in range(3):
            x_pos = GRID_X + col * CELL_SIZE
            y_pos = GRID_Y + row * CELL_SIZE
            if markers[row][col] == 1:
                screen.blit(X_img, (x_pos, y_pos))
            elif markers[row][col] == -1:
                screen.blit(O_img, (x_pos, y_pos))


def draw_game_result():
    """Display the game result"""
    font_win = p.font.Font(font_path, 36)  
    if winner == 0:
        win_text = font_win.render("It's a Draw!", True, (244, 162, 88))
    elif current_page == "pvp":
         win_text = font_win.render(f"Player {1 if winner == 1 else 2} Wins!", True, (244, 162, 88))
    else:
        win_text = font_win.render("X Wins!" if winner == 1 else "O Wins!", True, (244, 162, 88))

    win_rect = win_text.get_rect(center=(screen_width // 2, GRID_Y - 50)) 
    screen.blit(win_text, win_rect)



def check_winner():
    global winner
    global game_over
    y_pos = 0
    for x in markers:
        # Check columns
        if sum(x) == 3:
            winner = 1
            game_over = True
        if sum(x) == -3:
            winner = 2
            game_over = True
        # Check rows
        if markers[0][y_pos] + markers[1][y_pos] +  markers[2][y_pos] == 3:
            winner = 1
            game_over = True
        if markers[0][y_pos] + markers[1][y_pos] +  markers[2][y_pos] == -3:
            winner = 2
            game_over = True
        y_pos += 1
    # Check diagonals
    if markers[0][0] + markers[1][1] + markers[2][2] == 3 or markers[2][0] + markers[1][1] + markers[0][2] == 3:
        winner = 1
        game_over = True
    if markers[0][0] + markers[1][1] + markers[2][2] == -3 or markers[2][0] + markers[1][1] + markers[0][2] == -3:
        winner = 2
        game_over = True
    
    # Check for a draw (no winner, all cells filled)
    if game_over == False and all(markers[row][col] != 0 for row in range(3) for col in range(3)):
        game_over = True
        winner = 0  # No winner, it's a draw
        

def draw_status():
    font = p.font.Font(None, 30)
    status = f"Your symbol: {'X' if online_game['player_id'] == 0 else 'O'} | Current turn: {'X' if online_game['current_player'] == 0 else 'O'}"
    text = font.render(status, True, (0, 0, 0))
    win.blit(text, (10, HEIGHT - 30))
        

def page_1(overlay):
    """Main game loop for user vs user"""
    global clicked, player, markers, game_over

    running = True
    while running:
        screen.fill((252, 243, 227))  # Clear screen each frame
        screen.blit(overlay, (0, 0))
        draw_grid()
        draw_markers()

        # Display winner message above the grid if game_over is True
        if game_over:
            font_win = p.font.Font(font_path, 36)  
            if winner == 0:
                win_text = font_win.render("It's a Draw!", True, (244, 162, 88))
            else:
                win_text = font_win.render("X Wins!" if winner == 1 else "O Wins!", True, (244, 162, 88))

            win_rect = win_text.get_rect(center=(screen_width // 2, GRID_Y - 50)) 
            screen.blit(win_text, win_rect)
            
            draw_button(button_text, button_rect, button_font, button_color, button_image, screen)  # Draw Restart Button

            mouse_x, mouse_y = p.mouse.get_pos()
            if button_rect.collidepoint(mouse_x, mouse_y) and p.mouse.get_pressed()[0]: 
                restart_game()  

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            if event.type == p.MOUSEBUTTONDOWN and not clicked and not game_over:
                clicked = True

            if event.type == p.MOUSEBUTTONUP and clicked and not game_over:
                clicked = False
                pos = p.mouse.get_pos()

                # Calculate grid cell based on click position
                cell_x = (pos[0] - GRID_X) // CELL_SIZE
                cell_y = (pos[1] - GRID_Y) // CELL_SIZE

                # Ensure the click is inside the grid and the game is not over
                if 0 <= cell_x < 3 and 0 <= cell_y < 3:
                    if markers[cell_y][cell_x] == 0:  # Check if cell is empty
                        markers[cell_y][cell_x] = player  
                        player *= -1  # Switch player
                        check_winner()  # Check for a winner after the move

        p.display.update()
        

def page_2(overlay):
    global current_page, clicked, player, markers, game_over, winner
    
    running = True
    while running:
        screen.fill((252, 243, 227))
        screen.blit(overlay, (0, 0))
        draw_grid()
        draw_markers()
        
        if game_over:
            draw_game_result()
            draw_button(button_text, button_rect, button_font, button_color, button_image, screen)
        
        # AI move logic - MODIFIED SECTION
        if not game_over and player == -1:
            p.time.delay(500)
            move = ai_agent.act(markers)
            if move and markers[move[0]][move[1]] == 0:
                markers[move[0]][move[1]] = -1  # Or 2 if you changed symbols
                check_winner()
                if not game_over:
                    player = 1
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            
            if event.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                
                if not game_over and player == 1:
                    cell_x = (pos[0] - GRID_X) // CELL_SIZE
                    cell_y = (pos[1] - GRID_Y) // CELL_SIZE
                    
                    if 0 <= cell_x < 3 and 0 <= cell_y < 3 and markers[cell_y][cell_x] == 0:
                        markers[cell_y][cell_x] = 1
                        check_winner()
                        if not game_over:
                            player = -1
                
                if game_over and button_rect.collidepoint(pos):
                    restart_game()
                    running = False
                    current_page = "menu"
        
        p.display.update()

def page_3():
    """Online multiplayer game page with fixed turn management"""
    global current_page

    # Initialize connection
    if not connect_to_server():
        print("[CLIENT] Failed to connect to server")
        current_page = "menu"
        return

    # Start thread for receiving server updates
    Thread(target=receive_updates, daemon=True).start()

    # Game loop
    clock = p.time.Clock()
    running = True
    
    while running:
        # Event handling
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()

            # Handle mouse clicks
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()

                # Return to menu button
                if online_game.get("game_over") and button_rect.collidepoint(mouse_pos):
                    online_game["socket"].close()
                    current_page = "menu"
                    running = False

                # Board click handling
                elif (not online_game.get("waiting", True) and 
                      not online_game.get("game_over", False)):
                    
                    # Convert mouse position to grid coordinates
                    row = (mouse_pos[1] - GRID_Y) // CELL_SIZE
                    col = (mouse_pos[0] - GRID_X) // CELL_SIZE

                    # Validate move (empty cell and correct turn)
                    if (0 <= row < 3 and 0 <= col < 3 and
                        online_game["board"][row][col] == " " and
                        online_game.get("current_player") == online_game.get("player_id")):
                        
                        try:
                            # Send move to server
                            online_game["socket"].send(json.dumps({
                                "action": "make_move",
                                "row": row,
                                "col": col,
                                "player": online_game["player_id"]
                            }).encode())
                            print(f"[CLIENT] Sent move: ({row}, {col}) as Player {online_game['player_id']}")
                        except Exception as e:
                            print(f"[CLIENT] Failed to send move: {e}")
                            running = False
                            current_page = "menu"

        # Drawing
        screen.fill(BG_COLOR)
        
        # Draw game board
        draw_grid()
        for row in range(3):
            for col in range(3):
                if online_game["board"][row][col] == "X":
                    draw_x(row, col)
                elif online_game["board"][row][col] == "O":
                    draw_o(row, col)

        # Draw status messages
        if online_game.get("waiting", True):
            # Waiting for opponent
            font = p.font.Font(font_path, 24)
            text = font.render("Waiting for opponent...", True, (0, 0, 0))
            text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
            screen.blit(text, text_rect)
        else:
            # Turn indicator
            font = p.font.Font(font_path, 20)
            if online_game.get("current_player") == online_game.get("player_id"):
                status = "Your turn (" + ("X" if online_game["player_id"] == 0 else "O") + ")"
                color = (0, 128, 0)  # Green for your turn
            else:
                status = "Opponent's turn (" + ("X" if online_game["current_player"] == 0 else "O") + ")"
                color = (128, 0, 0)  # Red for opponent's turn
                
            status_text = font.render(status, True, color)
            screen.blit(status_text, (10, GRID_Y - 30))

        # Game over message
        if online_game.get("game_over"):
            font = p.font.Font(font_path, 36)
            if online_game["winner"] == "draw":
                result = "Game ended in a draw!"
            else:
                if (online_game["winner"] == "X" and online_game["player_id"] == 0) or \
                   (online_game["winner"] == "O" and online_game["player_id"] == 1):
                    result = "You won!"
                else:
                    result = "You lost!"
            
            text = font.render(result, True, (244, 162, 88))
            text_rect = text.get_rect(center=(screen_width//2, GRID_Y - 50))
            screen.blit(text, text_rect)
            
            # Return to menu button
            draw_button("Back to Menu", button_rect, button_font, button_color, button_image, screen)

        p.display.update()
        clock.tick(30)
    
run = True
while run:
    screen.fill((252, 243, 227))
    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)

    # Blit the shape 3 times, aligned vertically
    screen.blit(shape, (screen_width // 2 - shape_width // 2, 350))  # First shape
    screen.blit(shape, (screen_width // 2 - shape_width // 2, 350 + shape_height + 10))  # Second shape
    screen.blit(shape, (screen_width // 2 - shape_width // 2, 350 + 2 * (shape_height + 10)))  # Third shape

    # Blit the text inside each shape
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)

    # Mouse click detection
    mouse_x, mouse_y = p.mouse.get_pos()  # Get the current mouse position
    mouse_pressed = p.mouse.get_pressed()  # Get the mouse button state (left, middle, right)

    if mouse_pressed[0]:  # Left-click
        if text1_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the first rectangle
            page_1(overlay) 
        elif text2_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the second rectangle
            page_2(overlay)  
        elif text3_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the third rectangle
            page_3() 

    # If the game is over, draw the restart button
    if game_over:
        draw_button(button_text, button_rect, button_font, button_color, button_image, screen)

    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

    p.display.update()

            
p.quit()