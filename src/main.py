#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import resource
import math
import heapq
import operator
from consts import *
from npuzzle_gen import make_puzzle, make_goal
from collections import OrderedDict

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
Admissible and monotonic -> always give best path
"""
def heuristic_manhattan(cost_lc, cost_manh, npuzzle):
	tmp_board = npuzzle.board
	return sum([
		cost_manh[i][tmp_board[i]]
		for i in State.board_range
	])

def heuristic_lc(cost_lc, cost_manh, npuzzle):
	board = npuzzle.board
	size = npuzzle.size
	lc = 0
	# Iterate rows
	# foreach Ri in S
	for row in range(0, size):
		# Conflit dans la ligne
		lc_row = {}
		lc_row_conflict = {}

		# foreach Tj in Ri
		for tj in range(row * size, (row + 1) * size, 1):
			if board[tj] == 0 or cost_lc[board[tj]][1] != row:
				continue
			# C(Tj, Ri)
			c_row = 0
			lc_row_conflict[tj] = []
			for c in range(row * size, (row + 1) * size, 1):
				if board[c] == 0 or cost_lc[board[tj]][1] != cost_lc[board[c]][1]:
					continue
				# Si on a un conflit de X vers X-1
				if c < tj and cost_lc[board[tj]][0] < cost_lc[board[c]][0]:
					lc_row_conflict[tj].append(c)
					c_row += 1
				elif tj < c and cost_lc[board[c]][0] < cost_lc[board[tj]][0]:
					lc_row_conflict[tj].append(c)
					c_row += 1
			lc_row[tj] = c_row

		# While there is a non zero value in C
		if len(lc_row):
			tk = max(lc_row, key=lc_row.get)
			while lc_row[tk] > 0:
				# Remove tk
				lc_row[tk] = 0
				# Pour chaque tile tj en conflit with tk, faire -1
				for tj in lc_row_conflict[tk]:
					lc_row[tj] -= 1
				lc += 1
				tk = max(lc_row, key=lc_row.get)

	# foreach Ci in S
	for col in range(0, size):
		# Conflit dans la ligne
		lc_col = {}
		lc_col_conflict = {}

		# foreach Tj in Ri
		for tj in range(col, len(board), size):
			if board[tj] == 0 or cost_lc[board[tj]][0] != col:
				continue
			# C(Tj, Ri)
			c_col = 0
			lc_col_conflict[tj] = []
			for c in range(col, len(board), size):
				if board[c] == 0 or cost_lc[board[tj]][0] != cost_lc[board[c]][0]:
					continue
				# Si on a un conflit de X vers X-1
				if c < tj and cost_lc[board[tj]][1] < cost_lc[board[c]][1]:
					lc_col_conflict[tj].append(c)
					c_col += 1
				elif tj < c and cost_lc[board[c]][1] < cost_lc[board[tj]][1]:
					lc_col_conflict[tj].append(c)
					c_col += 1
			lc_col[tj] = c_col
		# While there is a non zero value in C
		if len(lc_col):
			tk = max(lc_col, key=lc_col.get)
			while lc_col[tk] > 0:
				# Remove tk
				lc_col[tk] = 0
				# Pour chaque tile tj en conflit with tk, faire -1
				for tj in lc_col_conflict[tk]:
					lc_col[tj] -= 1
				lc += 1
				tk = max(lc_col, key=lc_col.get)

	# 2 * lc + manh
	return lc + lc + heuristic_manhattan(cost_lc, cost_manh, npuzzle)

"""
Node of the Astar
"""
class State:
	pre_man = []
	pre_lc = []
	board_range = None
	heuristic_fun = heuristic_manhattan

	def __init__(self, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = NPuzzle(taquin.board, taquin.size, taquin.pos)# Current taquin
		self.taquin.move(action)
		self.heuristic = State.heuristic_fun(
			State.pre_lc, State.pre_man, self.taquin)
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
	def __gt__(self, other):
		return self.weight > other.weight
	# Pour le X in set
	def __eq__(self, other):
		return self.board == other.board
	def __ne__(self, other):
		return self.board != other.board

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
		close_set[curr_state] = 1

		found_state = curr_state
		if not curr_state.heuristic:
			found = True
			break

		for next_state in curr_state.find_moves():
			if next_state in close_set:
				continue
			elif next_state in open_set:
				old = open_set[next_state]
				if next_state.weight < old.weight:
					old.cost = next_state.cost
					old.heuristic = next_state.heuristic
					old.weight = next_state.weight
					old.parent = next_state.parent
					old.action = next_state.action
					# rebuild = True
					# open_lst.remove(old)
					# open_lst.push(next_state)
					# open_set[next_state] = next_state
			else:
				open_lst.push(next_state)
				open_set[next_state] = next_state
				count_node += 1

		count_turn += 1
		if count_turn % 10000 == 0:
			print("{} - {} turns, {} nodes, {} Mo".format(len(open_lst), count_turn, count_node,
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
	if SIZE:
		n_goal = make_goal(SIZE)
		n_taq = make_puzzle(SIZE, solvable=True, iterations=10000)
	else:
		n_goal = TAQUINS[GOAL]
		n_taq = TAQUINS[BASE]
	print("Base: {}".format(n_taq))
	print("Goal: {}".format(n_goal))

	taquin_base = NPuzzle(n_taq, int(math.sqrt(len(n_taq))), n_taq.index(0))
	goal = NPuzzle(n_goal, int(math.sqrt(len(n_goal))), n_goal.index(0))

	State.board_range = range(0, len(goal.board))
	if HEUR == 1:
		State.heuristic_fun = heuristic_lc

	def _manh(fromm, to, board, size):
		if to == 0:
			return 0
		r = abs(fromm % size - board.index(to) % size) \
			+ abs(fromm // size - board.index(to) // size)
		return r
	State.pre_man = tuple([tuple([
			_manh(fromm, to, goal.board, goal.size)
		for to in range(0, len(goal.board))])
	for fromm in range(0, len(goal.board))])

	def _lc(pos, board, size):
		if pos == 0:
			return [99999, 99999] # Should never be picked
		r = [abs(board.index(pos) % size), abs(board.index(pos) // size)]
		return r
	State.pre_lc = tuple([
			tuple(_lc(pos, goal.board, goal.size))
		for pos in range(0, len(goal.board))
	])

	# if not solvable(taquin_base):
	# 	print("Not solvable")
	# 	return 0

	astar(taquin_base)

	return 0

# Goal
#  1,  2,  3, 4,
# 12, 13, 14, 5,
# 11,  0, 15, 6,
# 10,  9,  8, 7,

# Base
# 5,  4,  9, 15,
# 6,  2,  8, 11,
# 1, 12,  7,  0,
# 3, 13, 14, 10,

#Manh = 2 + 1 + 5 + 2 + 4 + 4 + 2 + 2 + 4 + 3 + 4 + 2 + 2 + 2 + 3 = 42
#lc = 2 * (1) = 2

# 1er ou h > min moves (m=33, lc=35)
#  5,  2,  7,  4,
#  1,  6,  9, 15,
# 12, 11,  8, 10,
#  3, 13, 14,  0,

#Manh = 1 + 0 + 5 + 0 + 4 + 3 + 4 + 1 + 3 + 4 + 1 + 1 + 2 + 2 + 2 = 33
# lc = 2 * (1) = 2

if __name__ == '__main__':
	sys.exit(main())
