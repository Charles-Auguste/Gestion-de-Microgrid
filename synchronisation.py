import numpy as np
import os
from numpy.random import randint
from pulp import *

import player_charging_station
import player_data_center
import player_industrial_consumer
import player_solar_farm

Chargings = player_charging_station.Player()
SOL = player_solar_farm.Player()
Ind= player_industrial_consumer.Player()
Dat = player_data_center.Player()


def take_the_correct_decision(Charging,Solar,industrial,Data,alpha_autonomie):
    lp = pulp.LpProblem("optimisation.lp", LpMinimize)
    lp.setSolver()
    prod_vars_plus_solar_farm = {}
    prod_vars_moins_solar_farm = {}
    plus_solar_farm = []
    moins_solar_farm = []
    sortieplus_solar_farm = {}
    for t in range(Solar.horizon):
        var_name = "lbatplus1" + str(t)
        prod_vars_plus_solar_farm[t] = pulp.LpVariable(var_name, 0, 1 / Solar.efficiency * Solar.pmax)
        plus_solar_farm.append(prod_vars_plus_solar_farm[t])
        var_name = "sortieplus1" + str(t)
        sortieplus_solar_farm[t] = pulp.LpVariable(var_name, 0, None)
        var_name = "lbatmoins1" + str(t)
        prod_vars_moins_solar_farm[t] = pulp.LpVariable(var_name, -Solar.efficiency * Solar.pmax, 0)
        moins_solar_farm.append(prod_vars_moins_solar_farm[t])

        # condition de la batterie entre 0 et 100
        constraintName = "batterie inferieur 100 1" + str(t)
        lp += Solar.dt * pulp.lpSum(
            [(Solar.efficiency * prod_vars_plus_solar_farm[t1] + 1 / Solar.efficiency * prod_vars_moins_solar_farm[t1])
             for t1 in range(t + 1)]) <= Solar.capacity, constraintName
        constraintName = "batterie superieur a 0 1" + str(t)
        lp += Solar.dt * pulp.lpSum(
            [(Solar.efficiency * prod_vars_plus_solar_farm[t1] + 1 / Solar.efficiency * prod_vars_moins_solar_farm[t1])
             for t1 in range(t + 1)]) >= 0.0, constraintName

        # sortie plus
        constraintName = "sortie correcteplus1" + str(t)
        lp += prod_vars_plus_solar_farm[t] - Solar.sun[t] * Solar.taille / 1000 + prod_vars_moins_solar_farm[t] <= \
              sortieplus_solar_farm[t], constraintName



    prod_vars_plus_industrial_consumer = {}
    prod_vars_moins_industrial_consumer = {}
    plus_industrial_consumer = []
    moins_industrial_consumer = []
    sortieplus_industrial_consumer = {}
    for t in range(industrial.horizon):
        var_name = "lbatplus2" + str(t)
        prod_vars_plus_industrial_consumer[t] = pulp.LpVariable(var_name, 0,
                                                                1 / industrial.efficiency * industrial.pmax)
        plus_industrial_consumer.append(prod_vars_plus_industrial_consumer[t])
        var_name = "sortieplus2" + str(t)
        sortieplus_industrial_consumer[t] = pulp.LpVariable(var_name, 0, None)
        var_name = "lbatmoins2" + str(t)
        prod_vars_moins_industrial_consumer[t] = pulp.LpVariable(var_name, -industrial.efficiency * industrial.pmax, 0)
        moins_industrial_consumer.append(prod_vars_moins_industrial_consumer[t])

        # condition de la batterie entre 0 et 100
        constraintName = "batterie inferieur 100 2" + str(t)
        lp += industrial.dt * pulp.lpSum([(industrial.efficiency * prod_vars_plus_industrial_consumer[
            t1] + 1 / industrial.efficiency * prod_vars_moins_industrial_consumer[t1]) for t1 in
                                          range(t + 1)]) <= industrial.capacity, constraintName
        constraintName = "batterie superieur a 0 2" + str(t)
        lp += industrial.dt * pulp.lpSum([(industrial.efficiency * prod_vars_plus_industrial_consumer[
            t1] + 1 / industrial.efficiency * prod_vars_moins_industrial_consumer[t1]) for t1 in
                                          range(t + 1)]) >= 0.0, constraintName

        # sortie plus
        constraintName = "sortie correcteplus 2" + str(t)
        lp += prod_vars_plus_industrial_consumer[t] + industrial.demand[t] + prod_vars_moins_industrial_consumer[t] <= \
              sortieplus_industrial_consumer[t], constraintName


    prod_vars_plus_charging_station = {}
    prod_vars_moins_charging_station = {}
    amende = {}
    sortieplus_charging_station = {}
    Slow0plus = [];
    Slow0moins = [];
    Slow1plus = [];
    Slow1moins = [];
    Fast0plus = [];
    Fast0moins = [];
    Fast1plus = [];
    Fast1moins = []
    for t in range(Charging.horizon):
        prod_vars_moins_charging_station[t] = {}
        prod_vars_plus_charging_station[t] = {}
        for i in range(2):
            # creation des variables
            ###########################################################
            ## remplacer varname par signe
            var_name = "prod_" + str(t) + "_" + "slow" + str(i) + "plus"
            prod_vars_plus_charging_station[t][i] = pulp.LpVariable(var_name, 0.0,
                                                                    1 / Charging.efficiency * Charging.pmax_slow)
            if i == 0:
                Slow0plus.append(prod_vars_plus_charging_station[t][i])
            if i == 1:
                Slow1plus.append(prod_vars_plus_charging_station[t][i])
            var_name = "prod_" + str(t) + "_" + "slow" + str(i) + "moins"
            prod_vars_moins_charging_station[t][i] = pulp.LpVariable(var_name,
                                                                     -1 * Charging.efficiency * Charging.pmax_slow, 0)
            if i == 0:
                Slow0moins.append(prod_vars_moins_charging_station[t][i])
            if i == 1:
                Slow1moins.append(prod_vars_moins_charging_station[t][i])
            # batterie entre 0 et 40

            if t < Charging.depart["slow"][i]:
                constraintName = "batterie inferieur 40" + str(t) + "_" + "slow" + str(i)
                lp += (Charging.battery_stock["slow"][0][i] + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                        prod_vars_plus_charging_station[
                                                                                            t1][
                                                                                            i] + 1 / Charging.efficiency *
                                                                                        prod_vars_moins_charging_station[
                                                                                            t1][i] for t1 in range(
                    t + 1)])) <= 40.0, constraintName
                constraintName = "batterie superieur a 0" + str(t) + "_" + "slow" + str(i)
                lp += Charging.battery_stock["slow"][0][i] + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                       prod_vars_plus_charging_station[
                                                                                           t1][
                                                                                           i] + 1 / Charging.efficiency *
                                                                                       prod_vars_moins_charging_station[
                                                                                           t1][i] for t1 in range(
                    t + 1)]) >= 0.0, constraintName
            elif t < Charging.arrival["slow"][i]:
                constraintName = "voiture pas là" + str(t) + "_" + "slow" + str(i) + "moins"
                lp +=  prod_vars_moins_charging_station[t][
                    i] == 0.0, constraintName
                constraintName = "voiture pas là" + str(t) + "_" + "slow" + str(i) +"plus"
                lp += prod_vars_plus_charging_station[t][i]  == 0.0, constraintName

            else:
                constraintName = "batterie inferieur 40" + str(t) + "_" + "slow" + str(i)
                lp += Charging.battery_stock["slow"][0][i] - 4 + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                           prod_vars_plus_charging_station[
                                                                                               t1][
                                                                                               i] + 1 / Charging.efficiency *
                                                                                           prod_vars_moins_charging_station[
                                                                                               t1][i] for t1 in range(
                    t + 1)]) <= 40.0, constraintName
                constraintName = "batterie superieur a 0" + str(t) + "_" + "slow" + str(i)
                lp += Charging.battery_stock["slow"][0][i] - 4 + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                           prod_vars_plus_charging_station[
                                                                                               t1][
                                                                                               i] + 1 / Charging.efficiency *
                                                                                           prod_vars_moins_charging_station[
                                                                                               t1][i] for t1 in range(
                    t + 1)]) >= 0.0, constraintName

        for i in range(2):
            var_name = "prod_" + str(t) + "_" + "fast" + str(i) + "plus"
            prod_vars_plus_charging_station[t][i + 2] = pulp.LpVariable(var_name, 0.0,
                                                                        1 / Charging.efficiency * Charging.pmax_fast)
            if i == 0:
                Fast0plus.append(prod_vars_plus_charging_station[t][i + 2])
            if i == 1:
                Fast1plus.append(prod_vars_plus_charging_station[t][i + 2])
            var_name = "prod_" + str(t) + "_" + "fast" + str(i) + "moins"
            prod_vars_moins_charging_station[t][i + 2] = pulp.LpVariable(var_name,
                                                                         -Charging.efficiency * Charging.pmax_fast, 0.0)
            if i == 0:
                Fast0moins.append(prod_vars_moins_charging_station[t][i + 2])
            if i == 1:
                Fast1moins.append(prod_vars_moins_charging_station[t][i + 2])
            if t < Charging.depart["fast"][i]:
                constraintName = "batterie inferieur 40" + str(t) + "_" + "fast" + str(i)
                lp += Charging.battery_stock["fast"][0][i] + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                       prod_vars_plus_charging_station[
                                                                                           t1][
                                                                                           i + 2] + 1 / Charging.efficiency *
                                                                                       prod_vars_moins_charging_station[
                                                                                           t1][i + 2] for t1 in range(
                    t + 1)]) <= 40.0, constraintName
                constraintName = "batterie superieur a 0" + str(t) + "_" + "fast" + str(i)
                lp += Charging.battery_stock["fast"][0][i] + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                       prod_vars_plus_charging_station[
                                                                                           t1][
                                                                                           i + 2] + 1 / Charging.efficiency *
                                                                                       prod_vars_moins_charging_station[
                                                                                           t1][i + 2] for t1 in range(
                    t + 1)]) >= 0.0, constraintName
            elif t < Charging.arrival["fast"][i]:
                constraintName = "voiture pas là" + str(t) + "_" + "fast" + str(i)+ "moins"
                lp += prod_vars_moins_charging_station[t][
                    i + 2] == 0.0, constraintName

                constraintName = "voiture pas là" + str(t) + "_" + "fast" + str(i) + "plus"
                lp += prod_vars_plus_charging_station[t][i + 2] == 0.0, constraintName
            else:
                constraintName = "batterie inferieur 40" + str(t) + "_" + "fast" + str(i)
                lp += Charging.battery_stock["fast"][0][i] - 4 + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                           prod_vars_plus_charging_station[
                                                                                               t1][
                                                                                               i + 2] + 1 / Charging.efficiency *
                                                                                           prod_vars_moins_charging_station[
                                                                                               t1][i + 2] for t1 in
                                                                                           range(
                                                                                               t + 1)]) <= 40.0, constraintName
                constraintName = "batterie superieur a 0" + str(t) + "_" + "fast" + str(i)
                lp += Charging.battery_stock["fast"][0][i] - 4 + Charging.dt * pulp.lpSum([Charging.efficiency *
                                                                                           prod_vars_plus_charging_station[
                                                                                               t1][
                                                                                               i + 2] + 1 / Charging.efficiency *
                                                                                           prod_vars_moins_charging_station[
                                                                                               t1][i + 2] for t1 in
                                                                                           range(
                                                                                               t + 1)]) >= 0.0, constraintName

    # amende
    Amende = []
    for i in range(2):
        var_name = "amendeslow" + str(i)
        amende[i] = pulp.LpVariable(var_name, cat="Binary")
        Amende.append(amende[i])
        constraintName = "amende" + " slow" + str(i)
        lp += 10 * amende[i] >= 10 - (Charging.battery_stock["slow"][0][i] + Charging.dt * pulp.lpSum([
                                                                                                          Charging.efficiency *
                                                                                                          prod_vars_plus_charging_station[
                                                                                                              t1][
                                                                                                              i] + 1 / Charging.efficiency *
                                                                                                          prod_vars_moins_charging_station[
                                                                                                              t1][i] for
                                                                                                          t1 in range(
                Charging.depart["slow"][i])])), constraintName
    for i in range(2):
        var_name = "amendefast" + str(i)
        amende[i + 2] = pulp.LpVariable(var_name, cat="Binary")
        Amende.append(amende[i + 2])
        constraintName = "amende" + " fast" + str(i)
        lp += 10 * amende[i + 2] >= 10 - (Charging.battery_stock["fast"][0][i] + Charging.dt * pulp.lpSum([
                                                                                                              Charging.efficiency *
                                                                                                              prod_vars_plus_charging_station[
                                                                                                                  t1][
                                                                                                                  i + 2] + 1 / Charging.efficiency *
                                                                                                              prod_vars_moins_charging_station[
                                                                                                                  t1][
                                                                                                                  i + 2]
                                                                                                              for t1 in
                                                                                                              range(
                                                                                                                  Charging.depart[
                                                                                                                      "fast"][
                                                                                                                      i])])), constraintName
    for t in range(Charging.horizon):
        var_name = "sortieplus3" + str(t)
        sortieplus_charging_station[t] = pulp.LpVariable(var_name, 0, None)
        # sortie plus
        constraintName = "sortie correcteplus3" + str(t)
        lp += prod_vars_plus_charging_station[t][0] + prod_vars_moins_charging_station[t][0] + \
              prod_vars_plus_charging_station[t][1] + prod_vars_moins_charging_station[t][1] + \
              prod_vars_plus_charging_station[t][2] + prod_vars_moins_charging_station[t][2] + \
              prod_vars_plus_charging_station[t][3] + prod_vars_moins_charging_station[t][3] <= \
              sortieplus_charging_station[t], constraintName

    for t in range(Charging.horizon):
        var_name = "puissancemaximale" + str(t)
        lp += pulp.lpSum([prod_vars_plus_charging_station[t][i] + prod_vars_moins_charging_station[t][i] for i in
                          range(4)]) <= Charging.pmax_station, var_name

    Cost=0
    L=[]
    L2=[]
    for t in range(Data.horizon):
        if Data.prices["purchase"][t] * Data.heat_power[t] <= min(Data.hDC[t], Data.maximum_heat_transfer) * \
                Data.price_selling_water[t]:
            L2.append(1)
            L.append(Data.electric_load[t] + Data.cooling_system[t] + Data.heat_power[t])
            Cost += L[t] * Data.prices["purchase"][t] - min(Data.hDC[t], Data.maximum_heat_transfer) * \
                    Data.price_selling_water[t]
        else:
            L2.append(0)
            L.append(Data.electric_load[t] + Data.cooling_system[t])
            Cost += L[t] * Data.prices["purchase"][t] * Data.dt
    Load_MG_plus={}
    for t in range (Data.horizon) :
        var_name = "Load_mg_plus" + str(t)
        Load_MG_plus[t] = pulp.LpVariable(var_name, 0, None)
        constraintName = "sortie correcteplus4" + str(t)
        lp +=  Load_MG_plus[t]>=prod_vars_plus_charging_station[t][0] + prod_vars_moins_charging_station[t][0] + \
                                prod_vars_plus_charging_station[t][1] + prod_vars_moins_charging_station[t][1] + \
                                prod_vars_plus_charging_station[t][2] + prod_vars_moins_charging_station[t][2] + \
                                prod_vars_plus_charging_station[t][3] + prod_vars_moins_charging_station[t][3] + \
                                prod_vars_plus_industrial_consumer[t] + industrial.demand[t] + prod_vars_moins_industrial_consumer[t] + \
                                prod_vars_plus_solar_farm[t] - Solar.sun[t] * Solar.taille / 1000 + prod_vars_moins_solar_farm[t] + \
                                L[t], constraintName


    # fonction à optimiser
    lp.setObjective(Cost + Solar.dt * (pulp.lpSum([(Solar.prices["purchase"][t] * sortieplus_solar_farm[t] + (prod_vars_plus_solar_farm[t] - Solar.sun[t] * Solar.taille / 1000 + prod_vars_moins_solar_farm[t] - sortieplus_solar_farm[t]) * Solar.prices["sale"][t]) for t in range(Solar.horizon)]))\
                    + industrial.dt * (pulp.lpSum([(industrial.prices["purchase"][t] * sortieplus_industrial_consumer[t] + (prod_vars_plus_industrial_consumer[t] + industrial.demand[t] + prod_vars_moins_industrial_consumer[t] - sortieplus_industrial_consumer[t]) * industrial.prices["sale"][t]) for t in range(industrial.horizon)]))\
                    +pulp.lpSum([5*amende[i] for i in range(4)]) +
                        Charging.dt * pulp.lpSum([Charging.prices["purchase"][t] * sortieplus_charging_station[t] +
                                                  Charging.prices["sale"][t] * (prod_vars_plus_charging_station[t][0] + prod_vars_moins_charging_station[t][0] + prod_vars_plus_charging_station[t][1] + prod_vars_moins_charging_station[t][1] + prod_vars_plus_charging_station[t][2] + prod_vars_moins_charging_station[t][2] + prod_vars_plus_charging_station[t][3] + prod_vars_moins_charging_station[t][3] - sortieplus_charging_station[t]) for t in range(Charging.horizon)])\
                    +alpha_autonomie * (pulp.lpSum(2*Load_MG_plus[t]-(prod_vars_plus_charging_station[t][0] + prod_vars_moins_charging_station[t][0] + \
                                prod_vars_plus_charging_station[t][1] + prod_vars_moins_charging_station[t][1] + \
                                prod_vars_plus_charging_station[t][2] + prod_vars_moins_charging_station[t][2] + \
                                prod_vars_plus_charging_station[t][3] + prod_vars_moins_charging_station[t][3] + \
                                prod_vars_plus_industrial_consumer[t] + industrial.demand[t] + prod_vars_moins_industrial_consumer[t] + \
                                prod_vars_plus_solar_farm[t] - Solar.sun[t] * Solar.taille / 1000 + prod_vars_moins_solar_farm[t] + \
                                L[t]) for t in range (Data.horizon))))
    lp.solve()



    Slow0 = [];
    Slow1 = [];
    Fast0 = [];
    Fast1 = [];
    Ltotal = [];
    AmendeFinale = []
    for i in range(Charging.horizon):
        Slow0.append(Slow0plus[i].varValue + Slow0moins[i].varValue)
        Slow1.append(Slow1plus[i].varValue + Slow1moins[i].varValue)
        Fast0.append(Fast0plus[i].varValue + Fast0moins[i].varValue)
        Fast1.append(Fast1plus[i].varValue + Fast1moins[i].varValue)
        Ltotal.append(Slow0[i] + Slow1[i] + Fast0[i] + Fast1[i])
        Charging.grid_relative_load[i] = Ltotal[i]
        if i < Charging.arrival["slow"][0]:
            Charging.battery_stock["slow"][i][0] = Charging.dt * sum(
                Slow0plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Slow0moins[k].varValue for k in
                range(i))
        if i < Charging.arrival["slow"][1]:
            Charging.battery_stock["slow"][i][1] = Charging.dt * sum(
                Slow1plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Slow1moins[k].varValue for k in
                range(i))
        if i < Charging.arrival["fast"][0]:
            Charging.battery_stock["fast"][i][0] = Charging.dt * sum(
                Fast0plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Fast0moins[k].varValue for k in
                range(i))
        if i < Charging.arrival["fast"][1]:
            Charging.battery_stock["fast"][i][1] = Charging.dt * sum(
                Fast1plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Fast1moins[k].varValue for k in
                range(i))
        if i >= Charging.arrival["slow"][0]:
            Charging.battery_stock["slow"][i][0] = Charging.dt * sum(
                Slow0plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Slow0moins[k].varValue for k in
                range(i)) - 4
        if i >= Charging.arrival["slow"][1]:
            Charging.battery_stock["slow"][i][1] = Charging.dt * sum(
                Slow1plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Slow1moins[k].varValue for k in
                range(i)) - 4
        if i >= Charging.arrival["fast"][0]:
            Charging.battery_stock["fast"][i][0] = Charging.dt * sum(
                Fast0plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Fast0moins[k].varValue for k in
                range(i)) - 4
        if i >= Charging.arrival["fast"][1]:
            Charging.battery_stock["fast"][i][1] = Charging.dt * sum(
                Fast1plus[k].varValue * Charging.efficiency + 1 / Charging.efficiency * Fast1moins[k].varValue for k in
                range(i)) - 4
    for i in range(4):
        AmendeFinale.append(Amende[i].varValue)
    L = [Slow0, Slow1, Fast0, Fast1, Ltotal, AmendeFinale]

    Lbat_solar_farm = []
    for i in range(Solar.horizon):
        Lbat_solar_farm.append(plus_solar_farm[i].varValue + moins_solar_farm[i].varValue)
        Solar.battery_stock[i + 1] = sum(
            plus_solar_farm[k].varValue * Solar.efficiency + 1 / Solar.efficiency * moins_solar_farm[k].varValue for k
            in range(i)) * Solar.dt
    for i in range(Solar.horizon):
        Solar.grid_relative_load[i] = Lbat_solar_farm[i] - Solar.sun[i]

    Lbat_industrial_consumer = []
    for i in range(industrial.horizon):
        Lbat_industrial_consumer.append(plus_industrial_consumer[i].varValue + moins_industrial_consumer[i].varValue)
        industrial.battery_stock[i + 1] = sum(
            plus_industrial_consumer[k].varValue * industrial.efficiency + 1 / industrial.efficiency *
            moins_industrial_consumer[k].varValue for k in range(i)) * industrial.dt
    for i in range(industrial.horizon):
        industrial.grid_relative_load[i] = Lbat_industrial_consumer[i] - industrial.demand[i]
    print("The Max Value = ", value(lp.objective))

    return(0)

take_the_correct_decision(Chargings,SOL,Ind,Dat,1)

