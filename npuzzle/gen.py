#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


import random


__all__ = ["gen_goal", "gen_random", "solvable"]


def gen_snale(size, length):
	goal = [-1] * (size * size)
	tile = {"v": 1}
	i = 0

	def _fillit(goal, tile, src, dest, step):
		for k in range(src, dest, step):
			goal[k] = tile["v"]
			tile["v"] += 1

	while tile["v"] < length:
		# Top row
		_fillit(goal, tile, i * size + i, (i + 1) * size - i, 1)
		# Right col
		_fillit(goal, tile, (size - 1 - i) + (i + 1) * size,
			(size - 1 - i) + (size - (i + 1)) * size, size)
		# Bottom row
		_fillit(goal, tile, (size - i) * size - i - 1,
			(size - i - 1) * size + i - 1, -1)
		# Left col
		_fillit(goal, tile, i + (size - (i + 2)) * size,
			i + (i + 1) * size - 1, -size)
		# Next snale layer
		i += 1

	if -1 in goal:
		r = goal.index(-1)
	elif length in goal:
		r = goal.index(length)
	else:
		return None
	goal[r] = 0
	return goal


def gen_linear(size, length):
	goal = [x for x in range(1, length + 1)]
	goal[goal.index(length)] = 0
	return goal


def gen_goal(ntype, size):
	if size < 2:
		return None
	length = size * size
	if ntype == "snale":
		return gen_snale(size, length)
	elif ntype == "linear":
		return gen_linear(size, length)
	return None


UP = 0
DOWN = 1
EAST = 2
WEST = 3

def get_moves(npuzzle, size, pos, last):
	moves = []
	y = pos // size
	x = pos % size
	if y > 0 and last != DOWN:
		moves.append(UP)
	if y < size - 1 and last != UP:
		moves.append(DOWN)
	if x < size - 1 and last != WEST:
		moves.append(EAST)
	if x > 0 and last != EAST:
		moves.append(WEST)
	return moves

def move(npuzzle, size, pos, last):
	if last == UP:
		r = pos - size
	elif last == DOWN:
		r = pos + size
	elif last == EAST:
		r = pos + 1
	elif last == WEST:
		r = pos - 1
	npuzzle[pos], npuzzle[r] = npuzzle[r], 0

def gen_random(ntype, size, iterations, solvable):
	npuzzle = gen_goal(ntype, size)
	if npuzzle is None:
		return None
	random.seed()
	# Works for bottom linear and snale
	if not solvable:
		npuzzle[0], npuzzle[1] = npuzzle[1], npuzzle[0]
	last = -1
	for i in range(0, iterations):
		pos = npuzzle.index(0)
		moves = get_moves(npuzzle, size, pos, last)
		last = random.choice(moves)
		move(npuzzle, size, pos, last)
	return npuzzle


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
def solvable(ntype, puzzle, goal):
	even = count_inversion(puzzle, goal) % 2 == 0
	if ntype == "snale":
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
	elif ntype == "linear":
		if puzzle.size % 2 == 0:
			if puzzle.y % 2 == 0:
				return not even
			else:
				return even
		return even
	return False
