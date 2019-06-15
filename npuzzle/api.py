#!/usr/bin/python3
#-*- coding: utf-8 -*-
#


import threading
import signal

from . import parser
from . import npuzzle, heuristic, gen

__all__ = ["get_available_heuristics", "get_available_types", "solve",
			"make_random", "check_solvability",
			"is_solving", "stop_solving", "wait_solving"]


CURRENT_PROCESS = None

def get_available_heuristics():
	return heuristic.HEURISTICS_LIST


def get_available_types():
	return npuzzle.TYPES_LIST


def stop_solving():
	global CURRENT_PROCESS
	if CURRENT_PROCESS is not None:
		CURRENT_PROCESS.stop_running()
	return True


def is_solving():
	global CURRENT_PROCESS
	return CURRENT_PROCESS is not None and CURRENT_PROCESS.is_alive()


def wait_solving():
	global CURRENT_PROCESS
	if CURRENT_PROCESS is not None and CURRENT_PROCESS.is_alive():
		CURRENT_PROCESS.join()
	return True


def make_random(ntype, size, is_solvable=True, iterations=5000):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type [{}]".format(
			", ".join(npuzzle.TYPES_LIST))}
	if not parser.check_int(size, 2, 1024):
		return {"error": True, "data": "Bad size [2-1024]"}
	if not parser.check_int(iterations, 0, 1000000000):
		return {"error": True, "data": "Bad iterations [0-1000000000]"}
	if not parser.check_bool(is_solvable):
		return {"error": True, "data": "Solvable must be a boolean"}
	ret = {"error": False}

	ret["goal"] = gen.gen_goal(ntype, size)
	ret["npuzzle"] = gen.gen_random(ntype, size, iterations, is_solvable)
	ret["type"] = ntype
	ret["size"] = size
	ret["solvable"] = gen.solvable(ret["type"],
		npuzzle.make_taquin(ret["npuzzle"]),
		npuzzle.make_taquin(ret["goal"]))
	return ret


def check_solvability(ntype, npuzzle_input):
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type [{}]".format(
			", ".join(npuzzle.TYPES_LIST))}
	if not parser.check_npuzzle(npuzzle_input):
		return {"error": True, "data": "Bad input npuzzle"}
	ret = {"error": False}

	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	tmp = npuzzle.make_taquin(npuzzle_input)
	ret["size"] = tmp.size
	ret["goal"] = gen.gen_goal(ntype, tmp.size)
	ret["solvable"] = gen.solvable(ret["type"], tmp,
		npuzzle.make_taquin(ret["goal"]))
	return ret


def solve(ntype, npuzzle_input, p_greedy, p_heuristic, callback=None):
	global CURRENT_PROCESS
	if is_solving():
		return {"error": True, "data": "A npuzzle is being solved already"}
	if not parser.check_type(ntype):
		return {"error": True, "data": "Wrong type [{}]".format(
			", ".join(npuzzle.TYPES_LIST))}
	if not parser.check_npuzzle(npuzzle_input):
		return {"error": True, "data": "Bad input npuzzle"}
	if not parser.check_bool(p_greedy):
		return {"error": True, "data": "Greedy must be a boolean"}
	if not parser.check_heuristic(p_heuristic):
		return {"error": True, "data": "Bad heuristic [{}]".format(
			", ".join(heuristic.HEURISTICS_LIST))}
	ret = {"error": False}

	tmp = npuzzle.make_taquin(npuzzle_input)
	ret["type"] = ntype
	ret["npuzzle"] = npuzzle_input
	ret["goal"] = gen.gen_goal(ntype, tmp.size)
	ret["greedy"] = p_greedy
	ret["heuristic"] = p_heuristic
	ret["size"] = tmp.size
	ret["solvable"] = gen.solvable(ret["type"], tmp,
		npuzzle.make_taquin(ret["goal"]))
	if ret["solvable"] or True:
		CURRENT_PROCESS = Process(ret, callback)
		CURRENT_PROCESS.start()
	return ret


def signal_handler(sig, frame):
	if sig == signal.SIGINT:
		global CURRENT_PROCESS
		if CURRENT_PROCESS is not None:
			CURRENT_PROCESS.stop_running()


class Process(threading.Thread):
	def __init__(self, data, callback=None):
		threading.Thread.__init__(self, daemon=False)
		self.data = data
		self.callback = callback

	def run(self):
		self.data["running"] = True
		result = npuzzle.solve(self.data["npuzzle"],
			self.data["goal"], self.data["greedy"], self.data["heuristic"])
		if result is None:
			self.data["error"] = True
			self.data["data"] = "Can't solve the puzzle"
		else:
			self.data["solution"] = result["solution"]
			self.data["stats"] = result["stats"]
			self.data["found"] = result["found"]
		self.data["running"] = False
		if self.callback is not None:
			self.callback(self.data)

	def stop_running(self):
		npuzzle.RUNNING = False

	def get_data(self):
		return self.data


if __name__ == '__main__':
	pass
