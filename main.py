import os
import logging

from nothion import NotionClient

from src.aws_client import AWSClient
from src.bulloh_plotter import BullohPlotter
from src.data.constants.plot_settings.chart_types import ChartTypes
from src.data.constants.plot_settings.time_chart_settings import TimeChartSettings


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")


def main():
    notion = NotionClient(os.getenv('NT_AUTH'))
    plotter = BullohPlotter(notion)

    plotter.plot_charts(ChartTypes.TIME_CHART, TimeChartSettings.WEEK)
    plotter.plot_charts(ChartTypes.TIME_CHART, TimeChartSettings.MONTH)

    plotter.plot_charts(ChartTypes.STATS_CHART, TimeChartSettings.DAY)
    plotter.plot_charts(ChartTypes.STATS_CHART, TimeChartSettings.WEEK)
    plotter.plot_charts(ChartTypes.STATS_CHART, TimeChartSettings.MONTH)
    # TODO: Uncomment when habits are restored
    # plotter.plot_charts(ChartTypes.HABITS_CHART, TimeChartSettings.WEEK)
    # plotter.plot_charts(ChartTypes.HABITS_CHART, TimeChartSettings.MONTH)

    AWSClient().upload_files(plotter.plot_list)


if __name__ == "__main__":
    main()
