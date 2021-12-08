import fire
from enbmining import Client, save_csv


def main(output_path, debug=False):
    client = Client(negotiation='UNFCCC', debug=debug)
    issues = client.get_issues_metadata(start_page=1, end_page=9)
    save_csv(issues, output_path, sort_keys=True)


if __name__ == '__main__':
    fire.Fire(main)
