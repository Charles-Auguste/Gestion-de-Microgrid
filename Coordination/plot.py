# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 11:41:04 2018

@author: B57876
"""

# Plot functions

# IMPORT
# standard
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# PERSO
from calc_output_metrics import get_ic_scenarios, get_dc_scenarios, get_ev_scenarios, \
                                    get_team_names

# Global parameters to define style of figures
fig_size = (15, 9)
fig_dpi = 70
width_ticks = 2
eps_y = 0.2
eps_x = 0.01
eps_x_annotate = 0.02
eps_y_annotate = -0.02
legend_loc = "upper left"
text_loc = "upper right"
fig_format = "png"
# generic colors for iterations and regions
iter_colors = {0: "blue", 1: "orange", 2: "green", 3: "red", 4: "purple",
               5: "brown", 6: "pink", 7: "gray", 8: "olive", 9: "cyan", 10: "black"}
region_colors = {"grand_nord": "blue", "grand_est": "cyan", "grand_rhone": "yellow",
                 "bretagne": "purple", "grand_ouest": "olive", "grand_sud_ouest": "pink",
                 "grande_ardeche": "orange", "grand_sud_est": "red"}
team_colors = {0: "blue", 1: "orange", 2: "green", 3: "red", 4: "purple",
               5: "brown", 6: "pink", 7: "gray", 8: "olive", 9: "cyan", 10: "black"}
team_markers = {0: "o", 1: "v", 2: "^", 3: "<", 4: ">", 5: "1", 6: "s", 7: "p", 
                8: "*", 9: "d", 10: "x"}
actor_colors = {"solar_farm": "orange", "industrial_consumer": "gray",
                "charging_station": "blue", "data_center": "red"}
n_colors = len(team_colors)
n_markers = len(team_markers)

def get_max_value_of_plot(list_of_x_plot):

    max_value_of_plot = 0
    for x_plot in list_of_x_plot:
        if max(x_plot) > max_value_of_plot:
            max_value_of_plot = max(x_plot)
            
    return max_value_of_plot

def get_min_value_of_plot(list_of_x_plot):

    min_value_of_plot = 1E10
    for x_plot in list_of_x_plot:
        if min(x_plot) < min_value_of_plot:
            min_value_of_plot = min(x_plot)
            
    return min_value_of_plot

def generate_time_labels(full_date_plot, only_show_days, only_show_hours):
            
    if only_show_hours:
        return ["%s:%s" %(str(elt.hour) if elt.hour>=10 else "0"+str(elt.hour),
                          str(elt.minute) if elt.minute>=10 \
                            else "0"+str(elt.minute)) for elt in full_date_plot]
    elif only_show_days:
        return ["%i-%i-%i" %(elt.year,elt.month,elt.day) for elt in full_date_plot]
    else:
        return ["%i-%i-%i %s:%s" %(elt.year,elt.month,elt.day,
                                   str(elt.hour) if elt.hour>=10 else "0" \
                                   + str(elt.hour), str(elt.minute) \
                                   if elt.minute>=10 \
                                    else "0"+str(elt.minute)) for elt in full_date_plot]

def plot_list_of_tuples(tuples_plot, xlabel, ylabel, num_fig, save_fig, filename,
                        full_date_plot, only_show_days, only_show_hours,
                        delta_xticks):
    """
    OBJ: nice plot of SC over a period of multiple days
    
    IN:
        - tuples_plot: list of (vector of x-values to be plotted, 
        vector of y-values to be plotted, color, linestyle, marker, label)
        - xlabel: x-axis label
        - ylabel: y-axis label
    """
    
    n_elt_plot = len(tuples_plot)
            
    plt.figure(num=num_fig, figsize=fig_size, dpi=fig_dpi)
    
    for i_elt in range(n_elt_plot):
        # both markers and label
        if tuples_plot[i_elt][4] and tuples_plot[i_elt][5]:
            plt.plot(tuples_plot[i_elt][0], tuples_plot[i_elt][1], 
                     color=tuples_plot[i_elt][2], linewidth=1.5, 
                     linestyle=tuples_plot[i_elt][3], marker=tuples_plot[i_elt][4],
                     markersize=12, fillstyle="none", label=tuples_plot[i_elt][5])
        # only markers
        elif tuples_plot[i_elt][4]:
            plt.plot(tuples_plot[i_elt][0], tuples_plot[i_elt][1], 
                     color=tuples_plot[i_elt][2], linewidth=1.5, 
                     linestyle=tuples_plot[i_elt][3], marker=tuples_plot[i_elt][4],
                     markersize=12, fillstyle="none")
        # only label
        elif tuples_plot[i_elt][5]:
            plt.plot(tuples_plot[i_elt][0], tuples_plot[i_elt][1], 
                     color=tuples_plot[i_elt][2], linewidth=1.5, 
                     linestyle=tuples_plot[i_elt][3], label=tuples_plot[i_elt][5])
        # no marker, no label
        else:                 
            plt.plot(tuples_plot[i_elt][0], tuples_plot[i_elt][1], 
                     color=tuples_plot[i_elt][2], linewidth=1.5, 
                     linestyle=tuples_plot[i_elt][3], marker=tuples_plot[i_elt][4],
                     markersize=12, fillstyle="none")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # set xticks_labels
    # Axes
    axes = plt.gca()
    axes.xaxis.set_tick_params(width=width_ticks)
    axes.yaxis.set_tick_params(width=width_ticks)
    
    x_plot_for_min = []
    y_plot_for_min = []
    for i_elt in range(n_elt_plot):
        x_plot_for_min.append(tuples_plot[i_elt][0])
        y_plot_for_min.append(tuples_plot[i_elt][1])
    
    min_value_of_plot_x = get_min_value_of_plot(x_plot_for_min)
    max_value_of_plot_x = get_max_value_of_plot(x_plot_for_min)
    min_value_of_plot_y = get_min_value_of_plot(y_plot_for_min)
    max_value_of_plot_y = get_max_value_of_plot(y_plot_for_min)
    axes.set_ylim([min_value_of_plot_y - eps_y, max_value_of_plot_y + eps_y])
    axes.set_xlim([min_value_of_plot_x, max_value_of_plot_x])
    axes.grid(which='both')
    
    # not temporal xtick labels
    if not isinstance(full_date_plot, pd.DatetimeIndex):
        plt.xticks(np.arange(min_value_of_plot_x, max_value_of_plot_x + eps_x,
                             delta_xticks*(tuples_plot[0][0][1]-tuples_plot[0][0][0])))
    else:
        xtick_labels = generate_time_labels(full_date_plot, only_show_days, 
                                            only_show_hours)
        plt.xticks(np.arange(min_value_of_plot_x, max_value_of_plot_x, delta_xticks), 
                   xtick_labels[::delta_xticks], rotation='vertical')
        
    plt.legend(loc=legend_loc, frameon=False)

    if save_fig:
        plt.savefig("%s.%s" % (filename, fig_format))

    # close figure
    plt.close()

def plot_scatter_fig(tuples_scatter: list, num_fig: int, save_fig: bool,
                     filename: str, xlabel: str, ylabel: str):

    """
    Plot scatter figure
    
    :param tuples_scatter: list of (x-value, y-value, color, marker, label)
    """    
    
    marker_size = 150
    
    plt.figure(num=num_fig, figsize=fig_size, dpi=fig_dpi)
    for i in range(len(tuples_scatter)):
        # with a label
        if tuples_scatter[i][4]:
            plt.scatter(tuples_scatter[i][0], tuples_scatter[i][1], 
                        s=marker_size, facecolors="none", edgecolors=tuples_scatter[i][2],
                        marker=tuples_scatter[i][3], label=tuples_scatter[i][4]) 
        # without
        else:
            plt.scatter(tuples_scatter[i][0], tuples_scatter[i][1], 
                        s=marker_size, facecolors="none", edgecolors=tuples_scatter[i][2],
                        marker=tuples_scatter[i][3]) 
                    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    plt.legend(loc=legend_loc, frameon=False)

    if save_fig:
        plt.savefig("%s.%s" % (filename, fig_format))

    # close figure
    plt.close()

def plot_mg_load_during_coord_method(microgrid_prof: dict, region_plot: str,
                                     team_plot: str, filename: str, 
                                     full_date_plot: pd.date_range):
    """
    Plot microgrid total load profile during the coord. dynamic 
    
    :param microgrid_prof: dict. with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and value the associated aggreg. microgrid load profile
    :param region_plot: name of the region to be plotted
    :param team_plot: name of the team for the plot
    :param filename: full path to the image to be saved
    :param full_date_plot: range of dates corresponding to the optim. period
    """
    
    # get indices of the first scenarios used for plot
    first_ic_scen = get_ic_scenarios(microgrid_prof)[0]
    first_dc_scen = get_dc_scenarios(microgrid_prof)[0]
    first_ev_scen = get_ev_scenarios(microgrid_prof)[0]
    iterations = list(microgrid_prof[first_ic_scen][first_dc_scen][region_plot] \
                                                  [first_ev_scen][team_plot])
    common_x = np.arange(len(microgrid_prof[first_ic_scen][first_dc_scen][region_plot] \
                                              [first_ev_scen][team_plot][iterations[0]]))
    # plot using generic function
    # (vector of x-values to be plotted, y-values to be plotted, color, linestyle,
    # marker, label)
    tuples_plot = [(common_x, microgrid_prof[first_ic_scen][first_dc_scen][region_plot] \
                      [first_ev_scen][team_plot][i_iter], iter_colors[i_iter],
                    "-", "", "iter %i" % i_iter) for i_iter in iterations]
    
    plot_list_of_tuples(tuples_plot, "Date", "Power (kW)", 1, True, filename,
                        full_date_plot, False, True, 4)

def plot_all_teams_mg_load_last_iter(microgrid_prof: dict, microgrid_pmax: dict, 
                                     pv_prof: np.ndarray, region_plot: str, 
                                     filename: str, full_date_plot: pd.date_range):

    """
    Plot all teams microgrid total load profile at the end of the dynamic 
    
    :param microgrid_prof: dict. with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and value the associated aggreg. microgrid load profile
    :param microgrid_pmax: dict. with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration and value the associated microgrid pmax
    :param pv_prof: vector of PV prod. profile 
    :param region_plot: name of the region to be plotted
    :param filename: full path to the image to be saved
    :param full_date_plot: range of dates corresponding to the optim. period
    """

    # get indices of the first scenarios used for plot
    first_ic_scen = get_ic_scenarios(microgrid_prof)[0]
    first_dc_scen = get_dc_scenarios(microgrid_prof)[0]
    first_ev_scen = get_ev_scenarios(microgrid_prof)[0]
    team_names = get_team_names(microgrid_prof)
    
    # loop over teams to construct the input data for plot
    tuples_plot = []
    for team in team_names:
        iterations = list(microgrid_prof[first_ic_scen][first_dc_scen][region_plot] \
                                                        [first_ev_scen][team])
        if team == team_names[0]:
            common_x = np.arange(len(microgrid_prof[first_ic_scen][first_dc_scen] \
                                     [region_plot][first_ev_scen][team][iterations[0]]))

            tuples_plot = [(common_x, pv_prof, "yellow", "-", "", "PV prod.")]

        # (vector of x-values to be plotted, y-values to be plotted, color, linestyle,
        # marker, label)
        # add load profile
        tuples_plot.append((common_x, microgrid_prof[first_ic_scen][first_dc_scen] \
                                [region_plot][first_ev_scen][team][iterations[-1]],
                            team_colors[team_names.index(team)%n_colors], "-",
                            team_markers[team_names.index(team)%n_markers], 
                            "%s: load prof. (iter=%i)" % (team, iterations[-1])))
        # and associated suscribed pmax
        tuples_plot.append((common_x, microgrid_pmax[first_ic_scen][first_dc_scen] \
                                [region_plot][first_ev_scen][team][iterations[-1]] \
                                * np.ones(len(common_x)),
                            team_colors[team_names.index(team)%n_colors], "--",
                            "", "%s: contract. pmax" % team))
    
    plot_list_of_tuples(tuples_plot, "Date", "Power (kW)", 1, True, filename,
                        full_date_plot, False, True, 4)

def plot_per_actor_load_last_iter(load_profiles: dict, pv_prof: np.ndarray, 
                                  region_plot: str, team_plot: str,
                                  filename: str, full_date_plot: pd.date_range):
    """
    Plot per-actor at the last iteration of coord. dyn in a given team (microgrid)

    :param load_profiles: dictionary with keys 1. Industrial Cons. scenario; 
    2. Data Center scenario; 3. PV scenario; 4. EV scenario; 5. microgrid team name; 
    6. Iteration; 7. actor type (N.B. charging_station_1, charging_station_2... 
    if multiple charging stations in this microgrid) and values the associated
    load profile (kW)
    :param pv_prof: vector of PV prod. profile 
    :param region_plot: name of the region to be plotted
    :param team_plot: team for which plot is done
    :param filename: full path to the image to be saved
    :param full_date_plot: range of dates corresponding to the optim. period
    """

    # get indices of the first scenarios used for plot
    first_ic_scen = get_ic_scenarios(load_profiles)[0]
    first_dc_scen = get_dc_scenarios(load_profiles)[0]
    first_ev_scen = get_ev_scenarios(load_profiles)[0]
    iterations = list(load_profiles[first_ic_scen][first_dc_scen][region_plot] \
                                                  [first_ev_scen][team_plot])
    actors = list(load_profiles[first_ic_scen][first_dc_scen][region_plot] \
                                       [first_ev_scen][team_plot][iterations[0]])
    common_x = np.arange(len(load_profiles[first_ic_scen][first_dc_scen][region_plot] \
                                       [first_ev_scen][team_plot][iterations[0]][actors[0]]))

    # plot using generic function
    # (vector of x-values to be plotted, y-values to be plotted, color, linestyle,
    # marker, label)
    tuples_plot = [(common_x, pv_prof, "yellow", "-", "", "PV prod.")]
    tuples_plot.extend([(common_x, load_profiles[first_ic_scen][first_dc_scen][region_plot] \
                      [first_ev_scen][team_plot][iterations[-1]][actor],
                    actor_colors[actor], "-", "", actor) for actor in actors])
    
    plot_list_of_tuples(tuples_plot, "Date", "Power (kW)", 1, True, filename,
                        full_date_plot, False, True, 4)

def plot_all_teams_cost_auton_tradeoff_last_iter(cost_autonomy_tradeoff: dict,
                                                 filename: str):
    """
    Plot all teams*PV regions (cost, autonomy) points

    :param cost_autonomy_tradeoff: dict. with keys 1. the team names; 2. PV region
    names and values the associated (cost, autonomy score) aggreg. over the set 
    of other scenarios
    :param filename: full path to the image to be saved
    """
    
    tuples_scatter = []
    team_names = list(cost_autonomy_tradeoff)
    first_region = list(cost_autonomy_tradeoff[team_names[0]])[0]
    for team in cost_autonomy_tradeoff:
        for region in cost_autonomy_tradeoff[team]:
            current_label = team if region == first_region else ""
            # tuples_scatter: list of (x-value, y-value, color, marker, label)
            tuples_scatter.append((cost_autonomy_tradeoff[team][region]["cost"],
                                   cost_autonomy_tradeoff[team][region]["autonomy_score"],
                                   region_colors[region], 
                                   team_markers[team_names.index(team)%n_markers],
                                   current_label))

    # use generic scatter function
    plot_scatter_fig(tuples_scatter, 1, True, filename, "Cost (eur)", "Autonomy score")

def plot_all_teams_score_traj(scores_traj: dict, filename: str):
    """
    Plot all teams score trajectories (improved?) over a set of runs

    :param scores_traj: dict. with keys 1. team name ; 2. run dates and associated
    values the score
    :param filename: full path to the image to be saved
    """

    team_names = list(scores_traj)
    
    # plot using generic function
    # (vector of x-values to be plotted, y-values to be plotted, color, linestyle,
    # marker, label)
    n_run_dates = len(scores_traj[team_names[0]])
    tuples_plot = [(np.arange(n_run_dates), np.array(list(scores_traj[team].values())),
                    team_colors[team_names.index(team)%n_colors], "-",
                    team_markers[team_names.index(team)%n_markers], team) \
                                                        for team in scores_traj]
    
    plot_list_of_tuples(tuples_plot, "Date", "Power (kW)", 1, True, filename,
                        list(scores_traj[team_names[0]]), False, False, 1)
   

if __name__ == "__main__":
    import os
    import pandas as pd
    import datetime
    from datetime import timedelta
    
    # number of time-slots for test
    n_t = 10
    tuples_plot = [(np.arange(n_t), np.random.rand(n_t), "red", "-", "curve bottom"),
                   (np.arange(n_t), 2*np.random.rand(n_t), "blue", "--", "curve top")]
    
    xlabel = "Heures"
    ylabel = "Consommation (kW)"
    num_fig = 1
    save_fig = True
    filename = os.path.join(os.getcwd(), "my_first_fig")
    # define range of dates associated to discrete set of time-slots
    date_start = datetime.datetime(2021, 5, 5, 8, 30)
    delta_t_s = 3600 # time-slot duration (in s)
    date_end = date_start + timedelta(len(tuples_plot[0][0])*delta_t_s)
    full_date_plot = pd.date_range(start=date_start, end=date_end, 
                                   freq="%is" % delta_t_s)
    only_show_days = False
    only_show_hours = True
    delta_xticks = 1
    plot_list_of_tuples(tuples_plot, xlabel, ylabel, num_fig, save_fig, filename,
                        full_date_plot, only_show_days, only_show_hours,
                        delta_xticks)
