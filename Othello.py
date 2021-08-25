# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 20:10:52 2021

@author: nvana
"""

import numpy as np

# TODO : Consider replacing 8x8 grid with flat array and using modular arithmetic to speed up child finding

class Othello:
    black = 1
    white = -1
    blank = 0
    dimension = 8
    
    def __init__(self):
        self.initialize_board()
    
    def initialize_board(self):
        self.board = np.zeros((Othello.dimension, Othello.dimension), dtype=int)
        self.board[3,3] = Othello.white
        self.board[4,4] = Othello.white
        self.board[3,4] = Othello.black
        self.board[4,3] = Othello.black
    
    def get_indices(self, side, board=None):
        if board is None:
            board = self.board
        return np.where( board == side )
    
    def in_bounds(self, x, y):
        return x >= 0 and x < Othello.dimension - 1 \
                and y >= 0 and y < Othello.dimension - 1
    
    # Crawls towards [y+dy, x+dx]
    # If will only return indices if the crawl started at one color, crawled over the other color, and lands on a blank
    # Otherwise, returns None
    def crawl(self, x, y, dx, dy, start_side, last_side, board=None):
        if not self.in_bounds(x, y):
            return None
        
        if board is None:
            board = self.board
        
        if board[y,x] == Othello.blank:
            if last_side != start_side:
                return x, y
            else:
                return None
        
        last_side = board[y,x]
        return self.crawl(x+dx, y+dy, dx, dy, start_side, last_side, board=board)
    
    def crawl_flip(self, x, y, dx, dy, start_side, board=None):
        if board is None:
            board = self.board
            
        if not self.in_bounds(x, y) or board[y,x] == Othello.blank:
            return False
        
        if board[y,x] == start_side:
            return True
        
        flip = self.crawl_flip(x+dx, y+dy, dx, dy, start_side, board=board)
        if flip:
            # Flip the piece
            board[y,x] *= -1
    
    def get_possible_moves(self, x, y, board=None):
        if board is None:
            board = self.board
        moves = set()
        
        if not self.in_bounds(x, y):
            return moves
        
        side = board[y,x]
        
        for i in range(3):
            d_row = i-1
            for j in range(3):
                d_col = j-1
                if not (d_row == 0 and d_col == 0):
                    inds = self.crawl(x, y, d_col, d_row, side, side, board=board)
                    if not inds is None:
                        moves.add( inds )
        
        return moves
        
    def get_all_possible_moves(self, side, board=None):
        if board is None:
            board = self.board
            
        inds = self.get_indices(side, board=board)
        moves = set()
        for x, y in inds:
            # Union the set of current coordinates with the new ones
            moves |= self.get_possible_moves(x, y, board=board)
        
        return moves
    
    def place_piece(self, x, y, side, board=None):
        if board is None:
            board = self.board
            
        if board[y,x] != Othello.blank:
            return
        
        board[y,x] = side
        
        for i in range(3):
            d_row = i-1
            for j in range(3):
                d_col = j-1
                if not (d_row == 0 and d_col == 0):
                    self.crawl_flip(x+d_col, y+d_row, d_col, d_row, side, board=board)
    
    def get_children(self, side, board=None):
        if board is None:
            board = self.board
        
        children = []
        
        for x, y in self.get_all_possible_moves(side, board=board):
            child = np.array(board)
            self.place_piece(x, y, side, board=child)
            children.append(child)
        
        return children
    
    def board_to_string(self, board=None):
        if board is None:
            board = self.board
        
        return ",".join( board.astype(str).flatten() )
