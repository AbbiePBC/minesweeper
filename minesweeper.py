import random
from typing import Optional


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    # The idea is to make the sentence as simple as possible,
    # so that either the count of mines == the number of cells, and they're all mines,
    # or the count of mines == 0, and they're all safe.

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells in the sentence is equal to the count,
        # then all cells in the sentence must be mines.
        if len(self.cells) == self.count:
            return self.cells
        # Otherwise, we cannot infer that any cells are mines.
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is 0, then all cells in the sentence must be safe.
        if self.count == 0:
            return self.cells
        # Otherwise, we cannot infer that any cells are safe.
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If the cell is in the sentence, remove it,
        # and remove a mine from the count.
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If the cell is in the sentence, remove it,
        # but leave the count unchanged.
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        self.mark_safe(cell)
        # 3) add a new sentence to the AI's knowledge base
        #    based on the value of `cell` and `count`
        #    (i.e., a sentence consisting of all cells neighboring `cell`)

        # for all neighbouring cells, if they are not already safe, add them to the sentence

        x_index = cell[0]
        y_index = cell[1]

        neighbouring_cells = [(x_index - 1, y_index - 1), (x_index - 1, y_index), (x_index - 1, y_index + 1),
                                (x_index, y_index - 1), (x_index, y_index + 1),
                                (x_index + 1, y_index - 1), (x_index + 1, y_index), (x_index + 1, y_index + 1)]

        valid_neighbouring_cells = [neighbour for neighbour in neighbouring_cells \
                                    if 0 <= neighbour[0] < self.height and 0 <= neighbour[1] < self.width]

        new_sentence = Sentence(valid_neighbouring_cells, count)
        self.knowledge.append(new_sentence)

        # 4) mark any additional cells as safe or as mines
        #    if it can be concluded based on the AI's knowledge base

        safes_found = set(new_sentence.known_safes())
        for safe in safes_found:
            self.mark_safe(safe)

        mines_found = set(new_sentence.known_mines())
        for mine in mines_found:
            self.mark_mine(mine)

        # 5) add any new sentences to the AI's knowledge base
        #    if they can be inferred from existing knowledge

        if safes_found:
            neighbouring_possible_safes = set(valid_neighbouring_cells) - safes_found
            self.knowledge.append(Sentence(neighbouring_possible_safes, count - len(safes_found)))

        if mines_found:
            neighbouring_possible_mines = set(valid_neighbouring_cells) - mines_found
            self.knowledge.append(Sentence(neighbouring_possible_mines, count - len(mines_found)))



    def make_safe_move(self) -> Optional[tuple[int, int]]:
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in self.safes and (i, j) not in self.moves_made:
                    return (i, j)

        return None

    def make_random_move(self) -> Optional[tuple[int, int]]:
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_cells: list[tuple[int, int]] = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    possible_cells.append((i, j))
        if possible_cells:
            return random.choice(possible_cells)
        return None
