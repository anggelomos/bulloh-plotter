import os
import logging

from controllers.aws_controller import AWSController
from controllers.notion_controller import NotionController
from controllers.plotter_controller import PlotterController
from data.constants.plot_settings.chart_types import ChartTypes
from data.constants.plot_settings.time_chart_settings import TimeChartSettings


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    notion = NotionController(os.getenv('NT_auth'), notion_version="2022-06-28")
    plotter = PlotterController(notion)

    plotter.plot_charts(ChartTypes.TIME_CHART, TimeChartSettings.WEEK)
    plotter.plot_charts(ChartTypes.TIME_CHART, TimeChartSettings.MONTH)
    plotter.plot_charts(ChartTypes.HABITS_CHART, TimeChartSettings.WEEK)
    plotter.plot_charts(ChartTypes.HABITS_CHART, TimeChartSettings.MONTH)

    AWSController().upload_files(plotter.plot_list)


if __name__ == "__main__":
    main()
