from sys import exit
from random import randint
import copy
import emoji

# Cell is a class with one isntance variable, fill whcich should take an integer value: 1 for red, -1 for yellow, 0 for empty
class Cell:
    def __init__(self, fill):
        self.fill = fill

    def __str__(self):
        if self.fill == 1:
            return (emoji.emojize(':yellow_circle:'))
        elif self.fill == -1:
            return (emoji.emojize(':red_circle:'))
        elif self.fill == 0:
            return (emoji.emojize(':black_large_square:'))

    def __add__(self, other):
        return Cell(self.fill + other.fill)



def main():
    # board is a list of the columns of the board
    board = []
    # initialise the board by filling the list with 7 nested lists
    for i in range(7):
        board.append([])
        for k in range(6):
            # inialise 6 cells with fill 0 to represent empty
            board[i].append(Cell(0))
    print_board(board)
    # while loop which iterates for every turn, until game over
    while True:
        # validation of column number input
        while True:
            try:
                move = int(input("Input column you wish to place: ")) - 1
            except ValueError:
                print("Please input a number.")

            if not (move >= 0 and move <= 6):
                print("Invalid Move")
                continue

            # create a temporary board with a different address
            temp_board = copy.deepcopy(board)
            validation_board = copy.deepcopy(board)

            # validate move
            if playmove(move, validation_board, True) == 99:
                print("Column is already full.")
                continue

            # update the board and break out of the while that asks for move
            board = copy.deepcopy(playmove(move, temp_board, True))
            break




        print_board(board)
        print()
        print("-"*50)


         # check for win
        if assess_win(board) == 1:
            print("GAME OVER, HUMAN WINS")
            exit()
        elif assess_win(board) == -1:
            print("GAME OVER, AI WINS")
            exit()
        elif not generate_movelist(board):
            print("GAME OVER, DRAW")
            exit()

        # generate AI move +++++++++++++++++++++++++++++++++++++++++++++++++
        aimove = impossible(board)
        # create a temporary board with a different address
        temp_board = copy.deepcopy(board)
        # update the board and break out of the while that asks for move
        board = playmove(aimove, temp_board, False)


        print_board(board)
        print()
        print("-"*50)


        # check for win
        if assess_win(board) == 1:
            print("GAME OVER, HUMAN WINS")
            exit()
        elif assess_win(board) == -1:
            print("GAME OVER, AI WINS")
            exit()
        elif not generate_movelist(board):
            print("GAME OVER, DRAW")
            exit()

def impossible(board):
    # 1. make or deny four in a row
    if medium(board, False)[0] == True:
        #print("lethal")
        return medium(board, False)[1]
    # 2. make or deny win sequence
    lethalintwo = twomovelethal(board, False)
    if lethalintwo != 99:
        # win sequence must not blunder lethal in 1
        if not allow_lethal(lethalintwo, board, False):
            #print("2 move lethal")
            return lethalintwo
    blocklethalintwo = twomovelethal(board, True)
    if blocklethalintwo != 99:
        #print("block lethal in two")
        return blocklethalintwo

    # 2+. set up win sequence
    lethalinthree = threemovelethal(board, False)
    if lethalinthree != 99:
        # must not blunder lethal or opp win sequence
        # corner case: can allow opp win seq if opp win seq blunders lethal, this is implemented within allowlethalintwo function
        if not allow_lethal(lethalinthree, board, False) and not allow_lethalintwo(lethalinthree, board, False):
            #print("set up")
            return lethalinthree
    #3. deny columns optimally
    denial = deny_column(board, False)
    if denial[1] == "optimal":
        # dont blunder
        if not allow12(denial[0], board, False):
            # we dont want to place this denial if it is a self-block move
            if not allow_lethal(denial[0], board, True):
                #print(f"denial of column {denial[0] + 1}")
                return denial[0]

    #33. create 3 in a row without allowing winning moves
    centrethreeinarow = []
    for threeinarow_move in col3(board, False):
        if not allow12(threeinarow_move, board, False):
             # we dont want to place this if it is a self-block move
            if not allow_lethal(threeinarow_move, board, True):
                centrethreeinarow.append(threeinarow_move)
    if centrethreeinarow:
        #print("3 in a row")
        return centre_move(centrethreeinarow)

    #33-. block opp from making 3 in a row
    centreblock3 = []
    for oppthreeinarow_move in col3(board, True):
        if not allow12(oppthreeinarow_move, board, False):
            centreblock3.append(oppthreeinarow_move)
    if centreblock3:
        #print("block 3 in a row")
        return centre_move(centreblock3)

    #34. deny columns suboptimally
    if denial[1] == "suboptimal":
        # dont blunder
        if not allow12(denial[0], board, False):
            # we dont want to place this denial if it is a self-block move
            if not allow_lethal(denial[0], board, True):
                # dont allow if allows 3 in a row creation
                if not allow_3(denial[0], board, True):
                    return denial[0]

    #4. make unhindered 2 in a row
    col2move = col2(board, False)
    if col2move != 99:
        if not allow12(col2move, board, False):
            if not allow_3(col2move, board, False):
                #print("2 in a row")
                return col2move
    #4-. block unhindered 2 in a row
    col2block = col2(board, True)
    if col2block != 99:
        if not allow12(col2block, board, False):
            if not allow_3(col2block, board, False):
                #print("block 2 in a row")
                return col2block

    #5. play any move that is not a blunder, towards centre
    for endgame in [3, 2, 4, 1, 5, 0, 6]:
        if board[endgame][5].fill == 0:
            if not allow12(endgame, board, False) and not allow_3(endgame, board, False):
                return endgame
            if not allow12(endgame, board, False):
                return endgame

def allow_3(move, board, player):
    board0 = playmove(move, copy.deepcopy(board), player )
    if move in col3(board0, not player):
        return True
    return False

def deny_column(board, player):
    if player:
        winval = 1
    else:
        winval = -1
    # valid moves except top row
    movelist = []
    for i in range(7):
        if board[i][4].fill == 0:
            movelist.append(i)
    # list for the suboptimal moves
    suboptimal = []
    # test every one of the moves
    for col in movelist:
        # simulate placement
        board0 = playmove(col, copy.deepcopy(board), player)
        board01 = playmove(col, copy.deepcopy(board0), not player)
        board010 = playmove(col, copy.deepcopy(board01), player)

        # test if col move by opp gives you lethal IN THE SAME COLUMN (in the same columm is impt to avoid corner cases)
        # check that we are not overflowing the board
        if board0 != 99 and board01 != 99 and board010 != 99:
            if assess_win(board010) == winval:
                return col, "optimal"

        # test if col move by opp allows you to block lethal IN THE SAME COLUMN
        if board0 != 99 and board01 != 99:
            if lethal(board01, generate_movelist(board01), player)[0] == col and lethal(board01, generate_movelist(board01), player)[1] == "block":
                return col, "optimal"

        # test if same col move by opp allows you to create a 3-row and hence a new 4-row threat/lethal cell
        if board0 != 99 and board01 != 99:
            if col in col3(board01, player):
                # save this move for later as we want to check if the other moves fufill the better move
                suboptimal.append(col)
        # test if same col move by opp allows you to block their 3-row. we do so by checking by pretending its their move and seeing if they have can create a 3.
        # if board0 != 99 and board01 != 99:
        #     if col in col3(board01, not player):
        #         suboptimal.append(col)
    # if no move returned yet, we want to return a suboptimal move, if there is one. if list is empty we give negative results
    if not suboptimal:
        return 99, "none"
    # if list is not empty we return the move closest to middle.
    return centre_move(suboptimal), "suboptimal"

# this function takes a list of integers and return the one closest to the middle, ie 3
def centre_move(movelist):
    return min(movelist, key=lambda x:abs(x-3))



# emptycellindex is a list of 2 integers
# this function determines whether an empty cell is ALREADY a lethal cell. ie if filled by "player" game ends
def existing3(board, player, emptycellindex):
    if player:
        boolval = 1
    else:
        boolval = -1
    # search for horizontal 4
    for i in range(6):
        for j in range(4):
            # bool for whether empty cell is inside the four
            emptycellinside = False
            # sum area of interest
            sumh = Cell(0)
            for k in range(4):
                sumh = sumh + board[j + k][i]
                if (j + k) == emptycellindex[0] and i == emptycellindex[1]:
                    emptycellinside = True
            if sumh.fill == 3 * boolval and emptycellinside:
                return True

    # search for vertical 4
    for a in range(7):
        for b in range(3):
            # bool for whether empty cell is inside the four
            emptycellinside = False
            sumv = Cell(0)
            for c in range(4):
                sumv = sumv + board[a][b + c]
                if a == emptycellindex[0] and (b + c) == emptycellindex[1]:
                    emptycellinside = True
            if sumv.fill == 3 * boolval and emptycellinside:
                return True
    # search for diagonal 4, starting points are a 4x3 grid on top and bottom left
    for ii in range(3):
        for jj in range(4):
            # bool for whether empty cell is inside the four
            emptycellinsidep = False
            sump = Cell(0)
            # bool for whether empty cell is inside the four
            emptycellinsiden = False
            sumn = Cell(0)
            for kk in range(4):
                sump = sump + board[jj + kk][3 + ii - kk]
                if (jj + kk) == emptycellindex[0] and (3 + ii - kk) == emptycellindex[1]:
                    emptycellinsidep = True
                sumn = sumn + board[jj + kk][ii + kk]
                if (jj + kk) == emptycellindex[0] and (ii + kk) == emptycellindex[1]:
                    emptycellinsiden = True
            if sump.fill == 3 * boolval and emptycellinsidep:
                return True
            elif sumn.fill == 3 * boolval and emptycellinsiden:
                return True
    return False

def col2(board, player):
    # initialise list of moves
    twomoves = []
    # determine all valid moves
    movelist = generate_movelist(board)
    # iterate for every 4 contiguous cells
    if player:
        boolval = 1
    else:
        boolval = -1
    # search for horizontal 4s
    for i in range(6):
        for j in range(4):
            # sum area of interest
            sumh = Cell(0)
            # counter for no of filled cells
            filled_counter = 0
            for k in range(4):
                sumh = sumh + board[j + k][i]
                if board[j + k][i].fill != 0:
                    filled_counter = filled_counter + 1
            if sumh.fill == boolval and filled_counter == 1:
                for col in movelist:
                    # simulate placed in column
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumh = Cell(0)
                    for kx in range(4):
                        sumh = sumh + board0[j + kx][i]
                    if sumh.fill == 2 * boolval:
                        twomoves.append(col)


    # search for vertical 4s
    for a in range(7):
        for b in range(3):
            sumv = Cell(0)
            filled_counter = 0
            for c in range(4):
                sumv = sumv + board[a][b + c]
                if board[a][b + c].fill != 0:
                    filled_counter = filled_counter + 1
            if sumv.fill == boolval and filled_counter == 1:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumv = Cell(0)
                    for kc in range(4):
                        sumv = sumv + board0[a][b + kc]
                    if sumv.fill == 2 * boolval:
                        twomoves.append(col)

    # search for diagonal 4s, starting points are a 4x3 grid on top and bottom left
    for ii in range(3):
        for jj in range(4):
            sump = Cell(0)
            sumn = Cell(0)
            filled_counterp = 0
            filled_countern = 0
            for kk in range(4):
                sump = sump + board[jj + kk][3 + ii - kk]
                if board[jj + kk][3 + ii - kk].fill != 0:
                    filled_counterp = filled_counterp + 1
                sumn = sumn + board[jj + kk][ii + kk]
                if board[jj + kk][ii + kk] != 0:
                    filled_countern = filled_countern + 1
            if sump.fill == boolval and filled_counterp == 1:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sump = Cell(0)
                    for xkk in range(4):
                        sump = sump + board0[jj + xkk][3 + ii - xkk]
                        # stores the index of any empty cell in the four. will only be used if it is a lethal cell, as sum will be 3
                    if sump.fill == 2 * boolval:
                        twomoves.append(col)

            if sumn.fill == boolval and filled_countern == 1:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumn = Cell(0)
                    for ykk in range(4):
                        sumn = sumn + board0[jj + ykk][ii + ykk]
                    if sumn.fill == 2 * boolval:
                        twomoves.append(col)
    if twomoves:
        return centre_move(twomoves)
    else:
        return 99

# this function returns the columns for which 3 in a row (potential 4) can be made
def col3(board, player):
    # initialise list of moves
    threemoves = []
    # determine all valid moves
    movelist = generate_movelist(board)
    # iterate for every 4 contiguous cells
    if player:
        boolval = 1
    else:
        boolval = -1
    # search for horizontal 4s
    for i in range(6):
        for j in range(4):
            # sum area of interest
            sumh = Cell(0)
            for k in range(4):
                sumh = sumh + board[j + k][i]
            if sumh.fill == 2 * boolval:
                for col in movelist:
                    # simulate placed in column
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumh = Cell(0)
                    # variable to store the lethal cell of the 3 in a row
                    emptycell = []
                    for kx in range(4):
                        sumh = sumh + board0[j + kx][i]
                        # stores the index of any empty cell in the four. will only be used if it is a lethal cell, as sum will be 3
                        if board0[j + kx][i].fill == 0:
                            emptycell.append(j + kx)
                            emptycell.append(i)
                    if sumh.fill == 3 * boolval:
                        # validate whether this 3 can be blocked
                        blocked_board = playmove(emptycell[0], copy.deepcopy(board0), not player)
                        if blocked_board[emptycell[0]][emptycell[1]].fill == 0:
                            # validate whether the empty cell is part of an existing 3 threat
                            if not existing3(board, player, emptycell):
                                threemoves.append(col)


    # search for vertical 4s
    for a in range(7):
        for b in range(3):
            sumv = Cell(0)
            for c in range(4):
                sumv = sumv + board[a][b + c]
            if sumv.fill == 2 * boolval:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumv = Cell(0)
                    # variable to store the lethal cell of the 3 in a row
                    emptycell = []
                    for kc in range(4):
                        sumv = sumv + board0[a][b + kc]
                        # stores the index of any empty cell in the four. will only be used if it is a lethal cell, as sum will be 3
                        if board0[a][b + kc].fill == 0:
                            emptycell.append(a)
                            emptycell.append(b + kc)
                    if sumv.fill == 3 * boolval:
                        # validate whether this 3 can be blocked
                        blocked_board = playmove(emptycell[0], copy.deepcopy(board0), not player)
                        if blocked_board[emptycell[0]][emptycell[1]].fill == 0:
                            if not lethal(board0, generate_movelist(board0), not player)[1] == "block" and not lethal(board0, generate_movelist(board0), not player)[1] == "win":
                                # validate whether the empty cell is part of an existing 3 threat
                                if not existing3(board, player, emptycell):
                                    threemoves.append(col)

    # search for diagonal 4s, starting points are a 4x3 grid on top and bottom left
    for ii in range(3):
        for jj in range(4):
            sump = Cell(0)
            sumn = Cell(0)
            for kk in range(4):
                sump = sump + board[jj + kk][3 + ii - kk]
                sumn = sumn + board[jj + kk][ii + kk]
            if sump.fill == 2 * boolval:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sump = Cell(0)
                    # variable to store the lethal cell of the 3 in a row
                    emptycell = []
                    for xkk in range(4):
                        sump = sump + board0[jj + xkk][3 + ii - xkk]
                        # stores the index of any empty cell in the four. will only be used if it is a lethal cell, as sum will be 3
                        if board0[jj + xkk][3 + ii - xkk].fill == 0:
                            emptycell.append(jj + xkk)
                            emptycell.append(3 + ii - xkk)
                    if sump.fill == 3 * boolval:
                        # validate whether this 3 can be blocked
                        blocked_board = playmove(emptycell[0], copy.deepcopy(board0), not player)
                        if blocked_board[emptycell[0]][emptycell[1]].fill == 0:
                            # validate whether the empty cell is part of an existing 3 threat
                                if not existing3(board, player, emptycell):
                                    threemoves.append(col)

            if sumn.fill == 2 * boolval:
                for col in movelist:
                    calculation_board = copy.deepcopy(board)
                    board0 = playmove(col, calculation_board, player)
                    sumn = Cell(0)
                    # variable to store the lethal cell of the 3 in a row
                    emptycell = []
                    for ykk in range(4):
                        sumn = sumn + board0[jj + ykk][ii + ykk]
                        # stores the index of any empty cell in the four. will only be used if it is a lethal cell, as sum will be 3
                        if board0[jj + ykk][ii + ykk].fill == 0:
                            emptycell.append(jj + ykk)
                            emptycell.append(ii + ykk)
                    if sumn.fill == 3 * boolval:
                        # validate whether this 3 can be blocked
                        blocked_board = playmove(emptycell[0], copy.deepcopy(board0), not player)
                        if blocked_board[emptycell[0]][emptycell[1]].fill == 0:
                            if not lethal(board0, generate_movelist(board0), not player)[1] == "block" and not lethal(board0, generate_movelist(board0), not player)[1] == "win":
                                # validate whether the empty cell is part of an existing 3 threat
                                if not existing3(board, player, emptycell):
                                    threemoves.append(col)
    return threemoves

def generate_movelist(board):
    movelist = []
    for i in range(7):
        if board[i][5].fill == 0:
            movelist.append(i)
    return movelist

def allow12(move, board, player):
    if not allow_lethal(move, board, player) and not allow_lethalintwo(move, board, player):
        return False
    else:
        return True



def allow_lethalintwo(move0, board, player):
    calculation_board0 = copy.deepcopy(board)
    # simulate board from copy of original board to board0
    board0 = playmove(move0, calculation_board0, player)
    # determine if opp now has lethalintwo
    move01 = twomovelethal(board0, not player)
    # if this creates lethal in two for opp,
    if move01 != 99 and not allow_lethal(move01, board0, not player):
        # we check the corner case where opp's lethal in two allows lethal in 1 for prop
        # hence we would purposely allow the move, despite allowing lethal in two
        return True
    return False


# allow functions check, for the player, if a move is created for opp if move is played
def allow_lethal(move0, board, player):
    calculation_board0 = copy.deepcopy(board)
    # simulate board from copy of original board to board0
    board0 = playmove(move0, calculation_board0, player)
    # determine if opp now has lethal
    # determine all valid moves for opp
    movelist0 = []
    for i0 in range(7):
        if board0[i0][5].fill == 0:
            movelist0.append(i0)
    if lethal(board0, movelist0, not player)[1] == "win":
        return True
    return False

# play this move so that if given 1 more move, that move is a forced win seq. PROP prop opp prop win. so forcing prop opp(block)
def threemovelethal(board, player):
    # determine all valid moves
    movelist0 = []
    for i0 in range(7):
        if board[i0][5].fill == 0:
            movelist0.append(i0)
    # play every possible move first
    for move0 in movelist0:
        calculation_board0 = copy.deepcopy(board)
        # simulate board from copy of original board to board0
        board0 = playmove(move0, calculation_board0, player)

        # find out if opp now has to block lethal. but also check if you just blundered lethal
        if lethal(board0, generate_movelist(board0), not player)[1] == "win":
            continue
        if lethal(board0, generate_movelist(board0), not player)[1] == "block":
            # play the block move by opponent
            board01 = playmove(lethal(board0, generate_movelist(board0), not player)[0], board0, not player)
            # find out if you now have lethal in two
            forcedlethalintwo = twomovelethal(board01, player)
            if forcedlethalintwo != 99:
                return move0
            else:
                # else we go to next possible move as we want to avoid passing a 1 move lethal board into twomovelethal. error 101 should not be incurred.
                continue

        # find out if opp now has to block lethal in two. if so return move0.
        blocklethalintwo = twomovelethal(board0, player)
        if blocklethalintwo != 99:
            return move0

    return 99

def twomovelethal(board, player):
    # determine all valid moves
    movelist0 = []
    for i0 in range(7):
        if board[i0][5].fill == 0:
            movelist0.append(i0)
    # play every possible move first
    # we have to exclude the first move if it is lethal. ordinarily there should not be lethal in 1 here since hierarchy
    # would not reach this algorithm if there were. lethalinthree previously could pass such a board but should not now. but we still check.
    for move0 in movelist0:
        calculation_board0 = copy.deepcopy(board)
        # simulate board from copy of original board to board0
        board0 = playmove(move0, calculation_board0, player)

        # check that board now is not in a win state
        if player:
            winval = 1
        else:
            winval = -1
        if assess_win(board0) == winval:
            # if this is the bug where threemovelethal tries to make a deniable 3 in a row, return to tell threemovelethal to abandon this board passed into this function
            return 101

        # find valid moves for opposing
        validmoves01 = []
        for i01 in range(7):
            if board0[i01][5].fill == 0:
                validmoves01.append(i01)

        # find the move opposing will play to block (and not opp wins)
        # if there are two block moves opp has to play, the not blocked one will be used as next ai move
        if not lethal(board0, validmoves01, not player)[1] == "block":
            # no block move for opp to play, move on to next move0
            continue

        # block move found
        blockmove01 = lethal(board0, validmoves01, not player)[0]
        # simulate board from board0 to board 01
        board01 = playmove(blockmove01, board0, not player)

        # find valid moves for prop
        validmoves010 = []
        for i010 in range(7):
            if board01[i010][5].fill == 0:
                validmoves010.append(i010)
        # determine if prop has lethal now
        if lethal(board01, validmoves010, player)[1] == "win":
            return move0
    return 99





def medium(board, player):
    # determine all valid moves
    movelist = []
    for i in range(7):
        if board[i][5].fill == 0:
            movelist.append(i)
    move = lethal(board, movelist, player)[0]
    # if lethal or prevent lethal found return the move
    if move != 10:
        return True, move
    # else just return random move
    else:
        return False, easy(board)


# player is a bool which indicates for whom we are calculating for
# true for human false for AI
def lethal(board, movelist, player):
    # look for AI or player lethal
    # iterating for every possible move
    for move in movelist:
        calculation_board = copy.deepcopy(board)
        onemoveboard = playmove(move, calculation_board, player)
        if player:
            tempbool = 1
        else:
            tempbool = -1
        if assess_win(onemoveboard) == tempbool:
            return move, "win"
    # here, must be that no lethal is found, so search for lethal for opponent
    for move in movelist:
        calculation_board = copy.deepcopy(board)
        onemoveboard = playmove(move, calculation_board, not player)
        if player:
            tempbool = -1
        else:
            tempbool = 1
        if assess_win(onemoveboard) == tempbool:
            return move, "block"
    # no lethals in next 2 moves (AI then human)
    return 10, "no lethals"





def easy(board):
    while True:
        randmove = randint(0,6)
        # validate move
        validation_board = copy.deepcopy(board)
        if playmove(randmove, validation_board, False) == 99:
            continue
        else:
            return randmove


def print_board(board):
    for row in range(6):
        for column in range(7):
            if board[column][5 - row].fill == -1:
                print(f"\033[31m{board[column][5 - row]}\033[0m", end="")
            elif board[column][5 - row].fill == 1:
                print(f"\033[33m{board[column][5 - row]}\033[0m", end="")
            else:
                print(board[column][5 - row], end="")
            print(" ", end="")
        print()


# return values: 1 for human win, 0 for no win, -1 for ai win
def assess_win(board):
    # search for horizontal win
    for i in range(6):
        for j in range(4):
            # sum area of interest
            sumh = Cell(0)
            for k in range(4):
                sumh = sumh + board[j + k][i]
            if sumh.fill == 4:
                return 1
            elif sumh.fill == -4:
                return -1
    # search for vertical win
    for a in range(7):
        for b in range(3):
            sumv = Cell(0)
            for c in range(4):
                sumv = sumv + board[a][b + c]
            if sumv.fill == 4:
                return 1
            elif sumv.fill == -4:
                return -1
    # search for diagonal win, starting points are a 4x3 grid on top and bottom left
    for ii in range(3):
        for jj in range(4):
            sump = Cell(0)
            sumn = Cell(0)
            for kk in range(4):
                sump = sump + board[jj + kk][3 + ii - kk]
                sumn = sumn + board[jj + kk][ii + kk]
            if sump.fill == 4 or sumn.fill == 4:
                return 1
            elif sump.fill == -4 or sumn.fill == -4:
                return -1
    return 0

def playmove(move, temp_board, player):
    # topcell stores the index of next empty cell in the column
    topcell = 99
    for cell in range(6):
        if temp_board[move][cell].fill == 0:
            topcell = cell
            break
    # if user tries to put in a filled column, no topcell is found, so topcell = 99
    if topcell == 99:
        return 99
    # else valid move so update and return board
    else:
        # store the move in memory
        if player == True:
            temp_board[move][topcell].fill = 1
        else:
            temp_board[move][topcell].fill = -1
        return temp_board

if __name__ == "__main__":
    main()