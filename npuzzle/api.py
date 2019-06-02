#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


from . import parser
from .npuzzle_gen import make_puzzle, make_goal
from . import npuzzle


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
	ret["solvable"] = npuzzle.solvable(npuzzle.make_taquin(ret["npuzzle"]),
		npuzzle.make_taquin(ret["goal"]))
	return ret


def check_solvability(ntype, npuzzle_input):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type"}
	if not parser.check_npuzzle(npuzzle_input):
		return {"error": True, "data": "Bad input"}
	ret = {"error": False}

	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	tmp = npuzzle.make_taquin(npuzzle_input)
	ret["size"] = tmp.size
	ret["goal"] = make_goal(tmp.size)
	ret["solvable"] = npuzzle.solvable(tmp, npuzzle.make_taquin(ret["goal"]))
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

	tmp = npuzzle.make_taquin(npuzzle_input)
	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	ret["goal"] = make_goal(tmp.size)
	ret["greedy"] = greedy
	ret["heuristic"] = heuristic
	ret["size"] = tmp.size
	ret["solvable"] = npuzzle.solvable(tmp, npuzzle.make_taquin(ret["goal"]))
	if ret["solvable"]:
		result = npuzzle.solve(ret["type"], ret["npuzzle"], ret["goal"],
				ret["greedy"], ret["heuristic"])
		if result is None:
			return {"error": True, "data": "Can't solve the puzzle"}
		ret["solution"] = result["solution"]
		ret["stats"] = result["stats"]
		ret["found"] = result["found"]
	return ret


if __name__ == '__main__':
	pass
