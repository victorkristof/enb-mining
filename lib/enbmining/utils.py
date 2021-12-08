import csv


def save_csv(list_of_dict, output_path, sort_keys=False, keys=None):
    if keys is None:
        if sort_keys:
            keys = sorted(list_of_dict[0].keys())
        else:
            keys = list_of_dict[0].keys()
    with open(output_path, 'w', newline='') as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dict)
    print(f'Saved CSV to {output_path}')
