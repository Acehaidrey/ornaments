import csv
import os

from collections import defaultdict

DESCRIPTION = """
This festive and thoughtful ornament is perfect for adding to any tree! Each ornament is personalized for free with names, years, and sometimes additional writing. Please specify precisely where you’d like each name to go. Otherwise our talented artists always use their best judgement to make your ornament special. The ornaments are personalized with permanent ink by hand.
[Disclaimer] It is your responsibility to ensure the spelling you give us is correct. Double check all spelling because if an issue occurs, we will not be able to replace it. If you’d like to forgo personalization, just write “No Personalization” in the box.
Please also note, the color scheme, design, and all that you see in the first image for the ornament cannot be altered. They come pre made that way.
Orders with confusing or unclear instructions may be delayed until we are able to reconnect with you to verify the desired personalization. If we cannot reach you in a timely manner, we will send the ornament with our best judgement or without personalization and we will not refund for this case either.
Thank you!
"""


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
        csv_writer = csv.writer(out_csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
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
    pfs_purchased = {
        '1165-R', '1404', '1435', '1591-W/O STAMP', '1145', '1717', '2037', '2138', '2300', '600-b', '600-p', '600-RG'
    }
    prefix_ = 'OR' if item_id_upped not in pfs_purchased else 'PF'
    return prefix_ + item_id if not item_id.startswith(prefix_) else item_id


def find_missing_photos(folder_path, invoice_path):
    """Compare the photos given from fiver person to the items from invoice. Name comparison."""
    invoice_ids, downloads_ids = set(), set()
    with open(invoice_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0] == 'Number':
                continue
            # print(row)
            invoice_ids.add(row[0])

    for f in os.listdir(folder_path):
        # print(f)
        downloads_ids.add(f.strip('.jpg'))

    missing_items = invoice_ids - downloads_ids
    print(f'Invoice has {len(invoice_ids)} items. Downloads folder has {len(downloads_ids)} items.')
    if missing_items:
        print(sorted(list(invoice_ids)))
        print(sorted(list(downloads_ids)))
        print(sorted(list(missing_items)))
        print(len(missing_items))
        # print(invoice_ids.intersection(downloads_ids))


def format_item_name(item_name):
    """Function to apply custom rules to item name as there is no format."""
    # print('----')
    # print(item_name)
    item_name = item_name.upper().strip().replace('\n', ' ')
    item_name = item_name.replace('OR 1253-8', 'OR1253-8')
    # item_name = item_name.replace('OR1061-A', '(OR1061-A)')

    # remove multiple white space
    item_name_list = [i.strip() for i in item_name.split(' ')]
    item_name_list = [i for i in item_name_list if i]
    # put spaces in between category and item name. for any -, it will space before and after
    if not (item_name.startswith('OR') or item_name.startswith('PF')):
        temp_list = []
        for i in item_name_list:
            if not (i.startswith('(') and i.endswith(')')) and '-' in i and (i != 'T-REX' and i != 'T-BALL'):
                splitted = [x for x in i.split('-')]
                temp_list.append(' - '.join(splitted).strip('  '))
            else:
                temp_list.append(i)
        item_name_list = temp_list
    item_name = ' '.join(item_name_list)

    # print(item_name)
    # print('----')

    # if item_name.startswith('OR') or item_name.startswith('PF'):
    #     item_name_list = item_name.split(' ')
    #     if len(item_name_list) > 1:
    #         item_name = ' '.join(item_name_list[1:]) + f' ({item_name_list[0]})'

    return item_name


def rename_items_in_catalog(catalog_path, invoice_path):

    name_to_description = {}
    with open(invoice_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        count = 0
        for row in csv_reader:
            # print(row)
            fmt_desc = format_item_name(row['Description'])\
                .replace('PICTUREFRAME', 'PICTURE FRAME')\
                .replace('W/OSTAMP', 'W/O STAMP')
            desc_val = fmt_desc + f" ({row['Number'].upper()})"
            name_to_description.update({row['Number'].upper(): desc_val})
            count += 1
        print(f'{count} items found in invoice')

    recs, all_records = [], []
    with open(catalog_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        count = 0
        for row in csv_reader:
            row['Item Name'] = format_item_name(row['Item Name'])
            row['Enabled Mission Viejo'] = 'Y'
            row['Enabled Cerritos'] = 'Y'
            row['Enabled Westminster'] = 'Y'
            row['Tax - Sales Tax (7.75%)'] = 'Y'
            row['Square Online Item Visibility'] = 'visible'  # BE CAREFUL - NOT EVERYTHING SHOULD BE VISIBLE
            if row['Item Name'].startswith('OR') or row['Item Name'].startswith('PF') or row['Item Name'].startswith('RM'):
                item_name_list = row['Item Name'].split(' ')
                # this to handle case where ornament names are like 'OR1241 HOCKEY BOY'
                if row['Item Name'] not in name_to_description.keys() \
                        and len(item_name_list) > 1 \
                        and 'W/O STAMP' not in row['Item Name']:
                        row['Item Name'] = ' '.join(item_name_list[1:]) + f' ({item_name_list[0]})'
                else:
                    # get description name of catalog formatted as item name, or just use short item name if not found
                    row['Item Name'] = name_to_description.get(row['Item Name'], row['Item Name'])

                row['Description'] = DESCRIPTION.strip()
                row['Category'] = 'Ornament'
                recs.append(row)
                count += 1
            all_records.append(row)
        print(f'{count} items found in catalog that begin with OR/PF. {len(all_records)} processed from catalog file')

    for row in recs:
        print(row)
    print(len(recs))
    from pprint import pprint
    pprint(name_to_description)

    missing = [i['Item Name'] for i in recs if i['Item Name'].startswith('OR') or i['Item Name'].startswith('PF')]
    for i in missing:
        if i in name_to_description:
            print(f"{i}: {name_to_description['i']}")
        else:
            print(f'{i} not found in invoice')
    print(f'{len(missing)} missing items found')

    multiple_types = [i['Item Name'] for i in recs if 'OF EACH' in i['Item Name'] or '-A' in i['Item Name']]
    pprint(multiple_types)
    print(f'{len(multiple_types)} ornaments with multiple types found')

    output_path = catalog_path.strip('.csv') + '_CLEANEDUP.csv'
    with open(output_path, 'w+', newline='\n') as out_csvfile:
        csv_writer = csv.DictWriter(out_csvfile, fieldnames=recs[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(all_records)
        print(f'Wrote output to: {output_path}')
    return output_path


if __name__ == '__main__':
    csv_counted_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'ORNAMENTS_2022.csv')
    invoice_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'SO-61394.csv')
    fiver_photo_downloaded_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'Ornaments2022')
    new_named_catalog = os.path.join(os.path.expanduser('~'), 'Downloads', 'LATEST_CATALOG.csv')
    # output_path = format_inventory_received(csv_counted_path)
    # find_missing_photos(fiver_photo_downloaded_path, invoice_path)
    rename_items_in_catalog(new_named_catalog, invoice_path)
