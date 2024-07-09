import dash_bootstrap_components as dbc
from dash import dcc

from components import dashboard, navbar

layout = [
    dcc.Location(id="url", refresh=False),
    dbc.Container(
        id="wrapper", fluid=True, children=[navbar.navbar, dashboard.layout]
    ),
]
