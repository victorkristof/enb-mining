from enbmining import InteractionScraper, InterventionScraper
from enbmining.entities import Grouping, Party
from enbmining.utils import load_csv, load_html

parties_path = 'data/parties.txt'
groupings_path = 'data/groupings.txt'
issues_path = 'data/issues.csv'
html_folder = 'data/html'

parties = Party.load(parties_path)
groupings = Grouping.load(groupings_path)
issues = load_csv(issues_path)

issue = issues[0]
html = load_html(html_folder, issue['id'])

# %% Test "on behalf".
scraper = InteractionScraper(html, issue, parties, groupings)
sentences = [
    'Switzerland, for the EIG, proposed X.',
    'Switzerland for the EIG proposed X.',
    'Switzerland, for Canada, proposed X.',
    'Switzerland, on behalf of Canada, proposed',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# %% Test "agreement"
scraper = InteractionScraper(html, issue, parties, groupings)
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

# %% Test "supported by".
scraper = InteractionScraper(html, issue, parties, groupings)
sentences = [
    'CHINA, supported by EGYPT',
    'CHINA, for the G77, supported by NIGERIA',
    'INDIA and CHINA, supported by NIGERIA, OMAN and BRAZIL',
    'Supported by SAUDI ARABIA, CHINA stressed parties',
    'Supported by SAUDI ARABIA and EGYPT, CHINA stressed parties',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# %% Test "opposed by".
scraper = InteractionScraper(html, issue, parties, groupings)
sentences = [
    'JAMAICA, opposed by the EU, asked for',
    'TUVALU and JAMAICA, opposed by the EU, CANADA and AUSTRALIA, said that',
    'Opposed by SAUDI ARABIA, CHINA stressed parties',
]
for sentence in sentences:
    print(scraper._scrape_from_sentence(sentence))

# %% Test with a complex sentence.
scraper = InteractionScraper(html, issue, parties, groupings)
complex_sentence = '''Supported by Lesotho, for the LDCs, Spain, for the EU,\
 PANAMA, SOUTH AFRICA, AUSTRALIA, COLOMBIA, MALAWI, the PHILIPPINES and NORWAY\
 , AOSIS proposed'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(interaction.__repr__())

# %% Test with a complex sentence.
scraper = InteractionScraper(html, issue, parties, groupings)
complex_sentence = '''Switzerland, for the EIG, NORWAY, for Australia, New\
 Zealand, the US, Canada and Japan, the EU and MARSHALL ISLANDS, opposed by\
 CHINA, proposed that'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(interaction.__repr__())

# %% Test with a complex sentence.
scraper = InteractionScraper(html, issue, parties, groupings)
complex_sentence = '''CUBA, for Algeria, Argentina, Brazil, China, Ecuador,\
 Egypt, Malaysia, Nicaragua, the Philippines, Saudi Arabia, Venezuela,\
 Thailand, Pakistan, Uruguay, Sierra Leone, Paraguay, India and Bolivia,\
 supported by CHINA, outlined elements that'''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    if interaction.type != 'agreement':
        print(repr(interaction))

# %% Test with a complex sentence.
scraper = InteractionScraper(html, issue, parties, groupings)
complex_sentence = '''Guatemala for AILAC, Mexico for the Environmental\
 Integrity Group, the EU, the Philippines, Bangladesh, the Dominican Republic,\
 Viet Nam, Venezuela, and Sudan for the African Group, stressed '''
interactions = scraper._scrape_from_sentence(complex_sentence)
for interaction in interactions:
    print(repr(interaction))

# %% Test intervention.
scraper = InterventionScraper(html, issue, parties, groupings)
sentence = '''26th BASIC Ministerial Meeting: BASIC (Brazil, South Africa,\
 India, and China) countries convened in Durban, South Africa, from 19-20 May\
 2018.'''
interventions = scraper._scrape_from_sentence(sentence)
for intervention in interventions:
    print(intervention)

# %% Test intervention.
scraper = InterventionScraper(html, issue, parties, groupings)
sentence = 'Senegal, for the African Group, agreed, noting that'
scraper._scrape_from_sentence(sentence)

# %% Test intervention.
scraper = InterventionScraper(html, issue, parties, groupings)
sentence = 'Senegal, for Zaire and Mauritania, agreed, noting that'
scraper._scrape_from_sentence(sentence)
