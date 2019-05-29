#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import gc
import resource
import math
import heapq

from npuzzle_gen import make_puzzle, make_goal
from consts import *
from heuristic import *
from env import Env

"""
Possible actions
"""
UP = 0
DOWN = 1
EAST = 2
WEST = 3
NONE = 4

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
		if action == UP:
			modif = -self.size
		elif action == DOWN:
			modif = self.size
		elif action == EAST:
			modif = 1
		elif action == WEST:
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
			if i < len(self.board) - 1 and i % self.size < self.size - 1:
				r += "{}\t".format(v)
			else:
				r += "{}".format(v)
		return "".join(r)


"""
Node of the Astar
Greedy: weight = heuristic (cost is out of the equation)
Djisktra: weight = cost
"""
class State:
	env = None

	def __init__(self, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		# Current npuzzle
		self.taquin = NPuzzle(taquin.board, taquin.size, taquin.pos)
		self.taquin.move(action)
		self.heuristic = State.env.heuristic(State.env, self.taquin)
		# Cache
		self.weight = self.heuristic + (0 if State.env.greedy else self.cost)
		self.board = self.taquin.board
		self._hash = hash(str(self.board))

	def find_moves(self):
		action = self.action
		cost = self.cost + 1
		taquin = self.taquin
		moves = []
		app = moves.append
		if taquin.y > 0 and action != DOWN:
			 app(State(taquin, UP, self, cost))
		if taquin.y < taquin.size - 1 and action != UP:
			app(State(taquin, DOWN, self, cost))
		if taquin.x < taquin.size - 1 and action != WEST:
			app(State(taquin, EAST, self, cost))
		if taquin.x > 0 and action != EAST:
			app(State(taquin, WEST, self, cost))
		return moves

	# Pour le dict: hash = chaine du board en int
	def __hash__(self):
		return self._hash

	# Pour le tri et la comparaison
	def __lt__(self, other):
		if self.weight != other.weight:
			return self.weight < other.weight
		if self.heuristic != other.heuristic:
			return self.heuristic < other.heuristic
		return self.cost < other.cost

	# Pour le X in set
	def __eq__(self, other):
		return self.board == other.board


def astar(state_start):
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	open_lst.push(state_start)
	open_set[state_start] = state_start
	count_turn, count_node = 0, 1
	found = False
	curr_state = None
	while (len(open_lst) > 0):

		while True:
			try:
				curr_state = open_lst.pop()
			except:
				curr_state = None
				break
			# Si on tombe sur un marque, on le skippe et on reessaie
			if curr_state.cost == -1:
				continue
			del open_set[curr_state]
			close_set[curr_state] = 0
			break
		if curr_state is None:
			break

		if curr_state == State.env.goal:
			found = True
			break

		for next_state in curr_state.find_moves():
			if next_state in close_set:
				continue
			elif next_state in open_set:
				old = open_set[next_state]
				if next_state < old:
					# Mark it, push new and update set
					old.cost = -1
					open_lst.push(next_state)
					open_set[next_state] = next_state
			else:
				open_lst.push(next_state)
				open_set[next_state] = next_state
				count_node += 1

		count_turn += 1
		if count_turn % 10000 == 0:
			print("{} - {} turns, {} nodes, {} Mo".format(
				len(open_lst), count_turn, count_node,
				int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
			))

	if found:
		print("Success: ")
	else:
		print("Failure: ")
	print("turn = {}, nodes = {}, moves = {}".format(
			count_turn, count_node, 0 if curr_state is None else curr_state.cost))
	print()
	return 0


def count_inversion(base, goal):
	tt_inv = 0
	for i in range(0, len(base.board) - 1):
		if base.board[i] == 0:
			continue
		for j in range(i + 1, len(base.board)):
			if base.board[j] == 0:
				continue
			if goal.board.index(base.board[j]) < goal.board.index(base.board[i]):
				tt_inv += 1
	return tt_inv


"""
If multiple of 4 -> return even if y % 2 else not even
else if multiple of 2-> return not even if y % 2 else even
else if odd -> return even
"""
def solvable(puzzle, goal):
	even = count_inversion(puzzle, goal) % 2 == 0
	if puzzle.size % 4 == 0:
		if puzzle.y % 2 == 0:
			return even
		else:
			return not even
	elif puzzle.size % 2 == 0:
		if puzzle.y % 2 == 0:
			return not even
		else:
			return even
	return even


def main():
	if SIZE:
		n_goal = make_goal(SIZE)
		n_taq = make_puzzle(SIZE, solvable=SOLVABLE, iterations=ITERATIONS)
	else:
		n_goal = TAQUINS[GOAL]
		n_taq = TAQUINS[BASE]
	print("Base: {}".format(n_taq))
	print("Goal: {}".format(n_goal))

	npuzzle_start = NPuzzle(n_taq, int(math.sqrt(len(n_taq))), n_taq.index(0))
	npuzzle_goal = NPuzzle(n_goal, int(math.sqrt(len(n_goal))), n_goal.index(0))

	if HEUR == 0:
		heuristic = heuristic_uniform
	elif HEUR == 1:
		heuristic = heuristic_manhattan
	elif HEUR == 2:
		heuristic = heuristic_lc
	elif HEUR == 3:
		heuristic = heuristic_hamming_bad
	elif HEUR == 4:
		heuristic = heuristic_hamming_good
	elif HEUR == 5:
		heuristic = heuristic_euclidienne
	else:
		heuristic = heuristic_manhattan

	State.env = Env(npuzzle_goal, heuristic, GREEDY)
	state_start = State(npuzzle_start, NONE, None, 0)

	if not solvable(npuzzle_start, npuzzle_goal):
		print("Not solvable")
		if not CONTINUE:
			return 0

	# Ok puisqu'on garde la majorite des noeuds crees, +5-15% perf
	gc.disable()
	astar(state_start)
	gc.enable()
	return 0


if __name__ == '__main__':
	sys.exit(main())
