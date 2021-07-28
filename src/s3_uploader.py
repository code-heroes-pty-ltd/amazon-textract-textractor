import os

from botocore.exceptions import ClientError

from src.helper import S3Helper


def upload(source_dir, output_bucket):
    print("Uploading to S3...")

    generated_files = os.listdir(source_dir)
    for file in generated_files:
        abs_path = os.path.abspath(source_dir + file)
        print("Uploading file " + abs_path)
        try:
            S3Helper.upload_file_to_s3_bucket(abs_path, file, output_bucket)
        except ClientError as e:
            print(e)

    print("Document uploaded to S3 successfully.")
