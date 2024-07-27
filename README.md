# connect4.py

#### Video Demo: <https://youtu.be/sR3n9WvNalE>

#### Description:

Implementation details:
A command-line program implemented in Python, which allows the user to play a game of Connect 4 against an AI, which is very difficult to beat. Upon running `python connect4.py`, an empty board is generated, and the user is prompted for which column they would like to place their first chip in. The program validates the user and ensures the user inputs an integer, which corresponds to a column in the board, and also makes sure that the column they input is not already full. Upon any of these errors, an error message with an appropriate prompt is printed and the user is re-prompted for their move.

##### How the game is implemented:

The game itself is stored in a 2D list; that is, a list of lists of a custom class, "cell". Each cell represents a playable slot in an actual Connect 4 board. Objects of the class have 1 property, "fill", which allows us to store in memory whether a cell is filled or not, and which player's chip is inside. The value taken is 1 or -1 for the player and the AI respectively, and 0 if it is empty. These values are also important, as they are used in the various calculations the AI will do.

```python
# Cell is a class with one instance variable, fill which should take an integer value: 1 for red, -1 for yellow, 0 for empty
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
```

##### How the AI works:

The main AI function follows a hierarchy system for various types of moves. For instance, if the AI can win on the spot, it will prioritize such a move over, for instance, making 3 in a row.

```python
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
```

As demarcated by each of the numbered comments, the algorithm comprises of many sub-algorithms. From top down, the AI will prioritize better moves and moves down if the type of move cannot be found. For instance, if the AI is unable to find a forced move sequence, it could then consider finding if the player has a forced win sequence and then proceed to deny it. To summarize the hierarchy and types of moves the AI will play:

###### Hierarchy of moves:

1. Winning on the spot
2. Blocking the player from winning on the next move
3. Playing a forced win sequence
4. Preventing the player from playing a forced win sequence
5. Setting up a forced win sequence, i.e., if not blocked, the AI can then play a forced win sequence on the next move
6. Fill a column to create a bad move for the player in that column, thereby denying the column as a playable move. For instance, playing in column 6, so that if the player were to play in column 6 afterward, the AI can win on the spot. At this point in the hierarchy, we fill the column to create a move which would 1. result in a loss for the opponent, or 2. result in AI being able to block a win (cutting off the player's 3 in a row)
7. Creating three in a row, where the three in a row cannot be immediately blocked. This creates threats, which are what determine the winner in the endgame. The more potential 4 in a rows, the greater the chance of winning in an endgame.
8. Blocking the player from creating three in a row.
9. Fill a column to create a bad move for the player in that column. Now at this point in the hierarchy, where this is a weaker move than no. 6, we are filling the column so that now, if the player plays in the same column, it allows us to make a three in a row.
10. Make 2 in a row, provided that that 2 in a row is part of 4 adjacent cells where there are an additional 2 empty cells. In other words, make a 2 in a row that can potentially become a 4 in a row. Cases where it is impossible for the 2 cells in a row to become part of a 4 in a row are not played at this point in the hierarchy.
11. Block the opponent from making 2 in a row.
12. If none of the above tactics can be found, play in the center, as in general, the center has more possibilities of 4 in a row. At this point, the board is probably close to full and the moves made do not have much impact on the game (less the bad moves, such as a move that would allow the player to win on the next turn, which the AI will avoid).

###### Principles followed by the AI:

In general, the AI will follow the hierarchy, but we must also consider further impacts of the move. For instance, making three in a row would generally be a good move, but it would be a blunder if it allowed the player to play a forced win sequence or worse, win on the spot. As such, in general, the AI will not play the move if it allows the player, on the next turn, to play a move of higher hierarchy.

##### How the AI calculates:

The complex algorithm is built from much simpler building blocks. The most fundamental building block is the following function, which allows the program to determine if either player has won the game. Because we implemented an integer fill value for each cell, we can simply detect if 4 adjacent cells have a sum of magnitude 4.

```python
# return values: 1 for human win, 0 for no win, -1 for AI win
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
```

From this function alone, we can add much more complexity to the algorithm. For instance, since there are only a maximum of 7 possible moves each turn, it is viable for the program to simulate moves. This allows the program to calculate more complex moves, for instance, finding forced win sequences where there is no way to prevent the AI from winning in the next 2 moves. Below is the simplest example of this: `0 X X X 0`, where X is a red chip and 0 is an empty cell. There is no way of placing a yellow chip that would not allow red to win on their next turn.

The algorithm can simply calculate, by simulating 2 moves ahead and using the function above, to determine whether the AI can force a win.

From these small building blocks of functions, we can create more complex functions, which then serve as larger building blocks for even more complex calculations, eventually culminating in an expert-level AI that can churn out optimal moves based on the hierarchy system mentioned earlier.

##### How I decided to implement the algorithm this way:

I wanted to create an AI that was borne of my own intelligence and my own intelligence alone. To prepare for this project, I downloaded a Connect 4 app from the App Store and played more than 100 games against their AI on the hardest setting. Not only did I have to use pattern recognition and experience to teach myself how to play the game well, but I also had to break it down in a way that my playstyle could be implemented in code--and that was the fun of it. The key problem of how to convey my own playstyle in code allowed me to produce the hierarchy system as the solution.

Because I wanted it to be a challenge where the program is borne out of my own intelligence and nothing else, I purposely avoided researching strategies, tactics, and opening theory for the game. If I were to implement tactics, I would have learned the tactics on my own, simply by playing the game myself. Moreover, I had no doubt that many people have created Connect 4 AIs before, probably even for CS50. But I did not want to learn about how they did it and implemented this method completely originally. I am certain there are more elegant ways to build stronger, perfect, and completely unbeatable AIs, but my goal here was to learn and have fun, and absolutely not to make the world's strongest Connect 4 AI.
