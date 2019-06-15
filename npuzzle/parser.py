#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


import argparse
import sys
import re
import math
from .heuristic import HEURISTICS_LIST
from .npuzzle import TYPES_LIST
from functools import reduce


def check_type(p_type):
	if type(p_type) != str:
		return False
	if p_type not in TYPES_LIST:
		return False
	return True


def check_heuristic(p_arg):
	if type(p_arg) != str:
		return False
	if p_arg not in HEURISTICS_LIST:
		return False
	return True


def check_int(p_size, p_min, p_max):
	if type(p_size) != int:
		return False
	if p_size < p_min or p_size > p_max:
		return False
	return True


def check_bool(p_arg):
	return type(p_arg) == bool


def check_str(p_arg):
	if type(p_arg) != str:
		return False
	if len(p_arg) < 1:
		return False
	return True


def check_npuzzle(p_arg):
	if type(p_arg) != list:
		return False
	if len(p_arg) < 4:
		return False
	if type(p_arg[0]) != int:
		return False
	root = int(math.sqrt(len(p_arg)))
	if root * root != len(p_arg):
		return False
	# Check if all digit from 0 to len(puzzle) are present
	check_nb = [(x in p_arg) for x in range(0, len(p_arg))]
	if not reduce(lambda a, b: a and b, check_nb):
		return False
	return True


VALID_ACTIONS = ["gen", "check", "solve"]


def sanitize_arguments():
	parser = argparse.ArgumentParser(description='NPuzzle solver')
	subparsers = parser.add_subparsers()

	# Sub commands
	def _init_subparser(subparser, key):
		r = subparsers.add_parser(key)
		r.set_defaults(which=key)
		return r
	parsers = {
		key: _init_subparser(subparsers, key) for key in VALID_ACTIONS
	}


	# Common parameters
	group_verbose = parser.add_mutually_exclusive_group()
	group_verbose.add_argument("-q", "--quiet", action="store_true",
		default=False, help="No output")

	# Type of npuzzle
	parser.add_argument("-t", "--type", type=str, default="snale",
		help="Type of npuzzle: {}".format(", ".join(TYPES_LIST)))

	# Arguments gen
	parsers["gen"].add_argument("-u", "--unsolvable", action="store_true",
		help="The npuzzle generated must be unsolvable", default=False)
	parsers["gen"].add_argument("-s", "--size", type=int,
		help="The dimension of the npuzzle (> 1)", required=True)
	parsers["gen"].add_argument("-i", "--iteration", type=int, default=5000,
		help="Number of iterations to shuffle the npuzzle")
	parsers["gen"].add_argument("-o", "--output", action="store_true",
		default=False,
		help="The output should be formatted for a file")

	# Arguments check
	group_check = parsers["check"].add_mutually_exclusive_group(required=True)
	group_check.add_argument("-f", "--file", help="Provide a file")
	group_check.add_argument("-r", "--raw", help="Provide a raw puzzle")

	# Arguments solve
	group_check = parsers["solve"].add_mutually_exclusive_group(required=True)
	group_check.add_argument("-f", "--file", help="Provide a file")
	group_check.add_argument("-r", "--raw", help="Provide a raw puzzle")
	parsers["solve"].add_argument("-c", "--heuristic", type=str, required=True,
		help="Available heuristics: {}".format(", ".join(HEURISTICS_LIST)))
	parsers["solve"].add_argument("-g", "--greedy", default=False,
		action="store_true", help="Greedy mode")

	args = parser.parse_args()
	if not len(sys.argv) > 1:
		parser.print_help()
	return args
