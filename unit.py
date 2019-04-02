from felibs.feaifuncs import *
import numpy as np

def dist(s, f):
    return ((f[0]-s[0])**2 + (f[1]-s[1])**2)**0.5

class Unit():
	def __init__(self, name, stats, initial_state):
		self.name = name
		self.stats = stats
		self.max_move = stats['mov']
		self.state = initial_state
		
		self.all_states = [initial_state]
		self.all_moves = []

		self.states_to_indices = {}
		self.indices_to_states = {}

		self.moves_and_actions_to_indices = {}
		self.indices_to_moves_and_actions = {}



	def move(self, act_tuple):
		r_l, u_d, action = zip(act_tuple)
		r_l = r_l[0]
		u_d = u_d[0]
		action = action[0]

		if r_l > 0 and u_d > 0:
			move_unit(0,r_l, u_d, 0, False, self.max_move)
		
		elif r_l < 0 and u_d > 0:
			move_unit(-r_l,0, u_d, 0, False, self.max_move)
		
		elif r_l > 0 and u_d < 0:
			move_unit(0,r_l, 0, -u_d, False, self.max_move)
		
		elif r_l < 0 and u_d < 0:
			move_unit(-r_l,0, 0, -u_d, False, self.max_move)
		time.sleep(3)
		act = choose_option_given_opt(action)
		# else:
		# 	opts = grab_options()
		# 	act = choose_option(opts, random_opt=True)

		self.state = tuple([self.state[0]+r_l, self.state[1] + u_d])
		self.all_states.append(self.state)
		self.all_moves.append((r_l,u_d, act))

	def setup_qtable(self, map_x, map_y):
		state_space = map_x * map_y
		#formula for board is 2*n+1 squared
		#number spaces excluded in that square is 4 times the sum of the range from 1 to n moves
		action_space = (2*self.max_move + 1)**2 - 4*(sum(range(1,self.max_move+1)))
		n_actions = 3
		
		#initialize qtable
		self.qtable = np.zeros((state_space, n_actions * action_space))

		#setup dictionaries
		
		index = 0
		for i in range(map_x):
		    for j in range(map_y):
		        self.states_to_indices[(i,j)] = index
		        index += 1

		
		for i, state in enumerate(self.states_to_indices.keys()):
		    self.indices_to_states[i] = state

		
		mdi = 0
		for i in range(-self.max_move,self.max_move+1):
		    for j in range(-self.max_move,self.max_move+1):
		        #limiting our action space by manhattan distance
		        if abs(i) + abs(j) > self.max_move:
		            continue
		        else:
		        	#update for 
		            for action in ['Wait', 'Item', 'Attack']:
		                self.moves_and_actions_to_indices[(i,j, action)] = mdi
		                mdi += 1
		                
		
		for i, action in enumerate(self.moves_and_actions_to_indices.keys()):
		    self.indices_to_moves_and_actions[i] = action

	def initialize_qtable_with_target(self, target):
		for i, row in enumerate(self.qtable):
		    for j, value in enumerate(row):
		        action = self.indices_to_moves_and_actions[j]
		        x_final = self.state[0] + action[0]
		        y_final = self.state[1] + action[1]
		        next_square = (x_final,y_final)
		        init_value = 1 - (dist(next_square,target)/dist(self.state,target))
		        self.qtable[i,j] = init_value



