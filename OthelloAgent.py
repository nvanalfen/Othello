# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 21:33:20 2021

@author: nvana
"""
from Othello import Othello
import pandas as pd
import os
import random

info_file_path = "info"

class OthelloAgent:
    
    def __init__(self, side=Othello.black, data_file=None):
        self.side = side
        self.info = {}
        
        if not data_file is None:
            self.data_file = data_file
            self.load_data_file()
            
    # Set the parameters used in selecting a move
    # Parameters:
    #   win_score               - float, Score upon winning (multiply by self.multiplier)
    #   forward_discount        - float [0,1], Fraction to multiply by current value of a certain board (for each step away from current state)
    #   back_discount           - float [0,1], Discount to multiply for each step backwards from final board upon a win
    #   default_score           - float, Default score if the board has not yet been encountered
    #   layers                  - int, Number of layers forward to traverse when searching future moves
    #   move_type               - str, Type of selection method for making a move
    #   epsilon                 - float [0,1], chance of selecting a random move if using a non-deterministic move_type
    #   cumulative_traversal    - bool, if True -> add up values from each traversal layer, if False -> only use the value at the final layer
    #   single_track_traversal  - bool, if True -> use only the max value of a given layer, if False -> add all value of a given layer
    #                           - ex:   cumulative_traversal = False, single_track_traversal = True
    #                           -       In this case, only the final layer would be counted, but every configuration at that layer would contribute to the score
    def set_move_parameters(self, win_score=100, forward_discount=0.9, back_discount=0.9,
                            default_score=0, layers=1, move_type="greedy", epsilon=0.1,
                            cumulative_traversal=False, single_track_traversal=True):
        self.win_score = win_score
        self.forward_discount = forward_discount
        self.back_discount = back_discount
        self.default_score = default_score
        
        self.layers = int(layers)
        if self.layers < 1:
            self.layers = 1
            
        self.move_type = move_type
        
        self.epsilon = epsilon
        if self.epsilon < 0:
            self.epsilon = 0
        elif self.epsilon > 1:
            self.epsilon = 1
            
        self.cumulative_traversal = cumulative_traversal
        self.single_track_traversal = single_track_traversal
    
    def load_data_file(self):
        if os.path.exists( os.path.join(info_file_path, self.data_file) ):
            table = pd.read_csv( os.path.join(info_file_path, self.data_file) )
            table.set_index("Board", inplace=True)
            self.info = table.to_dict()["Score"]
        #self.info = { table["Board"][i] : table["Score"][i] for i in range(len(table)) }
    
    def save_data_file(self):
        assert ( not self.data_file is None )
        
        table = pd.DataFrame()
        table = table.from_dict(self.info, orient="index", columns=["Score"])
        table.reset_index(inplace=True)
        table = table.rename(columns = {"index" : "Board"})
        table.to_csv( os.path.join( info_file_path, self.data_file ), index=False )
        
    def get_score(self, board_representation):
        if board_representation in self.info:
            return self.info[ board_representation ]
        return self.default_score
    
    # MOVE SELECTION FUNCTION
    
    def traverse_n_layers(self, game, turn, board_representation, layer):
        if layer == self.layers:
            return self.get_score(board_representation) * ( self.forward_discount**layer )
        
        final_score = 0
        
        for child in game.get_children( -turn, board_representation ):
            score = self.traverse_n_layers(game, -turn, game.board_to_string(child), layer+1)
            
            if self.single_track_traversal:
                if score*self.side > final_score*self.side:
                    final_score = score
            else:
                final_score += score
        
        if self.cumulative_traversal:
            final_score += self.get_score(board_representation) * ( self.forward_discount**layer )
        return final_score
                
        
    def random_move(self, game):
        options = game.get_children(self.side)
        return random.choices(options)[0]
    
    def greedy_move(self, game):
        high_score = 0
        bssf = None
        
        for child in game.get_children(self.side):
            score = self.traverse_n_layers(game, -self.side, game.board_to_string(child), 1)
            if score*self.side > high_score*self.side or bssf is None:
                high_score = score
                bssf = child
                
        return bssf
    
    def greedy_probabilistic_move(self, game):
        options = []
        weights = []
        for child in game.get_children(self.side):
            score = self.traverse_n_layers(game, -self.side, game.board_to_string(child), 1) 
            options.append( child )
            weights.append( score )
        
        return random.choices(options, weights)[0]
    
    def epsilon_greedy_move(self, game):
        if random.random() < self.epsilon:
            return self.random_move(game)
        return self.greedy_move(game)
    
    def make_move(self, game):
        if self.move_type == "greedy":
            move = self.greedy_move(game)
        elif self.move_type == "epsilon_greedy":
            move = self.epsilon_greedy_move(game)
        elif self.move_type == "greedy_probabilistic":
            move = self.greedy_probabilistic_move(game)
        elif self.move_type == "random":
            move = self.random_move(game)
                
        game.make_move( move )