##### Technical validation machine-coded Earth Negotiation Bulletin (ENB) dataset
##### Authors: Paula Castro & Marlene Kammerer
##### Date: December 20, 2024

##### Part 3: Analysis of parties/ groupings and dyads, Figures 6-10
#####################################################################################
#####################################################################################

### Setup

# Python ≥3.5 is required
import sys
assert sys.version_info >= (3, 5)

# Common imports
import numpy as np
import os
import pandas as pd

# To store them in the project root directory
PROJECT_ROOT_DIR = "."
CHAPTER_ID = "technical_validation"
IMAGES_PATH = os.path.join(PROJECT_ROOT_DIR, "images")
os.makedirs(IMAGES_PATH, exist_ok=True)

def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(IMAGES_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)

# Ignore useless warnings (see SciPy issue #5998)
import warnings
warnings.filterwarnings(action="ignore", message="^internal gelsd")

#%% Import datasets

ENB_hc = pd.read_csv('data/ENB_hc_clean.csv', decimal = ',', sep= ',', encoding = "ISO-8859-1") # hand-coded
ENB_mc = pd.read_csv('data/ENB_mc_clean.csv', decimal = ',',  sep=',', encoding = "ISO-8859-1") # machine-coded
# subset mc

ENB_mc = ENB_mc[ENB_mc["year"] < 2014]
ENB_mc['type2'] = pd.Categorical(ENB_mc['type2'], ["agreement", "support", "behalf-of", "opposition"])
ENB_hc['type_recoded'] = pd.Categorical(ENB_hc['type_recoded'], ["agreement", "support", "behalf-of", "opposition"])

# recode G77/China to G77 in machine-coded data set
ENB_mc["sender"] = ENB_mc["sender"].replace("G-77/China", "G77")
ENB_mc["target"] = ENB_mc["target"].replace("G-77/China", "G77")

# recode UG to Umbrella in machine-coded data set
ENB_mc["sender"] = ENB_mc["sender"].replace("UG", "Umbrella")
ENB_mc["target"] = ENB_mc["target"].replace("UG", "Umbrella")

#%% Create country names in both datasets to make comparisons about countries; transform both to ISO codes

import country_converter as coco
# https://pypi.org/project/country-converter/

# hc
ENB_hc['sender_iso'] = ENB_hc.sender
ENB_hc['target_iso'] = ENB_hc.target

ENB_hc['sender_iso'] = coco.convert(names = ENB_hc['sender_iso'], to='ISO3', not_found = None)
ENB_hc['target_iso'] = coco.convert(names = ENB_hc['target_iso'], to='ISO3', not_found = None)

## mc
ENB_mc['sender_iso'] = ENB_mc.sender
ENB_mc['target_iso'] = ENB_mc.target

ENB_mc['sender_iso'] = coco.convert(names = ENB_mc['sender_iso'], to='ISO3', not_found = None)
ENB_mc['target_iso'] = coco.convert(names = ENB_mc['target_iso'], to='ISO3', not_found = None)

# Rename groups
ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Environmental Integrity Group", "EIG")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Environmental Integrity Group", "EIG")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Environmental Integrity Group", "EIG")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Environmental Integrity Group", "EIG")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("EITs", "EIT")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("EITs", "EIT")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("EITs", "EIT")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("EITs", "EIT")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("African Group", "AGN")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("African Group", "AGN")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("African Group", "AGN")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("African Group", "AGN")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Like Minded Developing Countries", "LMDC")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Like Minded Developing Countries", "LMDC")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Like Minded Developing Countries", "LMDC")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Like Minded Developing Countries", "LMDC")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("LMDCs", "LMDC")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("LMDCs", "LMDC")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("LMDCs", "LMDC")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("LMDCs", "LMDC")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Mountain Landlocked Developing Countries", "MLDC")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Mountain Landlocked Developing Countries", "MLDC")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Mountain Landlocked Developing Countries", "MLDC")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Mountain Landlocked Developing Countries", "MLDC")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Central Group Eleven", "CG_11")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Central Group Eleven", "CG_11")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Central Group Eleven", "CG_11")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Central Group Eleven", "CG_11")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("CG-11", "CG_11")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("CG-11", "CG_11")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("CG-11", "CG_11")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("CG-11", "CG_11")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Central Group", "CG_11")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Central Group", "CG_11")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Central Group", "CG_11")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Central Group", "CG_11")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Caribbean Community", "CARICOM")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Caribbean Community", "CARICOM")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Caribbean Community", "CARICOM")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Caribbean Community", "CARICOM")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Group of 9", "CG_9")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Group of 9", "CG_9")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Group of 9", "CG_9")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Group of 9", "CG_9")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Central America", "Central America")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Central America", "Central America")

ENB_mc["sender_iso"]  = ENB_mc["sender_iso"].replace("Central America", "Central America")
ENB_hc["sender_iso"]  = ENB_hc["sender_iso"].replace("Central America", "Central America")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Serbia and Montenegro", "SCG")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Serbia and Montenegro", "SCG")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Serbia and Montenegro", "SCG")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Serbia and Montenegro", "SCG")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("Yugoslavia", "YUG")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Yugoslavia", "YUG")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("Yugoslavia", "YUG")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Yugoslavia", "YUG")

ENB_mc["sender_iso"]  = ENB_mc["sender_iso"].replace("Visegrad Group", "Visegrad")
ENB_hc["sender_iso"]  = ENB_hc["sender_iso"].replace("Visegrad Group", "Visegrad")

ENB_mc["target_iso"]  = ENB_mc["target_iso"].replace("Visegrad Group", "Visegrad")
ENB_hc["target_iso"]  = ENB_hc["target_iso"].replace("Visegrad Group", "Visegrad")

ENB_mc["sender_iso"] = ENB_mc["sender_iso"].replace("LDCs", "LDC")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("LDCs", "LDC")

ENB_mc["target_iso"] = ENB_mc["target_iso"].replace("LDCs", "LDC")
ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("LDCs", "LDC")

ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Umbrella Group", "Umbrella")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Umbrella Group", "Umbrella")

ENB_hc["target_iso"] = ENB_hc["target_iso"].replace("Coalition of Rainforest Nations", "CfRN")
ENB_hc["sender_iso"] = ENB_hc["sender_iso"].replace("Coalition of Rainforest Nations", "CfRN")

# Create table with parties and groupings and number of interactions

# group senders
grouped_mc_sender = ENB_mc.groupby("sender_iso")
grouped_mc_sender = grouped_mc_sender.agg({"date": "count"})
grouped_mc_sender = grouped_mc_sender.reset_index()

grouped_hc_sender = ENB_hc.groupby("sender_iso")
grouped_hc_sender = grouped_hc_sender.agg({"date": "count"})
grouped_hc_sender = grouped_hc_sender.reset_index()

# group targets
grouped_mc_target = ENB_mc.groupby("target_iso")
grouped_mc_target = grouped_mc_target.agg({"date": "count"})
grouped_mc_target = grouped_mc_target.reset_index()

grouped_hc_target = ENB_hc.groupby("target_iso")
grouped_hc_target = grouped_hc_target.agg({"date": "count"})
grouped_hc_target = grouped_hc_target.reset_index()

# concatenate and save dataset
countries = pd.concat([grouped_mc_sender, grouped_hc_sender,  grouped_mc_target, grouped_hc_target], axis=1)

countries.columns = ['sender_mc', 'interactions_sender_mc', 'sender_hc', 'interactions_sender_hc', 'target_mc',
                     'interactions_target_mc', 'target_hc', 'interactions_target_hc']

countries.to_csv(r'data/Country_interactions.csv')


#%% Figure 6: Plot Top 10

import seaborn as sns
sns.set_style('dark')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use(['https://gist.githubusercontent.com/BrendanMartin/01e71bb9550774e2ccff3af7574c0020/raw/6fa9681c7d0232d34c9271de9be150e584e606fe/lds_default.mplstyle'])
mpl.rcParams.update({"figure.figsize": (8,6), "axes.titlepad": 22.0})

# sort and identify top parties and party groupings
top10_sender_mc = countries.sort_values(by=['interactions_sender_mc'], ascending=False)
top10_sender_mc = top10_sender_mc.head(10) ## Top 10 elements

top10_target_mc = countries.sort_values(by=['interactions_target_mc'], ascending=False)
top10_target_mc = top10_target_mc.head(10) ## Top 10 elements

top10_sender_hc = countries.sort_values(by=['interactions_sender_hc'], ascending=False)
top10_sender_hc = top10_sender_hc.head(10) ## Top 10 elements

top10_target_hc = countries.sort_values(by=['interactions_target_hc'], ascending=False)
top10_target_hc = top10_target_hc.head(10) ## Top 10 elements

# create variables
sender_mc = top10_sender_mc['sender_mc']
interactions_sender_mc = top10_sender_mc['interactions_sender_mc']

target_mc = top10_target_mc['target_mc']
interactions_target_mc = top10_target_mc['interactions_target_mc']

sender_hc = top10_sender_hc['sender_hc']
interactions_sender_hc = top10_sender_hc['interactions_sender_hc']

target_hc = top10_target_hc['target_hc']
interactions_target_hc = top10_target_hc['interactions_target_hc']

# make plot

plt.subplot(2,2,1)
sns.barplot(x=sender_mc, y=interactions_sender_mc, alpha=1, palette="mako")
plt.ylabel('Number of interactions', fontsize=10)
plt.xlabel('Top 10 senders, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,2)
sns.barplot(x=sender_hc, y=interactions_sender_hc, alpha=1, palette="mako")
plt.ylabel('Number of interactions', fontsize=10)
plt.xlabel('Top 10 senders, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,3)
sns.barplot(x=target_mc, y=interactions_target_mc, alpha=1, palette="mako")
plt.ylabel('Number of interactions', fontsize=10)
plt.xlabel('Top 10 targets, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,4)
sns.barplot(x=target_hc, y=interactions_target_hc, alpha=1, palette="mako")
plt.ylabel('Number of interactions', fontsize=10)
plt.xlabel('Top 10 targets, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

# plt.suptitle('Top 10 countries and coalitions, full dataset', fontsize=20)
save_fig("Figure6_Top10_full_dataset")
plt.show()

#%% Figure 7 and 8: Top 10 senders and targets; cooperation and conflict separated

# Separate conflictual and cooperative interactions

# only coop
ENB_hc_coop = ENB_hc[ENB_hc["type_recoded"] != "opposition"]
ENB_mc_coop = ENB_mc[ENB_mc["type2"] != "opposition"]

# only conf
ENB_hc_conf = ENB_hc[ENB_hc["type_recoded"] == "opposition"]
ENB_mc_conf = ENB_mc[ENB_mc["type2"] == "opposition"]

# create table with countries and number of cooperative interactions

# group sender coop
grouped_mc_sender_coop = ENB_mc_coop.groupby("sender_iso")
grouped_mc_sender_coop = grouped_mc_sender_coop.agg({"date": "count"})
grouped_mc_sender_coop = grouped_mc_sender_coop.reset_index()

grouped_hc_sender_coop = ENB_hc_coop.groupby("sender_iso")
grouped_hc_sender_coop = grouped_hc_sender_coop.agg({"date": "count"})
grouped_hc_sender_coop = grouped_hc_sender_coop.reset_index()

# group targets coop
grouped_mc_target_coop = ENB_mc_coop.groupby("target_iso")
grouped_mc_target_coop = grouped_mc_target_coop.agg({"date": "count"})
grouped_mc_target_coop = grouped_mc_target_coop.reset_index()

grouped_hc_target_coop = ENB_hc_coop.groupby("target_iso")
grouped_hc_target_coop = grouped_hc_target_coop.agg({"date": "count"})
grouped_hc_target_coop = grouped_hc_target_coop.reset_index()

# concatenate and save dataset
countries_coop = pd.concat([grouped_mc_sender_coop, grouped_hc_sender_coop,  grouped_mc_target_coop, grouped_hc_target_coop], axis=1)
countries_coop.columns = ['sender_mc', 'interactions_sender_mc', 'sender_hc', 'interactions_sender_hc', 'target_mc',
                          'interactions_target_mc', 'target_hc', 'interactions_target_hc']
countries_coop.to_csv(r'data/Country_interactions_coop.csv')

# create table with countries and number of conflictual interactions

# group sender conf
grouped_mc_sender_conf = ENB_mc_conf.groupby("sender_iso")
grouped_mc_sender_conf = grouped_mc_sender_conf.agg({"date": "count"})
grouped_mc_sender_conf = grouped_mc_sender_conf.reset_index()

grouped_hc_sender_conf = ENB_hc_conf.groupby("sender_iso")
grouped_hc_sender_conf = grouped_hc_sender_conf.agg({"date": "count"})
grouped_hc_sender_conf = grouped_hc_sender_conf.reset_index()

# group targets conf
grouped_mc_target_conf = ENB_mc_conf.groupby("target_iso")
grouped_mc_target_conf = grouped_mc_target_conf.agg({"date": "count"})
grouped_mc_target_conf = grouped_mc_target_conf.reset_index()

grouped_hc_target_conf = ENB_hc_conf.groupby("target_iso")
grouped_hc_target_conf = grouped_hc_target_conf.agg({"date": "count"})
grouped_hc_target_conf = grouped_hc_target_conf.reset_index()

# concatenate and save dataset
countries_conf = pd.concat([grouped_mc_sender_conf, grouped_hc_sender_conf, grouped_mc_target_conf, grouped_hc_target_conf], axis=1)
countries_conf.columns = ['sender_mc', 'interactions_sender_mc', 'sender_hc', 'interactions_sender_hc', 'target_mc',
                          'interactions_target_mc', 'target_hc', 'interactions_target_hc']
countries_conf.to_csv(r'data/Country_interactions_conf.csv')

#%% Identify Top 10, cooperation

# sort and identify top parties and party groupings
top10_sender_mc = countries_coop.sort_values(by=['interactions_sender_mc'], ascending=False)
top10_sender_mc = top10_sender_mc.head(10) ## Top 10 elements

top10_target_mc = countries_coop.sort_values(by=['interactions_target_mc'], ascending=False)
top10_target_mc = top10_target_mc.head(10) ## Top 10 elements

top10_sender_hc = countries_coop.sort_values(by=['interactions_sender_hc'], ascending=False)
top10_sender_hc = top10_sender_hc.head(10) ## Top 10 elements

top10_target_hc = countries_coop.sort_values(by=['interactions_target_hc'], ascending=False)
top10_target_hc = top10_target_hc.head(10) ## Top 10 elements

#%% Plot TOP10, cooperation

# create variables
sender_mc = top10_sender_mc['sender_mc']
interactions_sender_mc = top10_sender_mc['interactions_sender_mc']

target_mc = top10_target_mc['target_mc']
interactions_target_mc = top10_target_mc['interactions_target_mc']

sender_hc = top10_sender_hc['sender_hc']
interactions_sender_hc = top10_sender_hc['interactions_sender_hc']

target_hc = top10_target_hc['target_hc']
interactions_target_hc = top10_target_hc['interactions_target_hc']

# Senders

plt.subplot(2,2,1)
sns.barplot(x=sender_mc, y=interactions_sender_mc, alpha=1, palette="mako")
plt.ylabel('Number of cooperative interactions', fontsize=10)
plt.xlabel('Top 10 senders, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,2)
sns.barplot(x=sender_hc, y=interactions_sender_hc, alpha=1, palette="mako")
plt.ylabel('', fontsize=10)
plt.xlabel('Top 10 senders, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

# Targets

plt.subplot(2,2,3)
sns.barplot(x=target_mc, y=interactions_target_mc, alpha=1, palette="mako")
plt.ylabel('Number of cooperative interactions', fontsize=10)
plt.xlabel('Top 10 targets, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,4)
sns.barplot(x=target_hc, y=interactions_target_hc, alpha=1, palette="mako")
plt.ylabel('', fontsize=10)
plt.xlabel('Top 10 targets, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

# plt.suptitle('Top 10 countries and coalitions, only cooperation', fontsize=20)
save_fig("Figure7_Top10_cooperation")
plt.show()


#%% Identify Top 10, conflict

# sort and identify top parties and party groupings
top10_sender_mc = countries_conf.sort_values(by=['interactions_sender_mc'], ascending=False)
top10_sender_mc = top10_sender_mc.head(10) ## Top 10 elements

top10_target_mc = countries_conf.sort_values(by=['interactions_target_mc'], ascending=False)
top10_target_mc = top10_target_mc.head(10) ## Top 10 elements

top10_sender_hc = countries_conf.sort_values(by=['interactions_sender_hc'], ascending=False)
top10_sender_hc = top10_sender_hc.head(10) ## Top 10 elements

top10_target_hc = countries_conf.sort_values(by=['interactions_target_hc'], ascending=False)
top10_target_hc = top10_target_hc.head(10) ## Top 10 elements

#%% Plot TOP10, conflict

# create variables
sender_mc = top10_sender_mc['sender_mc']
interactions_sender_mc = top10_sender_mc['interactions_sender_mc']

target_mc = top10_target_mc['target_mc']
interactions_target_mc = top10_target_mc['interactions_target_mc']

sender_hc = top10_sender_hc['sender_hc']
interactions_sender_hc = top10_sender_hc['interactions_sender_hc']

target_hc = top10_target_hc['target_hc']
interactions_target_hc = top10_target_hc['interactions_target_hc']

# make plots
plt.subplot(2,2,1)
sns.barplot(x=sender_mc, y=interactions_sender_mc, alpha=1, palette="mako")
plt.ylabel('Number of conflictual interactions', fontsize=10)
plt.xlabel('Top 10 senders, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,2)
sns.barplot(x=sender_hc, y=interactions_sender_hc, alpha=1, palette="mako")
plt.ylabel('', fontsize=10)
plt.xlabel('Top 10 senders, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

# Targets mc

plt.subplot(2,2,3)
sns.barplot(x=target_mc, y=interactions_target_mc, alpha=1, palette="mako")
plt.ylabel('Number of conflictual interactions', fontsize=10)
plt.xlabel('Top 10 targets, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

plt.subplot(2,2,4)
sns.barplot(x=target_hc, y=interactions_target_hc, alpha=1, palette="mako")
plt.ylabel('', fontsize=10)
plt.xlabel('Top 10 targets, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')
plt.tick_params(labelsize=5)

# plt.suptitle('Top 10 Countries and coalitions, only conflict', fontsize=20)
save_fig("Figure8_Top10_conflict")
plt.show()

#%% Figure 9 & 10

# Count most frequent edges for coop and conf dataset
# Create a variable that maps sender to target to identify edges

## coop
ENB_mc_coop['edges'] = ENB_mc_coop['sender_iso']+'-'+ENB_mc_coop['target_iso']
ENB_hc_coop['edges'] = ENB_hc_coop['sender_iso']+'-'+ENB_hc_coop['target_iso']

# conf
ENB_mc_conf['edges'] = ENB_mc_conf['sender_iso']+'-'+ENB_mc_conf['target_iso']
ENB_hc_conf['edges'] = ENB_hc_conf['sender_iso']+'-'+ENB_hc_conf['target_iso']

# Plot TOP20  edges, coop

# create table with edges and number of interactions
grouped_mc_coop = ENB_mc_coop.groupby("edges")
grouped_mc_coop = grouped_mc_coop.agg({"date": "count"})
grouped_mc_coop = grouped_mc_coop.reset_index()

grouped_hc_coop = ENB_hc_coop.groupby("edges")
grouped_hc_coop = grouped_hc_coop.agg({"date": "count"})
grouped_hc_coop = grouped_hc_coop.reset_index()

edges_coop = pd.concat([grouped_mc_coop, grouped_hc_coop], axis=1)
edges_coop.columns = ['edges_mc_coop', 'interactions_mc_coop', 'edges_hc_coop', 'interactions_hc_coop']
edges_coop.to_csv(r'data/edges_interactions_coop.csv')

# TOP 20
top20_mc_coop = edges_coop.sort_values(by=['interactions_mc_coop'], ascending=False)
top20_mc_coop = top20_mc_coop.head(20) ## Top 20 elements

top20_hc_coop = edges_coop.sort_values(by=['interactions_hc_coop'], ascending=False)
top20_hc_coop = top20_hc_coop.head(20) ## Top 20 elements

edges_coop_mc = top20_mc_coop['edges_mc_coop']
interactions_coop_mc = top20_mc_coop ['interactions_mc_coop']

edges_coop_hc = top20_hc_coop['edges_hc_coop']
interactions_coop_hc = top20_hc_coop ['interactions_hc_coop']

#%%

plt.figure(figsize=(8,3.5))

plt.subplot(1,2,1)

sns.barplot(x=edges_coop_mc, y=interactions_coop_mc, alpha=0.8, palette="mako")
plt.tick_params(labelsize=5)
plt.ylabel('Number of cooperative interactions', fontsize=10)
plt.xlabel('Top 20 pairs, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')

# hand-coded
plt.subplot(1,2,2)
sns.barplot(x=edges_coop_hc, y=interactions_coop_hc, alpha=0.8, palette="mako")
plt.tick_params(labelsize=5)
plt.ylabel('', fontsize=10)
plt.xlabel('Top 20 pairs, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')

# plt.suptitle('Most frequent pairs (Top 20) mc vs. hc', fontsize=20)
save_fig("Figure9_Top20_edges_hc_mc")
plt.show()


#%% Plot TOP20  edges, conf

# create table with edges and number of interactions
grouped_mc_conf = ENB_mc_conf.groupby("edges")
grouped_mc_conf = grouped_mc_conf.agg({"date": "count"})
grouped_mc_conf = grouped_mc_conf.reset_index()

grouped_hc_conf = ENB_hc_conf.groupby("edges")
grouped_hc_conf = grouped_hc_conf.agg({"date": "count"})
grouped_hc_conf = grouped_hc_conf.reset_index()

edges_conf = pd.concat([grouped_mc_conf, grouped_hc_conf], axis=1)
edges_conf.columns = ['edges_mc_conf', 'interactions_mc_conf', 'edges_hc_conf', 'interactions_hc_conf']
edges_conf.to_csv(r'data/edges_interactions_conf.csv')

# TOP 20
top20_mc_conf = edges_conf.sort_values(by=['interactions_mc_conf'], ascending=False)
top20_mc_conf = top20_mc_conf.head(20) ## Top 20 elements

top20_hc_conf = edges_conf.sort_values(by=['interactions_hc_conf'], ascending=False)
top20_hc_conf = top20_hc_conf.head(20) ## Top 20 elements

edges_conf_mc = top20_mc_conf['edges_mc_conf']
interactions_conf_mc = top20_mc_conf ['interactions_mc_conf']

edges_conf_hc = top20_hc_conf['edges_hc_conf']
interactions_conf_hc = top20_hc_conf ['interactions_hc_conf']

#%%

plt.figure(figsize=(8,3.5))

plt.subplot(1,2,1)

sns.barplot(x=edges_conf_mc, y=interactions_conf_mc, alpha=0.8, palette="mako")
plt.tick_params(labelsize=5)
plt.ylabel('Number of conflictual interactions', fontsize=10)
plt.xlabel('Top 20 pairs, machine-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')

# hand-coded
plt.subplot(1,2,2)
sns.barplot(x=edges_conf_hc, y=interactions_conf_hc, alpha=0.8, palette="mako")
plt.tick_params(labelsize=5)
plt.ylabel('Number of conflictual interactions', fontsize=10)
plt.xlabel('Top 20 pairs, hand-coded dataset', fontsize=10)
plt.xticks(rotation='vertical')

# plt.suptitle('Most frequent pairs (Top 20) mc vs. hc, conflict', fontsize=20)
save_fig("Figure10_Top20_edges_hc_mc_conf")
plt.show()

## The END