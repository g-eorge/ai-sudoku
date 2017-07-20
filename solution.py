"""
Solve sodukos using constraint propagation and depth first search.
"""

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(set_a, set_b):
    "Cross product of elements in set_a and elements in set_b."
    return [s+t for s in set_a for t in set_b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [list(map(lambda x: x[0]+x[1], zip(rows, cols))),
                  list(map(lambda x: x[0]+x[1], zip(rows, reversed(cols))))]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        # Find boxes with two possibilities
        boxes_with_pairs = [box for box in unit if len(values[box]) == 2]

        # Look up the possible values for those boxes
        values_with_pairs = list(map(lambda box: values[box], boxes_with_pairs))

        # Index the values, to find the boxes that have the same value
        value_counts = {}
        for index, value in enumerate(values_with_pairs):
            if value not in value_counts:
                value_counts[value] = [boxes_with_pairs[index]]
            else:
                value_counts[value].append(boxes_with_pairs[index])

        # The naked twins are the ones that have two boxes with the same possible values
        found_naked_twins = [(vals, boxes) for vals, boxes in value_counts.items()
                             if len(boxes) == 2]

        # Eliminate the naked twins as possibilities for their peers
        for naked_twin in found_naked_twins:
            twins = naked_twin[1]
            eliminate_values = naked_twin[0]
            for box in unit:
                if box not in twins:
                    for value in eliminate_values:
                        assign_value(values, box, values[box].replace(value, ''))

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
                If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for char in grid:
        if char in digits:
            chars.append(char)
        if char == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for row in rows:
        print(''.join(values[row+col].center(width)+('|' if col in '36' else '')
                      for col in cols))
        if row in 'CF':
            print(line)
    return

def eliminate(values):
    """
    Elimination strategy.
    If a box has a value assigned,
        then none of the peers of this box can have this value.
    Args:
        values(dict): The sudoku in dictionary form
    """
    for box, val in values.items():
        if len(val) == 1:
            for peer in peers[box]:
                assign_value(values, peer, values[peer].replace(val, ''))

    return values

def only_choice(values):
    """
    Only choice strategy.
    If there is only one box in a unit which would allow a certain digit,
        then that box must be assigned that digit.
    Args:
        values(dict): The sudoku in dictionary form
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Solve the soduku using constraint propogation, if possible.
    Iterate eliminate() and only_choice().
    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        dict: The resulting sudoku in dictionary form
    """
    stalled = False
    while not stalled: # Check how many boxes have a determined value

        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."

    reduced_values = reduce_puzzle(values)

    if reduced_values is False:
        return False

    if all(len(reduced_values[s]) == 1 for s in reduced_values):
        return reduced_values

    unsolved_values = {square:vals for square, vals
                       in dict(reduced_values).items() if len(vals) > 1}

    # Choose one of the unfilled squares with the fewest possibilities

    square = sorted(unsolved_values.items(), key=lambda t: len(t[1]))[0]
    possibilities = square[1]

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!

    for number in possibilities:
        cloned_board = dict(reduced_values)
        cloned_board[square[0]] = number
        attempt = search(cloned_board)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
        Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. '
              + 'Not a problem! It is not a requirement.')
