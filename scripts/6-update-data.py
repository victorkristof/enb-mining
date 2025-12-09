#!/usr/bin/env python3
"""
Incremental updater for ENB data.

Workflow:
1) Read existing data/issues.csv and fetch the first two pages of UNFCCC issues from ENB
2) Identify new meetings (by meeting name) and assign IDs starting from last existing id + 1
3) Save these as data/new_issues.csv
4) Download HTML for the new issues to data/html_new/ using scripts/2-download-html.py
5) Scrape interventions/interactions from those HTML files using existing scripts 3 and 4, producing
   data/interventions_new.csv and data/interactions_new.csv
6) Append the new rows to the main CSVs (issues.csv, interventions.csv, interactions.csv)
7) Clean up the temporary CSV files
"""

import subprocess
from pathlib import Path

import pandas as pd
from enbmining import Client


def fetch_new_issues(existing_issues_path: Path, start_page: int = 1, end_page: int = 2):
    """Fetch issues from ENB and return those with meetings not already present."""
    existing_df = pd.read_csv(existing_issues_path)
    existing_meetings = set(existing_df['meeting'].dropna())
    last_id = int(existing_df['id'].max()) if len(existing_df) else 0

    client = Client(negotiation='UNFCCC')
    all_issues = client.get_issues_metadata(start_page=start_page, end_page=end_page)

    cols = list(existing_df.columns)
    new_issues = []
    next_id = last_id + 1
    for issue in all_issues:
        meeting = issue.get('meeting')
        if not meeting or meeting in existing_meetings:
            continue
        row = {c: issue.get(c, '') for c in cols if c != 'id'}
        row['id'] = next_id
        next_id += 1
        new_issues.append(row)

    return new_issues, cols


def run_script(script_path: Path, args: list[str]):
    """Run a helper script with provided arguments."""
    subprocess.check_call(['python3', str(script_path), *args])


def append_with_new_ids(existing_path: Path, new_path: Path):
    """Append new rows assigning fresh ids after the current max."""
    if not new_path.exists():
        return
    new_df = pd.read_csv(new_path)
    if new_df.empty:
        return

    existing_df = pd.read_csv(existing_path)
    max_id = int(existing_df['id'].max()) if len(existing_df) else 0
    new_df['id'] = range(max_id + 1, max_id + 1 + len(new_df))

    combined = pd.concat([existing_df, new_df], ignore_index=True)
    combined.to_csv(existing_path, index=False)


def main(
    issues_path: str = 'data/issues.csv',
    parties_path: str = 'data/parties.txt',
    groupings_path: str = 'data/groupings.txt',
    html_new_folder: str = 'data/html_new',
    start_page: int = 1,
    end_page: int = 2,
    debug: bool = False,
):
    issues_path = Path(issues_path)
    parties_path = Path(parties_path)
    groupings_path = Path(groupings_path)
    html_new_folder = Path(html_new_folder)

    tmp_new_issues = Path('data/new_issues.csv')
    tmp_interventions = Path('data/interventions_new.csv')
    tmp_interactions = Path('data/interactions_new.csv')

    print('Fetching issues from ENB...')
    new_issues, cols = fetch_new_issues(issues_path, start_page, end_page)
    if not new_issues:
        print('No new issues found. Exiting.')
        return

    # Save new issues with assigned IDs
    pd.DataFrame(new_issues, columns=cols).to_csv(tmp_new_issues, index=False)
    print(f'Found {len(new_issues)} new issues. Saved to {tmp_new_issues}.')

    # Ensure output folder for new HTML
    html_new_folder.mkdir(parents=True, exist_ok=True)

    # 1) Download HTML for new issues
    print('Downloading HTML for new issues...')
    run_script(Path('scripts/2-download-html.py'), [str(tmp_new_issues), str(html_new_folder)] + ([] if not debug else ['--debug']))

    # 2) Scrape interventions
    print('Scraping interventions for new issues...')
    run_script(
        Path('scripts/3-scrape-interventions.py'),
        [str(html_new_folder), str(tmp_new_issues), str(parties_path), str(groupings_path), str(tmp_interventions)],
    )

    # 3) Scrape interactions
    print('Scraping interactions for new issues...')
    run_script(
        Path('scripts/4-scrape-interactions.py'),
        [str(html_new_folder), str(tmp_new_issues), str(parties_path), str(groupings_path), str(tmp_interactions)],
    )

    # 4) Append to main CSVs
    print('Appending new issues to issues.csv...')
    existing_issues = pd.read_csv(issues_path)
    new_issues_df = pd.read_csv(tmp_new_issues)
    pd.concat([existing_issues, new_issues_df], ignore_index=True).to_csv(issues_path, index=False)

    print('Appending new interventions...')
    append_with_new_ids(Path('data/interventions.csv'), tmp_interventions)

    print('Appending new interactions...')
    append_with_new_ids(Path('data/interactions.csv'), tmp_interactions)

    # 5) Cleanup temp files
    for tmp in [tmp_new_issues, tmp_interventions, tmp_interactions]:
        if tmp.exists():
            tmp.unlink()
    print('Done.')


if __name__ == '__main__':
    main()
