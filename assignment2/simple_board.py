"""
simple_board.py

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, \
                       MAXSIZE, NULLPOINT

class SimpleGoBoard(object):

    def get_color(self, point):
        return self.board[point]

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            return True
        elif self.board[point] != EMPTY:
            return False
        if point == self.ko_recapture:
            return False
            
        # General case: detect captures, suicide
        opp_color = GoBoardUtil.opponent(color)
        self.board[point] = color
        legal = True
        has_capture = self._detect_captures(point, opp_color)
        if not has_capture and not self._stone_has_liberty(point):
            block = self._block_of(point)
            if not self._has_liberty(block): # suicide
                legal = False
        self.board[point] = EMPTY
        return legal

    def _detect_captures(self, point, opp_color):
        """
        Did move on point capture something?
        """
        for nb in self.neighbors_of_color(point, opp_color):
            if self._detect_capture(nb):
                return True
        return False

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)

    def reset(self, size):
        """
        Creates a start state, an empty board with the given size
        The board is stored as a one-dimensional array
        See GoBoardUtil.coord_to_point for explanations of the array encoding
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype = np.int32)
        self.liberty_of = np.full(self.maxpoint, NULLPOINT, dtype = np.int32)
        self._initialize_empty_points(self.board)
        self._initialize_neighbors()
        # add for trace moves
        self.moves = []
        self.hash_code = self.generate_code()
        self.draw_player = EMPTY

    def copy(self):
        b = SimpleGoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        # add for trace moves
        # already correct for the list pointer error
        b.moves = list(self.moves)
        b.hash_code = np.copy(self.hash_code)
        b.draw_player = self.draw_player
        return b

    def undo_move(self):
        location = self.moves.pop()
        self.board[location] = EMPTY
        self.current_player = GoBoardUtil.opponent(self.current_player)


    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1
        
    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def _on_board_neighbors(self, point):
        nbs = []
        for nb in self._neighbors(point):
            if self.board[nb] != BORDER:
                nbs.append(nb)
        return nbs
            
    def _initialize_neighbors(self):
        """
        precompute neighbor array.
        For each point on the board, store its list of on-the-board neighbors
        """
        self.neighbors = []
        for point in range(self.maxpoint):
            if self.board[point] == BORDER:
                self.neighbors.append([])
            else:
                self.neighbors.append(self._on_board_neighbors(point))
        
    def is_eye(self, point, color):
        """
        Check if point is a simple eye for color
        """
        if not self._is_surrounded(point, color):
            return False
        # Eye-like shape. Check diagonals to detect false eye
        opp_color = GoBoardUtil.opponent(color)
        false_count = 0
        at_edge = 0
        for d in self._diag_neighbors(point):
            if self.board[d] == BORDER:
                at_edge = 1
            elif self.board[d] == opp_color:
                false_count += 1
        return false_count <= 1 - at_edge # 0 at edge, 1 in center
    
    def _is_surrounded(self, point, color):
        """
        check whether empty point is surrounded by stones of color.
        """
        for nb in self.neighbors[point]:
            nb_color = self.board[nb]
            if nb_color != color:
                return False
        return True

    def _stone_has_liberty(self, stone):
        lib = self.find_neighbor_of_color(stone, EMPTY)
        return lib != None

    def _get_liberty(self, block):
        """
        Find any liberty of the given block.
        Returns None in case there is no liberty.
        block is a numpy boolean array
        """
        for stone in where1d(block):
            lib = self.find_neighbor_of_color(stone, EMPTY)
            if lib != None:
                return lib
        return None

    def _has_liberty(self, block):
        """
        Check if the given block has any liberty.
        Also updates the liberty_of array.
        block is a numpy boolean array
        """
        lib = self._get_liberty(block)
        if lib != None:
            assert self.get_color(lib) == EMPTY
            for stone in where1d(block):
                self.liberty_of[stone] = lib
            return True
        return False

    def _block_of(self, stone):
        """
        Find the block of given stone
        Returns a board of boolean markers which are set for
        all the points in the block 
        """
        marker = np.full(self.maxpoint, False, dtype = bool)
        pointstack = [stone]
        color = self.get_color(stone)
        assert is_black_white(color)
        marker[stone] = True
        while pointstack:
            p = pointstack.pop()
            neighbors = self.neighbors_of_color(p, color)
            for nb in neighbors:
                if not marker[nb]:
                    marker[nb] = True
                    pointstack.append(nb)
        return marker

    def _fast_liberty_check(self, nb_point):
        lib = self.liberty_of[nb_point]
        if lib != NULLPOINT and self.get_color(lib) == EMPTY:
            return True # quick exit, block has a liberty  
        if self._stone_has_liberty(nb_point):
            return True # quick exit, no need to look at whole block
        return False
        
    def _detect_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        Returns boolean.
        """
        if self._fast_liberty_check(nb_point):
            return False
        opp_block = self._block_of(nb_point)
        return not self._has_liberty(opp_block)
    
    def _detect_and_process_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        If yes, remove the stones.
        Returns the stone if only a single stone was captured,
            and returns None otherwise.
        This result is used in play_move to check for possible ko
        """
        if self._fast_liberty_check(nb_point):
            return None
        opp_block = self._block_of(nb_point)
        if self._has_liberty(opp_block):
            return None
        captures = list(where1d(opp_block))
        self.board[captures] = EMPTY
        self.liberty_of[captures] = NULLPOINT
        single_capture = None 
        if len(captures) == 1:
            single_capture = nb_point
        return single_capture

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            self.ko_recapture = None
            self.current_player = GoBoardUtil.opponent(color)
            return True
        elif self.board[point] != EMPTY:
            return False
        if point == self.ko_recapture:
            return False
            
        # General case: deal with captures, suicide, and next ko point
        opp_color = GoBoardUtil.opponent(color)
        in_enemy_eye = self._is_surrounded(point, opp_color)
        self.board[point] = color
        single_captures = []
        neighbors = self.neighbors[point]
        for nb in neighbors:
            if self.board[nb] == opp_color:
                single_capture = self._detect_and_process_capture(nb)
                if single_capture != None:
                    single_captures.append(single_capture)
        if not self._stone_has_liberty(point):
            # check suicide of whole block
            block = self._block_of(point)
            if not self._has_liberty(block): # undo suicide move
                self.board[point] = EMPTY
                return False
        self.ko_recapture = None
        if in_enemy_eye and len(single_captures) == 1:
            self.ko_recapture = single_captures[0]
        self.current_player = GoBoardUtil.opponent(color)
        return True

    def neighbors_of_color(self, point, color):
        """ List of neighbors of point of given color """
        nbc = []
        for nb in self.neighbors[point]:
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc
        
    def find_neighbor_of_color(self, point, color):
        """ Return one neighbor of point of given color, or None """
        for nb in self.neighbors[point]:
            if self.get_color(nb) == color:
                return nb
        return None
        
    def _neighbors(self, point):
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point):
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1, 
                point - self.NS + 1, 
                point + self.NS - 1, 
                point + self.NS + 1]
    
    def _point_to_coord(self, point):
        """
        Transform point index to row, col.
        
        Arguments
        ---------
        point
        
        Returns
        -------
        x , y : int
        coordination of the board  1<= x <=size, 1<= y <=size .
        """
        if point is None:
            return 'pass'
        row, col = divmod(point, self.NS)
        return row, col

    #--------------------------------------------------------------------------------------------
    # All about gomoku
    #--------------------------------------------------------------------------------------------

    def is_legal_gomoku(self, point, color):
        """
            Check whether it is legal for color to play on point, for the game of gomoku
            """
        return self.board[point] == EMPTY
    
    def play_move_gomoku(self, point, color):
        """
            Play a move of color on point, for the game of gomoku
            Returns boolean: whether move was legal
            """
        assert is_black_white(color)
        assert point != PASS
        if self.board[point] != EMPTY:
            return False
        self.board[point] = color
        # add for trace moves
        self.moves.append(point)
        self.current_player = GoBoardUtil.opponent(color)
        return True
        
    def _point_direction_check_connect_gomoko(self, point, shift):
        """
        Check if the point has connect5 condition in a direction
        for the game of Gomoko.
        """

        color = self.board[point]
        count = 1
        d = shift
        p = point
        while True:
            p = p + d
            if self.board[p] == color:
                count = count + 1
                if count == 5:
                    return True
            else:
                break    

        p = point
        while True:
            p = p - d
            if self.board[p] == color:
                count = count + 1
                if count == 5:
                    return True
            else:
                break 

        assert count <= 5
        return count == 5
    
    def point_check_game_end_gomoku(self, point):
        """
            Check if the point causes the game end for the game of Gomoko.
            """
        # check horizontal
        if self._point_direction_check_connect_gomoko(point, 1):
            return True
        
        # check vertical
        if self._point_direction_check_connect_gomoko(point, self.NS):
            return True
        
        # check y=x
        if self._point_direction_check_connect_gomoko(point, self.NS + 1):
            return True
        
        # check y=-x
        if self._point_direction_check_connect_gomoko(point, self.NS - 1):
            return True
        
        return False
    
    def check_game_end_gomoku(self):
        """
            Check if the game ends for the game of Gomoku.
            """
        white_points = where1d(self.board == WHITE)
        black_points = where1d(self.board == BLACK)
        
        for point in white_points:
            if self.point_check_game_end_gomoku(point):
                return True, WHITE
    
        for point in black_points:
            if self.point_check_game_end_gomoku(point):
                return True, BLACK

        return False, None

    def play_move_gomoku_auto_change_player(self, point):
        assert point != PASS
        self.board[point] = self.current_player
        self.moves.append(point)
        self.current_player = GoBoardUtil.opponent(self.current_player)

    def end_of_game(self):
        if len(self.moves) == 0:
            return False
        elif self.point_check_game_end_gomoku(self.moves[-1]) or len(self.get_empty_points()) == 0:
            return True
        return False
    
    def staticallyEvaluateForToPlay(self):
        if self.point_check_game_end_gomoku(self.moves[-1]):
            return -1
        else:
            return 0

    def code(self):
        hash_code = 0
        for i in range(0, len(self.board)):
            if self.board[i] != BORDER:
                hash_code ^= int(self.hash_code[i][self.board[i]])

        return hash_code

    def generate_code(self):
        code = np.zeros((len(self.board), 3))
        index = 0
        for i in range(0, len(self.board)):
            for color in range(3):
                code[i][color] = index
                index += 1

        return code

    def set_draw_winner(self, color):
        self.draw_player = color


    #-----------------------------------------------------------------------
    # Optimial using heuristic
    #-----------------------------------------------------------------------
    def check_in_line_with_empty(self, point, shift, color, num_of_points, check_empty1, check_empty2):
        count = 1
        count_empty = 0
        d = shift
        p = point
        while True:
            p = p + d
            if self.board[p] == color:
                count = count + 1
            else:
                if self.board[p] == EMPTY:
                    count_empty += 1
                break    

        p = point
        while True:
            p = p - d
            if self.board[p] == color:
                count = count + 1
            else:
                if self.board[p] == EMPTY:
                    count_empty += 1
                break  
        if check_empty1:
            return count >= num_of_points and count_empty == 1
        elif check_empty2:
            return count >= num_of_points and count_empty == 2
        else:
            return count >= num_of_points
    
    def check_in_line_with_empty_permit(self, point, shift, color):
        pass



    def try_to_block_oppoent_immediate_win(self, color):
        # xoooo.
        # ooo.o
        # oo.oo
        EMPTY_POINT = where1d(self.board == EMPTY)
        opponent = GoBoardUtil.opponent(color)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS , opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS+1, opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS-1, opponent, 5, False, False):
                # print(str(color) + " block with " + str(point))
                return point
        return False


    def heuristic_search_move(self, player):
        # Should figure out the order!!!
        i = self.try_to_play_immediate_win(player)
        if i:
            return i
        j = self.try_to_block_oppoent_immediate_win(player)
        if j:
            return j  
        n = self.win_in_2_move(player)
        if n:
            return n  
        k = self.win_in_2_move(GoBoardUtil.opponent(player))
        if k:
            return k
        m = self.try_play_intersection(player)
        if m:
            return m       
        return False

    def try_play_intersection(self, color):
        #    .
        # .oo..    
        #    o     
        #    o
        #    .
        EMPTY_POINT = where1d(self.board == EMPTY)
        for point in EMPTY_POINT:
            count = 0
            if self.check_in_line_with_empty(point, 1, color, 3, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS, color, 3, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS+1, color, 3, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS-1, color, 3, False, True):
                count += 1
            if count >= 2:
                # print(str(color) + " win intersection " + str(point))
                return point
        return False


    def try_to_play_immediate_win(self, color):
        # xxxx.
        # xxx.x
        # xx.xx
        # xxx.xxx
        EMPTY_POINT = where1d(self.board == EMPTY)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, color, 5, False, False) or self.check_in_line_with_empty(point, self.NS , color, 5, False, False) or self.check_in_line_with_empty(point, self.NS+1, color, 5, False, False) or self.check_in_line_with_empty(point, self.NS-1, color, 5, False, False):
                # print(str(color) + " immediate win " + str(point))
                return point
        return False
    

    def give_up(self, color):
        #     .
        # xoooo.
        # ....o
        # ....o
        # ....o
        # ....x
        opponent = GoBoardUtil.opponent(color)
        OPPOENT_POINT = where1d(self.board == opponent)
        for point in OPPOENT_POINT:
            count = 0
            if self.check_in_line_with_empty(point, 1, opponent, 4, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS, opponent, 4, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS+1, opponent, 4, False, True):
                count += 1
            if self.check_in_line_with_empty(point, self.NS-1, opponent, 4, False, True):
                count += 1
            if count >= 2:
                # print(str(color) + " give up")
                return True

        return False

    def win_in_2_move(self, color):
        # .xxx..
        # .x.xx.
        EMPTY_POINT = where1d(self.board == EMPTY)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS + 1, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS - 1, color, 4, False, True):
                print(str(color) + " win in 2 move")
                return point
        return False


    def heuristic_end_of_game(self):
        player = self.current_player
        if self.give_up(player):
            return True, -1
        return False, None
            






            




            