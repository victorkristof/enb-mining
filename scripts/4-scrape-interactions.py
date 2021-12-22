from enbmining import InteractionScraper
from enbmining.utils import load_csv, load_entities, load_html, print_progress

entities_path = 'data/entities_interactions.txt'
issues_path = 'data/issues.csv'
html_folder = 'data/html'

entities = load_entities(entities_path)
issues = load_csv(issues_path)

issue = issues[0]
html = load_html(html_folder, issue['id'])

# Test "on behalf".
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'Switzerland, for FRANCE, proposed X.',
    'Switzerland, for the EIG, proposed X.',
    'Switzerland, on behalf of the EIG, proposed X.',
    'Switzerland, on behalf of the EIG and Canada, proposed X.',
    'Switzerland, on behalf of the EIG, the US and Canada, proposed X.',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test "supported by".
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'INDIA and CHINA, supported by NIGERIA, OMAN and BRAZIL',
    'CHINA, for the G77, supported by NIGERIA',
    'Supported by SAUDI ARABIA, CHINA stressed parties',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test "opposed by".
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'JAMAICA, opposed by the EU, asked for',
    'TUVALU and JAMAICA, opposed by the EU, CANADA and AUSTRALIA, said that',
    'Opposed by SAUDI ARABIA, CHINA stressed parties',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test "agreement"
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'JAMAICA and TUVALU asked for',
    'JAMAICA, TUVALU, CANADA, and SWITZERLAND asked for',
    'TUVALU and JAMAICA, opposed by the EU, CANADA and AUSTRALIA, said that',
    'Opposed by SAUDI ARABIA and the US, CHINA stressed parties',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test with a complex sentence.
complex_sentence = '''Supported by Lesotho, for the LDCs, Spain, for the EU,\
PANAMA, SOUTH AFRICA, AUSTRALIA, COLOMBIA, MALAWI, the PHILIPPINES and NORWAY,\
AOSIS proposed'''
print(scraper._scrape_from_sentence(complex_sentence))

# Extract interactions
print('Extracting interactions...')
interventions = list()
num_issues = 0
for i, issue in enumerate(issues):
    if issue['type'] == 'summary':
        continue
    html = load_html(html_folder, issue['id'])

    scraper = InteractionScraper(html, issue, entities)
    sentences = scraper.extract_sentences()
