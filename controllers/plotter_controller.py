import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, List

import pendulum

from config import CHARTS_FOLDER, EXPECTED_POINTS
from controllers.notion_controller import NotionController
from data.constants.expected_time_metrics import get_expected_time_headers
from data.constants.habits import get_habit_headers
from data.constants.habits_time import get_habit_time_headers, irregular_habits_time_parser
from data.constants.plot_settings.chart_types import ChartTypes
from data.constants.plot_settings.time_chart_settings import TimeChartSettings
from data.constants.time_metrics import get_time_headers, TimeMetrics as TM
from pandas import DataFrame
from utilities.general_utilities import GeneralUtilities as GU


class PlotterController:

    def __init__(self, notion: NotionController):
        self.notion = notion
        self.today_date = pendulum.now("America/Bogota")
        self._date_format = "%Y-%m-%d"
        self._plot_list = []

    @property
    def plot_list(self):
        return self._plot_list

    def _time_chart_plotter(self, start_date: str, end_date: str, year: int, time_setting: TimeChartSettings) -> str:
        # Had to put the import here because the library is downloaded during runtime in the lambda_function.py
        import plotly.express as px

        logging.info(f"Plotting {time_setting.value} time chart from {start_date} to {end_date}")
        df = self.notion.get_data_between_dates(start_date, end_date)

        if time_setting == TimeChartSettings.WEEK:
            df["date"] = df["date"].apply(lambda date: datetime.strptime(date, self._date_format).strftime("%A"))

        data_range = [0, 12]
        line_headers = get_time_headers() + get_expected_time_headers()
        line_colors = ["#00b4d8", "#fb5607", "#ef233c", "#5a189a"] * 2
        fig = px.line(df, x="date", y=line_headers,
                      markers=True,
                      range_y=data_range,
                      color_discrete_sequence=line_colors)

        fig.update_layout(yaxis_title=None, xaxis_title=None)

        initial_range = len(get_time_headers())
        for line_index in range(initial_range, initial_range + len(get_time_headers())):
            fig.data[line_index].line.dash = "dash"
            fig.data[line_index].marker.opacity = 0

        title_index = f"{time_setting.value}_{df.iloc[0][f'{time_setting.value} #']}_{year}"
        chart_title = f"{CHARTS_FOLDER}{title_index}_time_chart.html"

        fig.write_html(chart_title)
        self._plot_list.append(chart_title)
        return chart_title

    @staticmethod
    def _get_habits_chart_time_data(df: DataFrame) -> Tuple[dict, int]:
        time_metrics = {}
        time_points = 0
        for metric in get_time_headers():
            amount_hours = GU.round_number(df[metric].sum())
            time_metrics[metric] = amount_hours

            if metric == TM.FOCUS_TIME.value:
                amount_hours *= 2

            time_points += GU.round_number(amount_hours)

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
            habit_percentage = GU.round_number(df[habit].value_counts(normalize=True).get(True, 0) * 100)
            habit_percentages[habit] = f"{habit_percentage}%"

        return habit_checks, habit_percentages, habit_points

    @staticmethod
    def _get_habits_time_data(df: DataFrame) -> dict:
        habit_times = {habit: 0 for habit in get_habit_headers()}
        irregular_habit_times = irregular_habits_time_parser
        for habit in get_habit_time_headers():
            habit_clean = habit.replace(" time", "")
            if habit_clean in habit_times:
                habit_times[habit_clean] = GU.round_number(df[habit].sum(), 1)
            elif habit in irregular_habit_times:
                habit_times[irregular_habit_times[habit]] = GU.round_number(df[habit].sum(), 1)
            else:
                raise ValueError(f"Could not find {habit_clean} in the habit times dictionary")

        return habit_times

    def _habits_chart_plotter(self, start_date: str, end_date: str, year: int, time_setting: TimeChartSettings) -> str:
        logging.info(f"Plotting {time_setting.value} habits chart from {start_date} to {end_date}")
        df = self.notion.get_data_between_dates(start_date, end_date)

        title_index = f"{time_setting.value}_{df.iloc[0][f'{time_setting.value} #']}_{year}"
        chart_title = f"{CHARTS_FOLDER}{title_index}_habits_chart.html"
        shutil.copyfile(f"templates/{time_setting.value}_habits_template.html", chart_title)

        time_metrics, time_points = self._get_habits_chart_time_data(df)
        habit_checks, habit_percentages, habit_points = self._get_habits_general_data(df)
        habit_times = self._get_habits_time_data(df)

        overall_points = time_points + habit_points
        time_metrics["overall points"] = f"{GU.round_number(overall_points/EXPECTED_POINTS[time_setting]*100)}%"

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
            start_date = date.start_of(time_setting.value).strftime(self._date_format)
            end_date = date.end_of(time_setting.value).strftime(self._date_format)
            if chart_type == ChartTypes.TIME_CHART:
                file_paths.append(self._time_chart_plotter(start_date, end_date, date.year, time_setting))
            elif chart_type == ChartTypes.HABITS_CHART:
                file_paths.append(self._habits_chart_plotter(start_date, end_date, date.year, time_setting))

        return file_paths
