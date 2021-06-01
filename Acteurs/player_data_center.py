import numpy as np
import os
from numpy.random import randint
from pulp import *

#Data_Center


class Player:
    def __init__(self):
        self.dt = 0.5
        self.horizon = int(24 / self.dt)    # horizon de temps
        self.electric_load = np.ones(self.horizon)      #puissance consommée par les serveurs = Lit
        self.hi = self.electric_load
        self.prices = {"purchase": np.ones(self.horizon), "sale": np.ones(self.horizon)}    # présent dans deux listes
        self.cooling_system=np.zeros(self.horizon)      #lCS
        self.hr=np.zeros(self.horizon)
        self.EER = 4
        self.COP = 5
        self.heat_power = np.zeros(self.horizon)
        self.hDC = np.zeros(self.horizon)
        self.COPhp = 0.4*333/(60-35)
        self.EERhp = self.COPhp - 1
        for t in range (self.horizon):
            self.cooling_system[t]=self.hi[t]/(self.EER*self.dt)
            self.hr[t]=self.COP*self.cooling_system[t]*self.dt
            self.heat_power[t] = self.hr[t]/(self.EERhp*self.dt)
            self.hDC[t] = self.COPhp*self.heat_power[t]*self.dt
        self.price_selling_water = np.random.rand(self.horizon)
        self.maximum_heat_transfer = 10     #10 KWh every half hour
        self.consototale = np.zeros(self.horizon)

    def set_scenario(self, scenario_data):
        self.electric_load = scenario_data
        self.hi = self.electric_load
        self.heat_power = np.zeros(self.horizon)
        self.hDC = np.zeros(self.horizon)
        self.COPhp = 0.4*333/(60-35)
        self.EERhp = self.COPhp - 1
        for t in range (self.horizon):
            self.cooling_system[t]=self.hi[t]/(self.EER*self.dt)
            self.hr[t]=self.COP*self.cooling_system[t]*self.dt
            self.heat_power[t] = self.hr[t]/(self.EERhp*self.dt)
            self.hDC[t] = self.COPhp*self.heat_power[t]*self.dt
        self.maximum_heat_transfer = 10     #10 KWh every half hour
        pass

    def set_prices(self, prices):
        self.prices = prices

    def compute_all_load(self):
        return self.take_the_correct_decision()

    def take_a_simple_decision(self):
        cost = 0
        for t in range(self.horizon):
            cost += (self.electric_load[t] + self.cooling_system[t]) * self.prices["purchase"][t] * self.dt
            self.consototale[t] = self.electric_load[t] + self.cooling_system[t]
        return cost

    def take_the_correct_decision(self):
        #A chaque pas de temps, si lHP*prix > pH*HDC, on n'active pas, si oui on active
        #Dans tous les cas on paye truc et cooling system
        L2 = [] # Activé ou pas
        Cost = 0
        L = [] # Li total - qui comprend ou non la vente de chaleur -
        for t in range(self.horizon):
            if self.prices["purchase"][t] * self.heat_power[t] <= min(self.hDC[t],self.maximum_heat_transfer) * self.price_selling_water[t] :
                L2.append(1)
                L.append(self.electric_load[t] + self.cooling_system[t] + self.heat_power[t])
                Cost += L[t] * self.prices["purchase"][t] - min(self.hDC[t],self.maximum_heat_transfer) * self.price_selling_water[t]
            else :
                L2.append(0)
                L.append(self.electric_load[t] + self.cooling_system[t])
                Cost += L[t] * self.prices["purchase"][t] * self.dt
        for i in range(self.horizon):
            self.consototale[i] = L[i]
        print(L)
        print(L2)
        print(Cost)
        return L

    def reset(self):
        pass



if __name__ == '__main__':
    Myplayer = Player()
    Myplayer.take_the_correct_decision()
    print(Myplayer.consototale)
