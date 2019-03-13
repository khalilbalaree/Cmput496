from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, where1d

class rules:
    def __init__(self, player, board, NS):
        self.player = player
        self.board = board
        self.NS = NS

    def policy_type_search_move(self):
        # Should figure out the order!!!
        i = self.try_to_play_immediate_win(self.player)
        if len(i) != 0:
            return i, "Win"
        j = self.try_to_block_oppoent_immediate_win(self.player)
        if len(j) != 0:
            return j, "BlockWin"
        n = self.win_in_2_move(self.player)
        if len(n) != 0:
            return n, "OpenFour"
        k = self.win_in_2_move(GoBoardUtil.opponent(self.player))
        if len(k) != 0:
            return k, "BlockOpenFour" 
        return None, "Random"

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
    
    
    def try_to_block_oppoent_immediate_win(self, color):
        # xoooo.
        # ooo.o
        # oo.oo
        result = []
        EMPTY_POINT = where1d(self.board == EMPTY)
        opponent = GoBoardUtil.opponent(color)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS , opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS+1, opponent, 5, False, False) or self.check_in_line_with_empty(point, self.NS-1, opponent, 5, False, False):
                # print(str(color) + " block with " + str(point))
                result.append(point)
        return result

    def try_to_play_immediate_win(self, color):
        # xxxx.
        # xxx.x
        # xx.xx
        # xxx.xxx
        result = []
        EMPTY_POINT = where1d(self.board == EMPTY)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, color, 5, False, False) or self.check_in_line_with_empty(point, self.NS , color, 5, False, False) or self.check_in_line_with_empty(point, self.NS+1, color, 5, False, False) or self.check_in_line_with_empty(point, self.NS-1, color, 5, False, False):
                # print(str(color) + " immediate win " + str(point))
                result.append(point)
        return result
    

    def win_in_2_move(self, color):
        # .xxx..
        # .x.xx.
        result = []
        EMPTY_POINT = where1d(self.board == EMPTY)
        for point in EMPTY_POINT:
            if self.check_in_line_with_empty(point, 1, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS + 1, color, 4, False, True) or self.check_in_line_with_empty(point, self.NS - 1, color, 4, False, True):
                # print(str(color) + " win in 2 move")
                result.append(point)
        return result