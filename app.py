import os
from datetime import datetime, date

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine, text

import helper
from APIs.currency_api import CurrencyAPI
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

# currency_api = None
currency_api = CurrencyAPI(os.getenv("CURRENCY_API"))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = layout.layout


def invalid_date_range(start_date: str, end_date: str) -> bool:

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    return start_date_obj > end_date_obj


def get_empty_figure() -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="No Data Aavailable",
        showarrow=False,
        font=dict(size=20),
        xref="paper",
        yref="paper",
    )
    # Adjust the layout to center the text
    fig.update_layout(
        xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
        template="plotly_white",
    )
    return fig


@app.callback(
    [
        Output("date_range", "start_date"),
        Output("date_range", "end_date"),
    ],
    Input("url", "pathname"),
)
def update_date_range(pathname: str):
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today

    return start_date, end_date


@app.callback(
    [Output("users_dropdown", "options"), Output("users_dropdown", "value")],
    [Input("users_dropdown", "options")],
)
def populate_users_dropdown(arg):

    engine = create_engine(pg_connection_string)

    with engine.begin() as conn:
        cursor = conn.execute(text("SELECT email from dim_user;"))

        users = [item[0] for item in cursor.fetchall()]

        return users, users[users.index("gabrie.kuka@gmail.com")]


@app.callback(
    Output("purchases_by_currency_pie_chart", "figure"),
    [
        Input("users_dropdown", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def currency_pie_chart(selected_user, start_date, end_date):

    engine = create_engine(pg_connection_string)

    if invalid_date_range(start_date, end_date):
        raise PreventUpdate

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

        if df.empty:
            return get_empty_figure()

        df["purchase_percentage"] = df["purchase_percentage"].round(2)

        fig = px.pie(
            df,
            names="currency",
            values="purchase_percentage",
            title="Which currency is used for most purchases?",
        )
        fig.update_layout(margin=dict(l=10, r=10, b=25, t=25))

        return fig


@app.callback(
    Output("incomes_and_expenses_sankey", "figure"),
    [
        Input("users_dropdown", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
        Input("currency_dropdown", "value"),
    ],
)
def incomes_and_expenses_sankey(selected_user, start_date, end_date, currency):
    if not (selected_user and start_date and end_date and currency):
        raise PreventUpdate

    if invalid_date_range(start_date, end_date):
        raise PreventUpdate

    engine = create_engine(pg_connection_string)

    incomes_query = text(
        """
            SELECT t.amount, a.currency, c.category FROM fact_transactions AS t 
                INNER JOIN dim_user AS u ON u.id = t.user_id 
                INNER JOIN dim_account AS a ON a.id = t.to_account_id
                INNER JOIN dim_category AS c ON c.id = t.category_id
                WHERE u.email = :selected_user AND t.from_account_id IS NULL 
                    AND t.date >= :start_date AND t.date <= :end_date
                ORDER BY t.created_on DESC;
        """
    )

    expenses_query = text(
        """
        SELECT t.amount, a.currency, c.category FROM fact_transactions AS t 
            INNER JOIN dim_user AS u ON u.id = t.user_id 
            INNER JOIN dim_account AS a ON a.id = t.from_account_id
            INNER JOIN dim_category AS c ON c.id = t.category_id
            WHERE u.email = :selected_user AND t.to_account_id IS NULL 
                AND t.date >= :start_date AND t.date <= :end_date
            ORDER BY t.created_on DESC;
    """
    )

    with engine.begin() as conn:
        incomes_df = pd.read_sql_query(
            incomes_query,
            conn,
            params={
                "selected_user": selected_user,
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        expenses_df = pd.read_sql_query(
            expenses_query,
            conn,
            params={
                "selected_user": selected_user,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

        if expenses_df.empty and incomes_df.empty:
            return get_empty_figure()

        # Convert currencies
        if not incomes_df.empty:
            incomes_df[f"amount_{currency.lower()}"] = incomes_df.apply(
                lambda row: currency_api.convert(
                    row["currency"], currency, row["amount"]
                ),
                axis=1,
            )
            incomes_df = incomes_df.drop(columns=["amount"])
            total_incomes = incomes_df[f"amount_{currency.lower()}"].sum()

            incomes_df["category"] = incomes_df["category"].replace(
                "Other", "Others"
            )

            incomes_by_category_df = (
                incomes_df.groupby("category")[f"amount_{currency.lower()}"]
                .sum()
                .reset_index()
            )

        if not expenses_df.empty:
            expenses_df[f"amount_{currency.lower()}"] = expenses_df.apply(
                lambda row: currency_api.convert(
                    row["currency"], currency, row["amount"]
                ),
                axis=1,
            )
            expenses_df = expenses_df.drop(columns=["amount"])
            total_expenses = expenses_df[f"amount_{currency.lower()}"].sum()

            # Expenses by category
            expenses_by_category_df = (
                expenses_df.groupby("category")[f"amount_{currency.lower()}"]
                .sum()
                .reset_index()
            )

        nodes = (
            list(incomes_by_category_df["category"])
            + ["Total Income", "Savings"]
            + list(expenses_by_category_df["category"])
        )

        links = []

        links.append(
            {
                "source": nodes.index("Total Income"),
                "target": nodes.index("Savings"),
                "value": total_incomes - total_expenses,
            }
        )

        for i, row in incomes_by_category_df.iterrows():
            links.append(
                {
                    "source": nodes.index(row["category"]),
                    "target": nodes.index("Total Income"),
                    "value": row[f"amount_{currency.lower()}"],
                }
            )

        # Add total income to expenses links
        for i, row in expenses_by_category_df.iterrows():
            links.append(
                {
                    "source": nodes.index("Total Income"),
                    "target": nodes.index(row["category"]),
                    "value": row[f"amount_{currency.lower()}"],
                }
            )

        node_colors = [
            (
                "rgba(0, 100, 0, 1)"
                if node == "Total Income"
                else (
                    "rgba(95, 158, 160, 1)"
                    if node == "Savings"
                    else (
                        "rgba(144, 238, 144, 1)"
                        if nodes.index(node) < nodes.index("Total Income")
                        else "rgba(255, 0, 0, 1)"
                    )
                )
            )
            for node in nodes
        ]

        link_colors = []
        for link in links:
            if link["target"] == nodes.index("Total Income"):
                # Links from income nodes to "Total Income" should be light green with transparency
                link_colors.append("rgba(144, 238, 144, 0.4)")
            elif link["source"] == nodes.index("Total Income"):
                # Links from "Total Income" to expense nodes should match expense node colors with transparency
                expense_node_color = node_colors[link["target"]]
                expense_color_with_transparency = expense_node_color.replace(
                    "1)", "0.4)"
                )
                link_colors.append(expense_color_with_transparency)
            else:
                # Link from "Total Income" to "Savings"
                link_colors.append("rgba(0, 100, 0, 0.4)")

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=12,
                        thickness=7,
                        label=nodes,
                        color=node_colors,
                    ),
                    link=dict(
                        source=[link["source"] for link in links],
                        target=[link["target"] for link in links],
                        value=[link["value"] for link in links],
                        color=link_colors,
                    ),
                )
            ]
        )

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
        )

    return fig


@app.callback(
    Output("expenses_bar_chart", "figure"),
    [
        Input("users_dropdown", "value"),
        Input("currency_dropdown", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def expenses_by_category_chart(selected_user, currency, start_date, end_date):
    if not (selected_user and start_date and end_date and currency):
        raise PreventUpdate

    if invalid_date_range(start_date, end_date):
        raise PreventUpdate

    engine = create_engine(pg_connection_string)

    query = text(
        """ 
            SELECT c.category, SUM(t.amount) as amount, a.currency FROM fact_transactions AS t
            INNER JOIN dim_user as u ON u.id = t.user_id
            INNER JOIN dim_account as a ON a.id = t.from_account_id
            INNER JOIN dim_category as c ON c.id = t.category_id
            WHERE u.email = :selected_user AND t.to_account_id IS NULL
            AND t.date >= :start_date AND t.date <= :end_date
            GROUP BY c.category, a.currency;

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

        if df.empty:
            return get_empty_figure()

        df[f"amount_{currency.lower()}"] = df.apply(
            lambda row: currency_api.convert(
                row["currency"], currency, row["amount"]
            ),
            axis=1,
        )
        df = df.drop(columns=["amount"])
        df = (
            df.groupby("category")[f"amount_{currency.lower()}"]
            .sum()
            .reset_index()
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["category"],
                y=df[f"amount_{currency.lower()}"],
                hovertemplate=f"<span>%{{x}}:</span> <b>%{{y:.2f}} {helper.SYMBOLS[currency]}</b><extra></extra>",
            )
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=35),
            title="Expenses by Category",
            yaxis=dict(tickformat=","),
        )

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

    if invalid_date_range(start_date, end_date):
        raise PreventUpdate

    engine = create_engine(pg_connection_string)

    query = text(
        """ 
            SELECT t.description, t.amount, a.currency, c.category, t.date FROM fact_transactions AS t 
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

        if df.empty:
            empty_row = pd.DataFrame([["No Data"] * 5], columns=df.columns)
            df = pd.concat([df, empty_row], ignore_index=True)

        return df.to_dict("records"), [
            {"name": i, "id": i} for i in df.columns
        ]


@app.callback(
    Output("expenses_aggs", "data"),
    [
        Input("recent_expenses", "derived_virtual_data"),
        Input("currency_dropdown", "value"),
    ],
)
def expenses_aggs(expenses, currency):
    if not (expenses and currency):
        raise PreventUpdate

    expenses_df = pd.DataFrame(expenses)

    expenses_df[f"amount_{currency.lower()}"] = expenses_df.apply(
        lambda x: currency_api.convert(x["currency"], currency, x["amount"]),
        axis=1,
    )

    values = expenses_df[f"amount_{currency.lower()}"]

    result = [
        {
            "measure": "Total",
            "value": f"{round(values.sum(), 2)} {helper.SYMBOLS[currency]}",
        },
        {
            "measure": "Mean",
            "value": f"{round(values.mean(), 2)} {helper.SYMBOLS[currency]}",
        },
        {
            "measure": "25% Quantile",
            "value": f"{round(values.quantile(0.25), 2)} {helper.SYMBOLS[currency]}",
        },
        {
            "measure": "50% Quantile (Median)",
            "value": f"{round(values.quantile(0.50), 2)} {helper.SYMBOLS[currency]}",
        },
        {
            "measure": "75% Quantile",
            "value": f"{round(values.quantile(0.75), 2)} {helper.SYMBOLS[currency]}",
        },
        {
            "measure": "Min, Max",
            "value": f"{round(values.min(), 2)} {helper.SYMBOLS[currency]}, {round(values.max(), 2)} {helper.SYMBOLS[currency]}",
        },
        {"measure": "# of Expenses", "value": values.count()},
    ]

    return result


@app.callback(
    Output("expenses_line_chart", "figure"),
    [
        Input("recent_expenses", "derived_virtual_data"),
        Input("currency_dropdown", "value"),
    ],
    [
        State("date_range", "start_date"),
        State("date_range", "end_date"),
    ],
)
def expenses_line_chart(expenses, currency, start_date, end_date):
    if not (expenses and currency):
        raise PreventUpdate

    expenses_df = pd.DataFrame(expenses)

    expenses_df[f"amount_{currency.lower()}"] = expenses_df.apply(
        lambda x: currency_api.convert(x["currency"], currency, x["amount"]),
        axis=1,
    )
    expenses_df["date"] = pd.to_datetime(expenses_df["date"])
    daily_expenses = (
        expenses_df.groupby(expenses_df["date"].dt.date)[
            f"amount_{currency.lower()}"
        ]
        .sum()
        .reset_index()
    )
    daily_expenses["moving_average"] = (
        daily_expenses[f"amount_{currency.lower()}"].rolling(window=5).mean()
    )

    fig = go.Figure()

    # Sum of daily expenses
    fig.add_trace(
        go.Scatter(
            x=daily_expenses["date"],
            y=daily_expenses[f"amount_{currency.lower()}"],
            mode="lines",
            name="Daily Expenses",
            hovertemplate=f"<span>%{{x}}:</span> <b>%{{y:.2f}} {helper.SYMBOLS[currency]}</b><extra></extra>",
        )
    )

    # 5 day moving average
    fig.add_trace(
        go.Scatter(
            x=daily_expenses["date"],
            y=daily_expenses["moving_average"],
            mode="lines",
            hovertemplate=f"<span>%{{x}}:</span> <b>%{{y:.2f}} {helper.SYMBOLS[currency]}</b><extra></extra>",
        )
    )

    fig.update_layout(
        height=350,
        width=610,
        plot_bgcolor="white",
        showlegend=False,
        xaxis_title="",
        yaxis_title=f"Amount ({helper.SYMBOLS[currency]})",
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(gridcolor="#DADADA"),
        annotations=[
            dict(
                x=daily_expenses["date"].iloc[-1],
                y=daily_expenses["moving_average"].iloc[-1],
                xref="x",
                yref="y",
                text=f"Current Moving Avg: {round(daily_expenses['moving_average'].iloc[-1], 2)} {helper.SYMBOLS[currency]}",
                showarrow=True,
                arrowhead=7,
                ax=-50,
                ay=-60,
            )
        ],
        # xaxis=dict(
        #    rangeselector=dict(
        #        buttons=list([
        #            dict(count=1, label='1m', step='month', stepmode='backward'),
        #            dict(count=6, label='6m', step='month', stepmode='backward'),
        #            dict(count=1, label='YTD', step='year', stepmode='todate'),
        #            dict(count=1, label='1y', step='year', stepmode='backward'),
        #            dict(step='all')
        #        ])
        #    ),
        #    #rangeslider=dict(visible=True),
        #    #type='date'
        # )
    )

    return fig


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=8992)
