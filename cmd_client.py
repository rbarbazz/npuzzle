#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import time
import re
import signal

from npuzzle import api, parser, gen, npuzzle


def get_puzzle_from_file(file):
	lines = []
	try:
		with open(file, 'r') as f:
			while True:
				line = f.readline()
				line = re.sub(r'#.*', '', line)
				if line == '': # EOF
					break
				line = line.strip()
				if len(line):
					lines += [line]
					if len(lines) > 128:
						print("File is too big")
						return None
	except:
		print("Error while reading the file")
		return None
	if len(lines) == 0:
		return None
	# Check first line -> size
	size = lines.pop(0)
	if not size.isdigit():
		return None
	size = int(size)
	taquin = []
	for line in lines:
		taquin += line.split()
	if size * size != len(taquin):
		return None
	return taquin


def get_puzzle_from_string(raw):
	if not re.match(r'^[\s]*([0-9]+[\s]*,[\s]*)+[0-9]+[\s]*$', raw):
		return None
	taquin = raw.split(',')
	try:
		r = list(map(int, taquin))
	except:
		r = None
	return r


def signal_handler(signalnum, stackframe):
	if signalnum == signal.SIGINT:
		api.stop_solving()
		print("Solving has been stopped by user")

def int_to_move(a):
	if a == 0:
		return "U"
	if a == 1:
		return "D"
	if a == 2:
		return "R"
	if a == 3:
		return "L"

def cb_solve(args, data):
	if data["error"]:
		print(data["data"])
		return
	if args.quiet:
		return
	print("Puzzle was {} solved!".format(
		"succesfully" if data["found"] else "unsuccesfully"))
	print("Type: {}, size: {}, solvable: {}, greedy: {}, heuristic: {}".format(
		data["type"], data["size"], data["solvable"], data["greedy"],
		data["heuristic"]))
	taquin = npuzzle.make_taquin(data["npuzzle"])
	goal = npuzzle.make_taquin(data["goal"])
	if data["found"]:
		print("\nFrom:\n{}\nTo:\n{}\n".format(taquin, goal))
	else:
		print("\nNot found\n")
	print("Solved with {} moves in {}sec".format(len(data["solution"]),
		data["stats"]["time"] / 1000000))
	print("Time complexity (number of loops): {}".format(
		data["stats"]["turns"]))
	print("Space complexity (max number of nodes): {}".format(
		data["stats"]["nodes_stocked"]))
	print("Nodes explored: {}".format(data["stats"]["nodes_created"]))
	print("Memory used: {}Mo".format(int(data["stats"]["memory"])))
	if data["found"]:
		print("\nSolution: {}".format(
			", ".join(list(map(int_to_move, data["solution"])))))

def process_solve(puzzle, args):
	r = api.solve(args.type, puzzle, args.greedy, args.heuristic, args.force,
		callback=lambda data: cb_solve(args, data))
	if r["error"]:
		print(r["data"])
		return
	if not args.quiet:
		print("Puzzle is being solved...")
		if r["force"] and not r["solvable"]:
			print("You asked to force the solving even if the puzzle is not "
				"solvable!")
		if not r["force"] and not r["solvable"]:
			print("The puzzle is not solvable, I'm too lazy too compute "
				"infinity!")
	api.wait_solving()

def process_gen(args, data):
	if data["error"]:
		print(data["data"])
		return
	if args.quiet:
		return
	taquin = npuzzle.make_taquin(data["npuzzle"])
	if not args.output:
		print("Puzzle was succesfully generated!")
		print("Type: {}, size: {}, solvable: {}, iterations: {}".format(
			data["type"], data["size"], data["solvable"], data["iteration"]))
	if args.output:
		print(data["size"])
	print(taquin)
	if not args.output:
		print("Copy/Paste it: {}".format(data["npuzzle"]))


def process_check(args, data):
	if data["error"]:
		print(data["data"])
		return
	if args.quiet:
		return
	taquin = npuzzle.make_taquin(data["npuzzle"])
	print("Puzzle was succesfully checked!")
	print("Type: {}, size: {}, solvable? -> {}, ".format(
		data["type"], data["size"], data["solvable"]))
	print(taquin)


def main():
	signal.signal(signal.SIGINT, signal_handler)

	# Parse args
	args = parser.sanitize_arguments()
	if args is None:
		return 0

	# Get puzzle in list format
	if "file" in args and args.file is not None:
		puzzle = get_puzzle_from_file(args.file)
		if puzzle is not None:
			puzzle = get_puzzle_from_string(",".join(puzzle))
	elif "raw" in args and args.raw is not None:
		puzzle = get_puzzle_from_string(args.raw)
	else:
		puzzle = None
	# Dispatch actions
	if args.which == "gen":
		r = api.make_random(args.type, args.size, not args.unsolvable,
			args.iteration)
		process_gen(args, r)
	elif args.which == "check":
		r = api.check_solvability(args.type, puzzle)
		process_check(args, r)
	elif args.which == "solve":
		process_solve(puzzle, args)
	else: # Never happens !
		print("Error: wrong arguments")
		return 0

	return 0


if __name__ == '__main__':
	sys.exit(main())
