# Mine Data from Earth Negotiations Bulletin

## Set up

Install the requirements and the local library:

```
pip install -r requirements.txt
pip install -e lib
```

Create a directory to store data:

```
mkdir -p data/html
```

Create the lists of entities (see below):

```
touch data/parties.txt data/groupings.txt
```

## Usage

1. Fetch metadata about issues from the ENB reports into a CSV file:

```
python scripts/1-list-issues.py data/issues.csv
```

2. Download the source of issues as HTML files:

```
python scripts/2-download-html.py data/issues.csv data/html
```

3. Extract the interventions from the HTML files:

```
python scripts/3-scrape-interventions.py data/html data/issues.csv data/parties.txt data/groupings.txt data/interventions.csv
```

4. Extract the interactions from the HTML files:

```
python scripts/4-scrape-interactions.py data/html data/issues.csv data/parties.txt data/groupings.txt data/interactions.csv
```

5. Classify the headings into negotiation bodies and issue areas:

```
python scripts/5-classify-headings.py
```

## List of entities

The scripts depend on lists of parties and party groupings (together referred to as "entities").
Each entity is defined as a canonical name (used in the output dataset) and can optionally be assigned to aliases.
These aliases will be used by the script to match variations of a canonical name in the raw data.
For example, if "the US" and "the United States" are used in the raw data, one can define that both should be identified as "the US".

### List of parties

The format of the list of parties, for example in `data/parties.txt`, is the following:

```
Party: Alias1, Alias2, ... [Grouping1, Grouping2, ...]
```

The aliases and the groupings are optional.
The determinant "the" must be omitted (it is added by the script).
For example, the following entries are valid:

```
Switzerland
United States: US, United States of America
Senegal [G77/China, African Group]
```

If needed, a semicolon can be used to separate aliases and groupings (for example, if a comma is used in the name of an entity).

### List of groupings

The format of the list of groupings, for example in `data/groupings.txt`, is the following:

```
Grouping: Alias1, Alias2, ...
```

The same rules as for the parties apply.
Here are examples of valid groupings:

```
Central Group
UG: Umbrella Group
```
