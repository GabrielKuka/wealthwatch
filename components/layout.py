import dash_bootstrap_components as dbc

from components import dashboard, navbar

layout = [
    dbc.Container(
        id="wrapper", fluid=True, children=[navbar.navbar, dashboard.layout]
    )
]
