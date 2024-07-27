# connect4.py

#### Video Demo: <https://youtu.be/sR3n9WvNalE>

#### Description:

Implementation details:
A command-line program implemented in Python, which allows the user to play a game of Connect 4 against an AI that is very difficult to beat. Upon running `python connect4.py`, an empty board is generated, and the user is prompted for which column they would like to place their first chip in. The program validates the user's input and ensures that it is a valid column on the board and not already full. If there are any errors, an appropriate error message is displayed, and the user is prompted again for their move.

##### How the game is implemented:

The game is stored in a 2D list, where each element represents a playable slot on the Connect 4 board. Each element has a property called "fill" which indicates whether the slot is empty (0), filled by the player (1), or filled by the AI (-1). This information is used in various calculations performed by the AI.

```python
# Cell is a class with one instance variable, "fill", which takes an integer value: 1 for red, -1 for yellow, 0 for empty
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

The AI follows a hierarchy system for various types of moves. It prioritizes moves that can lead to an immediate win, followed by moves that block the player from winning on the next move. It also considers moves that set up a win sequence, deny columns optimally, create three in a row, block the player from creating three in a row, deny columns suboptimally, make unhindered two in a row, block unhindered two in a row, and finally, play any move that is not a blunder towards the center.

The AI calculates the best move by simulating possible moves and using the `assess_win` function to determine if a move can lead to a win in the next two moves.

##### How the AI calculates:

The AI uses simple building blocks to perform complex calculations. The `assess_win` function is a fundamental building block that checks for horizontal, vertical, and diagonal wins on the board. By simulating moves and using this function, the AI can determine if it can force a win in the next two moves.

The algorithm combines these building blocks to create more complex functions, which then serve as larger building blocks for even more complex calculations. This culminates in an expert-level AI that can make optimal moves based on the hierarchy system.

##### How the algorithm was implemented:

The algorithm was implemented based on the developer's own intelligence and playstyle. The developer played over 100 games against an AI on the hardest setting to learn the game and develop their own strategy. They purposely avoided researching strategies, tactics, and opening theory to create an AI that reflects their own intelligence and playstyle.

The goal of the project was to learn and have fun, rather than creating the strongest Connect 4 AI. The developer wanted to challenge themselves by conveying their playstyle in code and implementing an original method without relying on existing strategies or tactics.
