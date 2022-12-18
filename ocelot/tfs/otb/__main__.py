import argparse

from .otbi import load_otbi

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

load_otbi(args.filename)
