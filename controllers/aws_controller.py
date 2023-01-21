import logging
from typing import List

import boto3


class AWSController:

    def __init__(self):
        self.bulloh_bucket_name = "bulloh-plotter"
        self.s3_client = boto3.client('s3')

    def upload_files(self, file_names: List[str]):
        for file_name in file_names:
            logging.info(f"Uploading file {file_name} to s3")
            self.s3_client.upload_file(file_name,
                                       self.bulloh_bucket_name,
                                       file_name.replace("charts/", ""),
                                       ExtraArgs={"ContentType": "text/html"})
