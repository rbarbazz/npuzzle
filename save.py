
	parser()
	if ARGUMENTS['size']:
		n_goal = make_goal(ARGUMENTS['size'])
		n_taq = make_puzzle(ARGUMENTS['size'], solvable=ARGUMENTS['solvable'], iterations=ARGUMENTS['iterations'])
	else:
		n_goal = ARGUMENTS['goal']
		n_taq = ARGUMENTS['base']

	npuzzle_start = NPuzzle(n_taq, int(math.sqrt(len(n_taq))), n_taq.index(0))
	npuzzle_goal = NPuzzle(n_goal, int(math.sqrt(len(n_goal))), n_goal.index(0))

	if ARGUMENTS['heur'] == 0:
		heuristic = heuristic_uniform
	elif ARGUMENTS['heur'] == 1:
		heuristic = heuristic_manhattan
	elif ARGUMENTS['heur'] == 2:
		heuristic = heuristic_lc
	elif ARGUMENTS['heur'] == 3:
		heuristic = heuristic_hamming_bad
	elif ARGUMENTS['heur'] == 4:
		heuristic = heuristic_hamming_good
	elif ARGUMENTS['heur'] == 5:
		heuristic = heuristic_euclidienne
	else:
		heuristic = heuristic_manhattan

	env = Env(npuzzle_goal, heuristic, ARGUMENTS['greedy'], True)
	State.env = env
	state_start = State(npuzzle_start, NONE, None, 0)


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