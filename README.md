# Artificial Intelligence Sudoku Solver

## An agent to solve sudokus using constraint propagation and depth-first search

This project combines three strategies to solve sudokos (including diagonal ones).

### Elimination strategy

If a box has a value assigned, then none of the peers of this box can have this value.

### Only choice

If there is only one box in a unit which would allow a certain digit, then that box must be assigned that digit.

### Naked twins

The naked twins constraint works by finding pairs of boxes containing the same two possible solutions occuring in the
same unit. Since this tells us that one of the two possibilities must belong in each box, we can remove those two
possibilities from all the other boxes in the unit if they occur.

### Depth-First Search

Pick a box with a minimal number of possible values. Try to solve each of the puzzles obtained by choosing each of these values, recursively.

### Example Solution

<div align="center">
<img src="https://github.com/g-eorge/ai-sudoku/blob/master/images/hard-solution.png" width="50%" />
</div>

### Install

This project requires **Python 3**.

### Run

`python solution.py`

##### Optional: Pygame

Optionally, you can also install pygame if you want to see the visualization.

Download pygame [here](http://www.pygame.org/download.shtml).
