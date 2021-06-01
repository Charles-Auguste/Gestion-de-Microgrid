# python 3
import json
import numpy as np
import random
import os
from collections import defaultdict
import pandas
import tqdm
import sys


class Manager:
    def __init__(self, team_name: str, path_to_player_file, path_to_price_file, regions):
        self.horizon = 24
        self.dt = 0.5
        self.nbr_iterations = 10
        self.nb_pdt = int(self.horizon/self.dt)

        self.regions = regions
        self.team_name = team_name
        self.path_to_player_file = path_to_player_file

        self.players = self.create_players(team_name, path_to_player_file)
        self.scenarios = self.read_all_scenarios()
        self.external_prices = self.read_national_grid_prices(path_to_price_file)

        self.__results = defaultdict(dict)
        self.scenarios_per_actor = {}

    def create_players(self, team_name: str, json_file):
        """initialize all players"""

        with open(json_file) as f:
            teams = json.load(f)

        new_players = []

        team = teams.get(team_name, None)
        if team is None:
            raise ValueError(f'team {team_name} is not found')

        if isinstance(team, dict):
            for player_type in ['charging_station', 'data_center', 'industrial_consumer', 'solar_farm']:
                player = {}
                player['team'] = team_name
                player['type'] = player_type
                mod = __import__(f"players.{team_name}.player_{player_type}", fromlist=["Player"])
                new_player = mod.Player()
                new_player.__manager__data = player
                new_players.append(new_player)
        elif isinstance(team, list):
            players = team
            for player in players:
                player['team'] = team_name
                mod = __import__(f"players.{team_name}.{player['folder']}.player", fromlist=["Player"])
                new_player = mod.Player()
                new_player.__manager__data = player
                new_players.append(new_player)

        return new_players

    def read_national_grid_prices(self, path):
        """initialize daily scenarios"""
        prices_data = pandas.read_csv(path, header=None, delimiter=" ")
        prices = prices_data.iloc[0].to_numpy()
        return {'purchase': prices, 'sale':prices.copy()}

    def read_all_scenarios(self):
        """initialize daily scenarios"""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(this_dir, "scenarios")
        # les scenarios pour chaque type de player
        scenario = {}

        for player_type in ['industrial_consumer', 'data_center', 'solar_farm', 'charging_station']:
            if player_type == "charging_station":
                
                #STATION DE RECHARGE
                car_data=pandas.read_csv(os.path.join(data_dir, "charging_station", "ev_scenarios.csv"), delimiter =";")
                nb_car=10
                charging_station={}
                for day in range (365):
                    day_name="scenario_"+str(day)
                    day_data={}
                    for car in range (10):
                        car_name="car_"+str(car)
                        car_dep_arr=[car_data["time_slot_dep"][10*day+car]*2,car_data["time_slot_arr"][10*day+car]*2]
                        day_data[car_name]=car_dep_arr
                    charging_station[day_name]=list(day_data.values())
                scenario[player_type]=charging_station

                #================================================================================================================================================================
                # pour acceder aux horaires de départ et d'arrivée d'une voiture pendant une journée : scenario["charging_station"]["scenario_i"]["car_j"]  --> renvoie une liste
                #================================================================================================================================================================

            elif player_type == "solar_farm":
                
                # FERME SOLAIRE
                solar_data=pandas.read_csv(os.path.join(data_dir, "solar_farm", "pv_prod_scenarios.csv"), delimiter =";")
                # 8 régions, 365 jours, 24 heures
                scenario_solar={}
                for region in range (8):
                    region_name = solar_data['region'][8760*region]
                    reg={} 
                    for jour in range (365):
                        day_name = "scenario_"+str(jour)
                        list_day = []
                        for heure in range (24):
                            list_day.append(solar_data["pv_prod (W/m2)"][8760*region+24*jour+heure])
                            list_day.append(solar_data["pv_prod (W/m2)"][8760*region+24*jour+heure])
                        reg[day_name]=list_day
                    scenario_solar[region_name]=reg
                scenario[player_type]=scenario_solar


                #======================================================================================================
                # pour acceder à une journée : scenario["solar_farm"]["region_i"]["scenario_j"]  --> renvoie une liste
                #======================================================================================================

            elif player_type == "industrial_consumer":
                
                # COMPLEXE INDUSTRIEL
                industrial_data=pandas.read_csv(os.path.join(data_dir,
                                                             "industrial_consumer", "indus_cons_scenarios.csv"), delimiter =";")
                nb_scenarios=0
                for i in industrial_data.index:
                    if(industrial_data["time_slot"][i]==1):
                        nb_scenarios+=1
                scenario_industrial={}
                for i in range (nb_scenarios):
                    nom_scenario="scenario_"+str(i)
                    list_scenario=[]
                    for j in range (48):
                        list_scenario.append(np.array(industrial_data["cons (kW)"][48*i+j])/10.)
                    scenario_industrial[nom_scenario]=list_scenario
                scenario[player_type]=scenario_industrial

                #===============================================================================================
                # pour acceder à une journée : scenario["industrial_farm"]["scenario_i"]  --> renvoie une liste
                #===============================================================================================
            elif player_type == "data_center":
                                 
                #DATA CENTER
                dcenter_data=pandas.read_csv(os.path.join(data_dir,"data_center", "data_center_scenarios.csv" ),delimiter = ";")
                data_center={}
                for scenar in range(10):
                    list_scenar=[]
                    scenar_name="scenario_"+str(scenar)
                    for time in range(48):
                        list_scenar.append(dcenter_data["cons (kW)"][10*scenar+time])
                    data_center[scenar_name]=list_scenar
                scenario["data_center"]=data_center

                #================================================================================================
                # pour acceder à un scenario : scenario["data_center"]["scenario_i"]  --> renvoie une liste
                #================================================================================================

        return scenario

    def initialize_prices(self):
        """initialize daily prices"""
        purchase_prices = np.zeros(self.nb_pdt)
        sale_prices = np.zeros(self.nb_pdt)
        return {"purchase": purchase_prices, "sale": sale_prices}

    def draw_random_scenario(self, region):
        """ Draw a scenario for the day """
        scenario = {}
        for player_type in ['industrial_consumer', 'solar_farm', 'data_center', 'charging_station']:
            if player_type == "solar_farm":
                id_scenario = random.choice(list(self.scenarios[player_type][region].keys()))
                random_scenario = self.scenarios[player_type][region][id_scenario]
                scenario[player_type] = random_scenario
                self.scenarios_per_actor[player_type] = region # int(id_scenario.split('_')[-1])
            elif player_type in ["charging_station", 'industrial_consumer', 'data_center']:
                id_scenario = random.choice(list(self.scenarios[player_type].keys()))
                random_scenario = self.scenarios[player_type][id_scenario]
                scenario[player_type] = random_scenario
                self.scenarios_per_actor[player_type] = id_scenario # int(id_scenario.split('_')[-1])
        return scenario

    def switch_region(self, scenario, region):
        id_scenario = random.choice(list(self.scenarios['solar_farm'][region].keys()))
        random_scenario = self.scenarios['solar_farm'][region][id_scenario]
        scenario['solar_farm'] = random_scenario
        self.scenarios_per_actor['solar_farm'] = region  # int(id_scenario.split('_')[-1])
        return scenario

    def get_microgrid_load(self):
        """ Compute the energy balance on a slot """
        microgrid_load = np.zeros(self.nb_pdt)
        loads = {}

        for player in self.players:
            load = player.compute_all_load()

            microgrid_load += load
            # storing loads for each player for future backup
            loads[player.__manager__data['type']] = load

        return microgrid_load, loads

    def compute_bills(self, microgrid_load, loads, prices):
        """ Compute the bill of each players """
        microgrid_bill = 0
        player_bills = defaultdict(float)
        for i in range (self.nb_pdt):
            microgrid_bill += microgrid_load[i]*prices.get("purchase")[i]
            for j in range(len(self.players)):
                player = self.players[j]
                for i in range (self.nb_pdt):
                    player_bills[player.__manager__data['type']] += prices.get("purchase")[i]*loads[player.__manager__data['type']][i]
        return microgrid_bill, player_bills

    def send_prices_to_players(self, prices):
        for player in self.players:
            # TODO: a remplacer
            player.set_prices(prices)
            pass

    def send_scenario_to_players(self, scenario):
        for player in self.players:
            # TODO: a remplacer
            if player.__manager__data['type'] in scenario:
                try:
                    player.set_scenario(scenario[player.__manager__data['type']])
                except AttributeError as e:
                    print(f'player {player.__manager__data["type"]} does not implement set_scenario')
                    raise e
            pass

    def play(self, scenario, region):
        """ Playing one party """
        self.reset()
        # initialisation de la boucle de coordination
        self.send_scenario_to_players(scenario)
        prices = self.initialize_prices()
        # debut de la coordination
        for iteration in range(self.nbr_iterations):  # main loop
            self.send_prices_to_players(prices)
            microgrid_load, player_loads = self.get_microgrid_load()
            microgrid_bill, player_bills = self.compute_bills(microgrid_load, player_loads, prices)
            self.store_results(region, iteration,
                               {
                                   'scenario': scenario,
                                   'player_loads': player_loads,
                                   'player_bills': player_bills,
                                   'microgrid_load': microgrid_load,
                                   'microgrid_bill': microgrid_bill
                               }
                               )
            prices, converged = self.get_next_prices(iteration, prices, microgrid_load)
            if converged:
                break

    def get_next_prices(self, iteration, prices, microgrid_load):
        old_purchase = prices.get("purchase")
        old_sale = prices.get("sale")
        grad = microgrid_load - np.mean(microgrid_load)
        dp = 1e-3 * 0.99**iteration
        purchase_prices = old_purchase + dp * grad
        sale_prices = old_sale + dp * grad
        new_prices = dict(purchase=purchase_prices, sale=sale_prices)
        return new_prices, False

    def store_results(self, simulation, iteration, data):
        self.__results[simulation][iteration] = data

    def reset(self):
        # reset the attributes of the manager
        for player in self.players:
            player.reset()

    def simulate(self, nb_simulation, simulation_name):
        # for each simulation
        scenario = self.draw_random_scenario(self.regions[0])
        original = sys.stdout
        null = open('/dev/null', 'w')
        pv_profiles = {}
        for region in tqdm.tqdm(self.regions):
            sys.stdout = null
            scenario = self.switch_region(scenario, region)
            pv_profiles[region] = np.array(scenario['solar_farm'])*100/1000.0
            self.play(scenario, region)
            sys.stdout = original

        self.reset()

        return self.data_viz(self.__results), pv_profiles

    def data_viz(self, results):
        data = {}
        for region, region_data in results.items():
            ptr = data
            for player_type in ['industrial_consumer', 'data_center', 'solar_farm', 'charging_station']:
                key = self.scenarios_per_actor[player_type]
                if player_type == 'solar_farm':
                    key = region
                if key not in ptr:
                    ptr[key] = {}
                ptr = ptr[key]
            if self.team_name not in ptr:
                ptr[self.team_name] = {}
            ptr = ptr[self.team_name]
            for iteration, data_iter in region_data.items():
                ptr[iteration] = data_iter['player_loads']
        return data
