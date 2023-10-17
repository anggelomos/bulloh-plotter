import os
import sys
import zipfile

from src._config import CHARTS_FOLDER, TMP_FOLDER
from src.aws_client import AWSClient
from main import main


def lambda_handler(event, conntext):
    # Downloading plotly dependency from S3 during runtime because of the lambda size limit
    zip_dependencies = "plotly-dependencies.zip"
    AWSClient().download_file(zip_dependencies, TMP_FOLDER + zip_dependencies)
    with zipfile.ZipFile(TMP_FOLDER + zip_dependencies, "r") as zip_ref:
        zip_ref.extractall(TMP_FOLDER)

    sys.path.insert(0, TMP_FOLDER)

    if not os.path.exists(CHARTS_FOLDER):
        os.makedirs(CHARTS_FOLDER)

    main()
