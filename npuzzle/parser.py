#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


import argparse
import sys
import re
import math
from .heuristic import get_available_heuristics

VALID_ACTIONS = ["gen", "import", "solve"]
VALID_TYPES = ["snale", "linear"]

def sanitize_arguments():
	parser = argparse.ArgumentParser(description='NPuzzle solver')
	subparsers = parser.add_subparsers()

	# Sub commands
	parsers = {
		key: subparsers.add_parser(key) for key in VALID_ACTIONS
	}

	# Common parameters
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", action="store_true", default=False,
		help="Print output")
	group.add_argument("-q", "--quiet", action="store_true", default=True,
		help="No output")
	# Type of npuzzle
	parser.add_argument("-t", "--type", type=str,
		help="Type of npuzzle: {}".format(", ".join(VALID_TYPES)))

	# Arguments
	parsers["gen"].add_argument("-u", "--unsolvable", action="store_true",
		help="The npuzzle generated must be unsolvable")
	parsers["gen"].add_argument("-s", "--size", type=int,
		help="The dimension of the npuzzle")
	parsers["gen"].add_argument("-i", "--iteration", type=int, default=5000,
		help="Number of iterations to shuffle the npuzzle")

	# parser.add_argument("-h", "--heuristic", type=str, default="manhattan",
	# 	help="Number of iterations to shuffle the npuzzle")
	# parser.add_argument("-i", "--iteration", type=int, default=5000,
	# 	help="Number of iterations to shuffle the npuzzle")




	args = parser.parse_args()


# ARGUMENTS = {
# 	'base': [],
# 	'goal': [],
# 	'size': 0,
# 	'greedy': False,
# 	'solvable': True,
# 	'iterations': 3000
# }

# def parser():
# 	parser = argparse.ArgumentParser(description='Solve a NPuzzle')
# 	group = parser.add_mutually_exclusive_group(required=True)
# 	group.add_argument('-f', default='', help='Read a NPuzzle from a file', dest='filename')
# 	group.add_argument('-c', default='', help='Input NPuzzle as a string of numbers separated by spaces', dest='taquin')
# 	group.add_argument('-s', type=int, default=0, help='Provide a size to generate a taquin', dest='size')
# 	parser.add_argument('-H', type=int, choices=range(6) , help='Specifiy heuristic to use [uniform, manhattan, lc, hamming_bad, hamming_good, euclidienne]', default=1)
# 	parser.add_argument('-g', action='store_true', default=False, dest='greedy', help='Greedy mode')
# 	parser.add_argument('-n', action='store_true', default=False, dest='visu', help='GUI mode')
# 	parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Verbose mode')
# 	args = parser.parse_args()

# 	try:
# 		if args.filename != '':
# 			with open(args.filename, 'r') as taquin_file:
# 				line = ''
# 				while line == '': # Get size
# 					line = re.sub(r'#.*', '', taquin_file.readline()).strip()
# 				if line.isdigit() :
# 					size = int(line)
# 				else:
# 					raise Exception('Wrong input file formatting')

# 				taquin = []
# 				for line in taquin_file:
# 					line = re.sub(r'#.*', '', line.strip())
# 					if line == '':
# 						continue
# 					splitted = line.split()
# 					if len(splitted) == size and re.match(r'^[\d\s]+$', line):
# 						taquin.append(list(map(int, splitted)))
# 					else:
# 						raise Exception('Wrong input file formatting')
# 					if len(taquin) > size:
# 						raise Exception('Wrong input file formatting')
# 			ARGUMENTS['base'] = [col for line in taquin for col in line]
# 			ARGUMENTS['goal'] = make_goal(size)

# 		if args.taquin != '':
# 			if not re.match(r'^[\d\s\,]+$', args.taquin):
# 				raise Exception('Wrong input string formatting')
# 			taquin = args.taquin.split(',')
# 			size = math.sqrt(len(taquin))
# 			if size ** 2 != len(taquin):
# 				raise Exception('Wrong input string formatting')
# 			ARGUMENTS['base'] = list(map(int, taquin))
# 			ARGUMENTS['goal'] = make_goal(size)
# 	except Exception as e:
# 		print(e)
# 		sys.exit()

# 	ARGUMENTS['size'] = args.size
# 	ARGUMENTS['heur'] = args.H
# 	ARGUMENTS['greedy'] = args.greedy
# 	ARGUMENTS['solvable'] = True
# 	ARGUMENTS['iterations'] = 3000
