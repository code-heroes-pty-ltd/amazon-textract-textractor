import glob
import os
import shutil

from src.textractor import Textractor
import signatures_parser
import s3_uploader


def main():
    source_bucket = 's3://isg-pdf-extraction/'
    output_bucket = 'isg-pdf-extracted'
    output_temp_dir = 'temp/'

    if not os.path.exists(output_temp_dir):
        os.mkdir(output_temp_dir)

    args = [
        '--documents', source_bucket,
        '--forms',
        '--output', output_temp_dir,
    ]
    documents = Textractor().run(args)

    for document in documents:
        is_top_up = is_file_top_up(document)
        signatures_parser.parse(get_json_response_path(output_temp_dir, document), is_top_up)

    remove_unused_pages(output_temp_dir)
    rename_files(output_temp_dir)
    s3_uploader.upload(output_temp_dir, output_bucket)

    if os.path.exists(output_temp_dir):
        shutil.rmtree(output_temp_dir, ignore_errors=True)


def is_file_top_up(file_name):
    return 'Top Up' in file_name


def remove_unused_pages(document_temp_dir):
    app_form_keep_files_pattern = [
        'page-2-forms',
        '_signatures_output.csv',
    ]

    top_up_keep_files_pattern = [
        'page-1-forms',
        '_signatures_output.csv',
    ]

    all_files = glob.glob(document_temp_dir + '*', recursive=True)
    for file in all_files:
        is_top_up = is_file_top_up(file)
        files_pattern = top_up_keep_files_pattern if is_top_up else app_form_keep_files_pattern
        if not any(pattern in file for pattern in files_pattern):
            os.remove(file)


def rename_files(output_temp_dir):
    app_form_file_names_map = {
        'page-2-forms.csv': 'app_form_{}_investment_details.csv',
        '_signatures_output.csv': 'app_form_{}_signatures.csv',
    }

    top_up_file_names_map = {
        'page-1-forms.csv': 'top_up_{}_investment_details.csv',
        '_signatures_output.csv': 'top_up_{}_signatures.csv',
    }

    all_files = glob.glob(output_temp_dir + '*', recursive=True)
    for file in all_files:
        is_top_up = is_file_top_up(file)
        files_pattern = top_up_file_names_map if is_top_up else app_form_file_names_map
        for pattern in files_pattern.keys():
            if pattern in file:
                new_file_name = output_temp_dir + files_pattern[pattern].format(get_document_name(file, output_temp_dir))
                os.rename(file, new_file_name)


def get_json_response_path(output_temp_dir, document):
    filename = get_document_name(document, output_temp_dir)
    return output_temp_dir + filename + '-pdf-response.json'


def get_document_name(document, output_temp_dir):
    return document.removesuffix('.pdf').removeprefix(output_temp_dir)


if __name__ == '__main__':
    main()
