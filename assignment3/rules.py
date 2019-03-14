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
        k = self.block_open_four(self.player)
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
        EMPTY_POINT = where1d(self.board == EMPTY)
        patterns = {'-ooo.-' : 4, '-o.oo-' : 2, '-.ooo-' : 1, '-oo.o-' : 3}
        for point in EMPTY_POINT:
            for pattern in patterns.keys():
                for shift in [1, -1, self.NS, -self.NS, self.NS + 1, - self.NS - 1, self.NS - 1, - self.NS + 1]:
                    isFound, result = self.check_pattern(pattern, point, color, shift, patterns[pattern])
                    if isFound:
                        return result
        return []

    def block_open_four(self, color):
        EMPTY_POINT = where1d(self.board == EMPTY)
        patterns = {'.x.xx.' : 0, '.xx.x.' : 0, '?.xxx..' : 1, '..xxx.?' : 0, '-.xxx.-': 1}
        for point in EMPTY_POINT:
            for pattern in patterns.keys():
                for shift in [1, -1, self.NS, -self.NS, self.NS + 1, - self.NS - 1, self.NS - 1, - self.NS + 1]:
                    isFound, result = self.check_pattern(pattern, point, color, shift, patterns[pattern])
                    if isFound:
                        return result
        return []

    def check_pattern(self, pattern, start_point, color, shift, start_index):
        opponent = GoBoardUtil.opponent(color)
        front = start_index
        d = shift
        p = start_point
        result = []
        for i in range(front):
            p -= d
            if pattern[i] == "x" and self.board[p] == opponent:
                continue
            elif pattern[i] == "o" and self.board[p] == color:
                continue
            elif pattern[i] == "." and self.board[p] == EMPTY:
                result.append(p)
                continue
            elif pattern[i] == "-" and self.board[p] == EMPTY:
                continue
            elif pattern[i] == "?" and self.board[p] != color and self.board[p] != EMPTY:
                continue  
            else:
                return False, None
        p = start_point
        for i in range(start_index + 1, len(pattern)):
            p += d
            if pattern[i] == "x" and self.board[p] == opponent:
                continue
            elif pattern[i] == "o" and self.board[p] == color:
                continue
            elif pattern[i] == "." and self.board[p] == EMPTY:
                result.append(p)
                continue
            elif pattern[i] == "-" and self.board[p] == EMPTY:
                continue
            elif pattern[i] == "?" and self.board[p] != color and self.board[p] != EMPTY:
                continue
            else:
                return False, None
        result.append(start_point)    

        return True, result