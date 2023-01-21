import logging
import os

from controllers.aws_controller import AWSController
from controllers.notion_controller import NotionController
from controllers.plotter_controller import PlotterController
from data.constants.plot_settings.time_chart_settings import TimeChartSettings


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    notion = NotionController(os.getenv('NT_auth'), notion_version="2022-06-28")
    plotter = PlotterController(notion)

    plotter.plot_time_chart(TimeChartSettings.WEEK)
    plotter.plot_time_chart(TimeChartSettings.MONTH)
    plotter.plot_habits_chart(TimeChartSettings.WEEK)
    plotter.plot_habits_chart(TimeChartSettings.MONTH)

    AWSController().upload_files(plotter.plot_list)


if __name__ == "__main__":
    main()
