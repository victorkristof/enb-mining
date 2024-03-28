import fire
import pandas as pd
from enbmining import Intervention, InterventionScraper
from enbmining.entities import Grouping, Party
from enbmining.utils import load_csv, load_html, print_progress


def main(html_folder, issues_path, parties_path, groupings_path, output_path):

    parties = Party.load(parties_path)
    groupings = Grouping.load(groupings_path)
    issues = load_csv(issues_path)

    # Extract interventions.
    print('Extracting interventions...')
    interventions = list()
    for i, issue in enumerate(issues):
        html = load_html(html_folder, issue['id'])
        scraper = InterventionScraper(html, issue, parties, groupings)
        # Keep only unique interventions. Problem with this method: the order of interventions is not preserved.
        # interventions.extend(set(scraper.scrape()))
        # Keep interventions sorted, but with some repetitions possible.
        interventions.extend(scraper.scrape())
        print_progress(i, issues, every_n=10)

    total = len(interventions)
    print(f'Extracted {total} interventions from {len(issues)} issues')

    # Save interventions.
    Intervention.to_csv(interventions, output_path)

    # Read interventions as df.
    df_interventions = pd.read_csv(output_path)
    print(df_interventions.head())

    # Eliminate duplicated interventions.
    df_interventions = df_interventions.drop_duplicates(subset=['issue_id', 'entity', 'date', 'sentence'])

    total2 = len(df_interventions)
    print(f'Eliminated {total - total2} duplicated interventions')
    print(f'Extracted {total2} unique interventions from {len(issues)} issues')

    # Save interventions.
    df_interventions.to_csv(output_path, index=False)


if __name__ == '__main__':
    fire.Fire(main)
