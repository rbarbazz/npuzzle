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
		1, 5, 3,
		4, 0, 7,
		6, 2, 8
	],
	"hard" : [
		7, 5, 3,
		4, 8, 1,
		0, 6, 2
	]
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
		self.board = values
		self.size = int(math.sqrt(len(values)))
		self.pos = self.board.index(0)

	@property
	def x(self):
		return self.pos % self.size
	@property
	def y(self):
		return self.pos / self.size

	def __eq__(self, other):
		return self.board == other.board



	def __copy__(self):
		cpy = type(self)(self.board)
		return cpy

	def move(self, action):
		new_taquin = copy.copy(self)
		if action == ACTION["N"]:
			self.board[self.pos] = self.board[self.pos - self.size]
			self.board[self.pos - self.size] = 0
		if action == ACTION["S"]:
			self.board[self.pos] = self.board[self.pos + self.size]
			self.board[self.pos + self.size] = 0
		if action == ACTION["E"]:
			self.board[self.pos] = self.board[self.pos + 1]
			self.board[self.pos + 1] = 0
		if action == ACTION["W"]:
			self.board[self.pos] = self.board[self.pos - 1]
			self.board[self.pos - 1] = 0
		return new_taquin

"""
	Etat en cours
"""
class State:
	def __init__(self, taquin):
		self.__cost = 0			# +1 each step
		self.__heuristic = 0	# 0 means goal
		self.__transition = -1	# ACTION
		self.__parent = None	# Ref to previous state
		self.__taquin = copy.copy(taquin)	# Current taquin after transition
		self.__pos = taquin.board.index(0)

	def __copy__(self):
		cpy = type(self)(self.__taquin)
		cpy.__dict__.update(self.__dict__)
		return cpy

	def transition(self, action):
		new_state = copy.copy(self)
		new_state.__cost += 1
		new_state.__transition = action
		new_state.__parent = self

		new_state.__taquin.move(action)
		new_state.__heuristic = 0

		return new_state

	def __lt__(self, other):
		return self.__heuristic < other.heuristic
	def __gt__(self, other):
		return self.__heuristic > other.heuristic
	def __le__(self, other):
		return self.__heuristic <= other.heuristic
	def __ge__(self, other):
		return self.__heuristic >= other.heuristic

	def __eq__(self, other):
		return self.__taquin == other.__taquin
	def __ne__(self, other):
		return self.__taquin != other.__taquin

	@property
	def parent(self):
		return self.__parent

	@property
	def pos(self):
		return [self.x, self.y]
	@property
	def size(self):
		return self.__taquin.size
	@property
	def x(self):
		return self.__pos % self.__taquin.size
	@property
	def y(self):
		return self.__pos / self.__taquin.size

	@property
	def taquin(self):
		return self.__parent

	@property
	def weight(self):
		return self.__cost + self.__heuristic

	@property
	def heuristic(self):
		return self.__cost + self.__heuristic

	def __str__(self):
		return str(self.__cost)

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
	if state.y > 0:
		yield state.transition(ACTION["N"])
	# S
	if state.y < state.size:
		yield state.transition(ACTION["S"])
	# E
	if state.x < state.size:
		yield state.transition(ACTION["E"])
	# W
	if state.x > 0:
		yield state.transition(ACTION["W"])

def astar(start, goal):
	open_lst = PriorityList()
	close_lst = []

	final_state = State(goal)
	open_lst.append(State(start))
	found = False
	while (len(open_lst) > 0):
		curr_state = open_lst.pop()
		if curr_state == final_state:
			found = True
			break

		for next_state in find_moves(curr_state):
			pass

	if found:
		print("Success")
	else:
		print("Failure")


def main():
	taquin_base = Taquin(TAQUINS["simple"])
	taquin_goal = Taquin(TAQUINS["goal"])

	astar(taquin_base, taquin_goal)

	return 0

if __name__ == '__main__':
	sys.exit(main())