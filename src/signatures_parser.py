from dataclasses import dataclass
import math
import json
import csv

key_full_name = 'Full Name'
key_date = 'Date'
key_email = 'Email'
key_right_column = 'right'
key_left_column = 'left'


def parse(file_name, is_top_up):
    with open(file_name, 'r') as file:
        response = json.load(file)

    signature_data = extract_signature_data(response, is_top_up)
    grouped_signature_data = group_by_page_column(signature_data)
    signatures = convert_to_list(grouped_signature_data)

    csv_file_name = file_name.removesuffix('.json') + '_signatures_output.csv'

    with open(csv_file_name, mode='w') as csv_file:
        fieldnames = [key_full_name, key_date, key_email]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for row in signatures:
            writer.writerow(row)


def extract_signature_data(response, is_top_up):
    signatures_list = []
    for responsePage in response:
        blocks = responsePage['Blocks']
        for block in blocks:
            if block['BlockType'] == "LINE":
                signature_data = find_signature_by_form_type(block, is_top_up)
                if signature_data is not None:
                    signatures_list.append(signature_data)

    return signatures_list


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


def find_signature_by_form_type(block, is_top_up):
    if is_top_up:
        return find_top_up_form_right_signature(block) or find_top_up_form_left_signature(block)
    else:
        return find_app_form_right_signature(block) or find_app_form_left_signature(block)


def find_app_form_left_signature(block):
    return find_signature(block, app_form_left_column_constraints, key_left_column)


def find_app_form_right_signature(block):
    return find_signature(block, app_form_right_column_constraints, key_right_column)


def find_top_up_form_left_signature(block):
    return find_signature(block, top_up_form_left_column_constraints, key_left_column)


def find_top_up_form_right_signature(block):
    return find_signature(block, top_up_form_right_column_constraints, key_right_column)


def find_signature(block, constraints, column):
    box = block['Geometry']['BoundingBox']
    top_box = box['Top']
    left_box = box['Left']
    if are_close(top_box, constraints.full_name_top, left_box, constraints.full_name_left):
        return map_to_dict(key_full_name, block, column)
    if are_close(top_box, constraints.date_top, left_box, constraints.date_left):
        return map_to_dict(key_date, block, column)
    if are_close(top_box, constraints.email_top, left_box, constraints.email_left):
        return map_to_dict(key_email, block, column)


def map_to_dict(key, block, column):
    return {'Key': key, 'Value': block['Text'], 'Page': block['Page'], 'Column': column, 'Id': block['Id']}


def are_close(top_a, top_b, left_a, left_b):
    return math.isclose(top_a, top_b, abs_tol=0.0015) & math.isclose(left_a, left_b, abs_tol=0.0015)


@dataclass
class SignatureConstraints:
    full_name_top: float
    full_name_left: float
    date_top: float
    date_left: float
    email_top: float
    email_left: float


app_form_right_column_constraints = SignatureConstraints(
    full_name_top=0.42458,
    full_name_left=0.52781,
    date_top=0.45682,
    date_left=0.52781,
    email_top=0.50047,
    email_left=0.52882,
)

app_form_left_column_constraints = SignatureConstraints(
    full_name_top=0.42459,
    full_name_left=0.09459,
    date_top=0.45682,
    date_left=0.09847,
    email_top=0.50061,
    email_left=0.09494,
)

top_up_form_right_column_constraints = SignatureConstraints(
    full_name_top=0.72552,
    full_name_left=0.53668,
    date_top=0.79200,
    date_left=0.53171,
    email_top=0.75876,
    email_left=0.53171,
)

top_up_form_left_column_constraints = SignatureConstraints(
    full_name_top=0.72538,
    full_name_left=0.09887,
    date_top=0.79188,
    date_left=0.09887,
    email_top=0.75863,
    email_left=0.09611,
)
