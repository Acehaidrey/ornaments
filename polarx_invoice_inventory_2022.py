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
        our_csv_reader = csv.DictReader(our_csv_file)
        invoice_csv_reader = csv.DictReader(invoice_csv_file)
        our_dict, invoice_dict = defaultdict(lambda: 0), defaultdict(lambda: 0)
        for row in our_csv_reader:
            our_dict[row['Ornament_Name']] = int(row['Box_Count'])
        for row in invoice_csv_reader:
            invoice_dict[row['Number']] = int(row['Qty Ordered'].strip().strip('ea'))
        # get overlap
        # get missing dates
        # build csv with the problematic records comparison
        print(our_dict)
        print(invoice_dict)
        keys_only_ours = our_dict.keys() - invoice_dict.keys()
        keys_only_theirs = invoice_dict.keys() - our_dict.keys()
        keys_overlapped = invoice_dict.keys() & our_dict.keys()
        print(sorted(list(keys_only_ours)))
        print(sorted(list(keys_only_theirs)))
        print(sorted(list(keys_overlapped)))
        print('-----')
        remove_prefix = {i.strip('OR').strip('PF') for i in keys_only_ours}.intersection({i.strip('OR').strip('PF') for i in keys_only_theirs})
        print(remove_prefix)
        print('-------')
        output_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'COMPARE_ORNAMENTS.csv')
        with open(output_path, 'w+', newline='\n') as out_csvfile:
            csv_writer = csv.DictWriter(out_csvfile, fieldnames=['Item Name', 'Invoice Count', 'True Count', 'Diff'])
            csv_writer.writeheader()
            for key in keys_overlapped:
                d = {
                    'Item Name': key,
                    'Invoice Count': invoice_dict[key],
                    'True Count': our_dict[key],
                    'Diff': our_dict[key] - invoice_dict[key]
                }
                csv_writer.writerow(d)
                print(d)
            for key in keys_only_theirs:
                d = {
                    'Item Name': key,
                    'Invoice Count': invoice_dict[key],
                    'True Count': 0,
                    'Diff': our_dict[key] - invoice_dict[key]
                }
                csv_writer.writerow(d)
                print(d)



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


def get_square_client():
    app_id = ''
    token = ''
    from square.client import Client

    client = Client(access_token=token, environment='production')
    return client


def get_all_catalog_items():
    token = ''
    from square.client import Client

    client = Client(access_token=token, environment='production')
    all_items = []
    cursor = 'start'
    while cursor:
        if cursor == 'start':
            cursor = None
        raw_return = client.catalog.list_catalog(types='ITEM', cursor=cursor)
        items = raw_return.body['objects']
        all_items.extend(items)
        cursor = raw_return.body['cursor'] if 'cursor' in raw_return.body.keys() else None
        print(f'Added {len(items)} items. Cursor is: {cursor}')
    print(f'Total number of items found {len(all_items)}')
    return all_items


def get_all_catalog_items_missing_images():
    token = ''
    from square.client import Client

    client = Client(access_token=token, environment='production')
    all_items = []
    cursor = 'start'
    while cursor:
        if cursor == 'start':
            cursor = None
        raw_return = client.catalog.list_catalog(types='ITEM', cursor=cursor)
        items = raw_return.body['objects']
        items_missing_images = [i for i in items if not i['item_data'].get('image_ids', None)] # ['item_data']['name']
        all_items.extend(items_missing_images)
        cursor = raw_return.body['cursor'] if 'cursor' in raw_return.body.keys() else None
        print(f'Added {len(items)} items. Cursor is: {cursor}')
    print(f'Total number of items found {len(all_items)} missing any images.')
    return all_items


def get_all_items_in_given_year(items, year_filter=2022):
    items = items or get_all_catalog_items()

    from datetime import datetime

    recent_items = []
    for item in items:
        created_at = item['created_at']
        try:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        yr = created_at_dt.year
        if yr == year_filter:
            recent_items.append(item)
    print(f'Total number of items found {len(recent_items)}')
    return recent_items


def update_photos_of_items():
    token = ''
    from square.client import Client
    import os, time

    fiver_photo_downloaded_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'Ornaments2022')
    client = Client(access_token=token, environment='production')

    found_items = []
    for f in os.listdir(fiver_photo_downloaded_path):
        image_id = f.strip('.jpg')
        req = client.catalog.search_catalog_items(body={"text_filter": image_id}).body
        try:
            items = req['items']
            print(f'For id {image_id} found {len(items)} items in catalog')
        except KeyError:
            print(f'ERROR: No results for {image_id}')
            items = []
        for item in items:
            item_id = item['id']
            item_name = item['item_data']['name']
            short_item_name = item_name.split(' ')[-1].strip('(').strip(')')
            found_items.extend(short_item_name)
            print(image_id, item_id, item_name, short_item_name)
            result = client.catalog.create_catalog_image(
                request={
                    "idempotency_key": str(time.time()),
                    "object_id": item_id,
                    "image": {
                        "type": "IMAGE",
                        "id": f"#{short_item_name}",
                        "image_data": {
                            "caption": item_name
                        }
                    }
                },
                image_file=open(os.path.join(fiver_photo_downloaded_path, f), 'rb')
            )
            if result.is_error():
                print(f'ERROR {image_id}, {item_name}, {result.errors}')
    return found_items


def fill_missing_update_photos_of_items():
    token = ''
    from square.client import Client
    import os, time

    fiver_photo_downloaded_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'Ornaments2022')
    client = Client(access_token=token, environment='production')

    items_missing_images = get_all_catalog_items_missing_images()
    all_images_in_folder = os.listdir(fiver_photo_downloaded_path)
    still_missing = []
    for item in items_missing_images:
        item_id = item['id']
        item_name = item['item_data']['name']
        short_item_name = item_name.split(' ')[-1].strip('(').strip(')')
        image_id = short_item_name + '.jpg'
        print(image_id, item_id, item_name, short_item_name)
        if image_id in all_images_in_folder:
            result = client.catalog.create_catalog_image(
                request={
                    "idempotency_key": str(time.time()),
                    "object_id": item_id,
                    "image": {
                        "type": "IMAGE",
                        "id": f"#{short_item_name}",
                        "image_data": {
                            "caption": item_name
                        }
                    }
                },
                image_file=open(os.path.join(fiver_photo_downloaded_path, image_id), 'rb')
            )
            if result.is_error():
                print(f'ERROR {image_id}, {item_name}, {result.errors}')
        else:
            print(f'ERROR {image_id} not found. {item_name}')
            still_missing.append(item_name)
    return still_missing


if __name__ == '__main__':
    csv_counted_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'ORNAMENTS_2022.csv')
    output_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'ORNAMENTS_2022_output.csv')
    invoice_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'SO-61394.csv')
    fiver_photo_downloaded_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'Ornaments2022')
    new_named_catalog = os.path.join(os.path.expanduser('~'), 'Downloads', 'LATEST_CATALOG.csv')
    # output2300_path = format_inventory_received(csv_counted_path)
    # find_missing_photos(fiver_photo_downloaded_path, invoice_path)
    # rename_items_in_catalog(new_named_catalog, invoice_path)
    # get_all_catalog_items()
    compare_invoice_count_to_our_count(output_path, invoice_path)


# curl https://connect.squareup.com/v2/catalog/images \
#   -X POST \
#   -H 'Square-Version: 2022-10-19' \
#   -H 'Authorization: Bearer '' \
#   -H 'Accept: application/json' \
#   -F 'file=@/Users/ahaidrey/Downloads/Ornaments2022/OR2026-4.jpg' \
#   -F 'request={
#     "idempotency_key": "OR2026-4",
#     "object_id": "NUY2THAJA53PAD62FMCIQTJK",
#     "image": {
#       "id": "#OR2026-4",
#       "type": "IMAGE",
#       "image_data": {
#         "caption": "FAMILY SERIES - FARM HOUSE FAMILY OF 4 (OR2026-4)"
#       }
#     }
#   }'
