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

    args = ['--documents', source_bucket, '--text', '--forms', '--tables', '--output', output_temp_dir]
    documents = Textractor().run(args)

    for document in documents:
        signatures_parser.parse(get_json_response_path(output_temp_dir, document))
        s3_uploader.upload(get_document_temp_dir_path(output_temp_dir, document), output_bucket)

    if os.path.exists(output_temp_dir):
        shutil.rmtree(output_temp_dir, ignore_errors=True)


def get_document_temp_dir_path(output_temp_dir, document):
    return output_temp_dir + document.removesuffix('.pdf') + '/'


def get_json_response_path(output_temp_dir, document):
    filename = document.removesuffix('.pdf')
    return output_temp_dir + filename + '/' + filename + '-pdf-response.json'


if __name__ == '__main__':
    main()
