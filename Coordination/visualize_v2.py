# -*- coding: utf-8 -*-
"""
Created on Mon May 17 06:05:12 2021

@author: B57876
"""

# Visualization + save outputs of a run
# IMPORT
# standard
import os
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
# perso
from create_ppt_summary_of_run import create_current_run_dir, create_summary_of_run_ppt
from calc_output_metrics import calc_per_actor_bills, calc_microgrid_collective_metrics, \
               calc_cost_autonomy_tradeoff_last_iter, get_best_team_per_region, \
               get_france_team_classif, save_all_metrics_to_csv, save_per_region_score_to_csv, \
               get_improvement_traj


# TODO get data from simu OJ format

def generate_pptx(data, pv_profiles):
    current_dir = os.getcwd()
    date_of_run = datetime.datetime.now()
    idx_run = 1
    
    # create directory for current run
    result_dir = create_current_run_dir(current_dir, date_of_run)

    # images used for some slides    
    regions_map_file = os.path.join(current_dir, "images", "pv_regions_no_names.png")
    podium_france_file = os.path.join(current_dir, "images", "podium_france_v2.png")

    # temporal parameters Q2OJ: fixed here or from your code?
    delta_t_s = 1800 # time-slot duration (s)
    start_optim_period = datetime.datetime(2018,1,1)
    optim_period = pd.date_range(start=start_optim_period, 
                                 end=start_optim_period+timedelta(hours=24),
                                 freq="%is" % delta_t_s)[:-1]
    coord_method = "price-coord. dyn."
    # Collective metrics calculation
    n_ts = 48 # number of discrete time-slots
    load_profiles = data #{} # TODO OJ: fixer ce dict. avec clés 1. Industrial Cons. scenario;
    # 2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    # 6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
#    if multiple charging stations in this microgrid) and values the associated
#    load profile (kW)
    # ATTENTION pour que cela marche (j'espère) il faut que les clés "PV scenario"
    # soit dans l'ensemble {"grand_nord", "grand_est", "grand_rhone", "bretagne", 
    # "grand_ouest", "grand_sud_ouest", "grande_ardeche", "grand_sud_est" -> fixer le 
    # jour de l'année choisie dans le fichier pv_prod_scenarios.csv et ne garder que la region
    # comme scénario PV pour l'instant ?
    # "external" (real) elec. prices Q2OJ: fixed here or from your code?
    purchase_price = 0.10 + 0.1 * np.random.rand(n_ts)
    sale_price = 0.05 + 0.1 * np.random.rand(n_ts)
    # pmax contract cost (fixed here "en dur")
    contracted_p_tariffs = {6: 123.6, 9: 151.32, 12: 177.24, 15: 201.36,
                            18: 223.68, 24: 274.68, 30: 299.52, 36: 337.56}
    # weights for the different collective microgrid metrics
    # TODO OB+OJ fixer valeurs choisies par Fanny et Nouhayla avant le run
    # N.B. pour l'instant "mg_transfo_aging" et "n_disj" pas utilisés
    coll_metrics_weights = {"pmax_cost": 1/365, "autonomy_score": 1,
                            "mg_transfo_aging": 0, "n_disj": 0}
    metrics_not_saved = ["mg_transfo_aging", "n_disj"]


    # 1) CALCULATION OF OUTPUT METRICS
    # calculate per-actor bill 
    # = dictionary with the same keys as load_profiles 
    # and values the associated bills
    per_actor_bills = calc_per_actor_bills(load_profiles, purchase_price,
                                           sale_price, delta_t_s)

    # and microgrid profile and collective metrics 
    # = two dict. with the same keys as load_profiles excepting the one
    # of the actors and values the aggregated microgrid load prof. (for microgrid_prof) 
    # and a dict. {"pmax_cost": cost of contracted max power, "autonomy_score": score of
    # autonomy measuring how much the microgrid is exchanging energy with the grid} (for
    # collective metrics)
    microgrid_prof, microgrid_pmax, collective_metrics = \
            calc_microgrid_collective_metrics(load_profiles, contracted_p_tariffs, 
                                              delta_t_s)

    # and finally cost-autonomy tradeoff 
    # = dict. with keys 1. the team names; 2. PV region names and
    # values the associated (cost, autonomy score) aggreg. over the set of other
    # scenarios
    cost_autonomy_tradeoff = \
        calc_cost_autonomy_tradeoff_last_iter(per_actor_bills, collective_metrics)

    # Get best team per region
    team_scores, best_teams_per_region, coll_metrics_names = \
            get_best_team_per_region(per_actor_bills, collective_metrics,
                                     coll_metrics_weights)
    
    # and France classification (simple aggreg. over per region scores - to be minimized)
    team_france_scores, teams_france_classif = get_france_team_classif(team_scores)
    
    # save detailed results to a .csv file
    save_all_metrics_to_csv(per_actor_bills, collective_metrics, coll_metrics_names,
                            coll_metrics_weights, metrics_not_saved, result_dir,
                            date_of_run)
    
    # and aggreg. per region .csv file
    save_per_region_score_to_csv(team_scores, result_dir, date_of_run)
    
    # get "improvement trajectory" over past runs (based on the presence
    # of result folders in current dir.)
    list_of_run_dates = [datetime.datetime.strptime(elt[4:], "%Y-%m-%d_%H%M") \
                         for elt in os.listdir(current_dir) \
                         if (os.path.isdir(elt) and elt.startswith("run_"))]
    scores_traj = get_improvement_traj(current_dir, list_of_run_dates,
                                       list(team_scores))

    # to print type of score (direction and mode of aggregation) in the .ppt
    type_of_score = ("MIN.", "Weighted (bill + contract. pmax) + %.2f * autonomy score" \
                                                % coll_metrics_weights["autonomy_score"]) 

    # create powerpoint with a summary of current run results
    create_summary_of_run_ppt(result_dir, date_of_run, idx_run, optim_period,
                              coord_method, regions_map_file, pv_profiles, load_profiles,
                              microgrid_prof, microgrid_pmax, cost_autonomy_tradeoff, team_scores,
                              best_teams_per_region, podium_france_file,
                              teams_france_classif, type_of_score, scores_traj)

