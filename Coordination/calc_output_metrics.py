# -*- coding: utf-8 -*-
"""
Created on Sun May  9 10:50:07 2021

@author: B57876
"""

# Calculate output metrics

# IMPORT
# standard
import os
import sys
import numpy as np
import pandas as pd
import datetime

# Q2OJ : quid si plantage dans le run d'une equipe -> sortie ?
# Qui verifie que les formats des profils de charge sont bons? (taille/type)
# ATTENTION Puissance dans "load" ?
def calc_per_actor_bills(load_profiles: dict, purchase_price: np.ndarray,
                         sale_price: np.ndarray, delta_t_s: int) -> dict:
    """
    Calculate per actor bill
    
    :param load_profiles: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    load profile (kW)
    :param purchase_price: elec. purchase price in €/kWh (>= 0)
    :param sale_price: elec. sale price in €/kWh (>= 0)
    :param delta_t_s: time-slot duration of the considered discrete time model
    :return: returns a dictionary with the same keys as load_profiles and values
    the associated bills
    """
    
    per_actor_bills = {}
    
    # Loop over Industrial Cons. scenarios
    for ic_scen in load_profiles:
        per_actor_bills[ic_scen] = {}
        
        # loop over Data Center scenarios
        for dc_scen in load_profiles[ic_scen]:
            per_actor_bills[ic_scen][dc_scen] = {}
    
            # Loop over PV scenarios
            for pv_scen in load_profiles[ic_scen][dc_scen]:
                per_actor_bills[ic_scen][dc_scen][pv_scen] = {}

                # Loop over EV scenarios
                for ev_scen in load_profiles[ic_scen][dc_scen][pv_scen]:
                    per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen] = {}
                    
                    # Loop over microgrid team names
                    for mg_name in load_profiles[ic_scen][dc_scen][pv_scen][ev_scen]:
                        per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen][mg_name] = {}

                        # Loop over iterations of the current microgrid team
                        for i_iter in load_profiles[ic_scen][dc_scen][pv_scen][ev_scen][mg_name]:
                            per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen][mg_name][i_iter] = {}

                            # Loop over actors of the current microgrid team
                            for actor_name in load_profiles[ic_scen][dc_scen][pv_scen][ev_scen][mg_name][i_iter]:
                                per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen][mg_name][i_iter][actor_name] \
                                   = calculate_bill(load_profiles[ic_scen][dc_scen] \
                                                    [pv_scen][ev_scen][mg_name][i_iter] \
                                                    [actor_name], purchase_price,
                                                    sale_price, delta_t_s)
    
    return per_actor_bills

def calc_microgrid_collective_metrics(load_profiles: dict, contracted_p_tariffs: dict,
                                      delta_t_s: int) -> dict:
    """
    Calculate collective metrics in a microgrid

    :param load_profiles: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    load profile (kW)
    :param contracted_p_tariffs: tariff of contracted power in a dict. with keys
    the threshold (max) power values and values the associated tariff (€/year).
    Note that above the last threshold the tariff is linearly extrapolated based
    on the last two values
    :param delta_t_s: time-slot duration of the considered discrete time model
    :return: returns 3 dict. with the same keys as load_profiles excepting the one
    of the actors and values the aggregated microgrid load prof. and microgrid pmax,
    and a dict. {"pmax_cost": cost of contracted max power, "autonomy_score": score of 
    autonomy measuring how much the microgrid is exchanging energy with the grid}
    """

    microgrid_prof = {}
    microgrid_pmax = {}
    collective_metrics = {}
    
    # Loop over Industrial Cons. scenarios
    for ic_scen in load_profiles:
        microgrid_prof[ic_scen] = {}
        microgrid_pmax[ic_scen] = {}
        collective_metrics[ic_scen] = {}
        
        # loop over Data Center scenarios
        for dc_scen in load_profiles[ic_scen]:
            microgrid_prof[ic_scen][dc_scen] = {}
            microgrid_pmax[ic_scen][dc_scen] = {}
            collective_metrics[ic_scen][dc_scen] = {}
    
            # Loop over PV scenarios
            for pv_scen in load_profiles[ic_scen][dc_scen]:
                microgrid_prof[ic_scen][dc_scen][pv_scen] = {}
                microgrid_pmax[ic_scen][dc_scen][pv_scen] = {}
                collective_metrics[ic_scen][dc_scen][pv_scen] = {}

                # Loop over EV scenarios
                for ev_scen in load_profiles[ic_scen][dc_scen][pv_scen]:
                    microgrid_prof[ic_scen][dc_scen][pv_scen][ev_scen] = {}
                    microgrid_pmax[ic_scen][dc_scen][pv_scen][ev_scen] = {}
                    collective_metrics[ic_scen][dc_scen][pv_scen][ev_scen] = {}
                    
                    # Loop over microgrid team names
                    for mg_name in load_profiles[ic_scen][dc_scen][pv_scen][ev_scen]:
                        microgrid_prof[ic_scen][dc_scen][pv_scen][ev_scen][mg_name] = {}
                        microgrid_pmax[ic_scen][dc_scen][pv_scen][ev_scen][mg_name] = {}
                        collective_metrics[ic_scen][dc_scen][pv_scen][ev_scen][mg_name] = {}

                        # Loop over iterations of the current microgrid team
                        for i_iter in load_profiles[ic_scen][dc_scen][pv_scen][ev_scen][mg_name]:

                            # calculate and save current iteration microgrid prof.
                            current_microgrid_prof = \
                                calculate_microgrid_profile(load_profiles[ic_scen][dc_scen] \
                                                                 [pv_scen][ev_scen][mg_name][i_iter])
                            microgrid_prof[ic_scen][dc_scen][pv_scen][ev_scen] \
                                    [mg_name][i_iter] = current_microgrid_prof
                            
                            # obtain collective metrics based on this profile
                            current_pmax, current_pmax_cost = \
                                calculate_pmax_cost(current_microgrid_prof,
                                                    contracted_p_tariffs)
                            microgrid_pmax[ic_scen][dc_scen][pv_scen][ev_scen][mg_name][i_iter] \
                                = current_pmax
                            collective_metrics[ic_scen][dc_scen][pv_scen][ev_scen][mg_name][i_iter] \
                              = {"pmax_cost": current_pmax_cost,
                                 "autonomy_score": calculate_autonomy_score(current_microgrid_prof,
                                                                            delta_t_s),
                                 "mg_transfo_aging": calculate_transfo_aging(current_microgrid_prof,
                                                                             delta_t_s),
                                 "n_disj": calculate_number_of_disj(current_microgrid_prof,
                                                                    delta_t_s)}
    
    return microgrid_prof, microgrid_pmax, collective_metrics
    
def calculate_bill(load_profile: np.ndarray, purchase_price: np.ndarray,
                   sale_price: np.ndarray, delta_t_s: int) -> float:
    
    return delta_t_s/3600 * sum(np.maximum(load_profile, 0) * purchase_price \
                                    + np.minimum(load_profile, 0) * sale_price)
        
def calculate_microgrid_profile(per_actor_load_prof: dict) -> np.ndarray:
    """
    Calculate microgrid profile based on per-actor ones
    """
    
    return np.sum([per_actor_load_prof[elt] for elt in per_actor_load_prof], axis=0)

def calculate_pmax_cost(daily_microgrid_prof: np.ndarray, 
                        contracted_p_tariffs: dict) -> float:
    """
    Calculate pmax cost (power component in the elec. tariff)
    
    :param daily_microgrid_prof: daily profile of the microgrid, that can be 
    positive or negative
    :param contracted_p_tariffs: dict. with keys the upper power thresholds
    and values the associated tariffs
    :return: returns (pmax, pmax cost)
    """
    
    # get all thresholds values and sort them
    power_thresholds = list(contracted_p_tariffs.keys())
    power_thresholds.sort()

    # if microgrid max. load (power) bigger than pmax values in contract, extrapolate    
    if max(abs(daily_microgrid_prof)) > power_thresholds[-1]:
        return max(abs(daily_microgrid_prof)), \
                    contracted_p_tariffs[power_thresholds[-1]] + \
                (max(abs(daily_microgrid_prof)) - power_thresholds[-1]) \
                 * (contracted_p_tariffs[power_thresholds[-1]] \
                                - contracted_p_tariffs[power_thresholds[-2]]) \
                / (power_thresholds[-1] - power_thresholds[-2])
    # else find the pmax contract threshold corresponding to the microgrid 
    # max. load (power)
    else:
        idx_p_threshold = np.where(power_thresholds \
                                       >= max(abs(daily_microgrid_prof)))[0][0]
        return power_thresholds[idx_p_threshold], \
                        contracted_p_tariffs[power_thresholds[idx_p_threshold]]

def calculate_autonomy_score(daily_microgrid_prof: np.ndarray, delta_t_s: int) -> float:
    """
    Calculate autonomy score
    
    :param daily_microgrid_prof: vector of microgrid daily load profile
    :param delta_t_s: time-slot duration of the considered discrete time model
    :return: returns an "autonomy score", which measures how much the microgrid
    is exchanging elec. with the grid
    """
    
    only_reinj_score = False
    
    # measure only the "reverse flows", from the microgrid to the elec. network
    if only_reinj_score:
        return - delta_t_s/3600 * sum(np.minimum(daily_microgrid_prof, 0))
    # measure all exchanges with the elec. network
    else:
        return delta_t_s/3600 * (sum(np.maximum(daily_microgrid_prof, 0)) \
                                    - sum(np.minimum(daily_microgrid_prof, 0)))

def calculate_transfo_aging(daily_microgrid_prof: np.ndarray, delta_t_s: int) -> float:
    """
    Calculate transformer aging
    
    :param daily_microgrid_prof: vector of microgrid daily load profile
    :param delta_t_s: time-slot duration of the considered discrete time model
    :return: returns transformer aging
    """
    
    # TODO code Clause 7 model, cf. simplified doc. sent to Vineeth
    
    return 40

def calculate_number_of_disj(daily_microgrid_prof: np.ndarray, delta_t_s: int) -> float:
    """
    Calculate number of disjonction of the circuit-breaker, based on an abacus
    
    :param daily_microgrid_prof: vector of microgrid daily load profile
    :param delta_t_s: time-slot duration of the considered discrete time model
    :return: returns number of breaks
    """
    
    # TODO code it based on a typical abacus
    
    return 0

def get_best_team_per_region(per_actor_bills: dict, collective_metrics: dict,
                             coll_metrics_weights: dict) -> dict:

    # TODO: take into account the fact that microgrid with a larger number of 
    # actors necessarily have "bigger" values for the metrics
    """
    Get best microgrid teams per region, and aggregated in France
    
    :param per_actor_bills: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    bill (€)
    :param collective_metrics: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and values a dict. {coll_metric_name: value}
    :param coll_metrics_weights: dict. with keys the name of the different 
    microgrid collective metrics and values the associated weight to be applied
    to compare the microgrid perf. in a given region
    :return: returns the best team (name) in each of the regions
    """
    
    # rule to choose the iteration to fix microgrid perf.
    # allowed values: "last", "best"
    # TODO: code the case for "best" choice, which needs to compare € and autonomy
    # aspects. Add a CO2 emissions metric?
    iter_choice_rule = "last"
    
    # get the list of simulated regions
    regions_simu = get_simulated_regions(per_actor_bills)
    
    # get the list of team names
    team_names = get_team_names(per_actor_bills)
    
    coll_metrics_names = get_coll_metrics_names(collective_metrics)
    
    team_scores = {}
    for team in team_names:
        team_scores[team] = {}
        for region in regions_simu:
            team_scores[team][region] = \
                calculate_team_score(team, region, per_actor_bills,
                                     collective_metrics, coll_metrics_names,
                                     coll_metrics_weights, iter_choice_rule)
    
    # get best team per region
    best_teams_per_region = {}
    for region in regions_simu:
        current_scores = [team_scores[team][region] for team in team_scores]
        current_best = min(current_scores)
        
        # get list of team(s) with best score for current region                                         
        best_teams_per_region[region] = [team for team in team_scores \
                                         if team_scores[team][region] == current_best]
        
    return team_scores, best_teams_per_region, coll_metrics_names

def get_france_team_classif(team_scores: dict) -> dict:
    """
    Get France team classification based on per region scores
    
    :param team_scores: dict. 1. team names ; 2. region names and values the scores
    """
    
    team_names = list(team_scores)

    team_france_scores = {team: sum(team_scores[team].values()) for team in team_scores}
    
    ordered_idx = np.argsort(list(team_france_scores.values()))
    
    france_team_classif = {i+1: (team_france_scores[team_names[ordered_idx[i]]], team_names[ordered_idx[i]]) \
                                       for i in range(len(team_france_scores))}
    
    return team_france_scores, france_team_classif

def get_ic_scenarios(per_actor_bills: dict) -> list:
    
    return list(per_actor_bills)
    
def get_dc_scenarios(per_actor_bills: dict) -> list:

    dc_scenarios = [list(per_actor_bills[ic_scen]) for ic_scen in per_actor_bills]
    
    # check that all IC scenarios have the same DC scenarios
    if not check_if_unique_list(dc_scenarios):
        print("Different IC scenarios does not have the same DC scenarios... -> STOP")
        sys.exit(1)
    
    return dc_scenarios[0]

def get_simulated_regions(per_actor_bills: dict) -> list:
    
    regions_simu = [list(per_actor_bills[ic_scen][dc_scen]) \
                            for ic_scen in per_actor_bills \
                                    for dc_scen in per_actor_bills[ic_scen]]
    
    # check that all IC and DC scenarios have the same PV scenario
    if not check_if_unique_list(regions_simu):
        print("Different (IC,DC) scenarios does not have the same PV scenarios... -> STOP")
        sys.exit(1)
    
    return regions_simu[0]

def get_ev_scenarios(per_actor_bills: dict) -> list:

    ev_scenarios = [list(per_actor_bills[ic_scen][dc_scen][pv_scen]) \
                          for ic_scen in per_actor_bills \
                                for dc_scen in per_actor_bills[ic_scen] \
                                    for pv_scen in per_actor_bills[ic_scen][dc_scen]]
    
    # check that all (IC,DC,PV) scenarios have the same EV scenarios
    if not check_if_unique_list(ev_scenarios):
        print("Different (IC,DC,PV) scenarios does not have the same EV scenarios... -> STOP")
        sys.exit(1)
    
    return ev_scenarios[0]

def get_team_names(per_actor_bills: dict) -> list:

    team_names = [list(per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen]) \
                          for ic_scen in per_actor_bills \
                                for dc_scen in per_actor_bills[ic_scen] \
                                    for pv_scen in per_actor_bills[ic_scen][dc_scen] \
                                        for ev_scen in per_actor_bills[ic_scen][dc_scen][pv_scen]]
    
    # check that all (IC,DC,PV,EV) scenarios have the same team names
    if not check_if_unique_list(team_names):
        print("Different (IC,DC,PV,EV) scenarios does not have the same team names... -> STOP")
        sys.exit(1)
    
    return team_names[0]

def get_coll_metrics_names(collective_metrics):

    # TODO: improve this -> existing Python dict. function?    
    first_ic_scen = list(collective_metrics)[0]
    first_dc_scen = list(collective_metrics[first_ic_scen])[0]
    first_pv_scen = list(collective_metrics[first_ic_scen][first_dc_scen])[0]
    first_ev_scen = list(collective_metrics[first_ic_scen][first_dc_scen] \
                                                             [first_pv_scen])[0]
    first_team = list(collective_metrics[first_ic_scen][first_dc_scen] \
                                              [first_pv_scen][first_ev_scen])[0]
    first_iter = list(collective_metrics[first_ic_scen][first_dc_scen] \
                                    [first_pv_scen][first_ev_scen][first_team])[0]
    
    coll_metrics_names = [list(collective_metrics[ic_scen][dc_scen][pv_scen][ev_scen][team][first_iter]) \
                          for ic_scen in collective_metrics \
                            for dc_scen in collective_metrics[ic_scen] \
                              for pv_scen in collective_metrics[ic_scen][dc_scen] \
                                for ev_scen in collective_metrics[ic_scen][dc_scen][pv_scen] \
                                  for team in collective_metrics[ic_scen][dc_scen][pv_scen][ev_scen]]

    # check that all (IC,DC,PV,EV,team) have the same collective metrics names
    if not check_if_unique_list(coll_metrics_names):
        print("Different (IC,DC,PV,EV,team) does not have the same collective metrics names... -> STOP")
        sys.exit(1)
    
    return coll_metrics_names[0]

def check_if_unique_list(my_list_of_lists: list) -> bool:
    """
    Check if all lists are equal in a list
    """
    
    list_len = len(my_list_of_lists)
    i = 1
    while i < list_len:
        if my_list_of_lists[i] == my_list_of_lists[0]:
            i += 1
        else:
            return False

    return True

def calculate_team_score(team_name: str, region: str, per_actor_bills: dict, 
                         collective_metrics: dict, coll_metrics_names: list,
                         coll_metrics_weights: dict, iter_choice_rule: str) -> float:
    """
    Calculate the score of a team for current run
    
    :param team_name: name of current team
    :param region: current region name, which is equal to PV scenario
    :param per_actor_bills: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    bill (€)
    :param collective_metrics: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and values the associated dict with collective metrics
    :param coll_metrics_names: names of the collective metrics in current results
    N.B. can be "strictly" included in the list of keys of coll_metrics_weights,
    if not all metrics have been used/calc. in this run
    :param coll_metrics_weights: dict. with keys the name of the different 
    microgrid collective metrics and values the associated weight to be applied
    to compare the microgrid perf. in a given region
    :param iter_choice_rule: iteration choice to set the perf. ("last", "best")
    :return: returns the score of current team
    """

    score = 0
    
    # the score is calculated as the weighted sum of the scores over all scenarios
    for ic_scen in per_actor_bills:
        for dc_scen in per_actor_bills[ic_scen]:
            for ev_scen in per_actor_bills[ic_scen][dc_scen][region]:
                if iter_choice_rule == "last":
                    last_iter = list(per_actor_bills[ic_scen][dc_scen] \
                                                     [region][ev_scen][team_name])[-1]
                    
                    score = \
                      calc_total_bill_and_score_fixed_iter(per_actor_bills[ic_scen] \
                               [dc_scen][region][ev_scen][team_name][last_iter],
                             collective_metrics[ic_scen][dc_scen][region] \
                                                [ev_scen][team_name][last_iter],
                                                coll_metrics_names, coll_metrics_weights)[1]
    
                elif iter_choice_rule == "best":
                    score_of_iter = \
                        [calc_total_bill_and_score_fixed_iter(per_actor_bills[ic_scen] \
                               [dc_scen][region][ev_scen][team_name][last_iter],
                             collective_metrics[ic_scen][dc_scen][region] \
                                                [ev_scen][team_name][current_iter],
                                                coll_metrics_names, coll_metrics_weights)[1] \
                                    for current_iter in per_actor_bills[ic_scen] \
                                                [dc_scen][region][ev_scen][team_name]]
                    
                    # add the min. score over all iterations
                    score += min(score_of_iter)
                    
                else:
                    print("Unknown rule to choose iteration for microgrid perf. calculation")

    return score

def calc_total_bill_and_score_fixed_iter(per_actor_bills_fixed_scen_and_iter: dict,
                                         collective_metrics_fixed_scen_and_iter: dict,
                                         coll_metrics_names: list, 
                                         coll_metrics_weights:dict) -> (float, float):
    """
    Calculate total bill in the microgrid based on per-actor ones, for a fixed
    (IC,DC,PV,EV) scenario and a fixed iteration of the price-coordination
    method

    :param per_actor_bills_fixed_scen_and_iter: dict. with keys the names 
    of the different actors of the microgrid and values the associated bills
    :param collective_metrics_fixed_scen_and_iter: dict. with keys the names of
    the used collective metrics and values their value
    :param coll_metrics_names: names of the collective metrics in current results
    N.B. can be "strictly" included in the list of keys of coll_metrics_weights,
    if not all metrics have been used/calc. in this run
    :param coll_metrics_weights: dict. with keys the names of the different
    collective metrics and values the associated weights
    :return: returns total bill and score
    """

    total_bill = sum([per_actor_bills_fixed_scen_and_iter[elt_actor] \
                          for elt_actor in per_actor_bills_fixed_scen_and_iter])
    
    score_of_iter = total_bill \
       + sum([collective_metrics_fixed_scen_and_iter[coll_metric] \
                           * coll_metrics_weights[coll_metric] for coll_metric \
                                                       in coll_metrics_names])
    return total_bill, score_of_iter

def calc_cost_autonomy_tradeoff_last_iter(per_actor_bills: dict, 
                                          collective_metrics: dict) -> dict:

    """
    Calculate cost/autonomy tradeoff
    
    :param per_actor_bills: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    bill (€)
    :param collective_metrics: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and values the associated dict with collective metrics
    :param coll_metrics_names: names of the collective metrics in current results
    N.B. can be "strictly" included in the list of keys of coll_metrics_weights,
    if not all metrics have been used/calc. in this run
    :return: returns a dict. with keys 1. the team names; 2. PV region names and
    values the associated (cost, autonomy score) aggreg. over the set of other
    scenarios
    """
    
    # TODO code case with best iteration
    
    aggreg_operations = {"cost": sum, "autonomy_score": np.mean}
    
    # get team names
    team_names = get_team_names(per_actor_bills)
    # and PV regions
    pv_regions = get_simulated_regions(per_actor_bills)
    
    cost_autonomy_tradeoff = {}
    for team in team_names:
        cost_autonomy_tradeoff[team] = {}
        for region in pv_regions:
            cost_autonomy_tradeoff[team][region] = {"cost": [], "autonomy_score": []}
            for ic_scen in per_actor_bills:
                for dc_scen in per_actor_bills[ic_scen]:
                    for ev_scen in per_actor_bills[ic_scen][dc_scen][region]:
                        last_iter = list(per_actor_bills[ic_scen][dc_scen] \
                                                     [region][ev_scen][team])[-1]
                        # add cost value
                        cost_autonomy_tradeoff[team][region]["cost"] \
                            .append(sum([per_actor_bills[ic_scen][dc_scen] \
                                      [region][ev_scen][team][last_iter][actor] \
                                        for actor in per_actor_bills[ic_scen][dc_scen] \
                                         [region][ev_scen][team][last_iter]]))
                        # and autonomy one
                        cost_autonomy_tradeoff[team][region]["autonomy_score"] \
                          .append(collective_metrics[ic_scen][dc_scen] \
                                   [region][ev_scen][team][last_iter]["autonomy_score"])
            
            # aggreg. cost/autonomy score over all (non PV) scenarios
            cost_autonomy_tradeoff[team][region]["cost"] = \
                aggreg_operations["cost"](cost_autonomy_tradeoff[team][region]["cost"])
            cost_autonomy_tradeoff[team][region]["autonomy_score"] = \
                aggreg_operations["autonomy_score"](cost_autonomy_tradeoff[team][region]["autonomy_score"])
    
    return cost_autonomy_tradeoff

def save_per_region_score_to_csv(team_scores: dict, result_dir: str,
                                 date_of_run: datetime.datetime):
    """
    Save per region score to a .csv file
    
    :param team_scores: dict. with keys 1. team name; 2. region name and values 
    the associated score of the current run
    :param result_dir: full path to the directory where results must be stored
    :param date_of_run: date of current run
    """
    
    # get team and region names
    team_names = list(team_scores)
    regions = [list(team_scores[team]) for team in team_names]
    
    # check that all teams have the same regions scenarios
    if not check_if_unique_list(regions):
        print("Different teams does not have the same region names... -> STOP")
        sys.exit(1)
    else:
        regions = regions[0]

    # initialize dict. of results with "team" and "region" fields
    dict_per_region_scores = {}
    dict_per_region_scores["team"] = list(np.repeat(team_names, len(regions)))
    dict_per_region_scores["region"] = list(np.tile(regions, len(team_names)))
    
    # add the per-region score
    dict_per_region_scores["score"] = \
        [team_scores[team][region] for team in team_names for region in regions]
    
    # save to .csv file
    save_df_to_csv(pd.DataFrame(dict_per_region_scores), ["score"],
                   ["team", "region", "score"], 
                   os.path.join(result_dir, "aggreg_per_region_res_run_%s" \
                                       % date_of_run.strftime("%Y-%m-%d_%H%M")))

def save_all_metrics_to_csv(per_actor_bills: dict, collective_metrics: dict,
                            coll_metrics_names: list, coll_metrics_weights: dict,
                            metrics_not_saved: list, result_dir: str,
                            date_of_run: datetime.datetime):
    """
    Save per region score to a .csv file
    
    :param per_actor_bills: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    bill (€)
    :param collective_metrics: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and values the associated dict with collective metrics
    :param coll_metrics_names: names of the collective metrics in current results
    :param coll_metrics_weights: dict. with keys the names of the different
    collective metrics and values the associated weights
    :param metrics_not_saved: list of collective metrics not to be saved in the
    .csv file
    :param result_dir: full path to the directory where results must be stored
    :param date_of_run: date of current run
    """
    
    dict_all_metrics = {"ic_scen": [], "dc_scen": [], "pv_scen": [], "ev_scen": [],
                        "team": [], "iter": [], "total_bill": []}

    # add collective metrics keys
    coll_metrics_tb_saved = list(set(coll_metrics_names) - set(metrics_not_saved))
    for elt in coll_metrics_tb_saved:
        dict_all_metrics[elt] = []
        
    # fullfill the dict. with a loop (very bad in general, but small here!!)    
    for ic_scen in per_actor_bills:
        for dc_scen in per_actor_bills[ic_scen]:
            for pv_scen in per_actor_bills[ic_scen][dc_scen]:
                for ev_scen in per_actor_bills[ic_scen][dc_scen][pv_scen]:
                    for team_name in per_actor_bills[ic_scen][dc_scen][pv_scen][ev_scen]:
                        for i_iter in per_actor_bills[ic_scen][dc_scen][pv_scen] \
                                                            [ev_scen][team_name]:
                    
                            # scenarios*team*iter
                            dict_all_metrics["ic_scen"].append(ic_scen)
                            dict_all_metrics["dc_scen"].append(dc_scen)
                            dict_all_metrics["pv_scen"].append(pv_scen)
                            dict_all_metrics["ev_scen"].append(ev_scen)
                            dict_all_metrics["team"].append(team_name)
                            dict_all_metrics["iter"].append(i_iter)
                            
                            # total bill
                            dict_all_metrics["total_bill"].append( \
                              calc_total_bill_and_score_fixed_iter(per_actor_bills[ic_scen] \
                                       [dc_scen][pv_scen][ev_scen][team_name][i_iter],
                                     collective_metrics[ic_scen][dc_scen][pv_scen] \
                                                     [ev_scen][team_name][i_iter],
                                                     coll_metrics_names, coll_metrics_weights)[0])
                             
                            # collective metrics
                            for elt in coll_metrics_tb_saved:
                                dict_all_metrics[elt] \
                                  .append(collective_metrics[ic_scen][dc_scen][pv_scen] \
                                                    [ev_scen][team_name][i_iter][elt])
    
    # save to .csv file
    col_order = ["ic_scen", "dc_scen", "pv_scen", "ev_scen", "team", "iter",
                 "total_bill"] + coll_metrics_tb_saved
    save_df_to_csv(pd.DataFrame(dict_all_metrics), ["total_bill"] + coll_metrics_tb_saved,
                   col_order, os.path.join(result_dir, 
                                           "res_run_%s" \
                                               % date_of_run.strftime("%Y-%m-%d_%H%M")))

def save_df_to_csv(df, fields_tb_rounded, col_order, filename):
    """
    Write a pandas dataframe to a .csv file
    """
    
    n_digits_out = 3
        
    # round info
    for elt_col in fields_tb_rounded:
        df[elt_col] = df[elt_col].apply(lambda x: round(x, n_digits_out))    
    
    df.to_csv("%s.csv" % filename, columns=col_order, sep=";",
              decimal=".", index=False)

def get_improvement_traj(current_dir: str, list_of_run_dates: list, team_names: list):
    """
    Get improvement trajectories (in terms of scores) of the different teams
    based on a list of run dates
    
    :param current_dir: full path to the dir. where all runs results are saved
    :param list_of_run_dates: list of dates for which a run has been processed
    :param team_names: list of teams to be considered
    """
    
    # initialize score trajectories
    scores_traj = {team: {} for team in team_names}
    
    # loop over run folders
    for run_date in list_of_run_dates:
        try:
            current_df = pd.read_csv(os.path.join(current_dir,
                                                  "run_%s" % run_date.strftime("%Y-%m-%d_%H%M"),
                                                  "aggreg_per_region_res_run_%s.csv" \
                                                  % run_date.strftime("%Y-%m-%d_%H%M")),
                                     sep=";", decimal=".")
            for team in team_names:
                # score of current run is the sum of scores over all regions
                scores_traj[team][run_date] = \
                            sum(list(current_df[current_df["team"]==team]["score"]))
        except:
            pass
    
    return scores_traj      
                                
if __name__ == "__main__":
   
    result_dir = os.getcwd()
    date_of_run = datetime.datetime.now()

    n_ts = 10
    load_profiles = {1: 
                       {1: 
                          {"h3": 
                                {1: 
                                   {"team1": 
                                            {1: 
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)},
                                             2:
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)},
                                             3:
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)}
                                             },
                                    "team2":
                                            {1: 
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)},
                                             2:
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)},
                                             3:
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)},
                                             4:
                                               {"solar_farm": np.random.rand(n_ts),
                                                "industrial_consumer": np.random.rand(n_ts),
                                                "charging_station": np.random.rand(n_ts),
                                                "data_center": np.random.rand(n_ts)}
                                             },
                                   }
                               }
                         }
                      }
                     }
    
    # Test per-actor bill calculation
    purchase_price = 0.10 + 0.1 * np.random.rand(n_ts)
    sale_price = 0.05 + 0.1 * np.random.rand(n_ts)
    delta_t_s = 1800
    per_actor_bills = calc_per_actor_bills(load_profiles, purchase_price,
                                           sale_price, delta_t_s)
    print("first per-actor bill (eur): ", 
          per_actor_bills[1][1]["h3"][1]["team1"][1]["solar_farm"])
    
    # Test collective metrics calculation
    contracted_p_tariffs = {6: 123.6, 9: 151.32, 12: 177.24, 15: 201.36,
                            18: 223.68, 24: 274.68, 30: 299.52, 36: 337.56}
    microgrid_prof, microgrid_pmax, collective_metrics = \
            calc_microgrid_collective_metrics(load_profiles, contracted_p_tariffs, 
                                              delta_t_s)
    print("first collective metric (eur/year, kWh): ",
          collective_metrics[1][1]["h3"][1]["team1"][1])
    
    # Get best team per region
    coll_metrics_weights = {"pmax_cost": 1/365, "autonomy_score": 1,
                            "mg_transfo_aging": 0, "n_disj": 0}
    team_scores, best_teams_per_region, coll_metrics_names = \
            get_best_team_per_region(per_actor_bills, collective_metrics,
                                     coll_metrics_weights)
    
    # save detailed results to a .csv file
    metrics_not_saved = ["mg_transfo_aging", "n_disj"]
    save_all_metrics_to_csv(per_actor_bills, collective_metrics, coll_metrics_names,
                            coll_metrics_weights, metrics_not_saved, result_dir,
                            date_of_run)
    
    # and aggreg. per region .csv file
    save_per_region_score_to_csv(team_scores, result_dir, date_of_run)