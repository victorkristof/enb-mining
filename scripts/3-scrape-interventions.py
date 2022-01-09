import fire
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
        interventions.extend(scraper.scrape())
        print_progress(i, issues, every_n=10)
    total = len(interventions)
    print(f'Extracted {total} interventions from {len(issues)} issues')

    # Save interventions.
    Intervention.to_csv(interventions, output_path)


if __name__ == '__main__':
    fire.Fire(main)
