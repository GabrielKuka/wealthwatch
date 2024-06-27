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
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    dbc.ModalTitle(
                                        id="modal-title", children=""
                                    ),
                                    close_button=True,
                                ),
                                dbc.ModalBody(id="modal-message", children=""),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Close",
                                        id="close-btn",
                                        className="ms-auto",
                                        n_clicks=0,
                                    )
                                ),
                            ],
                            id="modal",
                            centered=True,
                            is_open=False,
                        ),
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
                            dcc.Graph(id="purchases_by_currency_pie_chart"),
                        ],
                        style={"display": "flex", "flexDirection": "column"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        [
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
