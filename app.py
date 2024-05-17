from dash import Dash
from components import layout

app = Dash()

app.layout = layout.layout

if __name__ == "__main__":
    app.run(debug=True)