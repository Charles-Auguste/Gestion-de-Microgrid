#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 13:02:00 2020

@author: corentinguery
"""

import matplotlib.pyplot as plt
plt.switch_backend('agg') # seems necessary on linux, comment on windows
import numpy as np
import random as rd
from openpyxl import Workbook

xticks=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50] 
    
def plot_1(Tab,unite,titre, labl,joueur, path,name_simulation):
    """ 
    Tab is a (N,T) vector. Each line correspond to a scenario and each column to a time t.
    This function plots a grouped bar diagram with the average values of the vector for each t.
    For the path_to_folder, mind putting '\\' instead of '/'.
    """
    
    """
    Pour loads; bills; batterie IC SF; scenario IC_SF 
    """
    
    N=Tab.shape[0]
    T=Tab.shape[1]
    TabL=np.zeros(T) #vector with the average values for each t
    E=np.zeros(T) #vector with the STD for each t
    Total=0
    
    for t in range(T):
        TabL[t]=np.mean(Tab[:,t])
        E[t]=np.std(Tab[:,t])
        Total+=TabL[t]
        
    ind=np.arange(T)
    width=0.25

    p1=plt.bar(ind, TabL, 3*width, color='r', bottom=0,label = labl, yerr=E)
    plt.ylabel(unite)
    plt.xlim([-1,T+1])
    plt.legend(loc='upper right')
    plt.title(titre+ " "+joueur)
    plt.grid(False)
    plt.xlabel('time')
    plt.autoscale(True,axis='y')
    #plt.xticks(ticks=xticks)
    
    plt.savefig(name_simulation+"/plot/"+path)
    
    
    
    #plt.show()
    plt.close()
    
    

def plot_1bis(Tab,unite,titre, labl,joueur,cars, path, name_simulation):
    
    """
    Pour batterie_CS
    """
    
    N=Tab.shape[0]
    T=Tab.shape[1]
    TabL=np.zeros(T) #vector with the average values for each t
    E=np.zeros(T) #vector with the STD for each t
    Total=0
    
    for t in range(T):
        TabL[t]=np.mean(Tab[:,t])
        E[t]=np.std(Tab[:,t])
        Total+=TabL[t]
        
    ind=np.arange(T)
    width=0.25

    p1=plt.bar(ind, TabL, 3*width, color='r', bottom=0,label = labl, yerr=E)
    plt.ylabel(unite)
    plt.xlim([-1,T+1])
    plt.legend(loc='upper right')
    plt.title(titre + " "+joueur +" car " + cars)
    plt.grid(False)
    plt.xlabel('time')
    plt.autoscale(True, axis='y')
    #plt.xticks(ticks=xticks)
    
    plt.savefig(name_simulation+"/plot/"+path)
    
    #plt.show()
    plt.close()
    
    
 


def plot_2(Tab,unite,titre,path,label1,label2, name_simulation):
    
    "Pour grid_load et imbalances"
    
    T=Tab['demand'].shape[1]
    N=Tab['demand'].shape[0]
    demand=np.zeros(T)
    supply=np.zeros(T)
    Edemand=np.zeros(T)
    Esupply=np.zeros(T)
    
    for t in range(T):
        demand[t]=np.mean(Tab['demand'][:,t])
        supply[t]=np.mean(Tab['supply'][:,t])
        Edemand[t]=np.std(Tab['demand'][:,t])
        Esupply[t]=np.std(Tab['supply'][:,t])
        
        
    ind=np.arange(T)
    width=0.5

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, demand, width, label=label1,yerr=Edemand, color='r')
    rects2 = ax.bar(ind + width/2, supply, width, label=label2,yerr=Esupply, color='b')

    
    ax.set_ylabel(unite)
    ax.set_xlabel('time')
    ax.set_title(titre)
    ax.legend()
    ax.autoscale(True,axis='y')
    ax.set_xticks(ticks=xticks)

    fig.tight_layout()

    plt.savefig(name_simulation+"/plot/"+path)
    
    #plt.show()
    plt.close()
    
def plot_3(Tab,unite,titre,path, name_simulation):
    
        
    "Pour prices"
    
    T=Tab['internal'].shape[1]
    N=Tab['internal'].shape[0]
    internal=np.zeros(T)
    ext_purch=np.zeros(T)
    ext_sale=np.zeros(T)
    Einternal=np.zeros(T)
    Eext_purch=np.zeros(T)
    Eext_sale=np.zeros(T)
    
    for t in range(T):
        internal[t]=np.mean(Tab['internal'][:,t])
        ext_purch[t]=np.mean(Tab['external_purchase'][:,t])
        ext_sale[t]=np.mean(Tab['external_sale'][:,t])
        Einternal[t]=np.std(Tab['internal'][:,t])
        Eext_purch[t]=np.std(Tab['external_purchase'][:,t])
        Eext_sale[t]=np.std(Tab['external_sale'][:,t])
        
        
    ind=np.arange(T)
    width=0.5

    fig, ax = plt.subplots()
    
    p1=ax.plot(ind,internal, label='internal', color='b')
    p2=ax.plot(ind,ext_purch, label='ext_purchase',color='g')
    p3=ax.plot(ind,ext_sale, label='ext_sale',color='r')
    
    ax.set_ylabel(unite)
    ax.set_title(titre)
    ax.set_xlabel('time')
    
    ax.legend(loc='upper left')
    ax.autoscale(True,axis='y')
    ax.set_xticks(ticks=xticks)


    plt.savefig(name_simulation+"/plot/"+path)
    
    #plt.show()
    plt.close()
    
def plot_4(dico, name_simulation):
    
    "mean bills"
    wb = Workbook()
    ws = wb.active
    
    bills = []
    names = []
        
    for name,bill in dico.items():
        bills.append(bill)
        names.append(name)
        
        
        print(name+" : "+str(bill))
    ws.append(names)
    ws.append(bills)
    
    wb.save(name_simulation+"/plot/score.xlsx")

def plot_5(Tab,unite,titre,path, name_simulation):
    
        
    "Pour prices"
    
    T=Tab['purchase'].shape[1]
    N=Tab['purchase'].shape[0]
    purchase=np.zeros(T)
    sale=np.zeros(T)
    E_purch=np.zeros(T)
    E_sale=np.zeros(T)
    
    for t in range(T):
        purchase[t]=np.mean(Tab['purchase'][:,t])
        sale[t]=np.mean(Tab['sale'][:,t])
        E_purch[t]=np.std(Tab['purchase'][:,t])
        E_sale[t]=np.std(Tab['sale'][:,t])
        
        
    ind=np.arange(T)
    width=0.5

    fig, ax = plt.subplots()
    
    p1=ax.plot(ind,purchase, label='purchase', color='r')
    p2=ax.plot(ind,sale, label='sale',color='b')
    
    ax.set_ylabel(unite)
    ax.set_title(titre)
    ax.set_xlabel('time')
    
    ax.legend(loc='upper left')
    ax.autoscale(True,axis='y')
    ax.set_xticks(ticks=xticks)


    plt.savefig(name_simulation+"/plot/"+path)
    
    #plt.show()
    plt.close()
  

def plottotal(dico, unite, titre, labl, path_to_data,name_simulation):
    for cle,objet in dico.items():
        plot_1(objet,unite,titre,labl,cle,path_to_data + "_" + cle + ".png",name_simulation)



def plotCS(dico,unite,titre,labl,path,name_simulation):
    for cle,objet in dico.items():
        for cars in range (4):
            plot_1bis(dico[cle][:,cars,:],unite,titre,labl,cle,str(cars+1),path + "_" + cle +"_voiture_"+str(cars+1)+".png",name_simulation)
        


