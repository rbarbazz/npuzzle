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
	return 0


if __name__ == '__main__':
	sys.exit(main())
