#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys, os
import copy
import math
from collections import deque

TAQUINS = {
	"size" : 3,
	"goal" : [
		1, 2, 3,
		8, 0, 4,
		7, 6, 5
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
	"unsolvable" : [
		5, 3, 6,
		4, 0, 8,
		2, 7, 1
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
	def __init__(self, values):
		self.board = values.copy()
		self.size = int(math.sqrt(len(values)))
		self.pos = self.board.index(0)

	@property
	def x(self):
		return self.pos % self.size
	@property
	def y(self):
		return self.pos // self.size

	def __eq__(self, other):
		return self.board == other.board

	def __str__(self):
		r = ""
		for i, v in enumerate(self.board):
			if i != 0 and i % self.size == 0:
				r += "\n"
			r += "{}, ".format(v)
		return r

	def __copy__(self):
		cpy = type(self)(self.board)
		return cpy

	def move(self, action):
		if action == ACTION["N"]:
			self.board[self.pos] = self.board[self.pos - self.size]
			self.pos -= self.size
			self.board[self.pos] = 0
		elif action == ACTION["S"]:
			self.board[self.pos] = self.board[self.pos + self.size]
			self.pos += self.size
			self.board[self.pos] = 0
		elif action == ACTION["E"]:
			self.board[self.pos] = self.board[self.pos + 1]
			self.pos += 1
			self.board[self.pos] = 0
		elif action == ACTION["W"]:
			self.board[self.pos] = self.board[self.pos - 1]
			self.pos -= 1
			self.board[self.pos] = 0

def calc_heur(taquin):
	tt = 0
	for i, v in enumerate(taquin.board):
		i_goal = TAQUINS["goal"].index(v)
		gx, gy = i_goal % 3, i_goal // 3
		tt += abs(taquin.x - gx) + abs(taquin.y - gy)
	return tt

"""
	Etat en cours
"""
class State:
	def __init__(self, taquin):
		self.__cost = 0			# +1 each step
		self.__heuristic = calc_heur(taquin)	# 0 means goal
		self.__action = -1	# ACTION
		self.__parent = None	# Ref to previous state
		self.__taquin = copy.copy(taquin)	# Current taquin after transition

	def __copy__(self):
		cpy = type(self)(self.__taquin)
		return cpy

	def transition(self, action):
		new_state = copy.copy(self)
		new_state.__action = action
		new_state.__parent = self
		# print("Before move {}:".format(action))
		# print(new_state.__taquin)
		new_state.__taquin.move(action)
		# print("After move:")
		# print(new_state.__taquin)
		# print()
		new_state.__heuristic = calc_heur(new_state.__taquin)

		return new_state

	def inc_cost(self):
		self.__cost += 1

	def __lt__(self, other):
		return self.__heuristic < other.__heuristic
	def __gt__(self, other):
		return self.__heuristic > other.__heuristic
	def __le__(self, other):
		return self.__heuristic <= other.__heuristic
	def __ge__(self, other):
		return self.__heuristic >= other.__heuristic

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

	def weight(self):
		return self.__cost + self.__heuristic

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
	final_state = State(goal)
	open_lst.append(State(start))
	found = None
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		if curr_state == final_state:
			found = curr_state
			break

		for next_state in find_moves(curr_state):
			#print(next_state)
			try:
				old_o = open_lst.index(next_state)
			except ValueError:
				old_o = None
			try:
				old_c = close_lst.index(next_state)
			except ValueError:
				old_c = None
			if (old_o is not None and open_lst[old_o].weight() < next_state.weight()) \
			or (old_c is not None and close_lst[old_c].weight() < next_state.weight()):
				pass
			else:
				next_state.inc_cost()
				open_lst.append(next_state)
			#print()
		#print("\nNew turn")
		counter += 1
		if counter % 100 == 0:
			print(counter)
		close_lst.append(curr_state)

	if found is not None:
		print("Success {}".format(counter))
	else:
		print("Failure {}".format(counter))
		return 0

	while (found.parent is not None):
		print(found)
		found = found.parent


def main():
	taquin_base = Taquin(TAQUINS["other"])
	taquin_goal = Taquin(TAQUINS["goal"])

	astar(taquin_base, taquin_goal)

	return 0

if __name__ == '__main__':
	sys.exit(main())