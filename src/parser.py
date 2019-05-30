import argparse
import sys
import re
import math
from npuzzle_gen import make_goal

ARGUMENTS = {
	'base': [],
	'goal': [],
	'size': 0,
	'greedy': False,
	'solvable': True,
	'iterations': 3000 
}

def parser():
	parser = argparse.ArgumentParser(description='Solve a NPuzzle')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-f', default='', help='Read a NPuzzle from a file', dest='filename')
	group.add_argument('-c', default='', help='Input NPuzzle as a string of numbers separated by spaces', dest='taquin')
	group.add_argument('-s', type=int, default=0, help='Provide a size to generate a taquin', dest='size')
	parser.add_argument('-H', type=int, choices=range(6) , help='Specifiy heuristic to use [uniform, manhattan, lc, hamming_bad, hamming_good, euclidienne]', default=1)
	parser.add_argument('-g', action='store_true', default=False, dest='greedy', help='Greedy mode')
	parser.add_argument('-n', action='store_true', default=False, dest='visu', help='GUI mode')
	parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Verbose mode')
	args = parser.parse_args()

	try:
		if args.filename != '':
			with open(args.filename, 'r') as taquin_file:
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
			ARGUMENTS['base'] = [col for line in taquin for col in line]
			ARGUMENTS['goal'] = make_goal(size)

		if args.taquin != '':
			if not re.match(r'^[\d\s\,]+$', args.taquin):
				raise Exception('Wrong input string formatting')
			taquin = args.taquin.split(',')
			size = math.sqrt(len(taquin))
			if size ** 2 != len(taquin):
				raise Exception('Wrong input string formatting')
			ARGUMENTS['base'] = list(map(int, taquin))
			ARGUMENTS['goal'] = make_goal(size)
	except Exception as e:
		print(e)
		sys.exit()

	ARGUMENTS['size'] = args.size
	ARGUMENTS['heur'] = args.H
	ARGUMENTS['greedy'] = args.greedy
	ARGUMENTS['solvable'] = True
	ARGUMENTS['iterations'] = 3000
