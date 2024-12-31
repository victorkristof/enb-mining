##### Technical validation machine-coded Earth Negotiation Bulletin (ENB) data set
##### Authors: Paula Castro & Marlene Kammerer
##### Date: December 20, 2024

##### Part 02: Visualizations, Figures 1-5
#####################################################################################
#####################################################################################

### Setup

# Python ≥3.5 is required
import sys
assert sys.version_info >= (3, 5)

# Common imports
import numpy as np
import os
import geopandas as gpd
import geodatasets
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import scipy as sp
from shapely.geometry import Point, Polygon

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

#%%
# import datasets
ENB_hc = pd.read_csv('data/ENB_hc_clean.csv', decimal = ',', sep= ',', encoding = "ISO-8859-1") # hand-coded
ENB_mc = pd.read_csv('data/ENB_mc_clean.csv', decimal = ',',  sep=',', encoding = "ISO-8859-1") # machine-coded
interventions = pd.read_csv("data/ENB_mc_interventions.csv")
groupings = pd.read_csv("data/groupings.txt", sep=":", header=None, names=["group", "group_aliases"])
issues = pd.read_csv("data/issues.csv")

#%%
# ENB_hc has 61546 rows
# ENB_mc has 47710 rows (without curtain-raisers and summaries)

#% Subset machine-coded data set to before 2014 (hand-coded ends in 2013)
ENB_mc["year"] = ENB_mc["year"].astype(float)
ENB_mc_sub_2013 = ENB_mc[ENB_mc["year"] < 2014]

# ENB_mc has now 38339 rows

#%% Figure 1

file_path = "data/technical_validation/ne_110m_admin_0_countries.shp"

# Load the file into a GeoDataFrame
world = gpd.read_file(file_path)

# Display the first few rows
print(world.head())

# Map Adjustments
country_replacements = {
    "Antigua and Barbuda": "Antigua",
    "Côte d'Ivoire": "Ivory Coast",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Macedonia": "North Macedonia",
    "Republic of Korea": "South Korea",
    "Saint Kitts and Nevis": "Saint Kitts",
    "Saint Vincent and the Grenadines": "Saint Vincent",
    "Trinidad and Tobago": "Trinidad",
    # "United Kingdom": "UK",
    # "United States": "USA"
}
interventions['country'] = interventions['entity'].replace(country_replacements)
#%%

# Duplicate Country Rows for Special Cases
def duplicate_country(df, original, new):
    duplicate = df[df['country'] == original].copy()
    duplicate['country'] = new
    return pd.concat([df, duplicate], ignore_index=True)

interventions = duplicate_country(interventions, "Antigua", "Barbuda")
interventions = duplicate_country(interventions, "Saint Kitts", "Nevis")
interventions = duplicate_country(interventions, "Saint Vincent", "Grenadines")
interventions = duplicate_country(interventions, "Trinidad", "Tobago")

# Merge with World Map
world = world.rename(columns={"NAME_LONG": "country"})
world = world.merge(interventions, on="country", how="left")
interventions['country'] = interventions['entity'].replace(country_replacements)
#%%

world['interventions'] = pd.cut(
    world['n'],
    bins=[0, 1, 50, 200, 500, 1000, float("inf")],
    labels=["0", "1-50", "51-200", "200-500", "500-1000", ">1000"]
)

# Initialize a figure
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Plot boundaries separately for better visibility
world.boundary.plot(ax=ax, linewidth=1, color="black")

# Plot the choropleth map
world.plot(
    column='interventions',
    cmap='Blues',
    legend=True,
    # legend_kwds={'orientation': "horizontal"},  # Remove 'label'
    ax=ax
)

# Add legend title manually
colorbar = ax.get_legend()
colorbar.set_title("Number of interventions")

# Add a title
# plt.title("Interventions in UNFCCC Negotiations 1995-2023, as reported in ENBs", fontsize=15)

# Save the figure
save_fig("Figure1_interventions_map")

# Show the plot
plt.show()

#%% Figure 2

interactions_full = pd.merge(ENB_mc, issues, left_on="issue_id", right_on="id")
interactions_full['year'] = interactions_full['issue_date'].str.extract(r'(\d{4})')
interactions_coop2015 = interactions_full[
    (interactions_full['year'] == "2015") &
    (interactions_full['type'] != "'opposition'")
    ][['sender', 'target']]

#%%
# Create directed graph
G = nx.from_pandas_edgelist(interactions_coop2015, source='sender', target='target', create_using=nx.DiGraph())
# Attach attributes to graph nodes
for node in G.nodes():
    if node in groupings['group'].values:
        G.nodes[node]['Coalition'] = 'coalition'
    else:
        G.nodes[node]['Coalition'] = 'country'

degree_dict = dict(G.degree())
node_sizes = [degree_dict[node]*10  for node in G.nodes()]
node_colors = ["yellow" if G.nodes[node]['Coalition'] == 'coalition' else "lightblue" for node in G.nodes()]

# Remove isolated nodes
G.remove_nodes_from(list(nx.isolates(G)))
#%%

# Draw graph
plt.figure(figsize=(15, 10))
pos = nx.kamada_kawai_layout(G)
nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors , edge_color= "lightgrey", font_size=10, font_color="black", alpha=0.75)

# Add custom legend for node sizes
legend_labels = [10, 50, 100]  # Node degrees for legend
scaled_sizes = [size for size in legend_labels]  # Scale legend sizes like nodes

# Create legend handles
legend_handles = [
    plt.scatter([], [], s=size, c='skyblue', edgecolors='black', label=f"Degree {label}")
    for size, label in zip(scaled_sizes, legend_labels)
]

# Add legend to plot
plt.legend(handles=legend_handles, loc= "lower right", title="Node size by degree", fontsize=10, title_fontsize=12)

# plt.title("Cooperative interactions in UNFCCC negotiations (year 2015)")
plt.savefig("", dpi=300)
save_fig("Figure2_interactions_network_2015")
plt.show()


#%% Figure 3
# Plot and count the type variable for both datasets

import seaborn as sns
sns.set_style('dark')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use(['https://gist.githubusercontent.com/BrendanMartin/01e71bb9550774e2ccff3af7574c0020/raw/6fa9681c7d0232d34c9271de9be150e584e606fe/lds_default.mplstyle'])
mpl.rcParams.update({"figure.figsize": (8,6), "axes.titlepad": 22.0})

#%% For plotting purposes, sort the type / type_recoded variable in a customized way

ENB_mc_sub_2013['type2'] = pd.Categorical(ENB_mc_sub_2013['type2'], ["agreement", "support", "behalf-of", "opposition"])
ENB_hc['type_recoded'] = pd.Categorical(ENB_hc['type_recoded'], ["agreement", "support", "behalf-of", "opposition"])

#%% Comparison of interaction types between mc and hc datasets
# First, create table // dataframe with types and counts for both datasets
(unique_hc, counts_hc) = np.unique(ENB_hc["type_recoded"], return_counts=True)
(unique_mc, counts_mc) = np.unique(ENB_mc_sub_2013["type2"].astype(str), return_counts=True)
#%%
types = pd.DataFrame(unique_mc)
counts_hc = pd.DataFrame(counts_hc)
counts_mc = pd.DataFrame(counts_mc)
type_count = pd.concat([counts_hc, counts_mc], axis=1)
type_count.columns = ['Hand-coded', 'Machine-coded']
y_labels = ['Agreement', 'On behalf', 'Opposition', 'Support']
type_count.index = y_labels
type_count = type_count.reindex(['Agreement', 'On behalf', 'Support', 'Opposition'])

# set the colors
colors = ['#5cb85c', '#5bc0de']

# plot with annotations
type_count.plot(kind='bar', color=colors, figsize=(8, 6), rot=0, ylabel='Number of interactions', grid=True)
save_fig('Figure3_Type-count-plot')
plt.show()

#%% Figure 4: Plot total number of interactions over time, all types

# Create year variable in ENB_hc
ENB_hc["date"] = ENB_hc["date"].astype(str)
ENB_hc["year"] = ENB_hc["date"].str[:4]
ENB_hc["year"] = ENB_hc["year"].astype(float)

# Create four subsets per dataset

ENB_hc_onbehalf = ENB_hc[ENB_hc["type_recoded"] == 'behalf-of']
ENB_hc_support = ENB_hc[ENB_hc["type_recoded"] == 'support']
ENB_hc_agreement = ENB_hc[ENB_hc["type_recoded"] == 'agreement']
ENB_hc_opposition = ENB_hc[ENB_hc["type_recoded"] == 'opposition']

ENB_mc_onbehalf = ENB_mc_sub_2013[ENB_mc_sub_2013["type2"] == 'behalf-of']
ENB_mc_support = ENB_mc_sub_2013[ENB_mc_sub_2013["type2"] == 'support']
ENB_mc_agreement = ENB_mc_sub_2013[ENB_mc_sub_2013["type2"] == 'agreement']
ENB_mc_opposition = ENB_mc_sub_2013[ENB_mc_sub_2013["type2"] == 'opposition']

#%%
# Define colors
COLOR_ENB_hc = "#5cb85c"  # Green for hand-coded
COLOR_ENB_mc = "#5bc0de"  # Blue for machine-coded

# Ensure that we have a complete year range from 1995 to 2013
complete_years = pd.DataFrame({'year': range(1995, 2014)})

# Function to group data
def group_interactions(df, year_col, type_col):
    grouped = df.groupby(year_col).agg({type_col: "count"}).reset_index()
    grouped = pd.merge(complete_years, grouped, on=year_col, how="left") # completes any missing years in the series
    grouped[type_col] = grouped[type_col].fillna(0) # fills missing values with 0
    return grouped

# Function to plot grouped data
def plot_interactions(ax, grouped_hc, grouped_mc, legend_title, ylabel, xlabel):
    ax.plot(grouped_hc['year'].astype(str), grouped_hc['type_recoded'], color=COLOR_ENB_hc, lw=4, label="Hand-coded")
    ax.plot(grouped_mc['year'].astype(str), grouped_mc['type2'], color=COLOR_ENB_mc, lw=4, label="Machine-coded")
    # ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(title=legend_title, fontsize=10, loc='upper left')
    ax.tick_params(axis="y", labelcolor="black")
    ax.tick_params(axis="x", labelcolor="black", labelrotation=90)
    ax.grid(True)

# Process data
grouped_onbehalf_mc = group_interactions(ENB_mc_onbehalf, "year", "type2")
grouped_onbehalf_hc = group_interactions(ENB_hc_onbehalf, "year", "type_recoded")

grouped_support_mc = group_interactions(ENB_mc_support, "year", "type2")
grouped_support_hc = group_interactions(ENB_hc_support, "year", "type_recoded")

grouped_agreement_mc = group_interactions(ENB_mc_agreement, "year", "type2")
grouped_agreement_hc = group_interactions(ENB_hc_agreement, "year", "type_recoded")

grouped_opposition_mc = group_interactions(ENB_mc_opposition, "year", "type2")
grouped_opposition_hc = group_interactions(ENB_hc_opposition, "year", "type_recoded")

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))  # 2x2 grid layout

# Plot all interactions
plot_interactions(
    axes[0, 0],
    grouped_agreement_hc,
    grouped_agreement_mc,
    "Agreement interactions",
    "Number of interactions",
    ""
)
plot_interactions(
    axes[0, 1],
    grouped_support_hc,
    grouped_support_mc,
    "Support interactions",
    "",
    ""
)
plot_interactions(
    axes[1, 0],
    grouped_onbehalf_hc,
    grouped_onbehalf_mc,
    "On behalf interactions",
    "Number of interactions",
    "Year"
)
plot_interactions(
    axes[1, 1],
    grouped_opposition_hc,
    grouped_opposition_mc,
    "Opposition interactions",
    "",
    "Year"
)

# Adjust layout and save
# fig.suptitle("Interactions: Hand-Coded vs Machine-Coded Over Time", fontsize=20)
plt.tight_layout(rect=[0, 0, 1, 0.97])
save_fig("Figure4_Combined_Interactions_Plot")

plt.show()

#%% Figure 5: Plot of number of active senders and popular targets

# count of senders by year
grouped_mc_year_sender = ENB_mc_sub_2013.groupby("year")
grouped_mc_year_sender = grouped_mc_year_sender.agg({"sender": "nunique"})
grouped_mc_year_sender = grouped_mc_year_sender.reset_index()

grouped_hc_year_sender = ENB_hc.groupby("year")
grouped_hc_year_sender = grouped_hc_year_sender.agg({"sender": "nunique"})
grouped_hc_year_sender = grouped_hc_year_sender.reset_index()

# Convert year to integer in grouped_hc_year_sender and grouped_mc_year_sender
grouped_hc_year_sender['year'] = grouped_hc_year_sender['year'].astype(int)
grouped_mc_year_sender['year'] = grouped_mc_year_sender['year'].astype(int)

YEAR_HC_sender = grouped_hc_year_sender['year'].astype(str)
YEAR_MC_sender = grouped_mc_year_sender['year'].astype(str)

# count of targets by year
grouped_mc_year_target = ENB_mc_sub_2013.groupby("year")
grouped_mc_year_target = grouped_mc_year_target.agg({"target": "nunique"})
grouped_mc_year_target = grouped_mc_year_target.reset_index()

grouped_hc_year_target = ENB_hc.groupby("year")
grouped_hc_year_target = grouped_hc_year_target.agg({"target": "nunique"})
grouped_hc_year_target = grouped_hc_year_target.reset_index()

# Convert year to integer in grouped_hc_year_target and grouped_mc_year_target
grouped_hc_year_target['year'] = grouped_hc_year_target['year'].astype(int)
grouped_mc_year_target['year'] = grouped_mc_year_target['year'].astype(int)

YEAR_HC_target = grouped_hc_year_target['year'].astype(str)
YEAR_MC_target = grouped_mc_year_target['year'].astype(str)

#%% Plot number of active countries over time, total, for both datasets;

COLOR_ENB_hc = "#5cb85c"
COLOR_ENB_mc = "#5bc0de"

fig, axs = plt.subplots(2, 1, figsize=(6, 8))

# First subplot: Sender countries
ax1 = axs[0]
ax1.plot(YEAR_HC_sender, grouped_hc_year_sender['sender'], color=COLOR_ENB_hc, lw=3, label="Hand-coded")
ax1.plot(YEAR_MC_sender, grouped_mc_year_sender['sender'], color=COLOR_ENB_mc, lw=3, label="Machine-coded")
# ax1.set_xlabel("Year", color="black", fontsize=10)
ax1.set_ylabel("Number of countries", color="black", fontsize=10)
ax1.tick_params(axis="y", labelcolor="black", labelsize=8)
ax1.tick_params(axis="x", labelcolor="black", labelrotation=90, labelsize=8)
ax1.grid(True)
ax1.legend(title='Sender countries', fontsize=10, loc='lower left')

# Second subplot: Target countries
ax2 = axs[1]
ax2.plot(YEAR_HC_target, grouped_hc_year_target['target'], color=COLOR_ENB_hc, lw=3, label="Hand-coded")
ax2.plot(YEAR_MC_target, grouped_mc_year_target['target'], color=COLOR_ENB_mc, lw=3, label="Machine-coded")
ax2.set_xlabel("Year", color="black", fontsize=10)
ax2.set_ylabel("Number of countries", color="black", fontsize=10)
ax2.tick_params(axis="y", labelcolor="black", labelsize=8)
ax2.tick_params(axis="x", labelcolor="black", labelrotation=90, labelsize=8)
ax2.grid(True)
ax2.legend(title='Target countries', fontsize=10, loc='lower left')

# fig.suptitle("Sender and target countries over time, \nhand-coded (green) vs machine-coded (blue) datasets", fontsize=16)

save_fig("Figure5_Sender_target_countries_hc_vs_mc_plot")
plt.show()

## Go to 03_Party-groupings_analysis