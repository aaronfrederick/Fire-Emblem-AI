# Fire-Emblem-AI
An AI program that learns to play the 2003 GBA game Fire Emblem

## Notes:
I am playing the game on a downloaded emulator- visualboy advance and a downloaded ROM of Fire Emblem Blazing Sword.
To play the game programmatically, the emulator must be in the top right corner of the screen, that is where the image processing software is looking to obtain data.


## Programs:

feaifuncs.py is a group of functions to ease the input commands into VisualBoyAdvance as well as capturing screens and doing light image processing and classification using machine learning methods.

prologue.py uses the baseline functions in feaifuncs to take turns in the prologue setting.

The Automated Playing notebook plays the game making random decisions, showing the functionality of the .py files.

The Prologue Q Learning notebook plays the game using a Q-table, updating values with rewards as the level progresses. Due to how slowly the game plays with the emulator, I instantitated the Q-table with distance-based rewards that would have been added step by step but can be calculated faster manually ahead of time. This saves us from having to fill the Q-table with values we already could calculate, saving runtime.
