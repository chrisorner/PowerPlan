import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR])

app.layout = html.Div([

    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
