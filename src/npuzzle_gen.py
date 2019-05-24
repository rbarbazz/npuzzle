#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import gc
import resource
import math
import heapq
from consts import *
from npuzzle_gen import make_puzzle, make_goal


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

def get_lc(cost, board, size, sens, step):
	lc = 0
	# For each line ri of the puzzle
	for side in range(0, size):
		conflict_lst = {}
		conflict_count = {}
		if step == 1: # Row
			start_range = side * size
		else:
			start_range = side
		# For each block tj in ri
		# tj = pos in the puzzle
		for tj in range(start_range, start_range + step * size, step):
			# If we are on the cursor, or a block from another goal, do nothing
			if board[tj] == 0 or cost[board[tj]][sens[1]] != side:
				continue
			# First time we see this block, init
			conflict_lst[tj] = []
			conflict_count[tj] = 0
			# For each block tk < tj
			for tk in range(start_range, tj, step):
				# If we are on the cursor, or a block from another goal
				if board[tk] == 0 or cost[board[tk]][sens[1]] != side:
					continue
				# If cost[tk] > cost[tj] and tk < tj => conflict
				if cost[board[tk]][sens[0]] > cost[board[tj]][sens[0]]:
					conflict_lst[tj].append(tk)
					conflict_count[tj] += 1
					conflict_lst[tk].append(tj)
					conflict_count[tk] += 1

		if len(conflict_lst):
			# While their are conflicts, take the biggest
			tk = max(conflict_count, key=conflict_count.get)
			while conflict_count[tk] > 0:
				# Remove tk
				conflict_count[tk] = 0
				# For each conflict with tk (left and right)
				for c in conflict_lst[tk]:
					conflict_count[c] -= 1
				# Inc linear conflicts
				lc += 1
				tk = max(conflict_count, key=conflict_count.get)
	return lc


def heuristic_lc(cost, cost_manh, npuzzle):
	board = npuzzle.board
	size = npuzzle.size
	lc = 0
	# Row
	lc += get_lc(cost, board, size, (0, 1), 1)
	# Col
	lc += get_lc(cost, board, size, (1, 0), size)
	# 2 * lc + manh
	return lc + lc + heuristic_manhattan(cost, cost_manh, npuzzle)


"""
Uniform heuristic -> Djisktra
"""
def heuristic_uniform(cost, cost_manh, npuzzle):
	return 0


"""
Node of the Astar
Greedy: weight = heuristic (cost is out of the equation)
Djisktra: weight = cost
"""
class State:
	pre_man = []
	pre_lc = []
	board_range = None
	heuristic_fun = heuristic_manhattan
	greedy = False

	def __init__(self, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = NPuzzle(taquin.board, taquin.size, taquin.pos)# Current taquin
		self.taquin.move(action)
		self.heuristic = State.heuristic_fun(
			State.pre_lc, State.pre_man, self.taquin)
		# Cache
		self.weight = self.heuristic + (0 if State.greedy else self.cost)
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
		# return self.weight < other.weight

	# Pour le X in set
	def __eq__(self, other):
		return self.board == other.board


def astar(start, goal):
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	init_state = State(start, NONE, None, 0)
	open_lst.push(init_state)
	open_set[init_state] = init_state
	count_turn, count_node = 0, 1
	found = False
	curr_state = None
	while (len(open_lst) > 0):
		# Check empty
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
			close_set[curr_state] = True
			break

		if curr_state is None:
			break
		# if not curr_state.heuristic:
		if curr_state.board == goal.board:
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
If puzzle is odd:
	- Return True if inversion are even
If puzzle is even:
	- Return True if cursor is on even row from bottom and inversion is odd
	- Return True if cursor is on odd row from bottom and inversion is even
Return False in any other cases
"""
def solvable(puzzle, goal):
	even = count_inversion(puzzle, goal) % 2 == 0
	if puzzle.size % 2 == 0:
		if (puzzle.size - puzzle.y) % 2 == 0:
			return even
		else:
			return not even
	return even

def main():
	if SIZE:
		n_goal = make_goal(SIZE)
		n_taq = make_puzzle(SIZE, solvable=True, iterations=1000)
	else:
		n_goal = TAQUINS[GOAL]
		n_taq = TAQUINS[BASE]
	print("Base: {}".format(n_taq))
	print("Goal: {}".format(n_goal))

	taquin_base = NPuzzle(n_taq, int(math.sqrt(len(n_taq))), n_taq.index(0))
	goal = NPuzzle(n_goal, int(math.sqrt(len(n_goal))), n_goal.index(0))

	State.board_range = range(0, len(goal.board))
	if HEUR == 0:
		State.heuristic_fun = heuristic_uniform
	elif HEUR == 1:
		State.heuristic_fun = heuristic_manhattan
	elif HEUR == 2:
		State.heuristic_fun = heuristic_lc
	elif HEUR == 3:
		State.heuristic_fun = heuristic_lc
	State.greedy = GREEDY

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
			return [9999, 9999] # Should never be picked
		r = [abs(board.index(pos) % size), abs(board.index(pos) // size)]
		return r
	State.pre_lc = tuple([
			tuple(_lc(pos, goal.board, goal.size))
		for pos in range(0, len(goal.board))
	])

	if not solvable(taquin_base, goal):
		print("Not solvable")
		return 0

	# Ok puisqu'on garde la majorite des noeuds cree +5-15% perf
	gc.disable()
	astar(taquin_base, goal)
	gc.enable()
	return 0


if __name__ == '__main__':
	sys.exit(main())
