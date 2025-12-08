import fire
from enbmining import Interaction, InteractionScraper
from enbmining.entities import Grouping, Party
from enbmining.utils import load_csv, load_html, print_progress


def main(html_folder, issues_path, parties_path, groupings_path, output_path):

    parties = Party.load(parties_path)
    groupings = Grouping.load(groupings_path)
    issues = load_csv(issues_path)
    
    # Filter out empty issues
    issues = [issue for issue in issues if issue.get('id') and issue['id'].strip()]

    # Extract interactions
    print('Extracting interactions...')
    interactions = list()
    for i, issue in enumerate(issues):
        html = load_html(html_folder, issue['id'])
        scraper = InteractionScraper(html, issue, parties, groupings)
        interactions.extend(scraper.scrape())
        print_progress(i, issues, every_n=10)
    total = len(interactions)
    print(f'Extracted {total} interactions from {len(issues)} issues')

    # Save interactions.
    Interaction.to_csv(interactions, output_path)


if __name__ == '__main__':
    fire.Fire(main)
