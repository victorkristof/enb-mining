from enbmining import InteractionScraper
from enbmining.utils import load_csv, load_entities, load_html

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
    'Switzerland, for the EIG, proposed X.',
    'Switzerland for the EIG proposed X.',
    'Switzerland, on behalf of the EIG, proposed X.',
    'Switzerland, on behalf of the EIG and Canada, proposed X.',
    'Switzerland, on behalf of the EIG, and Canada, proposed X.',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test "agreement"
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'JAMAICA and TUVALU asked for',
    'JAMAICA, TUVALU, and SWITZERLAND asked for',
    'TUVALU and JAMAICA, opposed by the EU, CANADA and AUSTRALIA, said that',
    'Opposed by SAUDI ARABIA and the US, CHINA stressed parties',
    'Switzerland, for the EIG, and the EU regretted lack of',
    'Switzerland, for the EIG, CANADA and AUSTRALIA, regretted',
    'Switzerland, for the EIG, CANADA and AUSTRALIA, and the EU regretted',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# Test "supported by".
scraper = InteractionScraper(html, issue, entities)
sentences = [
    'CHINA, supported by EGYPT',
    'CHINA, for the G77, supported by NIGERIA',
    'INDIA and CHINA, supported by NIGERIA, OMAN and BRAZIL',
    'Supported by SAUDI ARABIA, CHINA stressed parties',
    'Supported by SAUDI ARABIA and EGYPT, CHINA stressed parties',
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

# Test with a complex sentence.
scraper = InteractionScraper(html, issue, entities)
complex_sentence = '''Supported by Lesotho, for the LDCs, Spain, for the EU,\
 PANAMA, SOUTH AFRICA, AUSTRALIA, COLOMBIA, MALAWI, the PHILIPPINES and NORWAY\
, AOSIS proposed'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(interaction.__repr__())

scraper = InteractionScraper(html, issue, entities)
complex_sentence = '''Switzerland, for the EIG, NORWAY, for Australia, New\
 Zealand, the US, Canada and Japan, the EU and MARSHALL ISLANDS, opposed by\
 CHINA, proposed that'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(interaction.__repr__())

scraper = InteractionScraper(html, issue, entities)
complex_sentence = '''CUBA, for Algeria, Argentina, Brazil, China, Ecuador,\
 Egypt, Malaysia, Nicaragua, the Philippines, Saudi Arabia, Venezuela,\
 Thailand Pakistan, Uruguay, Sierra Leone, Paraguay, India and Bolivia,\
 supported by CHINA, outlined elements that'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(interaction.__repr__())

scraper = InteractionScraper(html, issue, entities)
complex_sentence = '''Guatemala for AILAC, Mexico for the Environmental\
 Integrity Group, the EU, the Philippines, Bangladesh, the Dominican Republic,\
 Viet Nam, Venezuela, and Sudan for the African Group, stressed including\
 gender equality, with some parties variously calling for reference to human\
 rights, intergenerational equity, and the rights of indigenous peoples.'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    # if interaction.type != 'agreement':
    print(repr(interaction))
