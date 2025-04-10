import pygame as p
import os
import sys
import random
from enum import Enum

p.init()

screen_width = 500
screen_height = 700
font_path = "C:\\Windows\\Fonts\\segoesc.ttf"

screen = p.display.set_mode((screen_width, screen_height))
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



# DRL AI Integration (minimal changes to your structure)
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.model_loaded = False
        self._try_load_drl_model()
        
    def _try_load_drl_model(self):
        """Try to load the DRL model with fallback to random moves"""
        try:
            drl_path = r"C:\Users\User\Documents\1st business computing\semestre 2\fondaments des reseaux\projet reseaux\proj_res_xo\titactoe"
            if os.path.exists(drl_path):
                sys.path.append(drl_path)
            
            from drl_agent import DQNAgent as RealDQNAgent
            self.agent = RealDQNAgent(state_size=9, action_size=9)
            try:
                self.agent.load("tictactoe_dqn.h5")
                self.model_loaded = True
                print("DRL model loaded successfully")
            except Exception as e:
                print(f"DRL load error: {e}")
                self.model_loaded = False
        except ImportError as e:
            print(f"DRL import failed: {e}")
            self.model_loaded = False
    
    def act(self, state):
        """Get AI move, using DRL if available, otherwise random"""
        if self.model_loaded:
            try:
                # Convert board to DRL expected format
                drl_state = []
                for row in state:
                    for cell in row:
                        if cell == 0:    # Empty
                            drl_state.append(0)
                        elif cell == 1:  # X
                            drl_state.append(1)
                        else:            # O
                            drl_state.append(2)
                action = self.agent.act(drl_state)
                return (action // 3, action % 3)  # Convert to (row, col)
            except Exception as e:
                print(f"DRL error: {e}, using random move")
                return self._get_random_move(state)
        else:
            return self._get_random_move(state)
    
    def _get_random_move(self, board):
        """Fallback random move selection"""
        valid_moves = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    valid_moves.append((i, j))
        return random.choice(valid_moves) if valid_moves else None

# Initialize AI
ai_agent = DQNAgent(state_size=9, action_size=9)



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
        win_text = font_win.render(f"Player {winner} Wins!", True, (244, 162, 88))
    else:
        win_text = font_win.render("You Win!" if winner == 1 else "AI Wins!", True, (244, 162, 88))

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
                win_text = font_win.render(f"Player {winner} Wins!", True, (244, 162, 88))

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
        


def page_2(overlay):  # User vs AI
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
        
        # AI move logic
        if not game_over and player == -1:
            p.time.delay(500)  # Small delay for better UX
            move = ai_agent.act(markers)
            if move:
                row, col = move
                markers[row][col] = -1
                check_winner()
                if not game_over:
                    player = 1
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            
            if event.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                
                # Handle game move (only when game is active and player's turn)
                if not game_over and player == 1:
                    cell_x = (pos[0] - GRID_X) // CELL_SIZE
                    cell_y = (pos[1] - GRID_Y) // CELL_SIZE
                    
                    if 0 <= cell_x < 3 and 0 <= cell_y < 3 and markers[cell_y][cell_x] == 0:
                        markers[cell_y][cell_x] = 1
                        check_winner()
                        if not game_over:
                            player = -1
                
                # Handle restart button (same as page_1)
                if game_over and button_rect.collidepoint(pos):
                    restart_game()
                    running = False
                    current_page = "menu"  # Return to menu after restart
        
        p.display.update()

#def page_3():
    
    
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