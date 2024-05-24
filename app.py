import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dash_table, html, no_update
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine, text
import plotly.express as px
import os

from components import layout

# Warehouse connection
username = os.getenv("WEALTHWATCH_PG_USERNAME")
password = os.getenv("WEALTHWATCH_PG_PASSWORD")
dbname = os.getenv("WEALTHWATCH_PG_DBNAME")
port = 8995

host = "100.73.35.59"

pg_connection_string = (
    f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = layout.layout


@app.callback(
    [Output("users_dropdown", "options"), Output("users_dropdown", "value")],
    [Input("users_dropdown", "options")],
)
def populate_users_dropdown(arg):
    if not engine:
        raise PreventUpdate

    with engine.begin() as conn:
        cursor = conn.execute(text("SELECT email from dim_user;"))

        users = [item[0] for item in cursor.fetchall()]

        return users, users[users.index("gabrie.kuka@gmail.com")]


@app.callback(
    Output("purchases_by_currency_pie_chart", "figure"),
    [
        Input("users_dropdown", "value"),
        Input("purchases_by_currency_date_range", "start_date"),
        Input("purchases_by_currency_date_range", "end_date"),
    ],
)
def currency_pie_chart(selected_user, start_date, end_date):
    if not engine:
        return PreventUpdate

    with engine.begin() as conn:
        query = text(
            """ 
                WITH filtered_purchases AS (
                    SELECT
                        a.currency,
                        COUNT(*) AS total_purchase_count
                    FROM fact_transactions f
                    INNER JOIN dim_user u ON f.user_id = u.id
                    INNER JOIN dim_account a ON a.id = f.from_account_id
                    WHERE f.to_account_id IS NULL AND u.email = :selected_user
                    AND f.date >= :start_date AND f.date <= :end_date
                    GROUP BY a.currency
                )
                SELECT
                currency,
                total_purchase_count,
                total_purchase_count * 1.0 / SUM(total_purchase_count) OVER () AS purchase_percentage
                FROM filtered_purchases;
            """
        )
        df = pd.read_sql_query(
            query,
            conn,
            params={
                "selected_user": selected_user,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        fig = px.pie(
            df,
            names="currency",
            values="purchase_percentage",
            title="Which currency is used for most purchases? (YoY)",
        )

        return fig


@app.callback(
    Output("expenses_bar_chart", "figure"),
    [
        Input("users_dropdown", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def expenses_by_category_chart(selected_user, start_date, end_date):
    if not (selected_user and start_date and end_date):
        return PreventUpdate

    query = text(
        """ 
            SELECT c.category, SUM(t.amount) as Sum FROM fact_transactions AS t
            INNER JOIN dim_user as u ON u.id = t.user_id
            INNER JOIN dim_account as a ON a.id = t.from_account_id
            INNER JOIN dim_category as c ON c.id = t.category_id
            WHERE u.email = :selected_user AND t.to_account_id IS NULL
            AND t.date >= :start_date AND t.date <= :end_date
            AND a.currency = 'BGN' GROUP BY c.category;

        """
    )

    with engine.begin() as conn:
        df = pd.read_sql_query(
            query,
            conn,
            params={
                "selected_user": selected_user,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["category"], y=df["sum"]))
        fig.update_layout(title="Expenses by category")

        return fig


@app.callback(
    [Output("recent_expenses", "data"), Output("recent_expenses", "columns")],
    [
        Input("recent_expenses", "data"),
        Input("users_dropdown", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def recent_transactions(arg, selected_user, start_date, end_date):
    if not engine:
        raise PreventUpdate

    query = text(
        """ 
            SELECT u.name, t.description, t.amount, a.currency, c.category, t.date FROM fact_transactions AS t 
            INNER JOIN dim_user AS u ON u.id = t.user_id 
            INNER JOIN dim_account AS a ON a.id = t.from_account_id
            INNER JOIN dim_category AS c ON c.id = t.category_id
            WHERE u.email = :selected_user AND t.to_account_id IS NULL 
            AND t.date >= :start_date AND t.date <= :end_date
            ORDER BY t.date DESC;

    """
    )

    with engine.begin() as conn:
        df = pd.read_sql_query(
            query,
            conn,
            params={
                "selected_user": selected_user,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        return df.to_dict("records"), [
            {"name": i, "id": i} for i in df.columns
        ]


if __name__ == "__main__":

    engine = create_engine(pg_connection_string)

    app.run(debug=True, host="0.0.0.0", port=8992)
