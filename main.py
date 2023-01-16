import logging
import os

import plotly.express as px
import pandas as pd

from controllers.notion_controllers import NotionController
from data.constants.expected_time_metrics import get_expected_time_headers
from data.constants.time_metrics import get_time_headers


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    notion = NotionController(os.getenv('NT_auth'), notion_version="2021-08-16")

    df = notion.get_data_between_dates("2023-01-02", "2023-01-31")

    data_range = [0, 12]
    line_headers = get_time_headers() + get_expected_time_headers()
    line_colors = ["#00b4d8", "#fb5607", "#ef233c", "#5a189a"] * 2
    fig = px.line(df, x="date", y=line_headers,
                  markers=True,
                  range_y=data_range,
                  color_discrete_sequence=line_colors,
                  title="Week's time")

    initial_range = len(get_time_headers())
    for line_index in range(initial_range, initial_range + len(get_time_headers())):
        fig.data[line_index].line.dash = "dash"
        fig.data[line_index].marker.opacity = 0

    fig.write_html("first_figure.html", auto_open=True)


if __name__ == "__main__":
    main()
