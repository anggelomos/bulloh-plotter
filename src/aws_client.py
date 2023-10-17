import logging
from typing import List

import boto3

from ._config import CHARTS_FOLDER


class AWSClient:

    def __init__(self):
        self.bulloh_plotter_bucket_name = "bulloh-plotter"
        self.s3_client = boto3.client('s3')

    def download_file(self, file_name: str, file_path: str):
        logging.info(f"Downloading file {file_name} from s3")
        self.s3_client.download_file("bulloh-data", file_name, file_path)

    def upload_files(self, file_names: List[str]):
        for file_name in file_names:
            logging.info(f"Uploading file {file_name} to s3")
            self.s3_client.upload_file(file_name,
                                       self.bulloh_plotter_bucket_name,
                                       file_name.replace(CHARTS_FOLDER, ""),
                                       ExtraArgs={"ContentType": "text/html"})
