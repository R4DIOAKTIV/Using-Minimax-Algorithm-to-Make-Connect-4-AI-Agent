import numpy as np
import pygame
import sys

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

PLAYER_PIECE = 1
AI_PIECE = 2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(SIZE)
font = pygame.font.SysFont("monospace", 75)

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def animate_piece_drop(board, row, col, piece):
    for r in range(row+1):
        draw_board(board)
        pygame.draw.circle(screen, RED if piece == PLAYER_PIECE else YELLOW,
                           (int(col*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
        pygame.display.update()
        pygame.time.wait(50)

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if all(board[r, c+i] == piece for i in range(4)):
                return True

    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if all(board[r+i, c] == piece for i in range(4)):
                return True

    # Positive slope diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if all(board[r+i, c+i] == piece for i in range(4)):
                return True

    # Negative slope diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i, c+i] == piece for i in range(4)):
                return True
    return False

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000000000000
            elif winning_move(board, PLAYER_PIECE):
                return None, -10000000000000
            else:
                return None, 0
        else:
            return None, 0

    if maximizingPlayer:
        value = -np.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:
        value = np.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# Main Game Loop
board = create_board()
draw_board(board)  # Ensure the board is drawn at the beginning
game_over = False
turn = 0

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                board = create_board()
                game_over = False
                turn = 0

        if turn == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            col = event.pos[0] // SQUARESIZE
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                animate_piece_drop(board, row, col, PLAYER_PIECE)
                drop_piece(board, row, col, PLAYER_PIECE)

                if winning_move(board, PLAYER_PIECE):
                    label = font.render("Player 1 Wins!", 1, RED)
                    screen.blit(label, (40, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True
                turn += 1
                turn %= 2

        if turn == 1 and not game_over:
            col, _ = minimax(board, 5, -np.inf, np.inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                animate_piece_drop(board, row, col, AI_PIECE)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = font.render("AI Wins!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True
                turn += 1
                turn %= 2

        draw_board(board)
