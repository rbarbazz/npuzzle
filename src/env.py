#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import math


def precalc_manhattan(goal):
	def _manh(fromm, to, board, size):
		if to == 0:
			return 0
		r = abs(fromm % size - board.index(to) % size) \
			+ abs(fromm // size - board.index(to) // size)
		return r
	return tuple([tuple([
				_manh(fromm, to, goal.board, goal.size)
			for to in range(0, len(goal.board))])
		for fromm in range(0, len(goal.board))])


def precalc_euclidian(goal):
	def _euc(fromm, to, board, size):
		if to == 0:
			return 0.0
		r = math.sqrt((fromm % size - board.index(to) % size) ** 2 \
			+ (fromm // size - board.index(to) // size) ** 2)
		return r
	return tuple([tuple([
				_euc(fromm, to, goal.board, goal.size)
			for to in range(0, len(goal.board))])
		for fromm in range(0, len(goal.board))])


def precalc_linear_conflicts(goal):
	def _lc(pos, board, size):
		if pos == 0:
			return [9999, 9999] # Should never be picked
		r = [abs(board.index(pos) % size), abs(board.index(pos) // size)]
		return r
	return tuple([
				tuple(_lc(pos, goal.board, goal.size))
			for pos in range(0, len(goal.board))
		])


class Env:
	def __init__(self, p_npuzzle, p_heuristic, p_greedy):
		self.goal = p_npuzzle
		self.len_range = range(0, len(self.goal.board))
		self.size_range = range(0, self.goal.size)
		self.greedy = p_greedy
		self.heuristic = p_heuristic
		self.pre_man = precalc_manhattan(self.goal)
		self.pre_lc = precalc_linear_conflicts(self.goal)
		self.pre_euc = precalc_euclidian(self.goal)


if __name__ == '__main__':
	pass
