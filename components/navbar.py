import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Nav(
    id="navbar",
    children=[
        dbc.NavItem(html.H2("WealthWatch")),
        dbc.NavItem(
            dbc.Select(id="users_dropdown", placeholder="Select user"),
        ),
    ],
)
