import argparse
import sys
import re
import math


parser = argparse.ArgumentParser(description='Solve a NPuzzle')
group = parser.add_mutually_exclusive_group()
group.add_argument('-f', default='', help='Read a NPuzzle from a file', dest='filename')
group.add_argument('-c', default='', help='Input NPuzzle as a string of numbers separated by spaces', dest='taquin')
group.add_argument('-s', default=0, help='Provide a size to generate a taquin', dest='size')
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
		taquin = [col for line in taquin for col in line]

	if args.taquin != '':
		if not re.match(r'^[\d\s\,]+$', args.taquin):
			raise Exception('Wrong input string formatting')
		taquin = args.taquin.split(',')
		root = math.sqrt(len(taquin))
		if root ** 2 != len(taquin):
			raise Exception('Wrong input string formatting')
		taquin = list(map(int, taquin))
except Exception as e:
	print(e)
	sys.exit()

BASE = taquin
GOAL = []
HEUR = args.H
GREEDY = args.greedy
