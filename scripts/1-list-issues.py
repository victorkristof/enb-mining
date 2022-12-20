import fire
from enbmining import Client
from enbmining.utils import save_csv

# Metadata of meetings that should be scraped but that are absent from the ENB
# list of UNFCCC meetings.
missing_meetings = [
    {
        'meeting': '28th Sessions of the UNFCCC Subsidiary Bodies & Sessions of the Ad Hoc Working Groups',
        'meeting_date': '2–13 June 2008',
        'url': 'https://enb.iisd.org/events/28th-sessions-unfccc-subsidiary-bodies-sessions-ad-hoc-working-groups',
    },
    {
        'meeting': 'Bonn Climate Change Conference - June 2015',
        'meeting_date': '1–11 June 2015',
        'url': 'https://enb.iisd.org/events/bonn-climate-change-conference-june-2015',
    },
]


def main(output_path, debug=False):
    client = Client(negotiation='UNFCCC', debug=debug)
    issues = client.get_issues_metadata(
        start_page=1, end_page=9, missing_meetings=missing_meetings
    )
    save_csv(issues, output_path, sort_keys=True)


if __name__ == '__main__':
    fire.Fire(main)
