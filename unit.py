from felibs.feaifuncs import *
import numpy as np
import random

def dist(s, f):
    return ((f[0]-s[0])**2 + (f[1]-s[1])**2)**0.5

class Unit():
	def __init__(self, name, stats, initial_state, item_slot):
		self.name = name
		self.stats = stats
		self.max_move = stats['mov']
		self.state = initial_state
		self.item = item_slot
		
		self.all_states = [initial_state]
		self.all_moves = []

		self.states_to_indices = {}
		self.indices_to_states = {}

		self.moves_and_actions_to_indices = {}
		self.indices_to_moves_and_actions = {}


	def __str__(self):
		return f"{self.name} has a max movement of {self.max_move} and an item in the {self.item} slot"


	def move(self, act_tuple=(0,0,'no input'), random_move=False):
		#Set move parameters
		if random_move:
			# move = move_unit(random_move=True, max_manhattan=self.max_move)
			# r_l = move[0]
			# u_d = move[1]
			finding_move = True
			while finding_move:
				r_l = random.randint(-self.max_move, self.max_move+1)
				u_d = random.randint(-self.max_move, self.max_move+1)
				if r_l + u_d <= self.max_move:
					finding_move = False

		else:
			r_l, u_d, action = zip(act_tuple)
			r_l = r_l[0]
			u_d = u_d[0]
		
		#Execute upon move parameters
		if r_l >= 0 and u_d >= 0:
			press_key('d', r_l)
			press_key('w', u_d)
			#move_unit(0,r_l, u_d, 0, False, self.max_move)
		
		elif r_l <= 0 and u_d >= 0:
			press_key('a', r_l)
			press_key('w', u_d)
			#move_unit(-r_l,0, u_d, 0, False, self.max_move)
		
		elif r_l >= 0 and u_d <= 0:
			press_key('d', r_l)
			press_key('s', u_d)
			#move_unit(0,r_l, 0, -u_d, False, self.max_move)
		
		elif r_l <= 0 and u_d <= 0:
			press_key('a', r_l)
			press_key('s', u_d)
			#move_unit(-r_l,0, 0, -u_d, False, self.max_move)
		press_key("'")	

		self.current_move = [r_l,u_d]


	def act(self, act_tuple=(0,0,'no input'), random_act=False):
		if random_act:
			opts = grab_options()
			act = choose_option(opts, random_opt=True, slot=self.item)
		else:
			r_l, u_d, action = zip(act_tuple)
			action = action[0]
			act = choose_option_given_opt(action, slot=self.item)
			if act == 'Attack':
				time.sleep(2.5)


		self.state = (self.state[0]+self.current_move[0], self.state[1]+self.current_move[1])
		
		if self.state[0] < 0:
			self.state = (0, self.state[1])
		elif self.state[0] > self.map_dims[0]-1:
			self.state = (self.map_dims[0]-1, self.state[1])
		
		if self.state[1] < 0:
			self.state = (self.state[0], 0)
		elif self.state[1] > self.map_dims[1]-1:
			self.state = (self.state[0], self.map_dims[1]-1)

		self.current_move.append(act)
		self.all_moves.append(tuple(self.current_move))
		self.all_states.append(self.state)


	def setup_qtable(self, map_x, map_y):
		self.map_dims = (map_x, map_y)
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
		            for action in ['Attack', 'Item', 'Wait']:
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


	def update_qtable_invalid_move(self):
		state_index = self.states_to_indices[self.state]
		for act in ['Attack', 'Item', 'Wait']:
			action_index = self.moves_and_actions_to_indices[(self.current_move[0], self.current_move[1], act)]
			self.qtable[state_index, action_index] *= 0.8


	def update_qtable_with_reward(self, reward):
		state_index = self.states_to_indices[self.state]
		action_index = self.moves_and_actions_to_indices[self.all_moves[-1]]
		self.qtable[state_index, action_index] += reward


	def update_qtable_death(self, target=False):
		#when looping through units, we want to penalize the person that died the most, others less
		if target:
			death_penalty = 0.5
		else:
			death_penalty = 0.1

		state_index = self.states_to_indices[self.state]
		action_index = self.moves_and_actions_to_indices[self.all_moves[-1]]
		self.qtable[state_index, action_index] -= death_penalty


	def save_qtable(chapter):
		np.save(f'data/chapter{chapter}_{self.name}', self.qtable)


	def load_qtable(chapter):
		self.qtable = np.load(f'data/chapter{chapter}_{self.name}')

