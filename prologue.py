import pandas as pd
import pyautogui
import time
from felibs.feaifuncs import *


def gen_data_prologue(states = [], actions = [], metrics = []):
    taking_turns = True
    while taking_turns:
        state = []
        act = []

        #Grab Board State
        select_next_unit()
        press_key(';')
        time.sleep(0.2)
        name = grab_name()
        if not name:
            press_key('e')
            name = double_check_name()
            press_key(';')
            if not name:
                print('Broken for no name found')
                break
        act.append(name)
        press_key('w')
        press_key("'")
        press_key('s')
        press_key("'")
        board_state = grab_board_state()
        press_key(';',2)

        metric = board_state[1] + board_state[2]
        

        state.append(board_state[0])
        state.append(board_state[1])
        state.append(board_state[2])

        #Set Options on 1st Turn Only
        if state[2] == 1:
            set_options()
            time.sleep(0.2)

        #Execute Actions
        select_next_unit()
        press_key('e')
        d = grab_stats()
        df = pd.DataFrame(d, index=[name], columns=d.keys())
        state.extend(df.values[0])
        press_key(';')
        moves = move_unit(random_move=True)
        act.extend(list(moves))
        opts = grab_options()
        if not opts:
            act.append("Invalid move")
            print('Broken for Invalid Move')
            break
        else:
            selection = choose_option(opts, random_opt=True)
            act.append(selection)
        
        metrics.append(metric)
        states.append(state)
        actions.append(act)

        if state[2] == 1:
            time.sleep(5)
            press_key('Enter')
            time.sleep(1)
        else:
            enemy_phase_break(7)

        #Break loop if turn count greater than 8
        if state[2] > 8:
            print('Broken for exceeding turn count')
            break  
    return states, actions, metrics


def reset_to_prologue():
    """
    Assumes there is the resume chapter option
    DO NOT USE FUNCTION WITHOUT THIS OPTION, IT WILL SELECT ERASE DATA
    """ 
    pyautogui.hotkey('command', 'r')
    time.sleep(2.2)
    press_key('enter', 2, 2)
    press_key('s')
    press_key("'", 2, 0.5)
    time.sleep(1.8)
    press_key('a')
    press_key("'")
    time.sleep(2)
    press_key('enter', 4, 1.5)

