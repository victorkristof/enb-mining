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
python scripts/3-scrape-interventions.py data/html data/issues.csv data/entities.txt data/interventions.csv
```
