#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import signal

from npuzzle import api
from npuzzle import parser


def signal_handler(sig, frame):
	if sig == signal.SIGINT:
		sys.exit(0)


def main():
	signal.signal(signal.SIGINT, signal_handler)
	parser.sanitize_arguments()

	r = api.make_random("snale", 3, True)
	if r["error"]:
		print(r["data"])
		return 0
	print(r)
	r = api.check_solvability(r["type"], r["npuzzle"])
	if r["error"]:
		print(r["data"])
		return 0
	print(r)
	r = api.solve(r["type"], r["npuzzle"], False, "manhattan")
	if r["error"]:
		print(r["data"])
		return 0
	print(r)
	return 0


if __name__ == '__main__':
	sys.exit(main())
