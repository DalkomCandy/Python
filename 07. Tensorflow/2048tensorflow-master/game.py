import numpy as np

class Twenty48:
    """Simple 2048 game played on a matrix."""

    def __init__(self, dimensions=4):
        """Create game board matrix and create 2 random numbers on the board.

        dimensions -- length and width of game board (4 by default)
        """
        self.size = dimensions
        self.score = 0
        self.hasLost = False
        # Create empty board filled with zeroes of size provided
        self.board = [[0 for i in range(self.size)] for j in range(self.size)]
        # Create initial two random tiles
        self.add_to_board(2)

    def add_to_board(self, num):
        """Add 2 or 4 to game board. 90% chance of 2, 10% chance of 4.

        num -- number of random numbers to place on board
        """
        for i in range(num):
            # Check if board is full (game over)
            if not any(0 in subl for subl in self.board):
                return False
            value = 4 if np.random.rand() > 0.9 else 2  # Select value of tile
            # Keep repeating until coordinate is selected that is empty
            while True:
                x_coord = np.random.randint(self.size)
                y_coord = np.random.randint(self.size)
                # Add value to board at coordinate if the coordinate is empty
                if self.board[y_coord][x_coord] == 0:
                    self.board[y_coord][x_coord] = value
                    break
        return True

    def can_move(self):
        """Determines if any moves can be made by running shifters on 'test mode'
        """
        if self.shift_up(testRun=True) or self.shift_right(testRun=True) or self.shift_down(testRun=True) or self.shift_left(testRun=True):
            return True
        else:
            return False

    def shift_up(self,testRun=False):
        newBoard = list(self.board)
        score_to_add = 0
        # Invert list to make this the same problem as moving horizontally
        newBoard = np.transpose(newBoard)
        for row_iterator in range(0,len(newBoard)):
            # Sort values to end of list
            newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0)
            for value_iterator in range(0,len(newBoard[row_iterator])-1):
                current_value = newBoard[row_iterator][value_iterator]
                next_value = newBoard[row_iterator][value_iterator+1]
                
                if current_value == next_value:
                    newBoard[row_iterator][value_iterator] = current_value*2
                    newBoard[row_iterator][value_iterator+1] = 0
                    score_to_add += current_value*2 # Add merged block to score
                    # Sort again
                    newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0)  
        newBoard = np.transpose(newBoard)
        newBoard = newBoard.tolist()
        # See if any movement has occured. If it has, add tiles and check for loss.
        if newBoard != self.board and not testRun:
            self.board = newBoard
            self.add_to_board(1)
            if self.can_move() == True:
                self.score += score_to_add
            else:
                self.hasLost = True
        if testRun and newBoard != self.board: return True # Can any tiles move?

    def shift_right(self,testRun=False):
        newBoard = list(self.board)
        score_to_add = 0
        for row_iterator in range(0,len(newBoard)):
            # Sort values to end of list
            newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0, reverse=True)
            for value_iterator in range(len(newBoard[row_iterator])-1,0,-1):
                current_value = newBoard[row_iterator][value_iterator]
                next_value = newBoard[row_iterator][value_iterator-1]
                
                if current_value == next_value:
                    newBoard[row_iterator][value_iterator] = current_value*2
                    newBoard[row_iterator][value_iterator-1] = 0
                    score_to_add += current_value*2 # Add merged block to score
                    # Sort again
                    newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0, reverse=True)  
        # See if any movement has occured. If it has, add tiles and check for loss.
        if newBoard != self.board and not testRun:
            self.board = newBoard
            self.add_to_board(1)
            if self.can_move() == True:
                self.score += score_to_add
            else:
                self.hasLost = True
        if testRun and newBoard != self.board: return True # Can any tiles move?

    def shift_down(self,testRun=False):
        newBoard = list(self.board)
        score_to_add = 0
        # Invert list to make this the same problem as moving horizontally
        newBoard = np.transpose(newBoard)
        for row_iterator in range(0,len(newBoard)):
            # Sort values to end of list
            newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0, reverse=True)
            for value_iterator in range(len(newBoard[row_iterator])-1,0,-1):
                current_value = newBoard[row_iterator][value_iterator]
                next_value = newBoard[row_iterator][value_iterator-1]
                
                if current_value == next_value:
                    newBoard[row_iterator][value_iterator] = current_value*2
                    newBoard[row_iterator][value_iterator-1] = 0
                    score_to_add += current_value*2 # Add merged blocks to score
                    # Sort again
                    newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0, reverse=True)  
        newBoard = np.transpose(newBoard)
        newBoard = newBoard.tolist()
        # See if any movement has occured. If it has, add tiles and check for loss.
        if newBoard != self.board and not testRun:
            self.board = newBoard
            self.add_to_board(1)
            if self.can_move() == True:
                self.score += score_to_add
            else:
                self.hasLost = True
        if testRun and newBoard != self.board: return True # Can any tiles move?

    def shift_left(self,testRun=False):
        newBoard = list(self.board)
        score_to_add = 0
        for row_iterator in range(0,len(newBoard)):
            # Sort values to end of list
            newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0)
            for value_iterator in range(0,len(newBoard[row_iterator])-1):
                current_value = newBoard[row_iterator][value_iterator]
                next_value = newBoard[row_iterator][value_iterator+1]
                
                if current_value == next_value:
                    newBoard[row_iterator][value_iterator] = current_value*2
                    newBoard[row_iterator][value_iterator+1] = 0
                    score_to_add += current_value*2 # Add merged block to score
                    # Sort again
                    newBoard[row_iterator] = sorted(newBoard[row_iterator], key=lambda x: x == 0)  
        # See if any movement has occured. If it has, add tiles and check for loss.
        if newBoard != self.board and not testRun:
            self.board = newBoard
            self.add_to_board(1)
            if self.can_move() == True:
                self.score += score_to_add
            else:
                self.hasLost = True
        if testRun and newBoard != self.board: return True # Can any tiles move?
