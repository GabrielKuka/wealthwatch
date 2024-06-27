import dash_bootstrap_components as dbc
from dash import dcc, html


def create_modal(
    header: str = "This is the header",
    message: str = "This is the message",
    centered: bool = False,
):
    modal = (
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(header), close_button=True),
                dbc.ModalBody(message),
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
            centered=centered,
            is_open=True,
        ),
    )
    return modal
