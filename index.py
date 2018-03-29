from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
server = app.server
from apps import world, country


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
             [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/country':
        return country.layout
    else:
        return world.layout

if __name__ == '__main__':
    app.run_server()