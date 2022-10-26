import csv
import os

from collections import defaultdict


def format_inventory_received(csv_file_path):
    """
    The inventory we received that we counted. There are duplicate items that need to be grouped.
    Compare this to the invoice sent to find which have more or less sent.
    """
    csv_headers = ['Ornament_Name', 'Box_Count']
    output_dict = defaultdict(lambda: 0)
    count, dups = 0, set()
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            count += 1
            if row[0] not in csv_headers:
                try:
                    # print(', '.join(row))
                    _key = row[0].upper().strip().strip('_')  # to keep 0 prefix had to add _ in excel cell
                    _key = add_item_prefix(_key)
                    if _key in output_dict:
                        dups.add(_key)
                    output_dict[_key] += int(row[1].strip())
                except ValueError:
                    print(f'[Record Error] Could not parse count value: {row}.')
        print(f'Processed {len(output_dict.keys())} lines. Input Records Count: {count}. Found {len(dups)} Duplicate.')
        # print(output_dict, dups)
    output_path = csv_file_path.strip('.csv') + '_output.csv'
    with open(output_path, 'w+', newline='\n') as out_csvfile:
        csv_writer = csv.writer(out_csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(csv_headers)
        for key in sorted(output_dict.keys()):
            csv_writer.writerow([key, output_dict[key]])
        print(f'Wrote Output: {output_path}')
    return output_path


def compare_invoice_count_to_our_count(our_count_path, invoice_path):
    with open(our_count_path) as our_csv_file, open(invoice_path) as invoice_csv_file:
        our_csv_reader = csv.reader(our_csv_file, delimiter=',')
        invoice_csv_reader = csv.reader(invoice_csv_file, delimiter=',')
        our_dict, invoice_dict = defaultdict(lambda: 0), defaultdict(lambda: 0)
        for row in our_csv_reader:
            our_dict[row[0]] = int(row[1])
        for row in invoice_csv_reader:
            invoice_dict[row[0]] = int(row[1])
        # get overlap
        # get missing dates
        # build csv with the problematic records comparison


def add_item_prefix(item_id):
    item_id_upped = item_id.upper().strip('PF').strip('OR')
    pfs_purchased = {'1165-R', '1404', '1435', '1591-W/O STAMP', '1145', '1145 Dog in loving memory photo frame', '1717', '2037', '2138', '2300', '600-b', '600-p'}
    prefix_ = 'OR' if item_id_upped not in pfs_purchased else 'PF'
    return prefix_ + _key if not _key.startswith(_prefix) else _key


if __name__ == '__main__':
    csv_counted_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'ORNAMENTS_2022.csv')
    output_path = format_inventory_received(csv_counted_path)
