#!/usr/bin/python3
#/usr/local/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, PASS
from simple_board import SimpleGoBoard

class Gomoku3():
    def __init__(self, numSimulations):
        """
        Gomoku player that selects moves randomly 
        from the set of legal moves.
        Passe/resigns only at the end of game.

        """
        self.name = "GomokuAssignment3"
        self.version = 1.0
        self.numSimulations = numSimulations
        self.is_random = True
        
    def get_move(self, board, color):
        return GoBoardUtil.generate_random_move_gomoku(board)

    def genmove(self, state):
        moves = state.get_empty_points()
        numMoves = len(moves)
        if numMoves == 0:
            return PASS
        score = [0] * numMoves
        for i in range(numMoves):
            move = moves[i]
            score[i] = self.simulate(state, move)
        bestIndex = score.index(max(score))
        best = moves[bestIndex]
        assert best in state.get_empty_points()
        return best

    def simulate(self, state, move):
        stats = [0] * 3
        state.play_move_gomoku(move, state.current_player)
        moveNr = state.moveNumber()
        for _ in range(self.numSimulations):
            if self.is_random:
                winner, _ = state.simulate()
            else:
                winner, _ = state.ruleBaseSimulation()
            stats[winner] += 1
            state.resetToMoveNumber(moveNr)
        assert sum(stats) == self.numSimulations
        assert moveNr == state.moveNumber()
        state.undo_move()
        eval = (stats[BLACK] + 0.5 * stats[EMPTY]) / self.numSimulations
        if state.current_player == WHITE:
            eval = 1 - eval
        return eval

    def policyType(self, is_random):
        self.is_random = is_random


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(Gomoku3(10), board)
    con.start_connection()

if __name__=='__main__':
    run()