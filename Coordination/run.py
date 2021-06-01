import numpy as np
from simulate import Manager
import time
import os
import argparse
import json
import tqdm


def merge(a:dict, b:dict):
	for k, v in b.items():
		if k in a:
			if isinstance(v, dict):
				merge(a[k], v)
			else:
				a[k] = v
		else:
			a[k] = v



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--players', type=str, default='data/players.json', help='path to players.json file')
	parser.add_argument('-c', '--prices', type=str, default='data/prices.csv', help='path to scenario file (prices.csv)')
	parser.add_argument('-n', '--name', type=str, default='default', help='experiment name')
	parser.add_argument('-s', '--scenarios', type=int, default=1, help='number of runs')
	parser.add_argument('-r', '--regions', nargs='+', type=str, default=['all'], help='region names')
	parser.add_argument('--seed', type=int, default=123, help='set random seed')
	args = parser.parse_args()

	name = args.name
	this_dir = os.path.dirname(os.path.abspath(__file__))
	t = time.time()

	if args.regions == ['all']:
		args.regions = [
			"grand_nord",
			"grand_est",
			"grand_rhone",
			"bretagne",
			"grand_ouest",
			"grand_sud_ouest",
			"grande_ardeche",
			"grand_sud_est"
		]

	with open(args.players, 'r') as file:
		players = json.load(file)
	full_data = {}
	full_pv_profiles = {}
	for team in tqdm.tqdm(players.keys()):
		import random
		random.seed(args.seed)
		import numpy as np
		np.random.seed(args.seed)
		manager = Manager(team, args.players, args.prices, args.regions)
		data, pv_profiles = manager.simulate(args.scenarios, name)
		merge(full_data, data)
		merge(full_pv_profiles, pv_profiles)

	from visualize_v2 import generate_pptx
	generate_pptx(full_data, full_pv_profiles)


