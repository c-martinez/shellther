"""Shellther. Log your shell and sync it with Etherpad (or other repository).

Usage:
  shellther <padID> [--config <configfile>] --dedicated
  shellther <padID> [--config <configfile>] --section [--marker <marker>]

Options:
  -h --help     Show this screen.
  --dedicated   Use dedicated Etherpad to log console
  --section     Use a section in the Etherpad to log console
  --config <configfile>  Load configuration from config file (default: .config).
  --marker <marker>  Marker used as separator. If None, random marker is generated (default: random).
"""
from docopt import docopt

from shellther.main import parseArgs

def main():
    args = docopt(__doc__, version='Shellther v0.1')
    parseArgs(args)
