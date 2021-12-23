import fire
from enbmining import Interaction, InteractionScraper
from enbmining.utils import load_csv, load_entities, load_html, print_progress


def main(html_folder, issues_path, entities_path, output_path):

    entities = load_entities(entities_path)
    issues = load_csv(issues_path)

    # Extract interactions
    print('Extracting interactions...')
    interactions = list()
    for i, issue in enumerate(issues):
        html = load_html(html_folder, issue['id'])
        scraper = InteractionScraper(html, issue, entities)
        interactions.extend(scraper.scrape())
        print_progress(i, issues, every_n=10)
    print(
        f'Extracted {len(interactions)} interactions from {len(issues)} issues'
    )

    # Save interactions.
    Interaction.to_csv(interactions, output_path)


if __name__ == '__main__':
    fire.Fire(main)
