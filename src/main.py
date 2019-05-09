#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys, os
import copy
import math
import heapq
from collections import deque


GOAL = "goal_4_esca"
BASE = "base_4_arobion"

#GOAL = "goal_3_top"
#BASE = "base_31"

"""
52 moves, 12sec chez lui
66 moves en 1.1 sec ou 64 moves en 1.9sec chez nous selon le map
"""
TAQUINS = {

	"goal_4" : [1, 2, 3, 4,
				5, 6, 7, 8,
				9, 10, 11, 12,
				13, 14, 15, 0],
	"goal_3" : [1, 2, 3,
				4, 5, 6,
				7, 8, 0],
	"goal_3_top" : [0, 1, 2, 3,
				4, 5, 6,
				7, 8],
	"base_31" : [8, 7, 6, 0, 4, 1, 2, 5, 3],
	"base_31_2" : [8, 0, 6,  5, 4, 7, 2, 3, 1],
	"base_4" : [15, 6, 10, 3, 7, 8, 13, 5, 11, 9, 12, 0, 1, 2, 4, 14],

	"goal_3_esca": [1, 2, 3, 8, 0, 4, 7, 6, 5],
	"goal_4_esca": [1, 2, 3, 4, 12, 13, 14, 5, 11, 0, 15, 6, 10, 9, 8, 7],

	"base_4_easy": [1, 4, 5, 0, 12, 2, 15, 3, 14, 11, 7, 6, 10, 13, 9, 8],

	"base_4_arobion": [5, 4, 9, 15, 6, 2, 8, 11, 1, 12, 7, 0, 3, 13, 14, 10],

	"base_3_simple" : [1, 2, 3,
						4, 0, 5,
						7, 8, 6],
	# https://dgurkaynak.github.io/8-puzzle-solver/
	# Moves 18, nodes 291 5sec sur le site, nous instant
	"base_3_known" : [2, 3, 0,
						8, 1, 4,
						7, 6, 5],
	#28 moves, 2446 turns, 3767 nodes, ~4.2sec
	"base_3_fast" : [4, 8, 7,
					2, 0, 6,
					3, 5, 1],
	"unsolvable" : [3, 6, 5,
					7, 2, 4,
					0, 8, 1],
	"base_9": [ 1,  2,  3,  4,  5,  6,  7,  8,  9,
57, 56, 33, 35 ,36, 37, 38, 39, 10,
32, 30, 58, 72 ,59, 60, 61, 40, 11,
31, 55, 34, 74 ,76, 80, 62, 41, 12,
29, 54, 71, 73 ,78, 75, 63, 42, 13,
27, 28, 53, 70 ,79, 77, 64, 43, 14,
 0, 52, 69, 68 ,67, 66, 65, 44, 15,
26, 51, 50, 49 ,48, 47, 46, 45, 16,
25, 24, 23, 22 ,21, 20, 19, 18, 17,
],
	"goal_9": [1, 2, 3, 4, 5, 6, 7, 8, 9, 32, 33, 34, 35, 36, 37, 38, 39, 10, 31, 56, 57, 58, 59, 60, 61, 40, 11, 30, 55, 72, 73, 74, 75, 62, 41, 12, 29, 54, 71, 80, 0, 76, 63, 42, 13, 28, 53, 70, 79, 78, 77, 64, 43, 14, 27, 52, 69, 68, 67, 66, 65, 44, 15, 26, 51, 50, 49, 48, 47, 46, 45, 16, 25, 24, 23, 22, 21, 20, 19, 18, 17]
}


ACTIONS = {
	"None": 4, "N" : 0, "S" : 1, "E" : 2, "W" : 3
}

class PriorityQueue(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def push(self, item):
        heapq.heappush(self, item)

    def pop(self):
        return heapq.heappop(self)


#heur 3x3: [0, 1, 4, 6, 10]
#MAP_HEUR = [0, 1, 3, 7, 10, 14, 18, 25, 32, 39, 46, 58, 70, 82, 98, 115, 130]
MAP_HEUR = [0, 1, 4, 6, 9, 11, 12]
#MAP_HEUR = [0, 1, 2, 3, 4, 5, 6]

# Take a goal and current taquin
def init_heuristic_manhattan(manhattan_cost, puzzle):
	total = 0
	# Range de 1 (on compte pas le 0) a len
	for index in range(1, len(puzzle.board)):
		total += manhattan_cost[index][puzzle.board.index(index)]
	return total

#Environ 5-8% de vitesse en plus, pas terrible, cache de goal inutile (1% maxi)
POS_GOAL4 =  [
	(0, 0), (0, 1), (0, 2), (0, 3),
	(1, 0), (1, 1), (1, 2), (1, 3),
	(2, 0), (2, 1), (2, 2), (2, 3),
	(3, 0), (3, 1), (3, 2), (3, 3)
]
POS_GOAL3 =  [
	(0, 0), (0, 1), (0, 2),
	(1, 0), (1, 1), (1, 2),
	(2, 0), (2, 1), (2, 2)
]
def up_heuristic_manhattan(goal, current, parent):
	size = goal.size
	i_goal = goal.board.index(parent.taquin.board[current.taquin.pos])
	gx, gy = i_goal % size, i_goal // size
	tmp = abs(parent.x -gx) \
		+ abs(parent.y - gy)
	if tmp != current.list_heuristic[current.taquin.pos]:
		current.list_heuristic[parent.taquin.pos] = tmp
		diff = tmp - current.list_heuristic[current.taquin.pos]
		current.list_heuristic[current.taquin.pos] = 0
		return parent.heuristic + diff
	return parent.heuristic

def heuristic_badplace(goal, current):
	tt = 0
	for i, v in enumerate(current.board):
		if v == 0:
			continue
		if v != i + 1:
			tt += 1
	return tt

"""
	Represente un taquin
	board = list des numeros
"""
class Taquin:
	def __init__(self, values, size):
		self.board = [*values]
		self.size = size
		self._pos, self._x, self._y = 0, 0, 0
		self._up_pos(values.index(0))

	@property
	def pos(self):
		return self._pos
	@property
	def x(self):
		return self._x
	@property
	def y(self):
		return self._y

	def _up_pos(self, value):
		self._pos += value
		self._x = self._pos % self.size
		self._y = self._pos // self.size

	def __eq__(self, other):
		return self.board == other.board
	def __ne__(self, other):
		return self.board != other.board

	def move(self, action):
		if action == ACTIONS["N"]:
			self.board[self._pos] = self.board[self._pos - self.size]
			self._up_pos(-self.size)
		elif action == ACTIONS["S"]:
			self.board[self._pos] = self.board[self._pos + self.size]
			self._up_pos(self.size)
		elif action == ACTIONS["E"]:
			self.board[self._pos] = self.board[self._pos + 1]
			self._up_pos(1)
		elif action == ACTIONS["W"]:
			self.board[self._pos] = self.board[self._pos - 1]
			self._up_pos(-1)
		self.board[self._pos] = 0

	def __str__(self):
		r = ""
		for i, v in enumerate(self.board):
			if i != 0 and i % self.size == 0:
				r += "\n"
			r += "{}, ".format(v)
		return r

"""
	Etat en cours
"""
class State:
	pre_man = []

	def __init__(self, goal, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = copy.deepcopy(taquin)	# Current taquin
		if parent is not None:
			self.taquin.move(action)
			#self.list_heuristic = [*parent.list_heuristic]
			#self.heuristic = up_heuristic_manhattan(goal, self, parent)
			self.heuristic = init_heuristic_manhattan(State.pre_man, self.taquin)
		else:
			#self.list_heuristic = [0] * len(self.taquin.board)
			State.pre_man = [
			[abs(pos % goal.size
				- goal.board.index(tuile) % goal.size)
			+ abs(pos // goal.size
				- goal.board.index(tuile) // goal.size)
				for pos in range(len(goal.board))
			]
			for tuile in range(len(goal.board))
			]
			self.heuristic = init_heuristic_manhattan(State.pre_man, self.taquin)
		self.weight = self.cost + self.heuristic


	def transition(self, action, goal):
		return State(
			goal, self.taquin, action, self, self.cost + 1)

	# Pour le dict: hash = chaine du board en int
	def __hash__(self):
		return int("".join(map(str, self.taquin.board)))
	# Pour le tri et la comparaison
	def __lt__(self, other):
		return self.weight < other.weight
	# Pour le X in set
	def __eq__(self, other):
		return self.taquin.board == other.taquin.board

	@property
	def size(self):
		return self.taquin.size
	@property
	def x(self):
		return self.taquin.x
	@property
	def y(self):
		return self.taquin.y

	def __str__(self):
		return str(self.taquin)

def find_moves(state, goal):
	# N
	if state.y > 0 and state.action != ACTIONS["S"]:
		yield state.transition(ACTIONS["N"], goal)
	# S
	if state.y < state.size - 1 and state.action != ACTIONS["N"]:
		yield state.transition(ACTIONS["S"], goal)
	# E
	if state.x < state.size - 1 and state.action != ACTIONS["W"]:
		yield state.transition(ACTIONS["E"], goal)
	# W
	if state.x > 0 and state.action != ACTIONS["E"]:
		yield state.transition(ACTIONS["W"], goal)

def astar(start, goal):
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	init_state = State(goal, start, ACTIONS["None"], None, 0)
	open_lst.push(init_state)
	open_set[init_state] = init_state

	count_turn, count_node = 0, 0
	found = False
	found_state = None
	count_last = 0
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		del open_set[curr_state]
		close_set[curr_state] = curr_state

		found_state = curr_state
		if curr_state.taquin.board == goal.board:
			found = True
			break

		for next_state in find_moves(curr_state, goal):
			# if curr_state.weight <= next_state.weight:
			# 	print("{}".format(curr_state.weight - next_state.weight))
			if next_state in close_set:
				continue
			elif next_state in open_set:
				old = open_set[next_state]
				#print("{}, {}".format(next_state.weight, old.weight))
				if next_state < old:
					old.cost = next_state.cost
					old.heuristic = next_state.heuristic
					old.parent = next_state.parent
					old.weight = next_state.weight
					old.action = next_state.action
					# open_lst.remove(next_state)
					# open_lst.push(next_state)
					# open_set[next_state] = next_state
			else:
				open_lst.push(next_state)
				open_set[next_state] = next_state
				count_node += 1

		count_turn += 1
		if count_turn % 10000 == 0:
			print("{} turns".format(count_turn))

	print("Size: {}".format(count_last))
	if found:
		print("Success: ")
	else:
		print("Failure: ")
	print("turn = {}, nodes = {}, moves = {}".format(
			count_turn, count_node, found_state.cost))
	print()
	return 0

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
	taquin_base = Taquin(TAQUINS[BASE], int(math.sqrt(len(TAQUINS[BASE]))))
	taquin_goal = Taquin(TAQUINS[GOAL], int(math.sqrt(len(TAQUINS[GOAL]))))

	# if not solvable(taquin_base):
	# 	print("Not solvable")
	# 	return 0

	astar(taquin_base, taquin_goal)
	return 0


if __name__ == '__main__':
	sys.exit(main())
