##### Technical validation machine-coded Earth Negotiation Bulletin (ENB) data set
##### Authors: Paula Castro & Marlene Kammerer
##### Date: December 30, 2024

##### Part 01: Data preparation
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
import re
from datetime import timedelta


# To store them in the project root directory
PROJECT_ROOT_DIR = "."
CHAPTER_ID = "technical_validation"
IMAGES_PATH = os.path.join(PROJECT_ROOT_DIR, "images", CHAPTER_ID)
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
# Load hand-coded dataset; most current version obtained from Castro and Kammerer 2022: https://doi.org/10.7910/DVN/DAUJUF
# The dataset contains hand-coded information on the sender, target, date, and type of interaction for each issue in the Earth Negotiation Bulletin (ENB) dataset in the period 1995-2013.
# Only the relevant variables have been kept in the dataset used for this technical validation. 

ENB_hc = pd.read_csv('data/technical_validation/ENB_hc.csv', decimal=',', sep=',', encoding="utf-8")
ENB_mc = pd.read_csv('data/interactions_behalfrecoded.csv', decimal=',', sep=',', encoding="utf-8")
# In the above version of the machine-coded dataset, the on-behalf interactions were recoded to match the way they were coded in the hand-coded dataset. 
# See detailed explanation in script 000_Recoding_onbehalf.py.

issues = pd.read_csv('data/issues.csv', decimal=',', sep=',', encoding="utf-8")
interventions = pd.read_csv("data/interventions.csv")
groupings = pd.read_csv("data/groupings.txt", sep=":", header=None, names=["group", "group_aliases"])

#%% Dropping issues that are not needed

# Some documents are included in the machine-coded dataset, which were not included in the hand-coded dataset to avoid duplicates, specifically the ENB curtain-raisers and summaries.
# They include mostly the same information as the regular issues, or information about the context of the negotiations rather than their content. 
# However, there are some cases where the regular issues are missing. 
# In these cases, the summaries were used in the hand-coded dataset. 
# Hence, for the technical validation, we remove from the machine-coded dataset most summaries and curtain-raisers,
# but keep those summaries where regular issues are missing. This will be done with the following code:

# First, create a subset of the machine-coded dataset with only date, sender, target, text, and the party grouping.
# This is not necessary for the hand-coded dataset as it only contains the relevant variables.

ENB_mc_sub = ENB_mc[['date', 'issue_id', 'entity_a', 'entity_b', 'type2', 'sentence']]
ENB_mc_sub.head(5)

# Check for NaNs
ENB_mc_sub.columns[ENB_mc_sub.isnull().any()]  # None found

#%% Now, the information on which issues to keep or drop is added

# Rename some variables for consistency
ENB_mc_sub['issue_id'] = ENB_mc_sub['issue_id'].astype(str)
issues['issue_id'] = issues['id'].astype(str)

# Create a new variable that tells which summaries to keep
# Also, the issue type needs to be added to the ENB dataset
ENB_mc_sub['issue_type'] = ENB_mc_sub['issue_id'].map(issues.set_index('issue_id')['type'])

ENB_mc_sub['summary_keep'] = np.where(
    (ENB_mc_sub['issue_id'].isin({'45', '46', '47', '49', '50', '62', '63', '407', '445',
                                  '510', '535', '536', '688', '689', '690', '691'})) |
    (ENB_mc_sub['issue_type'] == 'issue'), "keep", "drop"
)

# Count number of observations to keep and drop
ENB_mc_sub['summary_keep'].value_counts()
# To keep 50293, to drop 38207, total 88500 observations

#%% Exclude summaries and curtain-raisers (but keep the exceptions)

ENB_mc_sub_clean = ENB_mc_sub[ENB_mc_sub["summary_keep"] == "keep"]

# Count new number of observations
ENB_mc_sub_clean.shape
# n=50293 after dropping

#%% Remove the category "others" from the countries

# Exclude "<others>" from senders and targets
ENB_mc_sub_clean = ENB_mc_sub_clean[
    ~ENB_mc_sub_clean["entity_a"].str.contains("<Others>") &
    ~ENB_mc_sub_clean["entity_b"].str.contains("<Others>")
    ]

# Rename entity_a/b to sender/target
ENB_mc_sub_clean.rename(columns={'entity_a': 'sender', 'entity_b': 'target'}, inplace=True)
ENB_mc_sub_clean.head(5)

ENB_mc_sub_clean.shape
# n=47710

#%% Clean the type (relation) variable in both datasets
# In the MC dataset, extract the letters
ENB_mc_sub_clean['type2'] = ENB_mc_sub_clean['type2'].str.extract(r"([a-zA-Z]+)").fillna('')
ENB_mc_sub_clean['type2'].value_counts()

# Replace "joint" with "behalf-of"
ENB_mc_sub_clean['type2'] = ENB_mc_sub_clean['type2'].replace({'joint': 'behalf-of'})
ENB_mc_sub_clean['type2'].value_counts()

#%% In the hand-coded dataset... rename relation to type
ENB_hc.rename(columns={'relation': 'type'}, inplace=True)

# Recode the type variable in both datasets
# In the ENB_hc, recode the numbers into strings (cp Codebook for Castro and Kammerer 2022)

type_map = {1: 'behalf-of', 2: 'support', 3: 'agreement', 4: 'opposition', 5: 'opposition'}
ENB_hc['type_recoded'] = ENB_hc['type'].map(type_map)
ENB_hc['type_recoded'].value_counts()

#%% Drop some specific issues in hand-coded dataset
# We do this because they are not covered by the machine-coded dataset.

exclude_enb_numbers = {'67', '98', '124', '125', '126', '138', '139',
                       '164', '190', '232', '243', '299', '355', '376', '396'}
ENB_hc_clean = ENB_hc[~ENB_hc["ENB_Nr"].astype(str).isin(exclude_enb_numbers)]

ENB_hc.shape
# 62097 observations
ENB_hc_clean.shape
# 61546 observations

#%% Clean the date variable

# Add a clean date variable to ENB_mc_sub (the existing variable is messy, with date ranges that cannot be automatically parsed to dates)
# To get the date for ENB_mc_sub, map the issue with the issue number of the meetings dataset
ENB_mc_sub_clean['date_clean'] = ENB_mc_sub_clean['issue_id'].map(issues.set_index('issue_id')['issue_date'])

# In date_clean, whenever there is a "-" sign, delete everything up to it, including the "-"
ENB_mc_sub_clean['date_clean'] = ENB_mc_sub_clean['date_clean'].str.replace(r'.*-', '', regex=True)
ENB_mc_sub_clean['date_clean'] = ENB_mc_sub_clean['date_clean'].str.replace(r'.*–', '', regex=True)
# this deals with ranges both within a month and across months

# Extract year, month, and day for MC dataset
ENB_mc_sub_clean['datetime'] = pd.to_datetime(ENB_mc_sub_clean['date_clean'], errors='coerce')
ENB_mc_sub_clean['year'] = ENB_mc_sub_clean['datetime'].dt.year
ENB_mc_sub_clean['month_numbers'] = ENB_mc_sub_clean['datetime'].dt.month
ENB_mc_sub_clean['day'] = ENB_mc_sub_clean['datetime'].dt.day

# Shift datetime by 1 day in MC dataset
# Reason for this: the hand-coded dataset contains the date when the ENB was issued; 
# this is 1 day after the actual negotiation day summarized, which is the one recorded in the machine-coded dataset.
ENB_mc_sub_clean['datetime_shift'] = ENB_mc_sub_clean['datetime'] + timedelta(days=1)

#%%
# Preprocess Interventions
interventions_full = pd.merge(interventions, issues, left_on='issue_id', right_on='id')

# Extract Year from `issue_date`
interventions_full['year'] = interventions_full['issue_date'].str.extract(r'(\d{4})')

# Determine Coalitions
interventions_full['coalition'] = interventions_full['entity'].apply(lambda x: 'coalition' if x in groupings['group'].values else 'country')
interventions_full['coalition_noEU'] = interventions_full['coalition']
interventions_full.loc[interventions_full['entity'] == 'EU', 'coalition_noEU'] = 'country'

# Remove `<Others>` and Curtain Raisers
interventions_full = interventions_full[~interventions_full['entity'].eq("<Others>")]
interventions_full = interventions_full[~interventions_full['type'].eq("curtain-raiser")]

# Filter Country Interventions
interventions_countries = interventions_full[interventions_full['coalition_noEU'] == 'country']
interventions_countries_nosummaries = interventions_countries[~interventions_countries['type'].eq("summary")]

# Aggregate Interventions
interventions_ctys_all_nosums = interventions_countries_nosummaries.groupby('entity').size().reset_index(name='n')

#%% Save datasets
ENB_hc_clean.to_csv('data/ENB_hc_clean.csv', index=False)
ENB_mc_sub_clean.to_csv('data/ENB_mc_clean.csv', index=False)
interventions_ctys_all_nosums.to_csv('data/ENB_mc_interventions.csv', index=False)

## Go to 02_Visualizations
