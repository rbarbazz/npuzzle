#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


from . import parser
from .npuzzle_gen import make_puzzle, make_goal
from .npuzzle import solvable, make_taquin


__all__ = ["make_random", "make_from_string", "solve"]


def make_random(ntype, size, is_solvable=True, iterations=5000):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type"}
	if not parser.check_int(size, 3, 1024):
		return {"error": True, "data": "Bad size"}
	if not parser.check_int(iterations, 0, 1000000000):
		return {"error": True, "data": "Bad iterations"}
	if not parser.check_bool(is_solvable):
		return {"error": True, "data": "Solvable must be a boolean"}
	ret = {"error": False}

	ret["goal"] = make_goal(size)
	ret["npuzzle"] = make_puzzle(size, is_solvable, iterations)
	ret["type"] = ntype
	ret["size"] = size
	ret["solvable"] = solvable(make_taquin(ret["npuzzle"]),
		make_taquin(ret["goal"]))
	return ret


def check_solvability(ntype, npuzzle_input):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type"}
	if not parser.check_npuzzle(npuzzle_input):
		return {"error": True, "data": "Bad input"}
	ret = {"error": False}

	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	tmp = make_taquin(npuzzle_input)
	ret["size"] = tmp.size
	ret["goal"] = make_goal(tmp.size)
	ret["solvable"] = solvable(tmp, make_taquin(ret["goal"]))
	return ret


def solve(ntype, npuzzle_input, greedy, heuristic):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type"}
	if not parser.check_npuzzle(npuzzle_input):
		return {"error": True, "data": "Bad input"}
	if not parser.check_bool(greedy):
		return {"error": True, "data": "Greedy must be a boolean"}
	if not parser.check_heuristic(heuristic):
		return {"error": True, "data": "Bad heuristic"}
	ret = {"error": False}

	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	ret["goal"] = make_goal(tmp.size)
	ret["greedy"] = greedy
	ret["heuristic"] = heuristic
	tmp = make_taquin(npuzzle_input)
	ret["size"] = tmp.size
	ret["solvable"] = solvable(tmp, make_taquin(ret["goal"]))
	if ret["solvable"]:
		ret["solution"] = []
		ret["stats"] = {}
	return ret


if __name__ == '__main__':
	pass
