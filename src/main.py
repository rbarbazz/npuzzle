#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys, os
import copy
import math


# GOAL = "goal_4"
# BASE = "base_4"

GOAL = "goal_3"
BASE = "base_3_fast"


TAQUINS = {
	"goal_4" : [1, 2, 3, 4,
				5, 6, 7, 8,
				9, 10, 11, 12,
				13, 14, 15, 0],
	"goal_3" : [1, 2, 3,
				4, 5, 6,
				7, 8, 0],
	"base_4" : [12, 5, 8, 10,
				1, 15, 3, 11,
				0, 14, 2, 6,
				4, 7, 9, 13],
	"base_3_simple" : [1, 2, 3,
						4, 0, 5,
						7, 8, 6],
	#28 moves, 3598 turns, 5710 nodes, ~8.3sec
	"base_3_fast" : [4, 8, 7,
					2, 0, 6,
					3, 5, 1],
	"unsolvable" : [3, 6, 5,
					7, 2, 4,
					0, 8, 1],
}


ACTIONS = {
	"None": 4, "N" : 0, "S" : 1, "E" : 2, "W" : 3
}


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


# Take a goal and current taquin
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

	def inc_x(self):
		self._up_pos(1)
	def dec_x(self):
		self._up_pos(-1)
	def inc_y(self):
		self._up_pos(self.size)
	def dec_y(self):
		self._up_pos(-self.size)

	def __eq__(self, other):
		return self.board == other.board
	def __ne__(self, other):
		return self.board != other.board

	def move(self, action):
		if action == ACTIONS["N"]:
			self.board[self._pos] = self.board[self._pos - self.size]
			self.dec_y()
		elif action == ACTIONS["S"]:
			self.board[self._pos] = self.board[self._pos + self.size]
			self.inc_y()
		elif action == ACTIONS["E"]:
			self.board[self._pos] = self.board[self._pos + 1]
			self.inc_x()
		elif action == ACTIONS["W"]:
			self.board[self._pos] = self.board[self._pos - 1]
			self.dec_x()
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
	def __init__(self, goal, taquin, action, parent, cost):
		self.action = action	# Action performs from last state
		self.parent = parent	# Ref to previous state
		self.cost = cost		# +1 each step
		self.taquin = copy.deepcopy(taquin)	# Current taquin
		self.taquin.move(action)
		self.heuristic = heuristic_manhattan(goal, self.taquin)
		self.weight = self.cost + self.heuristic

	def transition(self, action, goal):
		new_state = type(self)(
			goal, self.taquin, action, self, self.cost + 1)
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
		return self.taquin == other.taquin
	def __ne__(self, other):
		return self.taquin != other.taquin

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

def find_in_lst(lst, item):
	for i, v in enumerate(lst):
		if item == v:
			return i, v
	return None, None

def astar(start, goal):
	open_lst = PriorityList()
	close_lst = []
	open_lst.append(State(goal, start, ACTIONS["None"], None, 0))

	count_turn, count_node = 0, 0
	found = False
	found_state = None
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		close_lst.append(curr_state)

		found_state = curr_state
		if curr_state.taquin == goal:
			found = True
			break

		for next_state in find_moves(curr_state, goal):
			try:
				old_i = close_lst.index(next_state)
			except:
				old_i = None
			if old_i is not None \
			and next_state < close_lst[old_i]:
				close_lst.pop(old_i)
				open_lst.append(next_state)
				continue

			try:
				old_i = open_lst.index(next_state)
			except:
				old_i = None
			if old_i is not None \
			and next_state < open_lst[old_i]:
				open_lst.pop(old_i)
				open_lst.append(next_state)
				continue

			open_lst.append(next_state)
			count_node += 1

		count_turn += 1
		if count_turn % 1000 == 0:
			print("{} turns".format(count_turn))

	print()
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

	if not solvable(taquin_base):
		print("Not solvable")
		return 0

	astar(taquin_base, taquin_goal)

	return 0


if __name__ == '__main__':
	sys.exit(main())
