import simple_board
from board_util import GoBoardUtil, EMPTY, BLACK, WHITE
from transposition import TranspositionTable
import numpy as np

class solver():
    def __init__(self, board):
        self.current_board = board
        self.depth = 10
        self.table = TranspositionTable()
    
    def history_moves(self):
        return self.current_board.move

    def call_alpha_beta(self):
        proof_tree_depth_zero = {}
        result = self.alphabeta(self.current_board, -100, 100, self.depth, proof_tree_depth_zero)
        move = self.find_first_move(proof_tree_depth_zero)
        return result, move

    def alphabeta(self, state, alpha, beta, depth, proof_tree_depth_zero):
        # result = self.table.lookup(state.code())
        # # check on table
        # if result != None:
        #     # print(str(GoBoardUtil.get_twoD_board(state)))
        #     # print(result)
        #     return result
        if depth == 0 or state.end_of_game():    
            result = state.staticallyEvaluateForToPlay()    
            return self.store_result(state, result)
        
        #heristic endgame checking
        end, HV = state.heuristic_end_of_game()
        if end:
            return self.store_result(state, HV)      

        #heuristic search a move
        move = state.heuristic_search_move(state.current_player)
        if move:
            moves = [move]
        else:
            moves = state.get_empty_points()    

        for m in moves:
            state.play_move_gomoku_auto_change_player(m)
            # print(str(GoBoardUtil.get_twoD_board(state)))
            value = -self.alphabeta(state, -beta, -alpha, depth - 1, proof_tree_depth_zero)
            if value > alpha:
                if (depth == self.depth):
                    proof_tree_depth_zero[value] = m
                # self.store_result(state, result)
                alpha = value
            state.undo_move()
            if value >= beta: 
                if (depth == self.depth):
                    proof_tree_depth_zero[value] = m
                # self.store_result(state, result)
                return beta   # or value in failsoft (later)
        return alpha

    def find_first_move(self, proof_tree_depth_zero):
        return proof_tree_depth_zero.get(1)

    def store_result(self, state, result): 
        self.table.store(state.code(), result)
        return result


    # def call_negamax(self):
    #     self.current_board.set_draw_winner(GoBoardUtil.opponent(self.current_board.current_player))
    #     proof_tree = []
    #     win = self.negamaxBoolean(self.current_board, self.depth, proof_tree)
    #     if win:
    #         return self.current_board.current_player, proof_tree
    #     self.current_board.set_draw_winner(self.current_board.current_player)
    #     if self.negamaxBoolean(self.current_board, self.depth, proof_tree):
    #         return EMPTY,proof_tree
    #     else:
    #         return GoBoardUtil.opponent(self.current_board.current_player),proof_tree
    #     # print(result)
    #     # print(proof_tree[-1])


    # def negamaxBoolean(self, state, depth, proof_tree):
    #     result = self.table.lookup(state.code())
    #     if result != None:
    #         return result
    #     if state.end_of_game() or depth == 0:
    #         result = state.staticallyEvaluateForToPlay()
    #         return self.store_result(state, result)
    #     for m in state.get_empty_points():
    #         # print(str(GoBoardUtil.get_twoD_board(state)))
    #         state.play_move_gomoku_auto_change_player(m)
    #         success = not self.negamaxBoolean(state, depth - 1, proof_tree)
    #         state.undo_move()
    #         if success:
    #             proof_tree.append(m)
    #             return self.store_result(state, True)
        # return self.store_result(state, False)







            
                

        
        

    
    