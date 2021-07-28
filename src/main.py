import glob
import os
import shutil

from src.textractor import Textractor
import signatures_parser
import s3_uploader


def main():
    source_bucket = 's3://isg-pdf-extraction/'
    output_bucket = 'isg-pdf-extracted-test'
    output_temp_dir = 'temp/'

    if not os.path.exists(output_temp_dir):
        os.mkdir(output_temp_dir)

    args = [
        '--documents', source_bucket,
        '--text',
        '--output', output_temp_dir,
    ]
    documents = Textractor().run(args)

    # documents = [
        # 'Adam Clarke _ Angela McArdle REEF_Additional Investment Form Carindale $5K Top Up #1.pdf',
        # 'Daniel Barry Lamb ISG REEF Application Form $25K.pdf',
        # 'Sethi Superfund ISG PAF App Form SMP $50K 4 years CRN 25509300.pdf'
    # ]

    for document in documents:
        is_top_up = is_file_top_up(document)
        document_temp_dir = get_document_temp_dir_path(output_temp_dir, document)

        remove_unused_pages(document_temp_dir, is_top_up)
        signatures_parser.parse(get_json_response_path(output_temp_dir, document), is_top_up)
        s3_uploader.upload(document_temp_dir, output_bucket)

    if os.path.exists(output_temp_dir):
        shutil.rmtree(output_temp_dir, ignore_errors=True)


def is_file_top_up(file_name):
    return 'Top Up' in file_name


def remove_unused_pages(document_temp_dir, is_top_up):
    app_form_keep_files_pattern = [
        'page-2-',
        '_signatures_output.csv',
        'pdf-response.json'
    ]

    if not is_top_up:
        all_files = glob.glob(document_temp_dir + '*', recursive=True)
        for file in all_files:
            if not any(pattern in file for pattern in app_form_keep_files_pattern):
                os.remove(file)


def get_document_temp_dir_path(output_temp_dir, document):
    return output_temp_dir + document.removesuffix('.pdf') + '/'


def get_json_response_path(output_temp_dir, document):
    filename = document.removesuffix('.pdf')
    return output_temp_dir + filename + '/' + filename + '-pdf-response.json'


if __name__ == '__main__':
    main()
