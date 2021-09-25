import pygame as p
import ChessEngine

WIDTH = 512
HEIGHT = 512

DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images. Called once in main
'''

def load_Images():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wp", "bR", "bN", "bB", "bQ", "bK", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

'''
Main driver of code: Handles user input and updates game's graphics
'''

def main():
    p.init()

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_State = ChessEngine.GameState()
    validMoves = game_State.getValidMoves()
    moveMade = False #flag var for when move is made

    animate = False

    load_Images()
    running = True
    squareSelected = () #no square is selected, keeps track of the last click of the user
    playerClicks = [] #keeps track of player clicks

    gameOver = False
    

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    column = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE
                    if squareSelected == (row, column): #the user clicked on the same square twice  | or (game_State.board[squareSelected[1]][squareSelected[0]] == "--" and playerClicks == [])
                        squareSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        squareSelected = (row, column)
                        playerClicks.append(squareSelected) #append for both first and second clicks

                    if len(playerClicks) == 2: #after the 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], game_State.board)
                        print(move.getChessNotation()) ###MOVE THIS LATER
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                game_State.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    game_State.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    game_State = ChessEngine.GameState()
                    validMoves = game_State.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(game_State.moveLog[-1], screen, game_State.board, clock)
            validMoves = game_State.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, game_State, validMoves, squareSelected)

        if game_State.checkMate:
            gameOver = True
            if game_State.whiteToMove:
                drawText(screen, 'Black wins by chackmate')
            else:
                drawText(screen, 'White wins by chackmate')
        elif game_State.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, game_State, valid_Moves, square_Selected):
    if square_Selected != ():
        row, column = square_Selected
        if game_State.board[row][column][0] == ('w' if game_State.whiteToMove else 'b'):
            surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)
            surface.fill(p.Color('blue'))
            screen.blit(surface, (column*SQUARE_SIZE, row*SQUARE_SIZE))
            surface.fill(p.Color('yellow'))
            for move in valid_Moves:
                if move.start_Row == row and move.start_Column == column:
                    screen.blit(surface, (move.end_Column*SQUARE_SIZE, move.end_Row*SQUARE_SIZE))


'''
Responsible for all graphics within the current game state
'''
def drawGameState(screen, game_State, valid_Moves, square_Selected):
    drawBoard(screen)
    highlightSquares(screen, game_State, valid_Moves, square_Selected)
    drawPieces(screen, game_State.board)

'''
Draws the squares on the board
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column)%2]
            p.draw.rect(screen, color, p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

'''
Draws the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.end_Row - move.start_Row
    dC = move.end_Column - move.start_Column
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, column = (move.start_Row + dR*frame/frameCount, move.start_Column + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.end_Row + move.end_Column) % 2]
        endSquare = p.Rect(move.end_Column*SQUARE_SIZE, move.end_Row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.piece_Captured != '--':
            screen.blit(IMAGES[move.piece_Captured], endSquare)

        screen.blit(IMAGES[move.piece_Moved], p.Rect(move.end_Column*SQUARE_SIZE, move.end_Row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)
        
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()