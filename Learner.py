# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 22:02:49 2021

@author: nvana
"""
from Othello import Othello
from OthelloAgent import OthelloAgent
import time

def score_game(info, path, win_score, discount):
    power = 0
    for i in range(len(path))[::-1]:
        if not path[i] in info:
            info[ path[i] ] = 0
        # Add? Or average?
        info[ path[i] ] += win_score * ( discount**power )
        power += 1

def play(game, black_agent, white_agent, rounds, save_every, print_every, learn=True):
    black_wins = 0
    white_wins = 0
    ties = 0
    total_runs = 0
    
    for i in range(rounds):
        game.initialize_board()
        path = []
        turn = Othello.black
                
        while not game.is_complete():
            if turn == Othello.black:
                black_agent.make_move( game )
            else:
                white_agent.make_move( game )
            
            turn *= -1
            path.append( game.board_to_string() )
            
        if game.score_board() > 0:
            black_wins += 1
            if learn:
                score_game(black_agent.info, path, black_agent.win_score*black_agent.side, black_agent.back_discount)
        elif game.score_board() < 0:
            white_wins += 1
            if learn:
                score_game(black_agent.info, path, black_agent.win_score*white_agent.side, black_agent.back_discount)
        else:
            ties += 1
            
        total_runs += 1
                
        if i % print_every == 0:
            print("Black : ", black_wins,"/",total_runs)
            print("White : ", white_wins,"/",total_runs)
            print("Ties : ", ties,"/",total_runs)
            print("**********")
        if i % save_every == 0 and learn:
            black_agent.save_data_file()
            
    print("Black : ", black_wins,"/",total_runs)
    print("White : ", white_wins,"/",total_runs)
    print("Ties : ", ties,"/",total_runs)
    print("**********")
    if learn:
        black_agent.save_data_file()

if __name__ == "__main__":
    win_score = 500
    forward_discount = 0.9
    back_discount = 0.9
    default_score = 0
    layers = 3
    move_type = "epsilon_greedy"
    epsilon = 0.1
    cumulative_traversal = True
    single_track_traversal = False
    
    black_agent = OthelloAgent(side=Othello.black, data_file="three_layers.csv")
    black_agent.set_move_parameters(win_score=win_score, forward_discount=forward_discount,
                                default_score=default_score, layers=layers,
                                move_type=move_type, epsilon=epsilon, 
                                cumulative_traversal=cumulative_traversal,
                                single_track_traversal=single_track_traversal)
    
    white_agent = OthelloAgent(side=Othello.white, data_file="three_layers.csv")
    white_agent.info = black_agent.info
    white_agent.set_move_parameters(win_score=win_score, forward_discount=forward_discount,
                                default_score=default_score, layers=layers,
                                move_type=move_type, epsilon=epsilon, 
                                cumulative_traversal=cumulative_traversal,
                                single_track_traversal=single_track_traversal)
    
    game = Othello()
    
    #black_agent.move_type = "greedy"
    #white_agent.move_type = "random"
    
    start = time.time()
    play(game, black_agent, white_agent, 1000, 10, 10, learn=True)
    #play_against_computer(game, o_agent)
    print(time.time()-start)