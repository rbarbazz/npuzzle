#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import resource
import math
import heapq
from consts import *
from npuzzle_gen import make_puzzle, make_goal

"""
Possible actions
"""
ACTIONS = {
	"N": 0, "S": 1, "E": 2, "W": 3, "NONE": 4
}

"""
Ultra fast priority queue (binary heap with heapq)
"""
class PriorityQueue(list):
	def __init__(self, *args):
		list.__init__(self, *args)
		self.heappush = heapq.heappush
		self.heappop = heapq.heappop

	def push(self, item):
		self.heappush(self, item)

	def pop(self):
		return self.heappop(self)

"""
Ultra fast and compact npuzzle
"""
class NPuzzle:
	def __init__(self, values, size, pos):
		self.board = [*values]
		self.size = size
		self.pos = pos
		self.x = pos % size
		self.y = pos // size

	def move(self, action):
		if action == ACTIONS["N"]:
			modif = -self.size
		elif action == ACTIONS["S"]:
			modif = self.size
		elif action == ACTIONS["E"]:
			modif = 1
		elif action == ACTIONS["W"]:
			modif = -1
		else:
			modif = 0
		self.board[self.pos] = self.board[self.pos + modif]
		self.pos += modif
		self.x = self.pos % self.size
		self.y = self.pos // self.size
		self.board[self.pos] = 0

	def __eq__(self, other):
		return self.board == other.board
	def __ne__(self, other):
		return self.board != other.board

	def __str__(self):
		r = []
		for i, v in enumerate(self.board):
			if i != 0 and i % self.size == 0:
				r += "\n"
			r += "{}, ".format(v)
		return "".join(r)


"""
Ultra fast manhattan heurstic, precomputed
"""
def heuristic_manhattan(cost_manh, npuzzle):
	tmp_board = npuzzle.board
	return sum([
		cost_manh[i][tmp_board[i]]
		for i in State.board_range
	])


"""
Node of the Astar
"""
class State:
	pre_man = []
	board_range = None

	def __init__(self, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = NPuzzle(taquin.board, taquin.size, taquin.pos)# Current taquin
		self.taquin.move(action)
		self.heuristic = heuristic_manhattan(State.pre_man, self.taquin)
		# Cache
		self.weight = self.cost + self.heuristic
		self.board = self.taquin.board
		self._hash = hash(str(self.board))

	def find_moves(self):
		action = self.action
		cost = self.cost + 1
		taquin = self.taquin
		moves = []
		app = moves.append
		if taquin.y > 0 and action != ACTIONS["S"]:
			 app(State(taquin, ACTIONS["N"], self, cost))
		if taquin.y < taquin.size - 1 and action != ACTIONS["N"]:
			app(State(taquin, ACTIONS["S"], self, cost))
		if taquin.x < taquin.size - 1 and action != ACTIONS["W"]:
			app(State(taquin, ACTIONS["E"], self, cost))
		if taquin.x > 0 and action != ACTIONS["E"]:
			app(State(taquin, ACTIONS["W"], self, cost))
		return moves

	# Pour le dict: hash = chaine du board en int
	def __hash__(self):
		return self._hash
	# Pour le tri et la comparaison
	def __lt__(self, other):
		return self.weight < other.weight
	# Pour le X in set
	def __eq__(self, other):
		return self.board == other.board

def astar(start):
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	init_state = State(start, ACTIONS["NONE"], None, 0)
	open_lst.push(init_state)
	open_set[init_state] = init_state

	count_turn, count_node = 0, 0
	found = False
	found_state = None
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		del open_set[curr_state]
		close_set[curr_state] = curr_state

		found_state = curr_state
		if not curr_state.heuristic:
			found = True
			break

		for next_state in curr_state.find_moves():
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
			print("{} turns, {} nodes, {} Mo".format(count_turn, count_node,
				int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)))

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
	n_goal = make_goal(SIZE)
	# n_goal = TAQUINS["goal_4_esca"]
	goal = NPuzzle(n_goal, int(math.sqrt(len(n_goal))), n_goal.index(0))

	n_taq = make_puzzle(SIZE, solvable=True, iterations=10000)
	# n_taq = TAQUINS["base_4_arobion"]
	taquin_base = NPuzzle(n_taq, int(math.sqrt(len(n_taq))), n_taq.index(0))

	State.board_range = range(0, len(goal.board))

	def _manh(fromm, to, board, size):
		if to == 0:
			return 0
		r = abs(fromm % size - board.index(to) % size) \
			+ abs(fromm // size - board.index(to) // size)
		return r
	State.pre_man = [[
			_manh(fromm, to, goal.board, goal.size)
		for to in range(0, len(goal.board))]
	for fromm in range(0, len(goal.board))]




	# if not solvable(taquin_base):
	# 	print("Not solvable")
	# 	return 0

	astar(taquin_base)
	return 0


if __name__ == '__main__':
	sys.exit(main())
