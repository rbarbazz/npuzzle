#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys, os
import copy
import math
import heapq


GOAL = "goal_4_esca"
BASE = "base_4_arobion"

#GOAL = "goal_3_top"
#BASE = "base_31_top"

"""
52 moves, 14sec chez lui (manh et linear conflicts)
52 moves, 19sec chez nous (manh)
"""
TAQUINS = {
	"goal_3" : [1, 2, 3, 4, 5, 6, 7, 8, 0],
	"goal_3_esca": [1, 2, 3, 8, 0, 4, 7, 6, 5],
	"goal_3_top" : [0, 1, 2, 3, 4, 5, 6, 7, 8],
	"goal_4" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0],
	"goal_4_esca": [1, 2, 3, 4, 12, 13, 14, 5, 11, 0, 15, 6, 10, 9, 8, 7],

	"base_31_top" : [8, 7, 6, 0, 4, 1, 2, 5, 3],
	"base_31_2_top" : [8, 0, 6,  5, 4, 7, 2, 3, 1],

	"base_4_arobion": [5, 4, 9, 15, 6, 2, 8, 11, 1, 12, 7, 0, 3, 13, 14, 10],
	"base_4_easy": [1, 4, 5, 0, 12, 2, 15, 3, 14, 11, 7, 6, 10, 13, 9, 8],
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


def heuristic_manhattan(manhattan_cost, puzzle):
	total = 0
	# Range de 1 (on compte pas le 0) a len
	for index in range(1, len(puzzle.board)):
		total += manhattan_cost[index][puzzle.board.index(index)]
	return total

"""
	Represente un taquin
	board = list des numeros
"""
class Taquin:
	def __init__(self, values, size):
		self.board = [*values]
		self.size = size
		self.pos, self.x, self.y = 0, 0, 0
		self._up_pos(values.index(0))

	def _up_pos(self, value):
		self.pos += value
		self.x = self.pos % self.size
		self.y = self.pos // self.size

	def __eq__(self, other):
		return self.board == other.board
	def __ne__(self, other):
		return self.board != other.board

	def move(self, action):
		if action == ACTIONS["N"]:
			modif = -self.size
		elif action == ACTIONS["S"]:
			modif = self.size
		elif action == ACTIONS["E"]:
			modif = 1
		elif action == ACTIONS["W"]:
			modif = -1
		self.board[self.pos] = self.board[self.pos + modif]
		self._up_pos(modif)
		self.board[self.pos] = 0

	def __str__(self):
		r = ""
		for i, v in enumerate(self.board):
			if i != 0 and i % self.size == 0:
				r += "\n"
			r += "{}, ".format(v)
		return r

goal = Taquin(TAQUINS[GOAL], int(math.sqrt(len(TAQUINS[GOAL]))))

"""
	Etat en cours
"""
class State:
	pre_man = []

	def __init__(self, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = copy.deepcopy(taquin)	# Current taquin
		if parent is not None:
			self.taquin.move(action)
		else:
			State.pre_man = [
			[abs(pos % goal.size
				- goal.board.index(tuile) % goal.size)
			+ abs(pos // goal.size
				- goal.board.index(tuile) // goal.size)
				for pos in range(len(goal.board))
			]
			for tuile in range(len(goal.board))
			]
		self.heuristic = heuristic_manhattan(State.pre_man, self.taquin)
		self.weight = self.cost + self.heuristic


	def transition(self, action):
		return State(self.taquin, action, self, self.cost + 1)

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

def find_moves(state):
	# N
	if state.y > 0 and state.action != ACTIONS["S"]:
		yield state.transition(ACTIONS["N"])
	# S
	if state.y < state.size - 1 and state.action != ACTIONS["N"]:
		yield state.transition(ACTIONS["S"])
	# E
	if state.x < state.size - 1 and state.action != ACTIONS["W"]:
		yield state.transition(ACTIONS["E"])
	# W
	if state.x > 0 and state.action != ACTIONS["E"]:
		yield state.transition(ACTIONS["W"])

def astar(start):
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	init_state = State(start, ACTIONS["None"], None, 0)
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

		for next_state in find_moves(curr_state):
			if next_state in close_set:
				continue
			elif next_state in open_set:
				old = open_set[next_state]
				if next_state < old:
					old.cost = next_state.cost
					old.heuristic = next_state.heuristic
					old.parent = next_state.parent
					old.weight = next_state.weight
					old.action = next_state.action
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

	# if not solvable(taquin_base):
	# 	print("Not solvable")
	# 	return 0

	astar(taquin_base)
	return 0


if __name__ == '__main__':
	sys.exit(main())
