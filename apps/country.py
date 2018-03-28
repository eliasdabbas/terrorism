import datetime
import random
import textwrap
from itertools import product

from app import app

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

mydates = [datetime.date(year, month, 1) for year, month in product(range(1970, 2017), range(1, 13))]

terrorism = pd.read_csv('apps/data/terrorism.csv',
                        encoding='latin-1', low_memory=False,
                        usecols=['eventid', 'iyear', 'imonth', 'iday', 'country_txt', 'city', 'longitude', 'latitude', 
                        'nkill', 'nwound', 'summary', 'target1', 'gname', 'provstate'])

terrorism = terrorism[terrorism['imonth'] != 0]
terrorism['day_clean'] = [15 if x == 0 else x for x in terrorism['iday']]
terrorism['date'] = [pd.datetime(y, m, d) for y, m, d in zip(terrorism['iyear'], terrorism['imonth'], terrorism['day_clean'])]

layout = html.Div([ 
    html.Br(),
    html.H3('Global Terrorism Database: 1970 - 2016'),
    html.A('Explore Countries', href='/'),    
    dcc.Location(id='url_country', refresh=False),
    html.Div([
        dcc.Dropdown(id='country_list', 
                     value='',
                     options=[{'label': c, 'value': c}
                              for c in sorted(terrorism['country_txt'].unique())]),
        
    ], style={'width': '40%', 'margin-left': '30%'}),
    html.H2(id='page_title'), 
    dcc.Graph(id='map_country',
              figure={'data': [go.Scattergeo(lon=[], lat=[])]},
              config={'displayModeBar': False}),
    html.Div([
        dcc.RangeSlider(id='date_range', 
                        min=0,
                        max=563,
                        value=[480, 563]),
        html.Div(id='actual_date', style={'text-align': 'center'}),
        html.Br(),
    html.Div([
        html.Div([
            dcc.Dropdown(id='provstate',
                         multi=True,
                         value=[''],
                         placeholder='States / Provinces / Districts'),
        ], style={'width': '40%', 'display': 'inline-block', }),
        html.Div([
            dcc.Dropdown(id='cities',
                         multi=True,
                         value=[''],
                         placeholder='Cities'),
        ], style={'width': '40%', 'display': 'inline-block', })
    ], style={'width': '80%', 'margin-left': '20%'}),
        html.Br(),

    ], style={'background-color': '#eeeeee', 'margin-left': '7%', 'margin-right': '7%'}),
    html.Br(),  
    
    dcc.Graph(id='city_barchart',
              config={'displayModeBar': False}),
    
    dcc.Graph(id='perp_graph',
              config={'displayModeBar': False}),
    html.Div([
        dcc.RangeSlider(id='date_range_perp', 
                        min=0,
                        max=563,
                        value=[480, 563]),
        html.Div(id='actual_date_perp', style={'text-align': 'center'}),
        html.Br(),
        html.Div([
            dcc.Dropdown(id='perpetrators',
                         value=[''],
                         multi=True),
            html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

        ], style={'width': '50%', 'margin-left': '25%'}),
    ], style={'background-color': '#eeeeee', 'margin-left': '7%', 'margin-right': '7%'}),
], style={'background-color': '#eeeeee', 'font-family': 'Palatino'})

@app.callback(Output('page_title', 'children'),
             [Input('country_list', 'value')])
def set_page_title(country):
    if not country:
        return 'Please select the country above, then cities and date range below...'
    else:
        return 'Terrorist Attacks in the Provinces / States / Cities of ' + country

@app.callback(Output('provstate', 'options'),
             [Input('country_list', 'value')])
def set_provstate_options(country):
    return [{'label': prov, 'value': prov}
            for prov in sorted(terrorism[(terrorism['country_txt']==country) & terrorism['provstate'].notna()]['provstate'].unique())]

@app.callback(Output('cities', 'options'),
             [Input('country_list', 'value')])
def set_city_options(country):
    return [{'label': prov, 'value': prov}
            for prov in sorted(terrorism[(terrorism['country_txt']==country) & terrorism['city'].notna()]['city'].unique())]

@app.callback(Output('perpetrators', 'options'),
             [Input('country_list', 'value')])
def set_perpetrator_options(country):
    return [{'value': perp, 'label': perp}
            for perp in sorted(terrorism[terrorism['country_txt']==country]['gname'].unique())]


@app.callback(Output('map_country', 'figure'),
             [Input('provstate', 'value'), 
              Input('cities', 'value'), 
              Input('date_range', 'value'),
              Input('country_list', 'value')])
def plot_cities_map(provstates, cities, date_range, country):
    country = '' or country
    df = terrorism[(terrorism['provstate'].isin(provstates) | terrorism['city'].isin(cities)) & 
                    (terrorism['country_txt'] == country) &
                    terrorism['date'].between(mydates[date_range[0]], mydates[date_range[1]])]

    return {'data': [go.Scattergeo(lon=[x + random.gauss(0.04, 0.03) for x in df[df['provstate'] == c]['longitude']],
                                   lat=[x + random.gauss(0.04, 0.03) for x in df[df['provstate'] == c]['latitude']],
                                   name=c,
                                   hoverinfo='text',
                                   opacity=0.9,
                                   marker={'size': 9, 'line': {'width': .2, 'color': '#cccccc'}},
                                   hovertext=df[df['provstate'] == c]['city'].astype(str) + ', ' + df[df['provstate'] == c]['country_txt'].astype(str)+ '<br>' +
                                             [datetime.datetime.strftime(d, '%d %b, %Y') for d in df[df['provstate'] == c]['date']] + '<br>' +
                                             'Perpetrator: ' + df[df['provstate'] == c]['gname'].astype(str) + '<br>' +
                                             'Target: ' + df[df['provstate'] == c]['target1'].astype(str) + '<br>' + 
                                             'Deaths: ' + df[df['provstate'] == c]['nkill'].astype(str) + '<br>' +
                                             'Injured: ' + df[df['provstate'] == c]['nwound'].astype(str) + '<br><br>' + 
                                             ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else '' for x in df[df['provstate'] == c]['summary']])
                         for c in provstates] +
            
                    [go.Scattergeo(lon=[x + random.gauss(0.04, 0.03) for x in df[df['city'] == c]['longitude']],
                                   lat=[x + random.gauss(0.04, 0.03) for x in df[df['city'] == c]['latitude']],
                                   name=c,
                                   hoverinfo='text',
                                   opacity=0.9,
                                   marker={'size': 9, 'line': {'width': .2, 'color': '#cccccc'}},
                                   hovertext=df[df['city'] == c]['city'].astype(str) + ', ' + df[df['city'] == c]['country_txt'].astype(str)+ '<br>' +
                                             [datetime.datetime.strftime(d, '%d %b, %Y') for d in df[df['city'] == c]['date']] + '<br>' +
                                             'Perpetrator: ' + df[df['city'] == c]['gname'].astype(str) + '<br>' +
                                             'Target: ' + df[df['city'] == c]['target1'].astype(str) + '<br>' + 
                                             'Deaths: ' + df[df['city'] == c]['nkill'].astype(str) + '<br>' +
                                             'Injured: ' + df[df['city'] == c]['nwound'].astype(str) + '<br><br>' + 
                                             ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else '' for x in df[df['city'] == c]['summary']])
                         for c in cities],
            'layout': go.Layout(title='Terrorist Attacks in ' + country + '  ' +
                                    datetime.datetime.strftime(mydates[date_range[0]], '%b, %Y') + ' - ' + 
                                    datetime.datetime.strftime(mydates[date_range[1]], '%b, %Y') + '<br>' + 
                                    ', '.join(list(provstates)) + ' ' + ', '.join(list(cities)),
                                font={'family': 'Palatino'},
                                titlefont={'size': 22},
                                paper_bgcolor='#eeeeee',
                                plot_bgcolor='#eeeeee',
                                width=1420,
                                height=650,
                                annotations=[{'text': '<a href="https://www.twitter.com">@eliasdabbas</a>', 'x': .2, 'y': -.1, 
                                              'showarrow': False},
                                             {'text': 'Data: START Consortium', 'x': .2, 'y': -.13, 'showarrow': False}],                            
                      geo={'showland': True, 'landcolor': '#eeeeee',
                           'countrycolor': '#cccccc',
                           'showsubunits': True,
                           'subunitcolor': '#cccccc',
                           'subunitwidth': 5,
                           'showcountries': True,
                           'oceancolor': '#eeeeee',
                           'showocean': True,
                           'showcoastlines': True, 
                           'showframe': False,
                           'coastlinecolor': '#cccccc',
                           'lonaxis': {'range': [df['longitude'].min()-1, df['longitude'].max()+1]},
                           'lataxis': {'range': [df['latitude'].min()-1, df['latitude'].max()+1]}
                                        })
}

@app.callback(Output('actual_date', 'children'),
             [Input('date_range', 'value')])
def show_date(daterange):
    return datetime.datetime.strftime(mydates[daterange[0]], '%b, %Y'), ' - ', datetime.datetime.strftime(mydates[daterange[1]], '%b, %Y')

@app.callback(Output('city_barchart', 'figure'),
             [Input('provstate', 'value'), 
              Input('cities', 'value'), 
              Input('date_range', 'value'),
              Input('country_list', 'value')])
def plot_cities_barchart(provstates, cities, date_range, country):
    df_init = terrorism[(terrorism['provstate'].isin(provstates) | terrorism['city'].isin(cities)) & 
                        (terrorism['country_txt'] == country) &
                        terrorism['date'].between(mydates[date_range[0]], mydates[date_range[1]])]
    df = df_init.groupby(['iyear','provstate', 'city'], as_index=False).count()[['iyear','provstate', 'city', 'eventid']]
    df_provstate = df_init.groupby(['iyear','provstate'], as_index=False).count()[['iyear','provstate', 'eventid']]
    df_city = df_init.groupby(['iyear', 'city'], as_index=False).count()[['iyear', 'city', 'eventid']]

    return {'data': [go.Bar(x=df_provstate[df_provstate['provstate'] == prov]['iyear'],
                            y=df_provstate[df_provstate['provstate'] == prov]['eventid'],
                            name=prov)
                     for prov in provstates] + 
            
                    [go.Bar(x=df_city[df_city['city'] == city]['iyear'],
                            y=df_city[df_city['city'] == city]['eventid'],
                            name=city)
                     for city in cities],
            'layout': go.Layout(title='Terrorist Attacks in '  + country + '   ' + 
                                    datetime.datetime.strftime(mydates[date_range[0]], '%b, %Y') + ' - ' + 
                                    datetime.datetime.strftime(mydates[date_range[1]], '%b, %Y') + '<br>' +
                                    ', '.join(list(provstates) + list(cities)), 
                                plot_bgcolor='#eeeeee',
                                paper_bgcolor='#eeeeee',
                                font={'family': 'Palatino'})
}

@app.callback(Output('perp_graph', 'figure'),
             [Input('perpetrators', 'value'), 
              Input('date_range_perp', 'value'),
              Input('country_list', 'value')])
def plot_perps_map(perps, date_range, country):
    country = '' or country
    df = terrorism[terrorism['gname'].isin(perps) & 
                  (terrorism['country_txt'] == country)  & 
                   terrorism['date'].between(mydates[date_range[0]], mydates[date_range[1]])]

    return {'data': [go.Scattergeo(lon=df[df['gname'] == perp]['longitude'],
                                   lat=df[df['gname'] == perp]['latitude'],
                                   name=perp,
                                   hoverinfo='text',
                                   showlegend=True,
                                   marker={'size': 9, 'line': {'width': .2, 'color': '#cccccc'}},
                                   hovertext=df[df['gname'] == perp]['city'].astype(str) + ', ' + df[df['gname'] == perp]['country_txt'].astype(str)+ '<br>' +
                                             [datetime.datetime.strftime(d, '%d %b, %Y') for d in df[df['gname'] == perp]['date']] + '<br>' +
                                             'Perpetrator: ' + df[df['gname'] == perp]['gname'].astype(str) + '<br>' +
                                             'Target: ' + df[df['gname'] == perp]['target1'].astype(str) + '<br>' + 
                                             'Deaths: ' + df[df['gname'] == perp]['nkill'].astype(str) + '<br>' +
                                             'Injured: ' + df[df['gname'] == perp]['nwound'].astype(str) + '<br><br>' + 
                                             ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else '' for x in df[df['gname'] == perp]['summary']])
                     for perp in perps],
            'layout': go.Layout(title='Terrorist Attacks in ' + country + '  ' +
                                datetime.datetime.strftime(mydates[date_range[0]], '%b, %Y') + ' - ' + 
                                datetime.datetime.strftime(mydates[date_range[1]], '%b, %Y') + '<br>' + 
                                '<br>'.join(textwrap.wrap(', '.join(perps), 110)),
                      font={'family': 'Palatino'},
                      titlefont={'size': 22},
                      paper_bgcolor='#eeeeee',
                      plot_bgcolor='#eeeeee',
                      width=1420,
                      height=650,
                      annotations=[{'text': '<a href="https://www.twitter.com">@eliasdabbas</a>', 'x': .2, 'y': -.1, 
                                    'showarrow': False},
                                   {'text': 'Data: START Consortium', 'x': .2, 'y': -.13, 'showarrow': False}],                            
                      geo={'showland': True, 'landcolor': '#eeeeee',
                           'countrycolor': '#cccccc',
                           'showsubunits': True,
                           'subunitcolor': '#cccccc',
                           'subunitwidth': 5,
                           'showcountries': True,
                           'oceancolor': '#eeeeee',
                           'showocean': True,
                           'showcoastlines': True, 
                           'showframe': False,
                           'coastlinecolor': '#cccccc',
                           'lonaxis': {'range': [df['longitude'].min()-1, df['longitude'].max()+1]},
                           'lataxis': {'range': [df['latitude'].min()-1, df['latitude'].max()+1]}
                                        })
}

@app.callback(Output('actual_date_perp', 'children'),
             [Input('date_range_perp', 'value')])
def show_date_perp(daterange):
    return datetime.datetime.strftime(mydates[daterange[0]], '%b, %Y'), ' - ', datetime.datetime.strftime(mydates[daterange[1]], '%b, %Y')