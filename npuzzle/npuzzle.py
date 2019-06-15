#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import signal
import gc
import math
import heapq
from datetime import datetime

from .heuristic import *
from .env import Env, get_mem_usage


TYPES_LIST = ["snale", "linear"]
RUNNING = False

"""
Possible actions
"""
UP = 0
DOWN = 1
EAST = 2
WEST = 3
NONE = 4
DELETE = 5

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

	def __init__(self, taquin, action, parent, cost, env):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		# Current npuzzle
		self.taquin = NPuzzle(taquin.board, taquin.size, taquin.pos)
		self.taquin.move(action)
		self.heuristic = env.heuristic(env, self.taquin)
		# Cache
		self.weight = self.heuristic + (0 if env.greedy else self.cost)
		self.board = self.taquin.board
		self._hash = hash(str(self.board))

	def find_moves(self, env):
		action = self.action
		cost = self.cost + 1
		taquin = self.taquin
		moves = []
		app = moves.append
		if taquin.y > 0 and action != DOWN:
			 app(State(taquin, UP, self, cost, env))
		if taquin.y < taquin.size - 1 and action != UP:
			app(State(taquin, DOWN, self, cost, env))
		if taquin.x < taquin.size - 1 and action != WEST:
			app(State(taquin, EAST, self, cost, env))
		if taquin.x > 0 and action != EAST:
			app(State(taquin, WEST, self, cost, env))
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


def astar(env, state_start):
	global RUNNING
	gc.disable()
	open_lst = PriorityQueue()
	open_set = {}
	close_set = {}
	open_lst.push(state_start)
	open_set[state_start] = state_start
	found = False
	curr_state = None
	env.up_mem()
	while (len(open_lst) > 0 and RUNNING):
		while True:
			try:
				curr_state = open_lst.pop()
			except:
				curr_state = None
				break
			# Si on tombe sur un marque, on le skippe et on reessaie
			if curr_state.action == DELETE:
				continue
			del open_set[curr_state]
			close_set[curr_state] = 0
			break
		if curr_state is None:
			break

		if curr_state == env.goal:
			found = True
			break

		for next_state in curr_state.find_moves(env):
			if next_state in close_set:
				continue
			elif next_state in open_set:
				old = open_set[next_state]
				if next_state < old:
					# Mark it, push new and update set
					old.action = DELETE
					open_lst.push(next_state)
					open_set[next_state] = next_state
			else:
				open_lst.push(next_state)
				open_set[next_state] = next_state
				env.stats["nodes_created"] += 1

		env.stats["turns"] += 1
		if env.stats["turns"] % 1000 == 0:
			env.up_mem()
		if len(open_lst) > env.stats["nodes_stocked"]:
			env.stats["nodes_stocked"] = len(open_lst)

		if env.verbose and env.stats["turns"] % 5000 == 0:
			print("\rTurn: {} \tNodes: {} \tRAM Mo: {}".format(
				env.stats["turns"], env.stats["nodes_created"],
				env.stats["memory"]
			), end='')

	if env.verbose:
		print()

	# Store solution
	if found:
		while curr_state.parent is not None:
			env.solution.append(curr_state)
			curr_state = curr_state.parent
		env.solution.reverse()

	gc.enable()
	return found


def make_taquin(npuzzle_input):
	return NPuzzle(npuzzle_input, int(math.sqrt(len(npuzzle_input))),
		npuzzle_input.index(0))


def solve(npuzzle, goal, greedy, heuristic):
	global RUNNING
	RUNNING = True
	npuzzle_start = NPuzzle(npuzzle, int(math.sqrt(len(npuzzle))),
		npuzzle.index(0))
	npuzzle_goal = NPuzzle(goal, int(math.sqrt(len(goal))), goal.index(0))
	if heuristic not in globals():
		RUNNING = False
		return None
	tmp_heuristic = globals()[heuristic]

	env = Env(npuzzle_goal, tmp_heuristic, greedy, False)
	state_start = State(npuzzle_start, NONE, None, 0, env)

	start_time = datetime.now()
	found = astar(env, state_start)
	env.stats["time"] = datetime.now().microsecond - start_time.microsecond

	list_moves = [state.action for state in env.solution]
	result = {"solution": list_moves, "stats": env.stats, "found": found}
	RUNNING = False
	return result
