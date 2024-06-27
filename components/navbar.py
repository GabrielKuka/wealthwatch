import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime, date

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
        dbc.NavItem(
            dcc.DatePickerRange(
                id="date_range",
                display_format="DD/MM/YYYY",
                start_date=date(
                    datetime.now().year,
                    datetime.now().month,
                    1,
                ),
                end_date=date.today(),
            ),
        ),
    ],
)
