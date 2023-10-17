import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, List

import attrs
import pendulum
from nothion import NotionClient, PersonalStats
from pandas import DataFrame, concat

from ._config import CHARTS_FOLDER, EXPECTED_POINTS
from .data.constants.expected_time_metrics import get_expected_time_headers, expected_time_metrics
from .data.constants.habits import get_habit_headers
from .data.constants.habits_time import get_habit_time_headers, irregular_habits_time_parser
from .data.constants.plot_settings.chart_types import ChartTypes
from .data.constants.plot_settings.time_chart_settings import TimeChartSettings
from .data.constants.time_metrics import get_time_headers, TimeMetrics as TM
from src.general_utilities import GeneralUtilities as GU


class BullohPlotter:

    def __init__(self, notion: NotionClient):
        self.notion = notion
        self.today_date = pendulum.now("America/Bogota")
        self._date_format = "%Y-%m-%d"
        self._plot_list: List[str] = []

    @property
    def plot_list(self):
        return self._plot_list

    @staticmethod
    def _list_stats_to_dataframe(stats: List[PersonalStats]) -> DataFrame:
        return DataFrame([attrs.asdict(stat) for stat in stats])

    def _time_chart_plotter(self, start_date: datetime, end_date: datetime, time_setting: TimeChartSettings)\
            -> str:
        # Had to put the import here because the library is downloaded during runtime in the lambda_function.py
        import plotly.express as px  # type: ignore
        logging.info(f"Plotting {time_setting.value} time chart from {start_date} to {end_date}")

        plot_data = self._list_stats_to_dataframe(self.notion.get_stats_between_dates(start_date, end_date))
        plot_data = plot_data.drop("weight", axis=1)

        expected_data = DataFrame({metric: [expected_value]*len(plot_data)
                                   for metric, expected_value in expected_time_metrics.items()})

        plot_data = concat([plot_data, expected_data], axis=1)

        if time_setting == TimeChartSettings.WEEK:
            plot_data["date"] = plot_data["date"].apply(lambda date: datetime.strptime(date, self._date_format).
                                                        strftime("%A"))

        data_range = [0, 12]
        line_headers = get_time_headers() + get_expected_time_headers()
        line_colors = ["#00b4d8", "#fb5607", "#ef233c"] * 2
        fig = px.line(plot_data, x="date", y=line_headers,
                      markers=True,
                      range_y=data_range,
                      color_discrete_sequence=line_colors)

        fig.update_layout(yaxis_title=None, xaxis_title=None)

        initial_range = len(get_time_headers())
        for line_index in range(initial_range, initial_range + len(get_time_headers())):
            fig.data[line_index].line.dash = "dash"
            fig.data[line_index].marker.opacity = 0

        match time_setting:
            case TimeChartSettings.WEEK:
                date_number = start_date.strftime('%W')
            case TimeChartSettings.MONTH:
                date_number = start_date.strftime('%m')
            case _:
                date_number = 0

        title_index = f"{time_setting.value}_{date_number}_{start_date.year}"
        chart_title = f"{CHARTS_FOLDER}{title_index}_time_chart.html"

        fig.write_html(chart_title)
        self._plot_list.append(chart_title)
        return chart_title

    @staticmethod
    def _get_habits_chart_time_data(df: DataFrame) -> Tuple[dict, int]:
        time_metrics = {}
        time_points = 0
        for metric in get_time_headers():
            amount_hours = round(df[metric].sum(), 2)
            time_metrics[metric] = amount_hours

            if metric == TM.FOCUS_TIME.value:
                amount_hours *= 2

            time_points += round(amount_hours, 2)

        return time_metrics, time_points

    @staticmethod
    def _get_habits_general_data(df: DataFrame) -> Tuple[dict, dict, int]:
        habit_checks = {}
        habit_percentages = {}
        habit_points = 0
        for habit in get_habit_headers():
            habit_checks_amount = int(df[habit].sum())
            habit_checks[habit] = habit_checks_amount
            habit_points = habit_checks_amount
            # TODO: Check how to get the percentage of the habit
            # habit_percentage = round(df[habit].value_counts(normalize=True).get(True, 0) * 100, 2)
            habit_percentage = 10
            habit_percentages[habit] = f"{habit_percentage}%"

        return habit_checks, habit_percentages, habit_points

    @staticmethod
    def _get_habits_time_data(df: DataFrame) -> dict:
        habit_times = {habit: 0 for habit in get_habit_headers()}
        irregular_habit_times = irregular_habits_time_parser
        for habit in get_habit_time_headers():
            habit_clean = habit.replace(" time", "")
            if habit_clean in habit_times:
                habit_times[habit_clean] = round(df[habit].sum(), 1)
            elif habit in irregular_habit_times:
                habit_times[irregular_habit_times[habit]] = round(df[habit].sum(), 1)
            else:
                raise ValueError(f"Could not find {habit_clean} in the habit times dictionary")

        return habit_times

    def _habits_chart_plotter(self, start_date: datetime, end_date: datetime, year: int,
                              time_setting: TimeChartSettings) -> str:
        logging.info(f"Plotting {time_setting.value} habits chart from {start_date} to {end_date}")
        plot_data = self._list_stats_to_dataframe(self.notion.get_stats_between_dates(start_date, end_date))
        plot_data = plot_data.drop("weight", axis=1)

        title_index = f"{time_setting.value}_{plot_data.iloc[0][f'{time_setting.value} #']}_{year}"
        chart_title = f"{CHARTS_FOLDER}{title_index}_habits_chart.html"
        shutil.copyfile(f"templates/{time_setting.value}_habits_template.html", chart_title)

        time_metrics, time_points = self._get_habits_chart_time_data(plot_data)
        habit_checks, habit_percentages, habit_points = self._get_habits_general_data(plot_data)
        habit_times = self._get_habits_time_data(plot_data)

        overall_points = time_points + habit_points
        time_metrics["overall points"] = f"{round(overall_points/EXPECTED_POINTS[time_setting]*100, 2)}%"

        file = Path(chart_title)
        text = file.read_text("utf-8").replace("//timeValues", json.dumps(GU.adapt_keys(time_metrics)))
        text = text.replace("//habitTimeValues", json.dumps(GU.adapt_keys(habit_times)))

        if time_setting == TimeChartSettings.MONTH:
            text = text.replace("//habitCheckValues", json.dumps(GU.adapt_keys(habit_checks)))
            text = text.replace("//habitPercentageValues", json.dumps(GU.adapt_keys(habit_percentages)))

        file.write_text(text, "utf-8")
        self._plot_list.append(chart_title)
        return chart_title

    def plot_charts(self, chart_type: ChartTypes, time_setting: TimeChartSettings) -> List[str]:
        dates = []
        if time_setting == TimeChartSettings.WEEK:
            dates = [self.today_date, self.today_date.subtract(weeks=1), self.today_date.subtract(weeks=2)]
        elif time_setting == TimeChartSettings.MONTH:
            dates = [self.today_date, self.today_date.subtract(months=1)]

        file_paths = []
        for date in dates:
            start_date = date.start_of(time_setting.value)
            end_date = date.end_of(time_setting.value)
            if chart_type == ChartTypes.TIME_CHART:
                file_paths.append(self._time_chart_plotter(start_date, end_date, time_setting))
            elif chart_type == ChartTypes.HABITS_CHART:
                file_paths.append(self._habits_chart_plotter(start_date, end_date, date.year, time_setting))

        return file_paths
