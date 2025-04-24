import pygame
import chess

pygame.init()
WIDTH, HEIGHT = 640, 740  # Height includes scoreboard
SQUARE_SIZE = 80
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2-Player Chess")

# Colors (Lichess style)
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
HOVER_COLOR = (200, 200, 50)
DARK_GRAY = (50, 50, 50)
FONT = pygame.font.SysFont("timesnewroman", 20)

# Load images (Lichess-style PNGs named like 'wp.png', 'bk.png')
IMAGES = {}
BASE_PIECE_SIZE = int(SQUARE_SIZE * 0.8)
HOVER_PIECE_SIZE = SQUARE_SIZE

for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        name = f"{color}{piece}"
        img = pygame.image.load(f"{name}.png")
        IMAGES[name] = {
            'normal': pygame.transform.scale(img, (BASE_PIECE_SIZE, BASE_PIECE_SIZE)),
            'hover': pygame.transform.scale(img, (HOVER_PIECE_SIZE, HOVER_PIECE_SIZE))
        }

def draw_board(board, selected=None, legal_moves=[], hover_square=None):
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, 7 - rank)
            rect = pygame.Rect(file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            color = LIGHT if (rank + file) % 2 == 0 else DARK
            pygame.draw.rect(SCREEN, color, rect)

            if square == selected:
                pygame.draw.rect(SCREEN, HIGHLIGHT, rect, 4)
            elif square == hover_square:
                pygame.draw.rect(SCREEN, HOVER_COLOR, rect, 4)
            elif square in legal_moves:
                pygame.draw.circle(SCREEN, HIGHLIGHT, rect.center, 10)

            piece = board.piece_at(square)
            if piece:
                piece_str = f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"
                if square == hover_square:
                    piece_img = IMAGES[piece_str]['hover']
                    offset = (SQUARE_SIZE - HOVER_PIECE_SIZE) // 2
                else:
                    piece_img = IMAGES[piece_str]['normal']
                    offset = (SQUARE_SIZE - BASE_PIECE_SIZE) // 2
                SCREEN.blit(piece_img, (file*SQUARE_SIZE + offset, rank*SQUARE_SIZE + offset))

    for i in range(8):
        file_label = FONT.render(chr(ord('a') + i), True, (0, 0, 0))
        rank_label = FONT.render(str(8 - i), True, (0, 0, 0))
        SCREEN.blit(file_label, (i * SQUARE_SIZE + 5, HEIGHT - 100))
        SCREEN.blit(rank_label, (5, i * SQUARE_SIZE + 5))

def draw_scoreboard(captured_white, captured_black, white_score, black_score, draws, game_over, white_teleport_used, black_teleport_used):
    pygame.draw.rect(SCREEN, DARK_GRAY, (0, 640, WIDTH, 100))
    SCREEN.blit(FONT.render(f"White Captured: {''.join(captured_white)}", True, (255, 255, 255)), (10, 645))
    SCREEN.blit(FONT.render(f"Black Captured: {''.join(captured_black)}", True, (255, 255, 255)), (10, 670))
    scoreboard = f"Score - White: {white_score}  Black: {black_score}  Draws: {draws}"
    SCREEN.blit(FONT.render(scoreboard, True, (255, 255, 255)), (10, 700))
    SCREEN.blit(FONT.render(f"Teleport Used (White): {'Yes' if white_teleport_used else 'No'}", True, (255, 255, 255)), (350, 645))
    SCREEN.blit(FONT.render(f"Teleport Used (Black): {'Yes' if black_teleport_used else 'No'}", True, (255, 255, 255)), (350, 670))

    if game_over:
        pygame.draw.rect(SCREEN, (90, 90, 90), (480, 680, 140, 40))
        SCREEN.blit(FONT.render("Restart", True, (255, 255, 255)), (510, 690))

def restart_button_clicked(pos):
    x, y = pos
    return 480 <= x <= 620 and 680 <= y <= 720

def main():
    board = chess.Board()
    clock = pygame.time.Clock()
    selected_square = None
    legal_moves = []
    hover_square = None

    captured_white, captured_black = [], []
    white_score = black_score = draws = 0
    game_over = False

    white_teleport_used = False
    black_teleport_used = False

    knight_double_jump = None
    knight_double_jump_pending = False
    knight_cooldown = {chess.WHITE: 0, chess.BLACK: 0}

    running = True
    while running:
        draw_board(board, selected_square, legal_moves, hover_square)
        draw_scoreboard(captured_white, captured_black, white_score, black_score, draws, game_over, white_teleport_used, black_teleport_used)
        pygame.display.flip()
        clock.tick(30)

        hover_square = None
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] < 640:
            col = mouse_pos[0] // SQUARE_SIZE
            row = 7 - (mouse_pos[1] // SQUARE_SIZE)
            hover_square = chess.square(col, row)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if game_over and restart_button_clicked(pos):
                    board.reset()
                    captured_white.clear()
                    captured_black.clear()
                    white_teleport_used = False
                    black_teleport_used = False
                    knight_double_jump = None
                    knight_double_jump_pending = False
                    knight_cooldown = {chess.WHITE: 0, chess.BLACK: 0}
                    game_over = False
                    continue

                if board.is_game_over():
                    continue

                x, y = pos
                if y > 640:
                    continue
                col = x // SQUARE_SIZE
                row = 7 - (y // SQUARE_SIZE)
                square = chess.square(col, row)

                if event.button == 3:
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:
                        if piece.piece_type == chess.QUEEN:
                            teleport_used = white_teleport_used if board.turn == chess.WHITE else black_teleport_used
                            if not teleport_used:
                                selected_square = square
                                legal_moves = [sq for sq in chess.SQUARES if board.piece_at(sq) is None]
                                continue
                        elif piece.piece_type == chess.KNIGHT and knight_cooldown[board.turn] == 0:
                            knight_double_jump = square
                            knight_double_jump_pending = True
                            selected_square = square
                            legal_moves = [m.to_square for m in board.legal_moves if m.from_square == square]
                            continue

                if selected_square is None:
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:
                        selected_square = square
                        legal_moves = [m.to_square for m in board.legal_moves if m.from_square == square]
                else:
                    if square in legal_moves and board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.QUEEN and board.piece_at(square) is None:
                        board.remove_piece_at(selected_square)
                        board.set_piece_at(square, chess.Piece(chess.QUEEN, board.turn))
                        if board.turn == chess.WHITE:
                            white_teleport_used = True
                        else:
                            black_teleport_used = True
                        board.turn = not board.turn
                    else:
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            captured = board.piece_at(square)
                            if captured:
                                (captured_black if board.turn else captured_white).append(captured.symbol())
                            board.push(move)

                            if knight_double_jump_pending:
                                if knight_double_jump == selected_square:
                                    selected_square = square
                                    legal_moves = [m.to_square for m in board.legal_moves if m.from_square == square]
                                    knight_double_jump_pending = False  # Allow second move without switching turn
                                    knight_double_jump = square
                                    continue
                                elif knight_double_jump == square:
                                    knight_double_jump = None
                                    knight_cooldown[board.turn] = 3

                            if not knight_double_jump_pending:
                                if board.is_game_over():
                                    result = board.result()
                                    if result == '1-0':
                                        white_score += 1
                                    elif result == '0-1':
                                        black_score += 1
                                    else:
                                        draws += 1
                                    game_over = True
                                # Decrease cooldowns at the end of the turn
                                for color in [chess.WHITE, chess.BLACK]:
                                    if knight_cooldown[color] > 0:
                                        knight_cooldown[color] -= 1
                                board.turn = not board.turn

                    selected_square = None
                    legal_moves = []

    pygame.quit()

if __name__ == "__main__":
    main()
