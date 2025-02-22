import pygame as p

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
text2 = font.render("Second Text", True, (255, 255, 255))
text3 = font.render("Third Text", True, (255, 255, 255))

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
markers = [[0 for _ in range(3)] for _ in range(3)]
player = 1  
clicked = False
pos=[]
player = 1
winner = 0
game_over= False


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



def check_winner():
    global winner
    global game_over
    y_pos = 0
    for x in markers:
        #check collumn
        if sum(x) == 3:
            winner = 1
            game_over = True
        if sum(x) == -3:
            winner = 2
            game_over = True
            #check rows
        if markers[0][y_pos] + markers[1][y_pos] +  markers[2][y_pos] == 3 :
            winner = 1
            game_over = True
        if markers[0][y_pos] + markers[1][y_pos] +  markers[2][y_pos] == -3 :
            winner = 2
            game_over = True
        y_pos += 1
    #check_cross
    if markers[0][0] + markers[1][1] + markers[2][2] == 3 or markers[2][0] + markers[1][1] + markers[0][2] == 3 :
        winner = 1
        game_over = True
    if markers[0][0] + markers[1][1] + markers[2][2] == -3 or markers[2][0] + markers[1][1] + markers[0][2] == -3 :
        winner = 2
        game_over = True

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

def page_1(overlay):
    """Main game loop for the Tic-Tac-Toe game."""
    global clicked, player, markers, game_over

    running = True
    while running:
        screen.fill((252, 243, 227))  # Clear screen each frame
        screen.blit(overlay, (0, 0))
        draw_grid()
        draw_markers()

        # Display winner message above the grid if game_over is True
        if game_over:
            font_win = p.font.Font(font_path, 36)  # Adjust font size
            win_text = font_win.render(f"Player {winner} Wins!", True, (244,162,88))
            win_rect = win_text.get_rect(center=(screen_width // 2, GRID_Y - 50))  # Position above the grid
            screen.blit(win_text, win_rect)

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



    


# main loop 
run = True
while run:
    screen.fill((252,243,227))
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

    # Check if any shape is clicked
    if mouse_pressed[0]:  # Left click
        if text1_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the first rectangle
            print("First rectangle clicked")
            page_1(overlay)  # Move to next page (or action)
        elif text2_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the second rectangle
            print("Second rectangle clicked")
            page_2()  # Move to next page (or action)
        elif text3_rect.collidepoint(mouse_x, mouse_y):  # Check if the click is inside the third rectangle
            print("Third rectangle clicked")
            page_3()  # Move to next page (or action)
    
    
    
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False
            
    p.display.update()
            

p.quit()