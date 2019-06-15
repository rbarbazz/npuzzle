#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import time
import re
import signal

from npuzzle import api, parser, gen, npuzzle


def get_puzzle_from_file(file):
	with open(file, 'r') as taquin_file:
		line = ''
		while line == '': # Get size
			line = re.sub(r'#.*', '', taquin_file.readline()).strip()
		if line.isdigit() :
			size = int(line)
		else:
			raise Exception('Wrong input file formatting')
		taquin = []
		for line in taquin_file:
			line = re.sub(r'#.*', '', line.strip())
			if line == '':
				continue
			splitted = line.split()
			if len(splitted) == size and re.match(r'^[\d\s]+$', line):
				taquin.append(list(map(int, splitted)))
			else:
				raise Exception('Wrong input file formatting')
			if len(taquin) > size:
				raise Exception('Wrong input file formatting')
	return [col for line in taquin for col in line]


def get_puzzle_from_string(raw):
	if not re.match(r'^[\d\s\,]+$', raw):
		return None
	taquin = raw.split(',')
	return list(map(int, taquin))


def signal_handler(signalnum, stackframe):
	if signalnum == signal.SIGINT:
		api.stop_solving()
		print("Solving has been stopped by user")


def callback(data):
	print("Solver has finished !")
	print(data)


def main():
	signal.signal(signal.SIGINT, signal_handler)

	# Parse args
	args = parser.sanitize_arguments()

	# Get puzzle in list format
	if "file" in args and args.file is not None:
		puzzle = get_puzzle_from_file(args.file)
	elif "raw" in args and args.raw is not None:
		puzzle = get_puzzle_from_string(args.raw)
	else:
		puzzle = None

	# Dispatch actions
	if args.which == "gen":
		r = api.make_random(args.type, args.size, not args.unsolvable,
			args.iteration)
		print(r)
	elif args.which == "check":
		r = api.check_solvability(args.type, puzzle)
		print(r)
	elif args.which == "solve":
		print("Puzzle is being solved...")
		r = api.solve(args.type, puzzle, args.greedy, args.heuristic,
			callback=callback)
		api.wait_solving()
	else: # Never happens !
		print("Error: wrong arguments")
		return 0

	return 0


if __name__ == '__main__':
	sys.exit(main())
