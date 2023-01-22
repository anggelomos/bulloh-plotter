import sys
import os
import zipfile

from config import TMP_FOLDER, CHARTS_FOLDER
from controllers.aws_controller import AWSController
from main import main


def lambda_handler(event, conntext):
    # Downloading plotly dependency from S3 during runtime because of the lambda size limit
    zip_dependencies = "plotly-dependencies.zip"
    AWSController().download_file(zip_dependencies, TMP_FOLDER + zip_dependencies)
    with zipfile.ZipFile(TMP_FOLDER + zip_dependencies, "r") as zip_ref:
        zip_ref.extractall(TMP_FOLDER)

    sys.path.insert(0, TMP_FOLDER)

    if not os.path.exists(CHARTS_FOLDER):
        os.makedirs(CHARTS_FOLDER)

    main()
