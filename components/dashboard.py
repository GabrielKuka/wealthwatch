from datetime import date, datetime

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dash_table, dcc, html

layout = dbc.Container(
    id="dashboard_wrapper",
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        dash_table.DataTable(
                            id="recent_expenses",
                            style_header={
                                "font-weight": "bold",
                                "text-transform": "uppercase",
                                "text-align": "left",
                                "background-color": "#36454f",
                                "color": "white",
                            },
                            style_cell={"padding": "10px"},
                            page_size=10,
                        ),
                    ],
                    width="8",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                children=[
                                    dcc.DatePickerRange(
                                        id="date_range",
                                        min_date_allowed=date(2020, 1, 1),
                                        start_date=date(
                                            datetime.now().year,
                                            datetime.now().month,
                                            1,
                                        ),
                                        end_date=datetime.now(),
                                    ),
                                ],
                            ),
                            dcc.Graph(id="expenses_bar_chart"),
                        ],
                        style={"display": "flex", "flexDirection": "column"},
                    ),
                    width="4",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="purchases_by_currency_date_range",
                                min_date_allowed=date(2020, 1, 1),
                                start_date=date(
                                    datetime.now().year - 1,
                                    datetime.now().month,
                                    datetime.now().day,
                                ),
                                end_date=datetime.now(),
                            ),
                            dcc.Graph(id="purchases_by_currency_pie_chart"),
                        ],
                        style={"display": "flex", "flexDirection": "column"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="date_range_sankey",
                                display_format="MM/YYYY",
                                start_date=date(
                                    datetime.now().year,
                                    datetime.now().month,
                                    1,
                                ),
                                end_date=datetime.now(),
                            ),
                            html.Div(
                                "Incomes vs Expenses for the selected timeframe."
                            ),
                            dcc.Graph(id="incomes_and_expenses_sankey"),
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                        },
                    ),
                    width=8,
                ),
            ]
        ),
    ],
)
