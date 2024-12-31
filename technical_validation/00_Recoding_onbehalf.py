##### Technical validation machine-coded Earth Negotiation Bulletin (ENB) data set
##### Authors: Paula Castro & Marlene Kammerer
##### Version: December 20, 2024

##### Part 00: Recoding of on-behalf interactions to joint statements
#####################################################################################
#####################################################################################

## Goal of this script:
# Recoding of "on-behalf" interactions, so that their interpretation matches the one in the old hand-coded dataset:
# search for "on-behalf" in interactions$type
# duplicate those observations, but change "entity_a" into "entity_b" and vice versa (and also update the ids of the new observations)
# search for all "agreement"s with exactly the same sentence as "on-behalf"
# recode those "agreement"s as "joint_statement" (in a new type2 variable)
# recode all "on-behalf"s as "joint_statement" (in a new type2 variable)
## Why? There can be two interpretations of "on-behalf":
# The one in the machine-code dataset emphasizes that one actor (entity_a) is speaking on behalf of another actor (entity_b).
# The relationship is unidirectional.
# If entity_a speaks on behalf of several other entities, this is recorded as several "on-behalf" observations. 
# In addition, bi-directional "agreement" between those other entities is recorded.
# The interpretation in the hand-coded dataset emphasizes the fact that a group of entities is speaking together.
# The assumption is that they have prepared a joint statement or joint intervention in advance.
# So, the relationship is bi-directional, and all combinations between "entity_a" and the (possibly various) "entity_b" are coded as "joint_statement".


# Import necessary libraries
import os
import pandas as pd
from datetime import datetime

# Load data
interactions = pd.read_csv("data/interactions.csv")

# Subset the "behalf" observations --> these will be duplicated, but changing entity_a with entity_b
behalf = interactions[interactions['type'] == "'on-behalf'"].copy()

# Change the id so that the new observations get a new one
behalf['id'] = behalf['id'] + 0.5

# Rename columns (swap entity_b and entity_a)
behalf = behalf.rename(columns={"entity_a": "entity_b", "entity_b": "entity_a"})

# Create new variable for the recoded interaction
behalf['type2'] = "'joint_statement'"

# Now create missing values for the original "on-behalf" type, because speaking on behalf works only in the original direction
behalf['type'] = None

# In main dataset, look for rows where type == "'agreement'" and the sentence is the same as previous rows with type == "'on-behalf'"
# For these rows, recode type2 as "'joint_statement'"
interactions['check_behalf'] = interactions.groupby('sentence')['type'].transform(lambda x: "'on-behalf'" in x.values)

# View the result of the previous step
print(pd.crosstab(interactions['type'], interactions['check_behalf'], dropna=False))

# View the first rows of the dataset
print(interactions.head())

# Identify a few exceptions where agreement should not be recoded to a joint statement
exceptions = [
    (629, 'LDCs'), (629, 'LMDCs'), (629, 'EU'), (629, 'EIG'), (629, 'Georgia'), (629, 'Indonesia'),
    (632, 'LDCs'), (632, 'LMDCs'), (632, 'EU'), (632, 'EIG'), (632, 'Indonesia'),
    (642, 'African Group'), 
    (678, 'AOSIS'), (678, 'AILAC'), (678, 'EU'), 
    (717, 'AILAC'), 
    (719, 'Canada'), (719, 'Colombia'), (719, 'EU'),
    (729, 'LDCs'), (729, 'Canada'), 
    (529, 'EU'), (529, 'Papua New Guinea'),
    (503, 'EIG'), (503, 'EU'), (503, 'Marshall Islands'),
    (504, 'EIG'), (504, 'EU'), (504, 'Marshall Islands'),
    (501, 'Bolivia'), (501, 'Uruguay'), (501, 'Togo'),
    (502, 'AOSIS'), (509, 'AOSIS'), (509, 'Uruguay'), (509, 'Togo'),
    (469, 'Japan'), (477, 'Japan'),
    (107, 'Japan'), (107, 'Switzerland'),
    (110, 'Japan'), (110, 'Switzerland')
]

for issue_id, entity in exceptions:
    interactions.loc[
        (interactions['check_behalf'] == True) &
        (interactions['issue_id'] == issue_id) &
        (interactions['type'] == "'agreement'") &
        ((interactions['entity_a'] == entity) | (interactions['entity_b'] == entity)),
        'check_behalf'
    ] = False

# View the result of the previous step
print(pd.crosstab(interactions['type'], interactions['check_behalf'], dropna=False))


# In main dataset, create new variable in which to recode the interaction
interactions['type2'] = interactions['type']
interactions.loc[interactions['type'] == "'on-behalf'", 'type2'] = "'joint_statement'"
interactions.loc[(interactions['type'] == "'agreement'") & (interactions['check_behalf'] == True), 'type2'] = "'joint_statement'"

# Get rid of interactions$check_behalf
interactions.drop(columns=['check_behalf'], inplace=True)

# Add additional observations to main dataset and reorder according to id
interactions_complete = pd.concat([interactions, behalf], ignore_index=True)
interactions_complete.sort_values(by='id', inplace=True)

# Check the result
print(pd.crosstab(interactions_complete['type'], interactions_complete['type2'], dropna=False))

# Write the output to a new CSV file
interactions_complete.to_csv("data/interactions_behalfrecoded.csv", index=False)

## Go to 01_Data_cleaning_for_publication
