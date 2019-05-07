#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys, os
import copy
import math

# Exemple avec 4x4 => trop long
# GOAL = "goal_4"
# BASE = "ex4"

#Exemple 23sec
# GOAL = "goal_esca"
# BASE = "hard"

# Exemple 0.15sec
GOAL = "goal_lin"
BASE = "exin"

TAQUINS = {
	"goal_4" : [
		1, 2, 3, 4,
		5, 6, 7, 8,
		9, 10, 11, 12,
		13, 14, 15, 0
	],
	"ex4" : [
		12, 5, 8, 10,
		1, 15, 3, 11,
		0, 14, 2, 6,
		4, 7, 9, 13
	],
	"goal_esca" : [
		1, 2, 3,
		8, 0, 4,
		7, 6, 5
	],
	"goal_lin" : [
		1, 2, 3,
		4, 5, 6,
		7, 8, 0
	],
	"simple" : [
		1, 2, 0,
		8, 4, 3,
		7, 6, 5
	],
	"hard" : [
		3, 6, 5,
		7, 2, 4,
		0, 8, 1
	],
	"other" : [
		6, 3, 1,
		8, 0, 2,
		7, 4, 5
	],
	#21 coups, 386 noeuds
	"exin" : [
		4, 8, 3,
		2, 0, 7,
		6, 5, 1
	],
	"unsolvable" : [
		1, 2, 3,
		4, 5, 6,
		8, 7, 0
	],
}

ACTION = {
	"N" : 0,
	"S" : 1,
	"E" : 2,
	"W" : 3,
}

"""
	Represente un taquin
	board = list des numeros
"""
class Taquin:
	def __init__(self, values, size):
		self.board = values.copy()
		self.size = size
		self._pos, self._x, self._y = 0, 0, 0
		self.pos = values.index(0)

	@property
	def pos(self):
		return self._pos
	@property
	def x(self):
		return self._x
	@property
	def y(self):
		return self._y

	@pos.setter
	def pos(self, value):
		self._pos = value
		self._x = value % self.size
		self._y = value // self.size

	def inc_x(self):
		self.pos = self._pos + 1
	def dec_x(self):
		self.pos = self._pos - 1
	def inc_y(self):
		self.pos = self._pos + self.size
	def dec_y(self):
		self.pos = self._pos - self.size

	def __eq__(self, other):
		return self.board == other.board

	def move(self, action):
		if action == ACTION["N"]:
			self.board[self.pos] = self.board[self.pos - self.size]
			self.dec_y()
			self.board[self.pos] = 0
		elif action == ACTION["S"]:
			self.board[self.pos] = self.board[self.pos + self.size]
			self.inc_y()
			self.board[self.pos] = 0
		elif action == ACTION["E"]:
			self.board[self.pos] = self.board[self.pos + 1]
			self.inc_x()
			self.board[self.pos] = 0
		elif action == ACTION["W"]:
			self.board[self.pos] = self.board[self.pos - 1]
			self.dec_x()
			self.board[self.pos] = 0

	def __str__(self):
		r = ""
		for i, v in enumerate(self.board):
			if i != 0 and i % self.size == 0:
				r += "\n"
			r += "{}, ".format(v)
		return r

def heuristic_manhattan(goal, current):
	tt = 0
	size = goal.size
	for i, v in enumerate(current.board):
		if v == 0:
			continue
		i_goal = goal.board.index(v)
		gx, gy = i_goal % size, i_goal // size
		tx, ty = i % size, i // size
		tt += abs(tx - gx) + abs(ty - gy)
	return tt

taquin_goal = Taquin(TAQUINS[GOAL], int(math.sqrt(len(TAQUINS[GOAL]))))

"""
	Etat en cours
"""
class State:
	def __init__(self, taquin, up_heur=False):
		self.__cost = 0			# +1 each step
		self.__heuristic = 0	# 0 means goal
		self.__action = -1	# ACTION
		self.__parent = None	# Ref to previous state
		self.__taquin = copy.deepcopy(taquin) # Current taquin after transition
		self.__weight = 0
		if up_heur:
			self.__heuristice = heuristic_manhattan(
				taquin_goal, self.__taquin)
			self.up_weight()

	def transition(self, action):
		new_state = type(self)(self.__taquin)
		new_state.__taquin.move(action)
		new_state.__heuristic = heuristic_manhattan(
				taquin_goal, new_state.__taquin)
		new_state.__cost = self.__cost + 1
		new_state.__action = action
		new_state.__parent = self
		new_state.up_weight()
		return new_state

	def __lt__(self, other):
		return self.weight < other.weight
	def __gt__(self, other):
		return self.weight > other.weight
	def __le__(self, other):
		return self.weight <= other.weight
	def __ge__(self, other):
		return self.weight >= other.weight

	def __eq__(self, other):
		return self.__taquin == other.__taquin
	def __ne__(self, other):
		return self.__taquin != other.__taquin

	@property
	def parent(self):
		return self.__parent

	@property
	def size(self):
		return self.__taquin.size
	@property
	def x(self):
		return self.__taquin.x
	@property
	def y(self):
		return self.__taquin.y

	@property
	def taquin(self):
		return self.__taquin

	@property
	def cost(self):
		return self.__cost
	@property
	def heuristic(self):
		return self.__heuristic

	@property
	def weight(self):
		return self.__weight

	def up_weight(self):
		self.__weight = self.__cost + self.__heuristic

	@property
	def action(self):
		return self.__action

	def __str__(self):
		return str(self.__taquin)

"""
	Inverse
"""
class PriorityList(list):
	def __init__(self, *args):
		list.__init__(self, *args)

	def append(self, new_item):
		insert_index = len(self)
		for index, item in enumerate(self):
			if (new_item > item):
				insert_index = index
				break
		self.insert(insert_index, new_item)

def find_moves(state):
	# N
	if state.y > 0 and state.action != ACTION["S"]:
		yield state.transition(ACTION["N"])
	# S
	if state.y < state.size - 1 and state.action != ACTION["N"]:
		yield state.transition(ACTION["S"])
	# E
	if state.x < state.size - 1 and state.action != ACTION["W"]:
		yield state.transition(ACTION["E"])
	# W
	if state.x > 0 and state.action != ACTION["E"]:
		yield state.transition(ACTION["W"])

def astar(start, goal):
	open_lst = PriorityList()
	close_lst = []
	counter = 0
	counter_node = 0
	final_state = State(goal, True)
	open_lst.append(State(start, True))
	found = None
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		close_lst.append(curr_state)

		if curr_state == final_state:
			found = curr_state
			break

		for next_state in find_moves(curr_state):
			try:
				old_c = close_lst.index(next_state)
			except ValueError:
				old_c = None
			if old_c is not None \
			and next_state.weight < close_lst[old_c].weight:
				close_lst.pop(old_c)
				open_lst.append(next_state)
				continue

			try:
				old_o = open_lst.index(next_state)
			except ValueError:
				old_o = None
			if old_o is not None \
			and next_state.weight < open_lst[old_o].weight:
				open_lst.pop(old_o)
				open_lst.append(next_state)
				continue

			open_lst.append(next_state)
			counter_node += 1

		counter += 1
		if counter % 1000 == 0:
			print(counter)

	if found is not None:
		print("Success: turn = {}, nodes = {}".format(counter, counter_node))
	else:
		print("Failure: turn = {}, nodes = {}".format(counter, counter_node))
		return 0

	nb_hit = 0
	while (found.parent is not None):
		found = found.parent
		nb_hit += 1
	print("Moves: {}".format(nb_hit))

def solvable(taquin):
	inv = 0
	for i, v in enumerate(taquin.board):
		if v == 0:
			continue
		for w in taquin.board[i:]:
			if w == 0:
				continue
			if v > w:
				inv += 1
	return inv % 2 == 0

def main():
	taquin_base = Taquin(TAQUINS[BASE],
		int(math.sqrt(len(TAQUINS[BASE]))))
	if not solvable(taquin_base):
		print("Not solvable")
		#return 0

	astar(taquin_base, taquin_goal)

	return 0

if __name__ == '__main__':
	sys.exit(main())
