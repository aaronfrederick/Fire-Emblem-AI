import numpy as np
import pandas as pd
from PIL import ImageGrab
import cv2
import time
import pytesseract
import pickle
from sklearn.linear_model import LogisticRegression
import pyautogui
import random
import math
from unit import Unit


def attack_in_opts(opts):
    if not opts:
        return False

    if 'Attack' in opts:
        return True

    for option in opts:
        if 'tac' in option:
            return True
            
    return False
  

def check_death_quote(death_quotes_dict):
    '''
    looks for a quote on screen and checks if that quote is a death quote
    returns a name if someone died, returns empty string otherwise
    BUG ALERT: RETURNS NOT DEATH WHEN NO QUOTE
    '''
    screen = np.array(ImageGrab.grab(bbox=(0,0,600,400)))
    long_screen = subscreen(290,165,480,265, screen)
    short_screen = subscreen(210,165,500,265, screen)
    long_text = pytesseract.image_to_string(long_screen)
    short_text = pytesseract.image_to_string(short_screen)
    if not long_text and not short_text:
        return ''
    elif len(long_text) > len(short_text):
        if long_text in death_quotes_dict.keys():
            return death_quotes_dict[long_text]
        else:
            return 'NOT DEATH'
    else:
        if short_text in death_quotes_dict.keys():
            return death_quotes_dict[short_text]
        else:
            return 'NOT DEATH'


def choose_option(options, random_opt=False, slot=1):
    """
    When a unit is finished moving, this function selects their next choice
    currently supported actions:
    -Attack
    -Item
    -Wait
    unsupported:
    -Support
    -Staff
    -Rescue
    -Drop
    -Trade
    -Shop
    -Armory
    -Give
    """
    if random_opt:
        ind = random.randint(0,len(options)-1)
        choice = options[ind]
        #if 'ttac' in choice:
        if 'Attack' in options:
            press_key("'",3)
            return 'Attack'
        elif 'tem' in choice:
            press_key("s",ind)
            press_key("'")
            use_item()
            return 'Item'
        else:
            wait()
            return 'Wait'
    
    else:
        if 'Attack' in options:
            press_key("'",3)
            return 'Attack'

        else:
            choice = random.randint(0,len(options))
            if 'tem' in options[choice]:
                    press_key('s',choice)
                    press_key("'")
                    use_item(slot)
                    return 'Item'
            else:
                wait()
                return 'Wait'

def choose_option_given_opt(choice, slot=1):
    if choice == 'Wait':
        wait()
        return 'Wait'
    elif choice == 'Item':
        press_key("w", 2)
        press_key("'")
        use_item(slot)
        return 'Item'
    elif choice == 'Attack':
        press_key("'", 3)
        return 'Attack'

def double_check_name():
    screen = np.array(ImageGrab.grab(bbox=(125,297,175,332)))
    for i, row in enumerate(screen):
        for j, pixel in enumerate(row):
            brightness = sum(pixel)
            if brightness > 890:
                screen[i][j] = np.array([0, 0, 0, 255], dtype=np.uint8)
    return pytesseract.image_to_string(screen)
            

def enemy_phase_break(stall = 5):
    time.sleep(stall)

    
def grab_board_state(model = 'block_text_logreg.pkl'):
    """
    *expects screen to be at 'status' menu*
    
    Function to measure loss
    - player unit count: if decreases, cancel run (someone has died)
    - enemy unit count: if decreases, increase run's fitness/reward
    - turn count: when increases, decrease fitness/reward
    - gold count: leave out initially, but eventually factor into loss function
    
    """
    time.sleep(0.5)
    
    block_reader = pickle.load(open(model, 'rb'))
    screen = np.array(ImageGrab.grab(bbox=(0,0,600,600)))
    
    player_unit_count_sc1 = subscreen(398,225,422,255,screen)
    puc1 = int(block_reader.predict(padder(player_unit_count_sc1).reshape(30*24*4).reshape(1,-1))[0])
    player_unit_count_sc10 = subscreen(374,225,398,255,screen)
    puc10 = int(block_reader.predict(padder(player_unit_count_sc10).reshape(30*24*4).reshape(1,-1))[0])
    puc = 10 * puc10 + puc1
    
    enemy_unit_count_sc1 = subscreen(520,224,544,254,screen)
    euc1 = int(block_reader.predict(padder(enemy_unit_count_sc1).reshape(30*24*4).reshape(1,-1))[0])
    enemy_unit_count_sc10 = subscreen(498,224,522,254,screen)
    euc10 = int(block_reader.predict(padder(enemy_unit_count_sc10).reshape(30*24*4).reshape(1,-1))[0])
    euc = 10 * euc10 + euc1
    
    turn_count_sc1 = subscreen(243,367,267,397,screen)
    tc1 = int(block_reader.predict(padder(turn_count_sc1).reshape(30*24*4).reshape(1,-1))[0])
    turn_count_sc10 = subscreen(219,367,243,397,screen)
    tc10 = int(block_reader.predict(padder(turn_count_sc10).reshape(30*24*4).reshape(1,-1))[0])
    tc = 10 * tc10 + tc1
    return puc,euc,tc


def grab_name():
    """
    *Assumes cursor over a unit but no movement yet*
    Screencaps the 2 areas where there could be a name, returns the last value
    in the pytesseract list.  ONLY TESTED ON L-P CAUTION
    """
    img1 = np.array(ImageGrab.grab(bbox=(110,110,210,152)))
    img2 = np.array(ImageGrab.grab(bbox=(110,390,210,430)))
    text1 = pytesseract.image_to_string(cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY))
    text2 = pytesseract.image_to_string(cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY))
    if text1.split():
        return text1.split()[len(text1.split())-1]
    elif text2.split():
        return text2.split()[len(text2.split())-1]


def grab_stats(model = 'block_text_logreg.pkl'):
    """
    *Assumes cursor over a unit*
    Presses 'R' on unit and creates a table with values for each stat
    Saves images with each stat into data/raw
    Extension should be in the form {NAME}{MODE}{CHAPTER}
    where enemies are e1, e2, ..., en
    where mode is ln/lh/en/eh/hn/hh
    and where chapter is either p,1,11,12,etc.
    
    """
    
    
    block_reader = pickle.load(open(model, 'rb'))
    stats = {}
    
    screen = np.array(ImageGrab.grab(bbox=(0,0,600,600)))
    
    str_img = subscreen(338,160,362,190, screen)
    stats['str'] = int(block_reader.predict(padder(str_img).reshape(30*24*4).reshape(1,-1))[0])
    
    skl_img = subscreen(338,198,362,228,screen)
    stats['skl'] = int(block_reader.predict(padder(skl_img).reshape(30*24*4).reshape(1,-1))[0])
    
    spd_img = subscreen(338,239,362,269,screen)
    stats['spd'] = int(block_reader.predict(padder(spd_img).reshape(30*24*4).reshape(1,-1))[0])
    
    luk_img = subscreen(338,278,362,308,screen)
    stats['luk'] = int(block_reader.predict(padder(luk_img).reshape(30*24*4).reshape(1,-1))[0])
    
    def_img = subscreen(338,320,362,350,screen)
    stats['def'] = int(block_reader.predict(padder(def_img).reshape(30*24*4).reshape(1,-1))[0])
    
    res_img = subscreen(338,358,362,388,screen)
    stats['res'] = int(block_reader.predict(padder(res_img).reshape(30*24*4).reshape(1,-1))[0])
    
    mov_img = subscreen(498,160,522,190,screen)
    stats['mov'] = int(block_reader.predict(padder(mov_img).reshape(30*24*4).reshape(1,-1))[0])
    
    
    curr_hp_1 = subscreen(58,438,79,465,screen)
    try:
        chp_tens = 10* int(block_reader.predict(padder(curr_hp_1).reshape(30*24*4).reshape(1,-1))[0])
    except:
        chp_tens = 0
    curr_hp_2 = subscreen(80,438,100,465,screen)
    stats['chp'] = chp_tens + int(block_reader.predict(padder(curr_hp_2).reshape(30*24*4).reshape(1,-1))[0])
    
    
    max_hp_1 = subscreen(120,438,140,465,screen)
    mhp_tens = 10* int(block_reader.predict(padder(max_hp_1).reshape(30*24*4).reshape(1,-1))[0])
    max_hp_2 = subscreen(140,438,160,465,screen)
    stats['mhp'] = mhp_tens + int(block_reader.predict(padder(max_hp_2).reshape(30*24*4).reshape(1,-1))[0])

    return stats


def grab_options():
    """
    *Assumes a completed move*
    Screencaps the 2 areas where the options menu could be
    Returns *CLEANED* list of options for the character to execute
    current status: kind of (but not really) reads the 5-option menu only
    not the 2-option menu
    
    processed image makes no difference
    """
    options = []
    screen = np.array(ImageGrab.grab(bbox=(0,0,600,400)))
    
    #long_1 = np.array(ImageGrab.grab(bbox=(30,130,150,350)))
    long_1 = subscreen(30,130,150,350, screen)
    short_1 = subscreen(30,157,150,263,screen)
    med_1 = subscreen(30,164,150,290,screen)
    long_2 = subscreen(470,140,590,355,screen)
    short_2 = subscreen(455,157,572,263,screen)
    mid_2 = subscreen(455,164,572,290,screen)
    
    long_text1 = pytesseract.image_to_string(inverted_grayscale(long_1))
    short_text1 = pytesseract.image_to_string(inverted_grayscale(short_1))
    mid_text1 = pytesseract.image_to_string(inverted_grayscale(med_1))
    long_text2 = pytesseract.image_to_string(inverted_grayscale(long_2))
    short_text2 = pytesseract.image_to_string(inverted_grayscale(short_2))
    mid_text2 = pytesseract.image_to_string(inverted_grayscale(mid_2))
    
    for entry in [short_text1.split(),short_text2.split(),
                 mid_text1.split(), mid_text2.split(),
                 long_text1.split(), long_text2.split()]:
        for token in entry:
            if len(token) > 3 and token not in options:
                options.append(token)
    return options


def inverted_grayscale(color_image):
    processed_img = cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY)
    processed_img = cv2.bitwise_not(processed_img)
    procssed_img = cv2.Canny(processed_img,threshold1=400, threshold2=410)
    #return 0.5*processed_img - 70
    return processed_img


def move_unit(left=0,right=0,up=0,down=0, random_move=False, max_manhattan=5):
    if random_move==True:
        finding_move = True
        while finding_move:
            left = random.randint(0,max_manhattan+1)
            right = random.randint(0,max_manhattan+1)
            up = random.randint(0,max_manhattan+1)
            down = random.randint(0,max_manhattan+1)
            if abs(left-right) + abs(up-down) <= max_manhattan:
                finding_move = False
    ret_list = [right-left,up-down]
    #optimize the movement process so excess moves aren't performed
    if left>right:
        press_key('a', left-right)
    elif right>left:
        press_key('d', right-left)
    if up>down:
        press_key('w', up-down)
    elif down>up:
        press_key('s', down-up)

    
    press_key("'")
    time.sleep(0.2)
    return tuple(ret_list)


def padder(test_img):
    
    test_reshape = []
    for i, row in enumerate(test_img):
        new_row = []
        for j, entry in enumerate(row):
            new_row.append(np.array(entry))
        for _ in range(24-len(new_row)):
            new_row.append(np.array([0,0,0,255]))
        test_reshape.append(new_row)
    for _ in range(30-len(test_reshape)):
        new_row2 = []
        for __ in range(24):
            new_row2.append(np.array([0,0,0,255]))
        test_reshape.append(np.array(new_row2))

    ret_img = np.array((test_reshape), dtype=np.uint8)

    if ret_img.shape == (30,24,4):
        return ret_img
    else:
        print('Wrong Shape! The shape of the current image is', end=' ')
        print(ret_img.shape)


def press_key(key, n_times = 1, interrupt=0):
    for _ in range(n_times):
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)
        time.sleep(interrupt)


def processed_img(original_image):
    processed_img = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    procssed_img = cv2.Canny(processed_img,threshold1=300, threshold2=450)
    return processed_img


def select_next_unit():
    press_key('q')
    press_key("'")


def select_vba():
    #Select VBA
    pyautogui.moveTo(7,54,0.2)
    pyautogui.click()
    time.sleep(0.3)


def set_options(right=5,down=5):
    press_key('d',right)
    press_key('s',down)
    press_key("'")
    press_key('s',2)
    press_key("'")
    press_key('d',3)
    press_key('s')
    press_key('d')
    press_key('s')
    press_key('d',2)
    press_key(';')

        
def subscreen(x0,y0,x1,y1, screen):
    sub_img = []
    for i in range(y0,y1,1):
        row=[]
        for j in range(x0,x1,1):
            row.append(screen[i][j])
        sub_img.append(np.array(row))
    sub_img = np.array(sub_img)
    return sub_img


def use_item(slot=1,random_item=False):
    if random_item:
        press_key('s',random.randint(0,5), 0.5)
    else:
        press_key('s',slot, 0.5)
    press_key("'",2)
    press_key(";")
    time.sleep(0.2)
    press_key(";", 2)
    wait()
    #wait()


def wait():
    time.sleep(0.2)
    press_key('w')
    time.sleep(0.2)
    press_key("'")


################################################################################################################
###################################  RESET FUNCTIONS FOR DIFFERENT CHAPTERS  ###################################
################################################################################################################

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

def reset_to_ch1():
    """
    Assumes there is the resume chapter option
    DO NOT USE FUNCTION WITHOUT THIS OPTION, IT WILL SELECT ERASE DATA
    """ 
    pyautogui.hotkey('command', 'r')
    time.sleep(2.2)
    press_key('enter', 2, 2)
    press_key('s')
    press_key("'", 2, 0.5)
    time.sleep(1.2)
    press_key('a')
    press_key("'")
    time.sleep(2)
    press_key('enter', 4, 1.4)


################################################################################################################
###################################  TEST FUNCTIONS FOR SOLVING CHAPTERS  ######################################
################################################################################################################



