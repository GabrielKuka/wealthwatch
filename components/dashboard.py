from datetime import date, datetime

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dash_table, dcc, html

layout = dbc.Container(
    id="dashboard_wrapper",
    fluid=True,
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        dash_table.DataTable(
                            id="recent_expenses",
                            filter_action="native",
                            filter_options={"case": "insensitive"},
                            sort_action="native",
                            sort_mode="multi",
                            style_filter={"background-color": "#8A98A1"},
                            style_header={
                                "font-weight": "bold",
                                "text-transform": "uppercase",
                                "text-align": "left",
                                "background-color": "#36454f",
                                "color": "white",
                            },
                            style_cell={
                                "padding": "10px",
                                "textAlign": "left",
                            },
                            style_cell_conditional=[
                                {
                                    "if": {"column_id": "currency"},
                                    "width": "20px",
                                }
                            ],
                            page_size=10,
                        ),
                    ],
                    width="7",
                ),
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                dash_table.DataTable(
                                    id="expenses_aggs",
                                    columns=[
                                        {"name": "Measure", "id": "measure"},
                                        {"name": "Value", "id": "value"},
                                    ],
                                    style_cell={
                                        "textAlign": "left",
                                        "width": "60px",
                                        "maxWidth": "80px",
                                    },
                                    style_header={
                                        "font-weight": "bold",
                                        "text-transform": "uppercase",
                                        "text-align": "left",
                                        "background-color": "#36454f",
                                        "color": "white",
                                    },
                                ),
                                dcc.Graph(
                                    id="expenses_line_chart",
                                    style={"padding": "0"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "5px",
                                "height": "100px",
                            },
                        )
                    ]
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="expenses_bar_chart"),
                    ],
                    width="4",
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="incomes_and_expenses_sankey",
                            style={"padding": "0"},
                        ),
                    ],
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dcc.Graph(id="purchases_by_currency_pie_chart"),
                    ],
                    style={"display": "flex", "flexDirection": "column"},
                ),
                width=4,
            ),
        ),
    ],
)
