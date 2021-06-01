import numpy as np
import os
from numpy.random import randint
from pulp import *


class Player:

    def __init__(self):
        self.dt = 0.5
        self.horizon = int(24 / self.dt)  # horizon de temps
        self.efficiency = 0.95
        self.taille = 100  # Surface de chaque panneau en m2
        self.sun = np.ones(self.horizon + 1)  # énergie récupéré du soleil correspond à lpv
        self.bill = np.zeros(48)
        self.load = np.zeros(48)  # chargement de la batterie (li)
        self.penalty = np.zeros(48)
        self.grid_relative_load = np.zeros(48)
        self.battery_stock = np.zeros(49)  # a(t)
        self.capacity = 100
        self.max_load = 70
        self.pmax = 20
        self.prices = {"purchase": np.ones(48), "sale": np.ones(48)}
        self.imbalance = {"purchase_cover": [], "sale_cover": []}

    def take_a_simple_decision(self):  # on achète juste tout ce qui est demandé sans utiliser la batterie
        cout = 0
        for t in range(self.horizon):
            cout += -self.sun[t]*self.taille/1000 * self.prices["sale"][t] * self.dt
        return (cout)

    def set_scenario(self, scenario_data):
        self.sun = scenario_data

    def set_prices(self, prices):
        self.prices = prices

    def take_the_correct_decision(self):
        lp = pulp.LpProblem("optimisation.lp", LpMinimize)
        lp.setSolver()
        prod_vars_plus = {}
        prod_vars_moins = {}
        plus = []
        moins = []
        sortieplus = {}
        for t in range(self.horizon):
            var_name = "lbatplus" + str(t)
            prod_vars_plus[t] = pulp.LpVariable(var_name, 0, 1 / self.efficiency * self.pmax)
            plus.append(prod_vars_plus[t])
            var_name = "sortieplus" + str(t)
            sortieplus[t] = pulp.LpVariable(var_name, 0, None)
            var_name = "lbatmoins" + str(t)
            prod_vars_moins[t] = pulp.LpVariable(var_name, -self.efficiency * self.pmax, 0)
            moins.append(prod_vars_moins[t])

            # condition de la batterie entre 0 et 100
            constraintName = "batterie inferieur 100" + str(t)
            lp += self.dt * pulp.lpSum([(self.efficiency * prod_vars_plus[t1] + 1 / self.efficiency * prod_vars_moins[t1]) for t1 in range(t + 1)]) <= self.capacity, constraintName
            constraintName = "batterie superieur a 0" + str(t)
            lp += self.dt * pulp.lpSum([(self.efficiency * prod_vars_plus[t1] + 1 / self.efficiency * prod_vars_moins[t1]) for t1 in range(t + 1)]) >= 0.0, constraintName

            # sortie plus
            constraintName = "sortie correcteplus" + str(t)
            lp += prod_vars_plus[t] - self.sun[t]*self.taille/1000 + prod_vars_moins[t] <= sortieplus[t], constraintName
        lp.setObjective(self.dt * (pulp.lpSum([(self.prices["purchase"][t] * sortieplus[t] + (prod_vars_plus[t] - self.sun[t]*self.taille/1000 + prod_vars_moins[t] - sortieplus[t]) * self.prices["sale"][t]) for t in range(self.horizon)])))
        # lp.setObjective(pulp.lpSum([(prod_vars_plus[t] - self.sun[t + 1] + prod_vars_moins[t]) for t in range(self.horizon - 1)]))
        # lp += pulp.lpSum(self.dt*(self.prices["purchase"][0] * prod_vars_plus[0] - prod_vars_moins[0] * self.prices["sale"][0] + pulp.lpSum([(self.prices["purchase"][t + 1] * sortieplus[t] + (prod_vars_plus[t] - self.sun[t + 1] + prod_vars_moins[t] - sortieplus[t]) * self.prices["sale"][t + 1]) for t in range(self.horizon - 1)])))
        lp.solve()
        print("Status:", LpStatus[lp.status], "\n")
        Lbat = []
        for i in range(self.horizon):
            Lbat.append(plus[i].varValue + moins[i].varValue)
            self.battery_stock[i + 1] = sum(plus[k].varValue * self.efficiency + 1 / self.efficiency * moins[k].varValue for k in range(i))*self.dt
        for i in range(self.horizon):
            self.grid_relative_load[i] = Lbat[i] - self.sun[i]
        L2 = []
        for i in range(self.horizon):
            L2.append(prod_vars_moins[i].varValue)
        print("The Max Value = ", value(lp.objective))
        return Lbat

    def compute_all_load(self):
        self.take_the_correct_decision()
        return self.grid_relative_load

    def update_battery_stock(self, time, load):
        if abs(load) > self.max_load:
            load = self.max_load * np.sign(load)  # saturation au maximum de la batterie

        new_stock = self.battery_stock[time] + (
                    self.efficiency * max(0, load) - 1 / self.efficiency * max(0, -load)) * self.dt

        # On rétablit les conditions si le joueur ne les respecte pas :

        if new_stock < 0:  # impossible, le min est 0, on calcule le load correspondant
            load = - self.battery_stock[time] / (self.efficiency * self.dt)
            new_stock = 0

        elif new_stock > self.capacity:
            load = (self.capacity - self.battery_stock[time]) / (self.efficiency * self.dt)
            new_stock = self.capacity

        self.battery_stock[time + 1] = new_stock

        return load

    def compute_load(self, time, sun):
        load_player = self.take_decision(time)
        load_battery = self.update_battery_stock(time, load_player)
        self.load[time] = load_battery - sun

        return self.load[time]

    def observe(self, t, sun, price, imbalance, grid_relative_load):
        self.sun.append(sun)

        self.prices["purchase"].append(price["purchase"])
        self.prices["sale"].append(price["sale"])

        self.imbalance["purchase_cover"].append(imbalance["purchase_cover"])
        self.imbalance["sale_cover"].append(imbalance["sale_cover"])
        self.grid_relative_load[t] = grid_relative_load

    def reset(self):
        self.load = np.zeros(48)
        self.bill = np.zeros(48)
        self.penalty = np.zeros(48)
        self.grid_relative_load = np.zeros(48)

        last_bat = self.battery_stock[-1]
        self.battery_stock = np.zeros(49)
        self.battery_stock[0] = last_bat

        self.sun = []
        self.prices = {"purchase": [], "sale": []}
        self.imbalance = {"purchase_cover": [], "sale_cover": []}


def verification(player,grid_relative_load) :
    ##solution est les différents li lié à la batterie
    cout=0
    batterie=0
    prod_vars_plus=np.zeros(player.horizon)
    prod_vars_moins=np.zeros(player.horizon)
    for t in range (player.horizon) :
        prod_vars_plus[t]=max(0, grid_relative_load[t]+player.sun[t]*player.taille/1000)
        prod_vars_moins[t]=min(0, grid_relative_load[t]+player.sun[t]*player.taille/1000)
        if (player.dt *
            sum([player.efficiency * prod_vars_plus[t1] + 1 / player.efficiency * prod_vars_moins[t1] for t1 in
             range(t + 1)]) > player.capacity) :
            print("erreur batterie superieur 100")
        if (player.dt *
                sum([player.efficiency * prod_vars_plus[t1] + 1 / player.efficiency * prod_vars_moins[t1] for t1 in
                     range(t + 1)]) < 0):
            print("erreur batterie negative")
    return(sum([max(0,grid_relative_load[t])*player.prices["purchase"][t]+min(0,grid_relative_load[t])*player.prices["sale"][t]]))


if __name__ == '__main__':
    solar = Player()
