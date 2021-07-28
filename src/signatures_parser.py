import math
import json
import csv

key_full_name = 'Full Name'
key_date = 'Date'
key_email = 'Email'


def parse(file_name):
    with open(file_name, 'r') as file:
        response = json.load(file)

    signature_data = extract_signature_data(response)
    grouped_signature_data = group_by_page_column(signature_data)
    signatures = convert_to_list(grouped_signature_data)

    csv_file_name = file_name.removesuffix('.json') + '_output.csv'

    with open(csv_file_name, mode='w') as csv_file:
        fieldnames = [key_full_name, key_date, key_email]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for row in signatures:
            writer.writerow(row)


def extract_signature_data(response):
    signature_data = []
    for responsePage in response:
        blocks = responsePage['Blocks']
        for block in blocks:
            if block['BlockType'] == "LINE":
                left_signature_data = find_left_signature(block)
                if left_signature_data is not None:
                    signature_data.append(left_signature_data)
                else:
                    right_signature_data = find_right_signature(block)
                    if right_signature_data is not None:
                        signature_data.append(right_signature_data)
    return signature_data


def group_by_page_column(signature_data):
    result = {}
    for data in signature_data:
        key = (data['Page'], data['Column'])
        if key in result:
            grouped_items = result[key]
        else:
            grouped_items = []
        grouped_items.append(data)
        result[key] = grouped_items
    return result


def convert_to_list(grouped_signature_data):
    signatures = []
    for signature_data in grouped_signature_data.values():
        signature_item = {}
        for key_value in signature_data:
            signature_item[key_value['Key']] = key_value['Value']
        signatures.append(signature_item)
    print('Found signatures: {}'.format(signatures))
    return signatures


def find_left_signature(block):
    signature_top = 0.42459
    signature_left = 0.09459
    date_top = 0.45682
    date_left = 0.09847
    email_top = 0.50061
    email_left = 0.09494

    return find_signature(block, date_left, date_top, email_left, email_top, signature_left, signature_top, 'left')


def find_right_signature(block):
    signature_top = 0.42458
    signature_left = 0.52781
    date_top = 0.45682
    date_left = 0.52781
    email_top = 0.50047
    email_left = 0.52882

    return find_signature(block, date_left, date_top, email_left, email_top, signature_left, signature_top, 'right')


def find_signature(block, date_left, date_top, email_left, email_top, signature_left, signature_top, column):
    box = block['Geometry']['BoundingBox']
    top_box = box['Top']
    left_box = box['Left']
    if are_close(top_box, signature_top, left_box, signature_left):
        return map_to_dict(key_full_name, block, column)
    if are_close(top_box, date_top, left_box, date_left):
        return map_to_dict(key_date, block, column)
    if are_close(top_box, email_top, left_box, email_left):
        return map_to_dict(key_email, block, column)


def map_to_dict(key, block, column):
    return {'Key': key, 'Value': block['Text'], 'Page': block['Page'], 'Column': column, 'Id': block['Id']}


def are_close(top_a, top_b, left_a, left_b):
    return math.isclose(top_a, top_b, abs_tol=0.001) & math.isclose(left_a, left_b, abs_tol=0.001)
