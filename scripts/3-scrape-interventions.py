import fire
from enbmining import Intervention, InterventionScraper
from enbmining.utils import Entity, load_csv, load_html, print_progress


def main(html_folder, issues_path, entities_path, output_path):

    # entities_path = 'data/entities_interactions.txt'
    # html_folder = 'data/html'
    # issues_path = 'data/issues.csv'

    entities = Entity.load_entities(entities_path)
    issues = load_csv(issues_path)

    # Extract interventions.
    print('Extracting interventions...')
    interventions = list()
    for i, issue in enumerate(issues):
        html = load_html(html_folder, issue['id'])
        scraper = InterventionScraper(html, issue, entities)
        interventions.extend(scraper.scrape())
        print_progress(i, issues, every_n=10)
    total = len(interventions)
    print(f'Extracted {total} interventions from {len(issues)} issues')

    # Save interventions.
    Intervention.to_csv(interventions, output_path)


if __name__ == '__main__':
    fire.Fire(main)
