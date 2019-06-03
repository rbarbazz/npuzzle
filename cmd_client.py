#!/usr/bin/python3
#-*- coding: utf-8 -*-
#

import sys
import time

from npuzzle import api, parser, gen, npuzzle


def callback(data):
	print("Thread responds:")
	print(data)


def main():
	r = gen.gen_random("snale", 3, 3000, True)
	r1 = npuzzle.make_taquin(r)
	print("Base:\n{}".format(r1))
	print(api.check_solvability("snale", r))
	r = api.solve("snale", r, True, "manhattan", callback)
	if r["error"]:
		print(r["data"])
		return 0
	# print(r)
	api.wait_solving()
	return 0

	parser.sanitize_arguments()

	print("Heuristics: {}".format(api.get_available_heuristics()))
	print("Types: {}".format(api.get_available_types()))
	print("Make random:")
	r = api.make_random("snale", 4, True, 1000)
	if r["error"]:
		print(r["data"])
		return 0
	print(r)
	print("Check solvability:")
	r = api.check_solvability(r["type"], r["npuzzle"])
	if r["error"]:
		print(r["data"])
		return 0
	print(r)
	if r["solvable"]:
		print("Is running ?: {}".format(api.is_solving()))
		print("Solve:")
		# Start solve in a new thread
		r = api.solve(r["type"], r["npuzzle"], False, "manhattan", callback)
		if r["error"]:
			print(r["data"])
			return 0
		print(r)

	print("\nWait 3secs")
	api.wait_solving()
	#Stop the current process and return
	api.stop_solving()

	return 0


if __name__ == '__main__':
	sys.exit(main())
