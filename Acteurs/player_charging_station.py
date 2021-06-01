import numpy as np
import os
from numpy.random import randint
from pulp import *
#from Modules.pulp_utils import *

## Charging Station

class Player:

    def __init__(self):
        self.dt = 0.5
        self.horizon = int(24/self.dt)   # horizon de temps
        self.prices = {"purchase" : np.ones(self.horizon),"sale" : np.ones(self.horizon)} #présent dans deux listes
        self.efficiency = 0.95
        self.bill = np.zeros(self.horizon) # Where 5e penalities will be stocked
        self.penalty=np.zeros(self.horizon)
        self.grid_relative_load=np.zeros(self.horizon)#combien on échange avec l'extérieur
        self.load = np.zeros(self.horizon) # List l4
        self.load_battery_periode = {"fast" : np.zeros((self.horizon,2)),"slow" : np.zeros((self.horizon,2))} # How the player wants to charge/discharge the vehicules
        self.battery_stock = {"slow" : np.zeros((self.horizon+1,2)), "fast" : np.zeros((self.horizon+1,2))} # State of the batteries le +1 vient du fait que poteaux barrière
        self.nb_fast_max = 2 # Number of Stations Fasts and Lows max
        self.nb_slow_max = 2
        self.nb_slow = 2 # Number of Stations Fast and Slow currently used
        self.nb_fast = 2
        self.pmax_fast = 22
        self.pmax_slow = 3
        self.cmax = 40*4 # Maximal capacity of the CS when the 4 slots are used KEZAKO
        self.depart = {"slow" : np.array([12,14]), "fast" : np.array([12,14])} # Time of departure of every cars, initialize at the end of the day
        self.arrival = {"slow" : np.array([36,38]), "fast" : np.array([36,34])} # Time of arrival of every cars, initialize at the end of the day
        self.here = {"slow" : np.ones(2), "fast" : np.ones(2)}# est ce que les voitures sont la
        self.imbalance={"purchase_cover":[], "sale_cover": []}#aucune idée
        self.pmax_station = 40
        self.p_station = 0

    def set_scenario(self, scenario_data):
        arr_dep = scenario_data[:self.nb_slow+self.nb_fast]
        self.depart = {"slow": [d[1] for d in arr_dep[:self.nb_slow]], "fast": [d[1] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}
        self.arrival = {"slow": [d[0] for d in arr_dep[:self.nb_slow]], "fast": [d[0] for d in arr_dep[self.nb_slow:self.nb_fast+self.nb_slow]]}

    def set_prices(self, prices):
        self.prices = prices

    def take_a_simple_decision(self):# ne revend pas d'electricité et se contente de charger les batteries quasiment à bloc
        self.load_battery_periode={"fast" : np.zeros((self.horizon,2)),"slow" : np.zeros((self.horizon,2))}
        self.grid_relative_load = np.zeros(self.horizon)
        self.battery_stock = {"slow": np.zeros((self.horizon + 1, 2)), "fast": np.zeros((self.horizon + 1, 2))}
        cout=0
        for speed in ["slow","fast"]:#on considère que load battery period sont les différents li
            for i in range (2):
                for t in range (self.horizon) :
                    if (self.depart[speed][i]>t):
                        if (speed =="fast") :
                            if (self.battery_stock[speed][t][i]<40-15*self.dt) :#attention à ne pas dépasser les valeurs de la batterie
                                self.load_battery_periode[speed][t][i] = 15
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i]*self.dt*self.efficiency+self.battery_stock[speed][t][i]
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i]
                        else :
                            if (self.battery_stock[speed][t][i] < 40 - 3 * self.dt):
                                self.load_battery_periode[speed][t][i] = 3
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i] * self.dt*self.efficiency + self.battery_stock[speed][t][i]
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i]
                    if(self.depart[speed][i] <= t < self.arrival[speed][i]):
                        self.battery_stock[speed][t+1][i] = self.battery_stock[speed][t][i]
                    if (self.arrival[speed][i] == t):
                        if (speed =="fast") :
                            if (self.battery_stock[speed][t][i] < 40 - 4 - 15 * self.dt):  # attention à ne pas dépasser les valeurs de la batterie
                                self.load_battery_periode[speed][t][i] = 15
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i] * self.dt*self.efficiency + self.battery_stock[speed][t][i] - 4
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i] - 4
                        else :
                            if (self.battery_stock[speed][t][i] < 40 - 4 - 3 * self.dt):
                                self.load_battery_periode[speed][t][i] = 3
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i] * self.dt*self.efficiency + self.battery_stock[speed][t][i] - 4
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i] - 4
                    if (self.arrival[speed][i] < t):
                        if (speed =="fast") :
                            if (self.battery_stock[speed][t][i]<40-15*self.dt) :#attention à ne pas dépasser les valeurs de la batterie
                                self.load_battery_periode[speed][t][i] = 15
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i]*self.dt*self.efficiency+self.battery_stock[speed][t][i]
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i]
                        else :
                            if (self.battery_stock[speed][t][i] < 40 - 3 * self.dt):
                                self.load_battery_periode[speed][t][i] = 3
                                self.battery_stock[speed][t+1][i] = self.load_battery_periode[speed][t][i] * self.dt*self.efficiency + self.battery_stock[speed][t][i]
                            else :
                                self.battery_stock[speed][t + 1][i] = self.battery_stock[speed][t][i]
                    self.grid_relative_load[t] += self.load_battery_periode[speed][t][i]
                    cout += self.load_battery_periode[speed][t][i]*self.prices["purchase"][t]*self.dt
        return (cout)


    def take_the_correct_decision(self):# on donne la solution correcte au vu des heures de départ et d'arrivée des trucs
        lp = pulp.LpProblem("optimisation.lp", LpMinimize)
        lp.setSolver()
        prod_vars_plus = {}
        prod_vars_moins = {}
        amende = {}
        sortieplus = {}
        Slow0plus = []; Slow0moins = []; Slow1plus = []; Slow1moins = []; Fast0plus = []; Fast0moins = []; Fast1plus = []; Fast1moins = []
        for t in range (self.horizon):
            prod_vars_moins[t] = {}
            prod_vars_plus[t] = {}
            for i in range(2):
                # creation des variables
                ###########################################################
                ## remplacer varname par signe
                var_name = "prod_" + str(t) + "_" + "slow" + str(i) + "plus"
                prod_vars_plus[t][i] = pulp.LpVariable(var_name, 0.0, 1/self.efficiency*self.pmax_slow)
                if i == 0:
                    Slow0plus.append(prod_vars_plus[t][i])
                if i == 1:
                    Slow1plus.append(prod_vars_plus[t][i])
                var_name = "prod_" + str(t) + "_" + "slow" + str(i) + "moins"
                prod_vars_moins[t][i] = pulp.LpVariable(var_name,-1*self.efficiency*self.pmax_slow ,0)
                if i == 0:
                    Slow0moins.append(prod_vars_moins[t][i])
                if i == 1:
                    Slow1moins.append(prod_vars_moins[t][i])
                #batterie entre 0 et 40

                if t<self.depart["slow"][i]:
                    constraintName= "batterie inferieur 40"+ str(t) + "_" + "slow" + str(i)
                    lp +=(self.battery_stock["slow"][0][i]+ self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i] + 1/self.efficiency*prod_vars_moins[t1][i] for t1 in range(t+1)])) <= 40.0, constraintName
                    constraintName = "batterie superieur a 0" + str(t) + "_" + "slow" + str(i)
                    lp += self.battery_stock["slow"][0][i] + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i] + 1/self.efficiency*prod_vars_moins[t1][i] for t1 in range(t+1)]) >= 0.0, constraintName
                elif t<self.arrival["slow"][i]:
                    constraintName = "voiture pas là" + str(t) + "_" + "slow" + str(i)
                    lp += prod_vars_plus[t][i]+prod_vars_moins[t][i]== 0.0, constraintName
                else :
                    constraintName= "batterie inferieur 40"+ str(t) + "_" + "slow" + str(i)
                    lp +=self.battery_stock["slow"][0][i] - 4 + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i] + 1/self.efficiency*prod_vars_moins[t1][i] for t1 in range(t+1)]) <= 40.0, constraintName
                    constraintName = "batterie superieur a 0" + str(t) + "_" + "slow" + str(i)
                    lp += self.battery_stock["slow"][0][i] - 4 + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i] + 1/self.efficiency*prod_vars_moins[t1][i] for t1 in range(t+1)]) >= 0.0, constraintName

            for i in range(2):
                var_name = "prod_" + str(t) + "_" + "fast" + str(i) + "plus"
                prod_vars_plus[t][i+2] = pulp.LpVariable(var_name, 0.0, 1 / self.efficiency * self.pmax_fast)
                if i == 0:
                    Fast0plus.append(prod_vars_plus[t][i+2])
                if i == 1:
                    Fast1plus.append(prod_vars_plus[t][i+2])
                var_name = "prod_" + str(t) + "_" + "fast" + str(i) + "moins"
                prod_vars_moins[t][i+2] = pulp.LpVariable(var_name, -self.efficiency * self.pmax_fast,0.0)
                if i == 0:
                    Fast0moins.append(prod_vars_moins[t][i+2])
                if i == 1:
                    Fast1moins.append(prod_vars_moins[t][i+2])
                if t < self.depart["fast"][i]:
                    constraintName = "batterie inferieur 40" + str(t) + "_" + "fast" + str(i)
                    lp += self.battery_stock["fast"][0][i] + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i+2] + 1/self.efficiency*prod_vars_moins[t1][i+2] for t1 in range(t+1)]) <= 40.0, constraintName
                    constraintName = "batterie superieur a 0" + str(t) + "_" + "fast" + str(i)
                    lp += self.battery_stock["fast"][0][i] + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i+2] + 1/self.efficiency*prod_vars_moins[t1][i+2] for t1 in range(t+1)]) >= 0.0, constraintName
                elif t < self.arrival["fast"][i]:
                    constraintName = "voiture pas là" + str(t) + "_" + "fast" + str(i)
                    lp += prod_vars_plus[t][i+2] + prod_vars_moins[t][i+2] == 0.0, constraintName
                else:
                    constraintName = "batterie inferieur 40" + str(t) + "_" + "fast" + str(i)
                    lp += self.battery_stock["fast"][0][i] - 4 + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i+2] + 1/self.efficiency*prod_vars_moins[t1][i+2] for t1 in range(t+1)]) <= 40.0, constraintName
                    constraintName = "batterie superieur a 0" + str(t) + "_" + "fast" + str(i)
                    lp += self.battery_stock["fast"][0][i] - 4 + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i+2] + 1/self.efficiency*prod_vars_moins[t1][i+2] for t1 in range(t+1)]) >= 0.0, constraintName

        #amende
        Amende = []
        for i in range (2):
            var_name= "amendeslow"+str(i)
            amende[i] = pulp.LpVariable(var_name, cat="Binary")
            Amende.append(amende[i])
            constraintName="amende"+ " slow"+str(i)
            lp += 10*amende[i]>=10-(self.battery_stock["slow"][0][i] + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i] + 1/self.efficiency*prod_vars_moins[t1][i] for t1 in range(self.depart["slow"][i])])) , constraintName
        for i in range (2):
            var_name= "amendefast"+str(i)
            amende[i+2] = pulp.LpVariable(var_name, cat="Binary")
            Amende.append(amende[i+2])
            constraintName="amende"+ " fast"+str(i)
            lp += 10*amende[i+2] >= 10 - (self.battery_stock["fast"][0][i]  + self.dt*pulp.lpSum([self.efficiency*prod_vars_plus[t1][i+2] + 1/self.efficiency*prod_vars_moins[t1][i+2] for t1 in range(self.depart["fast"][i])])), constraintName
        for t in range(self.horizon):
            var_name = "sortieplus" + str(t)
            sortieplus[t] = pulp.LpVariable(var_name, 0, None)
            # sortie plus
            constraintName = "sortie correcteplus" + str(t)
            lp += prod_vars_plus[t][0] + prod_vars_moins[t][0] +prod_vars_plus[t][1] + prod_vars_moins[t][1]+prod_vars_plus[t][2] + prod_vars_moins[t][2]+prod_vars_plus[t][3] + prod_vars_moins[t][3] <= sortieplus[t], constraintName

        for t in range(self.horizon):
            var_name = "puissancemaximale" + str(t)
            lp += pulp.lpSum([prod_vars_plus[t][i]+prod_vars_moins[t][i] for i in range (4)])<=self.pmax_station, var_name
        lp.setObjective(pulp.lpSum([5*amende[i] for i in range(4)]) +
                        self.dt*pulp.lpSum([self.prices["purchase"][t]*sortieplus[t] +
                                            self.prices["sale"][t] * (prod_vars_plus[t][0] + prod_vars_moins[t][0] +prod_vars_plus[t][1] + prod_vars_moins[t][1]+prod_vars_plus[t][2] + prod_vars_moins[t][2]+prod_vars_plus[t][3] + prod_vars_moins[t][3]-sortieplus[t]) for t in range(self.horizon)]))
        lp.solve()
        print("Status:", LpStatus[lp.status], "\n")

        #Répartition des valeurs dans les listes

        Slow0 = []; Slow1 = []; Fast0 = []; Fast1 = []; Ltotal = []; AmendeFinale = []
        for i in range(self.horizon):
            Slow0.append(Slow0plus[i].varValue + Slow0moins[i].varValue)
            Slow1.append(Slow1plus[i].varValue + Slow1moins[i].varValue)
            Fast0.append(Fast0plus[i].varValue + Fast0moins[i].varValue)
            Fast1.append(Fast1plus[i].varValue + Fast1moins[i].varValue)
            Ltotal.append(Slow0[i]+Slow1[i]+Fast0[i]+Fast1[i])
            self.grid_relative_load[i] = Ltotal[i]
            if i < self.arrival["slow"][0]:
                self.battery_stock["slow"][i][0] = self.dt*sum(Slow0plus[k].varValue*self.efficiency + 1/self.efficiency*Slow0moins[k].varValue for k in range(i))
            if i < self.arrival["slow"][1]:
                self.battery_stock["slow"][i][1] = self.dt*sum(Slow1plus[k].varValue*self.efficiency + 1/self.efficiency*Slow1moins[k].varValue for k in range(i))
            if i < self.arrival["fast"][0]:
                self.battery_stock["fast"][i][0] = self.dt*sum(Fast0plus[k].varValue*self.efficiency + 1/self.efficiency*Fast0moins[k].varValue for k in range(i))
            if i < self.arrival["fast"][1]:
                self.battery_stock["fast"][i][1] = self.dt*sum(Fast1plus[k].varValue*self.efficiency + 1/self.efficiency*Fast1moins[k].varValue for k in range(i))
            if i >= self.arrival["slow"][0]:
                self.battery_stock["slow"][i][0] = self.dt*sum(Slow0plus[k].varValue*self.efficiency + 1/self.efficiency*Slow0moins[k].varValue for k in range(i)) - 4
            if i >= self.arrival["slow"][1]:
                self.battery_stock["slow"][i][1] = self.dt*sum(Slow1plus[k].varValue*self.efficiency + 1/self.efficiency*Slow1moins[k].varValue for k in range(i)) - 4
            if i >= self.arrival["fast"][0]:
                self.battery_stock["fast"][i][0] = self.dt*sum(Fast0plus[k].varValue*self.efficiency + 1/self.efficiency*Fast0moins[k].varValue for k in range(i)) - 4
            if i >= self.arrival["fast"][1]:
                self.battery_stock["fast"][i][1] = self.dt*sum(Fast1plus[k].varValue*self.efficiency + 1/self.efficiency*Fast1moins[k].varValue for k in range(i)) - 4
        for i in range(4):
            AmendeFinale.append(Amende[i].varValue)
        L = [Slow0,Slow1,Fast0,Fast1,Ltotal,AmendeFinale]
        print("The Max Value = ", value(lp.objective))
        print("prodvarplus0 =", prod_vars_plus[0][0].varValue)
        print("prodvarplus1 =", prod_vars_plus[0][1].varValue)
        print("prodvarplus2 =", prod_vars_plus[0][2].varValue)
        print("prodvarplus3 =", prod_vars_plus[0][3].varValue)
        return L






    def take_decision(self, time):
        #Exemple : simple politics
        load_battery = {"fast" : np.zeros(2),"slow" : np.zeros(2)}
        #if time<6*2:
        #    load_battery = {"fast" : 17*np.ones(2),"slow" : 3*np.ones(2)}
            #From 0 am to 6 am we charge as fast as we can
        #if time>18*2:
        #    load_battery = {"fast" : -17*np.ones(2),"slow" : -3*np.ones(2)}
            #From 6 pm to 12pm we sell the stock we have
        # TO BE COMPLETED
        # Be carefull if the sum in load_battery is over pmax_station = 40 then the cars wont be charged as you want.
        # Have to return load_battery to put in update_batterie_stock to get the load.
        # load_battery must be in the following format : {"fast" : [load_car_fast_1,load_car_fast_2],"slow" : [load_car_slow_1,load_car_slow_2]}
        return load_battery

    def update_battery_stock(self,time,load_battery):

        self.nb_cars(time) # We check what cars is here

        p_max = {"slow" : [3*self.here["slow"][0],3*self.here["slow"][1]], "fast" : [22*self.here["fast"][0],22*self.here["fast"][1]]}

        c_max = {"slow" : [40*self.here["slow"][0],40*self.here["slow"][1]], "fast" : [40*self.here["fast"][0],40*self.here["fast"][1]]}

        # p_max and c_max depend on whether the car is here or not.
        self.p_station = 0
        for speed in ["slow","fast"] :
            for i in range(2):
                if abs(load_battery[speed][i]) > p_max[speed][i]:
                    load_battery[speed][i] = p_max[speed][i]*np.sign(load_battery[speed][i])
            # Can't put more power than p_max


        new_stock = { "slow" : [0,0], "fast" : [0,0] }

        new_stock["slow"][0] = self.battery_stock["slow"][time][0] + (self.efficiency*max(0,load_battery["slow"][0])+min(0,load_battery["slow"][0])/self.efficiency)*self.dt
        new_stock["slow"][1] = self.battery_stock["slow"][time][1] + (self.efficiency*max(0,load_battery["slow"][1])+min(0,load_battery["slow"][1])/self.efficiency)*self.dt
        # We update the new stock of each batteries "slow"

        new_stock["fast"][0]=self.battery_stock["fast"][time][0] + (self.efficiency*max(0,load_battery["fast"][0])+min(0,load_battery["fast"][0])/self.efficiency)*self.dt
        new_stock["fast"][1]=self.battery_stock["fast"][time][1] + (self.efficiency*max(0,load_battery["fast"][1])+min(0,load_battery["fast"][1])/self.efficiency)*self.dt
        # We update the new stock of each batteries "fast"


        for speed in ["slow","fast"] :
            for i in range(2):
                if new_stock[speed][i] < 0:
                    load_battery[speed][i] = -(self.battery_stock[speed][time][i])/(self.efficiency*self.dt)
                    new_stock[speed][i] = 0
            # We can't discharge the batterie under 0

                elif new_stock[speed][i] > c_max[speed][i]:
                    load_battery[speed][i] = (c_max[speed][i] - self.battery_stock[speed][time][i] ) / (self.efficiency*self.dt)
                    new_stock[speed][i] = c_max[speed][i]
            # We can't charge the batteries over their maximum capacities

        for speed in ["slow","fast"] :
            for i in range(2):
                if abs(load_battery[speed][i]) > p_max[speed][i]:
                    load_battery[speed][i] = p_max[speed][i]*np.sign(load_battery[speed][i])
            # Can't put more power than p_max
                self.p_station += load_battery[speed][i]
                if self.p_station > self.pmax_station:
                    load_battery[speed][i]-= self.p_station - self.pmax_station
                    self.p_station = self.pmax_station
            #Can't put more power than the station can take : pmax_station = 40
        for speed in ["slow","fast"] :
            for i in range(2):
                if self.here[speed][i]==0:
                    new_stock[speed][i]=self.battery_stock[speed][time][i]
                if time == self.arrival[speed][i]:
                    if self.battery_stock[speed][time][i]>4:
                        new_stock[speed][i] = self.battery_stock[speed][time][i]-4
                    else :
                        new_stock[speed][i] = 0
                    # When the cars comes back it has lost 4 kWh in the battery
                self.battery_stock[speed][time+1][i]=new_stock[speed][i]
            # Update of batteries stocks
                self.load_battery_periode[speed][time][i] = load_battery[speed][i]

        return load_battery # We return load_battery clear of the player's potential mistakes




    def nb_cars(self,time):
        s = 0
        for i in range(self.nb_slow_max):
            if (self.depart["slow"][i]<time) and (self.arrival["slow"][i]>time):
                self.here["slow"][i]=0
            else:
                self.here["slow"][i]=1
                s+=1
        f = 0
        for j in range(self.nb_fast_max):
            if (self.depart["fast"][j]<time) and (self.arrival["fast"][j]>time):
                self.here["fast"][j]=0
            else:
                self.here["fast"][j]=1
                f+=1
        self.nb_slow = s
        self.nb_fast = f
        # Acctualise how many cars and which are at the station at t = time.


    def compute_penalty(self,time):
        for speed in ["slow","fast"] :
            for i in range(2):
                if time == self.depart[speed][i] and self.battery_stock[speed][time][i]/40 < 0.25:
                    self.bill[time]+=5
                    self.penalty[time]+=5

        # If at the departure time of the veicule its battery isn't charged at least at 25% then you pay a 5e fine

    def compute_all_load(self):
        self.take_the_correct_decision()
        return self.grid_relative_load

    def compute_load(self, time, data):

        for i in range(4):   #the players discovers in live if the car is leaving or returning in the station
            if data["departures"][i]==1 and i<2:
                self.depart["slow"][i]=time
            if data["departures"][i]==1 and i>1:
                self.depart["fast"][i-2]=time

            if data["arrivals"][i]==1 and i<2:
                self.arrival["slow"][i]=time
            if data["arrivals"][i]==1 and i>1:
                self.arrival["fast"][i-2]=time

        load_battery = self.take_decision(time) # How you charge or discharge is the players choice
        load = self.update_battery_stock(time, load_battery)
        for i in range(2):
            self.load[time] += load["slow"][i] + load["fast"][i]
        self.compute_penalty(time)
        return self.load[time]


    def observe(self, time, data, price, imbalance,grid_relative_load):

        self.prices["purchase"].append(price["purchase"])
        self.prices["sale"].append(price["sale"])

        self.imbalance["purchase_cover"].append(imbalance["purchase_cover"])
        self.imbalance["sale_cover"].append(imbalance["sale_cover"])

        self.grid_relative_load[time]=grid_relative_load

    def reset(self):
        self.bill = np.zeros(self.horizon)
        self.penalty=np.zeros(self.horizon)
        self.grid_relative_load=np.zeros(self.horizon)
        self.load = np.zeros(self.horizon)
        self.load_battery_periode = {"fast" : np.zeros((self.horizon,2)),"slow" : np.zeros((self.horizon,2))}

        last_bat = {"slow": self.battery_stock["slow"][-1,:], "fast": self.battery_stock["fast"][-1,:]}
        self.battery_stock = {"slow" : np.zeros((self.horizon+1,2)), "fast" : np.zeros((self.horizon+1,2))}
        self.battery_stock["slow"][0] = last_bat["slow"]
        self.battery_stock["fast"][0] = last_bat["fast"]


        self.nb_slow = 2
        self.nb_fast = 2
        self.here = {"slow" : np.ones(2), "fast" : np.ones(2)}
        self.depart = {"slow" : np.array([self.horizon-1,self.horizon-1]), "fast" : np.array([self.horizon-1,self.horizon-1])}
        self.arrival = {"slow" : np.array([self.horizon-1,self.horizon-1]), "fast" : np.array([self.horizon-1,self.horizon-1])}
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}
        self.p_station = 0


def verification(player,tai) :
    #tai =li
    cout = 0
    peauc=player.efficiency
    peaud=player.efficiency
    horaire=[[0,0],[0,0],[0,0],[0,0]]
    for j in range (2) :
        horaire[j][0]=player.depart["slow"][j]
        horaire[j + 2][0] = player.depart["fast"][j]
        horaire[j][1] = player.arrival["slow"][j]
        horaire[j+2][1] = player.arrival["fast"][j]
    batterie=np.zeros(player.horizon + 1)
    for i in range (48):
        li = 0
        heure=i
        for j in range (4):
            if (heure == horaire[j][0] ):
                if batterie[j] <= 10 : cout+=5
                if batterie[j] < 4 :
                    print('erreur batterie pas assez chargée')

                    return(0)
            if heure >= horaire[j][0] and heure < horaire[j][1]:
                if tai[j][i] !=0 :
                    print('erreur impossible de charger la voiture si elle n est pas sur la station')
                    return(0)
            if heure == horaire[j][1]:
                    batterie[j] -= 4
                ##modification de la batterie
            if tai[j][i]>0: ##les deux premières voitures sont à pmax
                if j<2 :
                    if peauc*tai[j][i]>player.pmax_fast :
                        print("erreur puissance maximale dépassée pour une voiture")
                        print(i)
                        return(0)
                    else : batterie[j] += peauc*tai[j][i]*0.5
                else :
                    if peauc*tai[j][i]> player.pmax_slow :
                        print("erreur puissance maximale dépassée pour une voiture")

                        return(0)
                    else : batterie[j] += peauc*tai[j][i]*0.5
            else :   ##les deux premières voitures sont à pmax
                if j < 2:
                    if -1/peaud * tai[j][i] > player.pmax_fast:
                        print("erreur puissance maximale dépassé pour une voiture")
                        return (0)
                    else:
                        batterie[j] += 1/peauc * tai[j][i]*0.5
                else:
                    if peaud * tai[j][i] > player.pmax_slow:
                        print("erreur puissance maximale dépassé pour une voiture")
                        return (0)
                    else:
                        batterie[j] += 1/peaud * tai[j][i]*0.5
            if batterie[j] <0 or batterie[j]>40:
                print('erreur capacité de la batterie non respectée')
                return(0)
            li+=tai[j][i]
        liplus=max(sum(tai[j][i] for j in range (4)),0)
        limoins=min(sum(tai[j][i] for j in range (4)),0)
        cout += liplus*player.prices["purchase"][i]+limoins*player.prices["sale"][i]
        if (abs(li)>40) :
            print ('erreur trop d echange d electricite avec l exterieur')
            return(0)
    return(cout)


if __name__ == '__main__':
    #Exécution de la fonction

    Myplayer = Player()

    ##verification du profil "correct" calculé
    print("\nVerification des contraintes pour load 'pulp':")
    load_pulp = Myplayer.take_the_correct_decision()
    verification(Myplayer, load_pulp)

    ##verification du profil "correct" calculé
    print("\nVerification des contraintes pour load 'decision simple':")
    load_simple = Myplayer.take_a_simple_decision()
    verification(Myplayer, load_simple)