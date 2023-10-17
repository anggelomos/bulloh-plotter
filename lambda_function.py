import os
import zipfile

from src._config import CHARTS_FOLDER
from src.aws_client import AWSClient
from main import main


def lambda_handler(event, conntext):
    # Downloading plotly dependency from S3 during runtime because of the lambda size limit
    zip_dependencies = "plotly-dependencies.zip"
    AWSClient().download_file(zip_dependencies, zip_dependencies)
    with zipfile.ZipFile(zip_dependencies, "r") as zip_ref:
        zip_ref.extractall()

    if not os.path.exists(CHARTS_FOLDER):
        os.makedirs(CHARTS_FOLDER)

    main()
