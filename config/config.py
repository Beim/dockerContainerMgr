import json
import os

curr_dir = os.path.split(os.path.abspath(__file__))[0]

with open("%s/config.json" % curr_dir) as f:
    CONFIG = json.load(f)