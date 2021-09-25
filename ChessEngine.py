class GameState():
    def __init__(self):
        #board is an 8** 2 dimensional list, each element of the list
        #has two characters
        #first letter: color, second letter: type
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible= ()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    '''
    Takes a move as a parameter and executes, all moves except castling, en-passant, and pawn promotion
    '''
    def makeMove(self, move):
        self.board[move.start_Row][move.start_Column] = "--"
        self.board[move.end_Row][move.end_Column] = move.piece_Moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.piece_Moved == 'wK':
            self.whiteKingLocation = (move.end_Row, move.end_Column)
        elif move.piece_Moved == 'bK':
            self.blackKingLocation = (move.end_Row, move.end_Column)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.end_Row][move.end_Column] = move.piece_Moved[0] + 'Q'

        #enpassant
        if move.isEnpassantMove:
            self.board[move.end_Row][move.end_Column] = '=='

        if move.piece_Moved[1] == 'p' and abs(move.start_Row - move.end_Row) == 2:
            self.enpassantPossible = ((move.start_Row + move.end_Row)//2, move.start_Column)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.end_Column - move.start_Column == 2:
                self.board[move.end_Row][move.end_Column-1] = self.board[move.end_Row][move.end_Column+1]
                self.board[move.end_Row][move.end_Column+1] = '--'
            else:
                self.board[move.end_Row][move.end_Column+1] = self.board[move.end_Row][move.end_Column-2]
                self.board[move.end_Row][move.end_Column-2] = '--'

        #update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_Row][move.start_Column] = move.piece_Moved
            self.board[move.end_Row][move.end_Column] = move.piece_Captured
            self.whiteToMove = not self.whiteToMove
            if move.piece_Moved == 'wK':
                self.whiteKingLocation = (move.start_Row, move.start_Column)
            elif move.piece_Moved == 'bK':
                self.blackKingLocation = (move.start_Row, move.start_Column)
            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.end_Row][move.end_Column] = '--'
                self.board[move.start_Row][move.end_Column] = move.piece_Captured
                self.enpassantPossible = (move.end_Row, move.end_Column)

            if move.piece_Moved[1] == 'p' and abs(move.start_Row - move.end_Row) == 2:
                self.enpassantPossible = ()

            #undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

            #undo castle move
            if move.isCastleMove:
                if move.end_Column - move.start_Column == 2:
                    self.board[move.end_Row][move.end_Column+1] = self.board[move.end_Row][move.end_Column-1]
                    self.board[move.end_Row][move.end_Column-1] = '--'
                else:
                    self.board[move.end_Row][move.end_Column-2] = self.board[move.end_Row][move.end_Column+1] 
                    self.board[move.end_Row][move.end_Column+1] = '--'


    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.piece_Moved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.piece_Moved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.piece_Moved == 'wR':
            if move.start_Row == 7:
                if move.start_Column == 0:
                    self.currentCastlingRight.wqs = False
                elif move.start_Column == 7:
                    self.currentCastlingRight.wks = False
        elif move.piece_Moved == 'bR':
            if move.start_Row == 0:
                if move.start_Column == 0:
                    self.currentCastlingRight.bqs = False
                elif move.start_Column == 7:
                    self.currentCastlingRight.bks = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible

        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        moves =  self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove  
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square row, column
    '''
    def squareUnderAttack(self, row, column):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  
        for move in oppMoves:
            if move.end_Row == row and move.end_Column == column:
                self.whiteToMove = not self.whiteToMove
                return True
        return False   


    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)): # number of rows
            for column in range(len(self.board[row])): # number of columns in given row
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, moves) #call the appropiate move function
        return moves

    '''
    Get all the pawn moves located at row, column and add these moves to the list
    '''
    def getPawnMoves(self, row, column, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[row-1][column] == "--": #1 square pawn advance
                moves.append(Move((row, column), (row-1, column), self.board))
                if row == 6 and self.board[row-2][column] == "--": #2 square pawn advance
                    moves.append(Move((row, column), (row-2, column), self.board))
            if column - 1 >= 0: #captures to the left
                if self.board[row-1][column-1][0] == 'b':
                    moves.append(Move((row, column), (row-1, column-1), self.board))
                elif (row - 1, column - 1) == self.enpassantPossible:
                    moves.append(Move((row, column), (row-1, column-1), self.board, enpassantMove=True))
            if column + 1 <= 7: #capture to the right
                if self.board[row-1][column+1][0] == 'b':
                    moves.append(Move((row, column), (row-1, column+1), self.board))
                elif (row - 1, column + 1) == self.enpassantPossible:
                    moves.append(Move((row, column), (row-1, column+1), self.board, enpassantMove=True))
        
        else: #black pawn moves
            if self.board[row+1][column] == "--": #1 square pawn advance
                moves.append(Move((row, column), (row+1, column), self.board))
                if row == 1 and self.board[row+2][column] == "--": #2 square pawn advance
                    moves.append(Move((row, column), (row+2, column), self.board))
            if column - 1 >= 0: #captures to the left
                if self.board[row+1][column-1][0] == 'w':
                    moves.append(Move((row, column), (row+1, column-1), self.board))
                elif (row + 1, column - 1) == self.enpassantPossible:
                    moves.append(Move((row, column), (row+1, column-1), self.board, enpassantMove=True))
            if column + 1 <= 7: #capture to the right
                if self.board[row+1][column+1][0] == 'w':
                    moves.append(Move((row, column), (row+1, column+1), self.board))
                elif (row + 1, column + 1) == self.enpassantPossible:
                    moves.append(Move((row, column), (row+1, column+1), self.board, enpassantMove=True))
        #add pawn promotions later

    '''
    Get all the rook moves located at row, column and add these moves to the list
    '''
    def getRookMoves(self, row, column, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8): #can move max of 7 squares
                endRow = row + direction[0] * i
                endColumn = column + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8: #on board
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyColor: #enemy place valid
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                        break
                    else: #friendly place invalid
                        break
                else: #off board
                    break

    '''
    Get all the knight moves located at row, column and add these moves to the list
    '''
    def getKnightMoves(self, row, column, moves):
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for direction in directions:
            endRow = row + direction[0]
            endColumn = column + direction[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8: #on board
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != allyColor: #not an ally piece, either enemy or empty
                    moves.append(Move((row, column), (endRow, endColumn), self.board))

    '''
    Get all the bishop moves located at row, column and add these moves to the list
    '''
    def getBishopMoves(self, row, column, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8): #can move max of 7 squares
                endRow = row + direction[0] * i
                endColumn = column + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8: #on board
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--": #empty space valid
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyColor: #enemy place valid
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                        break
                    else: #friendly place invalid
                        break
                else: #off board
                    break

    '''
    Get all the queen moves located at row, column and add these moves to the list
    '''
    def getQueenMoves(self, row, column, moves):
        self.getRookMoves(row, column, moves)
        self.getBishopMoves(row, column, moves)

    '''
    Get all the king moves located at row, column and add these moves to the list
    '''
    def getKingMoves(self, row, column, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = row + directions[i][0]
            endColumn = column + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8: #on board
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != allyColor: #not an ally piece, either enemy or empty
                    moves.append(Move((row, column), (endRow, endColumn), self.board))
        

    '''
    Generate all valid castle moves for king
    '''
    def getCastleMoves(self, row, column, moves):
        if self.squareUnderAttack(row, column):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, column, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, column, moves)

    def getKingsideCastleMoves(self, row, column, moves):
        if self.board[row][column+1] == '--' and self.board[row][column+2] == '--':
            if not self.squareUnderAttack(row, column+1) and not self.squareUnderAttack(row, column+2):
                moves.append(Move((row, column),(row, column+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, column, moves):
        if self.board[row][column-1] == '--' and self.board[row][column-2] == '--' and self.board[row][column-3] == '--':
            if not self.squareUnderAttack(row, column-1) and not self.squareUnderAttack(row, column-2):
                moves.append(Move((row, column), (row, column-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    # maps keys to values
    #key : value

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}

    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToColumns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    columnsToFiles = {v: k for k, v in filesToColumns.items()}

    def __init__(self, start_Square, end_Square, board, enpassantMove=False, isCastleMove=False):
        self.start_Row = start_Square[0]
        self.start_Column = start_Square[1]
        self.end_Row = end_Square[0]
        self.end_Column = end_Square[1]
        self.piece_Moved = board[self.start_Row][self.start_Column]
        self.piece_Captured = board[self.end_Row][self.end_Column]
        
        self.isPawnPromotion = (self.piece_Moved == 'wp' and self.end_Row == 0) or (self.piece_Moved == 'bp' and self.end_Row == 7)

        #enpassant
        self.isEnpassantMove = enpassantMove
        if self.isEnpassantMove:
            self.piece_Captured= 'wp' if self.piece_Moved == 'bp' else 'bp'

        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.start_Row * 1000 + self.start_Column * 100 + self.end_Row * 10 + self.end_Column

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_Row, self.start_Column) + self.getRankFile(self.end_Row, self.end_Column)

    def getRankFile(self, row, column):
        return self.columnsToFiles[column] + self.rowsToRanks[row]
    