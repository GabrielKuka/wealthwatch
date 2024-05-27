import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Nav(
    id="navbar",
    children=[
        dbc.NavItem(html.H2("WealthWatch")),
        dbc.NavItem(
            dbc.Select(id="users_dropdown", placeholder="Select user"),
        ),
        dbc.NavItem(
            dbc.Select(
                id="currency_dropdown",
                style={"flexBasis": "20%"},
                value="EUR",
                options=["EUR", "BGN", "USD", "ALL"],
            ),
        ),
    ],
)
