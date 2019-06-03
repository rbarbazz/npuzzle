
	if env.verbose:
		print("Initial npuzzle:\t{}".format(n_taq))
		print("Goal npuzzle:\t\t{}".format(n_goal))
		print()

	if not solvable(npuzzle_start, npuzzle_goal):
		if env.verbose:
			print("Not solvable")
		if not CONTINUE:
			return 0

	# Ok puisqu'on garde la majorite des noeuds crees, +5-15% perf
	gc.disable()
	found = astar(env, state_start)
	gc.enable()

	if env.verbose:
		print()
		if not found:
			print("Failure :(")
		else:
			env.up_mem()
			print("Success :)")
			print(("{} moves in {} turns, {} nodes explored with a maximum of "
				"{} nodes stocked at one time."
				"\nTotal memory used: {} Mo").format(
				len(env.solution), env.stats["turns"],
				env.stats["nodes_created"], env.stats["nodes_stocked"],
				env.stats["memory"]))
		print()

#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


"""
			Benchmark on base_4_arobion
Greedy:
	Uniform: Cancelled at 9.45M of nodes (20.01M tested), 10M56 turns, 14.10Go ram
	Manhattan: 11 063 nodes, 5513 turns, 174 moves
	Linear conflicts: 746 nodes, 356 turns, 114 moves
	Custom: 746 nodes, 356 turns, 114 moves
A*:
	Uniform: Cancelled at 9.45M of nodes (20.01M tested), 10M56 turns, 14.10Go ram
	Manhattan: 229464 nodes, 119145 turns, 52 moves, 185Mo ram
	Linear conflicts: 95645 nodes, 49225 turns, 52 moves, 80Mo ram
	Custom: 746 nodes, 356 turns, 114 moves, Mo ram

For 4+ size, hamming and euclidian are very bad

Conclusion:
Greedy is ultimately fast, but gives very poor results
Uniform is super slow since it explores all cases, give best result
Other heurisitcs are fast and give the best result (with an acceptable heuristic)
We can achieve pretty good result with a custom but non acceptable heuristic
"""

"""
52 moves, 14sec à 42 (manh et linear conflicts) arobion
52 moves, 18sec à 42 chez nous (manh)
"""

"""
Maximum valid state of 3: 9! / 2 = 181 440, max moves 31
Maximum valid state of 4: 16! / 2 = 10 461 394 944 000, max moves 61 ?
"""

TAQUINS = {
	"goal_3" : [1, 2, 3, 4, 5, 6, 7, 8, 0],
	"goal_3_esca": [1, 2, 3, 8, 0, 4, 7, 6, 5],
	"goal_3_top" : [0, 1, 2, 3, 4, 5, 6, 7, 8],
	"goal_4" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0],
	"goal_4_esca": [1, 2, 3, 4, 12, 13, 14, 5, 11, 0, 15, 6, 10, 9, 8, 7],
	"goal_5_esca" : [1, 2, 3, 4, 5, 16, 17, 18, 19, 6, 15, 24, 0, 20, 7, 14,
					23, 22, 21, 8, 13, 12, 11, 10, 9],

	"base_31_top" : [8, 7, 6, 0, 4, 1, 2, 5, 3],
	"base_31_2_top" : [8, 0, 6,  5, 4, 7, 2, 3, 1],

	"base_4_arobion": [5, 4, 9, 15, 6, 2, 8, 11, 1, 12, 7, 0, 3, 13, 14, 10],
	"base_4_sub_arobion": [12, 1, 5, 4, 6, 11, 2, 15, 0, 9, 8, 7, 3, 13, 14, 10],
	"base_4_test": [5, 7, 15, 12, 0, 1, 3, 14, 6, 11, 9, 8, 2, 10, 4, 13],

	"base_5": [4, 6, 12, 19, 9, 3, 8, 20, 17, 16, 22, 18, 0, 13, 15, 5, 21, 23,
				2, 1, 24, 14, 10, 11, 7],

}
