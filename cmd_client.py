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


def process_solve(args, data):
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
	print("\nFrom:\n{}\nTo:\n{}\n".format(taquin, goal))
	print("Solved with {} moves in {}sec".format(len(data["solution"]),
		data["stats"]["time"] / 1000000))
	print("Time complexity (number of loops): {}".format(
		data["stats"]["turns"]))
	print("Space complexity (max number of nodes): {}".format(
		data["stats"]["nodes_stocked"]))
	print("Nodes explored: {}".format(data["stats"]["nodes_created"]))
	print("Memory used: {}Mo".format(int(data["stats"]["memory"])))

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
		process_gen(args, r)
	elif args.which == "check":
		r = api.check_solvability(args.type, puzzle)
		process_check(args, r)
	elif args.which == "solve":
		if not args.quiet:
			print("Puzzle is being solved...")
		r = api.solve(args.type, puzzle, args.greedy, args.heuristic,
			callback=lambda data: process_solve(args, data))
		api.wait_solving()
	else: # Never happens !
		print("Error: wrong arguments")
		return 0

	return 0


if __name__ == '__main__':
	sys.exit(main())
