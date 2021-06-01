# python 3
#
# script for initializing the game from a players.json file
# optional improvements: git clone, perform tests


import os
import json
import argparse
from git import Repo, InvalidGitRepositoryError

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--players', type=str, default='data/players.json', help='path to players.json file')
	parser.add_argument('-t', '--team', type=str, help='team name')
	args = parser.parse_args()

	this_dir = os.path.dirname(os.path.abspath(__file__))

	with open(args.players) as f:
		teams = json.load(f)

	checkout_teams = None
	if args.team is None:
		checkout_teams = list(teams.keys())
	else:
		checkout_teams = [args.team]

	for team_name in checkout_teams:
		team = teams.get(team_name, None)
		if team is None:
			exit(1)
		print (f'checking out {team_name}')

		if isinstance(team, dict):
			code_path = os.path.join(this_dir, "players", team_name)
			# initialize player folders, git clone & test ?
			os.makedirs(code_path, exist_ok=True)
			try:
				# on essaie de puller le dépôt
				Repo(code_path).remotes.origin.pull()  # pull each player
			except InvalidGitRepositoryError as err:
				# ce n'est pas un dépôt git, on clone
				Repo.clone_from(team['url'], code_path)  # clone each player
		elif isinstance(team, list):
			players = team
			for val in players:
				code_path = os.path.join(this_dir, "players", team_name, val['folder'])
				# initialize player folders, git clone & test ?
				os.makedirs(code_path, exist_ok=True)

				try:
					# on essaie de puller le dépôt
					Repo(code_path).remotes.origin.pull()  # pull each player
				except InvalidGitRepositoryError as err:
					# ce n'est pas un dépôt git, on clone
					Repo.clone_from(val['url'], code_path)  #clone each player
