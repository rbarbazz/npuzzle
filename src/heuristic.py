#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


"""
Ultra fast manhattan heurstic, precomputed
Admissible and monotonic -> always give best path
"""
def heuristic_manhattan(env, npuzzle):
	board = npuzzle.board
	cost = env.pre_man
	return sum([
		cost[i][board[i]]
		for i in env.len_range
	])


"""
Uniform heuristic -> Djisktra
"""
def heuristic_uniform(env, npuzzle):
	return 0

"""
Count placed tile
"""
def heuristic_hamming_good(env, npuzzle):
	board = npuzzle.board
	goal = env.goal.board
	tt = 0
	for i in env.len_range:
		if board[i] != 0 and board[i] == goal[i]:
			tt += 1
	return tt


"""
Count bad placed tile
"""
def heuristic_hamming_bad(env, npuzzle):
	board = npuzzle.board
	goal = env.goal.board
	tt = 0
	for i in env.len_range:
		if board[i] != 0 and board[i] != goal[i]:
			tt += 1
	return tt


"""

"""
def heuristic_euclidienne(env, npuzzle):
	board = npuzzle.board
	cost_euc = env.pre_euc
	return int(sum([
		cost_euc[i][board[i]]
		for i in env.len_range
	]))


"""

"""
def get_lc(env, cost, board, size, sens, step):
	lc = 0
	# For each line ri of the puzzle
	for side in env.size_range:
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


"""

"""
def heuristic_lc(env, npuzzle):
	board = npuzzle.board
	size = npuzzle.size
	cost = env.pre_lc
	lc = 0
	# Row
	lc += get_lc(env, cost, board, size, (0, 1), 1)
	# Col
	lc += get_lc(env, cost, board, size, (1, 0), size)
	# 2 * lc + manh
	return lc + lc + heuristic_manhattan(env, npuzzle)


if __name__ == '__main__':
	pass
