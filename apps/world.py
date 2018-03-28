import random
import textwrap
import datetime as dt 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from app import app
terrorism = pd.read_csv('apps/data/terrorism.csv', 
                        encoding='latin-1', low_memory=False, 
                        usecols=['iyear', 'imonth', 'iday', 'country_txt', 'city', 'longitude', 'latitude', 
                        'nkill', 'nwound', 'summary', 'target1', 'gname'])

terrorism = terrorism[terrorism['imonth'] != 0]
terrorism['day_clean'] = [15 if x == 0 else x for x in terrorism['iday']]
terrorism['date'] = [pd.datetime(y, m, d) for y, m, d in zip(terrorism['iyear'], terrorism['imonth'], terrorism['day_clean'])]


from app import app

layout = html.Div([
    html.Br(),
    html.H3('Global Terrorism Database: 1970 - 2016'),
    html.A('Explore Cities', href='/country'),
    dcc.Graph(id='map_world',
              config={'displayModeBar': False}),
    html.Div([
        dcc.RangeSlider(id='years',
                        min=1970,
                        max=2016,
                        dots=True,
                        value=[2010, 2016],
                        marks={str(yr): "'" + str(yr)[2:] for yr in range(1970, 2017)}),
         
        html.Br(), html.Br(), 
    ], style={'width': '75%', 'margin-left': '12%', 'background-color': '#eeeeee'}),
    html.Div([
        dcc.Dropdown(id='countries',
                     multi=True,
                     value=[''],
                     placeholder='Select Countries',
                     options=[{'label': c, 'value': c}
                              for c in sorted(terrorism['country_txt'].unique())])        
    ], style={'width': '50%', 'margin-left': '25%', 'background-color': '#eeeeee'}),
    
    dcc.Graph(id='by_year_country_world',
              config={'displayModeBar': False}),
    html.Hr(), 
    html.Content('Top Countries', style={'margin-left': '45%', 'font-size': 25}),
    html.Br(), html.Br(),
    html.Div([
        html.Div([
            html.Div([
                dcc.RangeSlider(id='years_attacks',
                                min=1970,
                                max=2016,
                                dots=True,
                                value=[2010, 2016],
                                marks={str(yr): str(yr) for yr in range(1970, 2017, 5)}),
                html.Br(),
                
            ], style={'margin-left': '5%', 'margin-right': '5%'}),
            dcc.Graph(id='top_countries_attacks',
                      figure={'layout': {'margin': {'r': 10, 't': 50}}},
                      config={'displayModeBar': False})
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.Div([
                dcc.RangeSlider(id='years_deaths',
                                min=1970,
                                max=2016,
                                dots=True,
                                value=[2010, 2016],
                                marks={str(yr): str(yr) for yr in range(1970, 2017, 5)}),
                html.Br(),
                
            ], style={'margin-left': '5%', 'margin-right': '5%'}),

            dcc.Graph(id='top_countries_deaths',
                      config={'displayModeBar': False},
                      figure={'layout': {'margin': {'l': 10, 't': 50}}})

        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    html.A('@eliasdabbas', href='https://www.twitter.com/eliasdabbas'), 
    html.P(),
    html.Content('  Code: '),
    html.A('github.com/eliasdabbas/terrorism', href='https://github.com/eliasdabbas/terrorism'), html.Br(), html.Br(),
    html.Content('Data: National Consortium for the Study of Terrorism and Responses to Terrorism (START). (2016). '
                 'Global Terrorism Database [Data file]. Retrieved from https://www.start.umd.edu/gtd')
    
], style={'background-color': '#eeeeee', 'font-family': 'Palatino'})

@app.callback(Output('by_year_country_world', 'figure'),
             [Input('countries', 'value'), Input('years', 'value')])
def annual_by_country_barchart(countries, years):
    df = terrorism[terrorism['country_txt'].isin(countries) & terrorism['iyear'].between(years[0], years[1])]
    df = df.groupby(['iyear', 'country_txt'], as_index=False)['date'].count()
    
    return {
        'data': [go.Bar(x=df[df['country_txt'] == c]['iyear'],
                        y=df[df['country_txt'] == c]['date'], 
                        name=c)
                 for c in countries] ,
        'layout': go.Layout(title='Yearly Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#eeeeee',
                            paper_bgcolor='#eeeeee',
                            font={'family': 'Palatino'})
    }

@app.callback(Output('map_world', 'figure'),
             [Input('countries', 'value'), Input('years', 'value')])
def countries_on_map(countries, years):
    df = terrorism[terrorism['country_txt'].isin(countries) & terrorism['iyear'].between(years[0], years[1])]
    
    return {
        'data': [go.Scattergeo(lon=[x + random.gauss(0.04, 0.03) for x in df[df['country_txt'] == c]['longitude']],
                               lat=[x + random.gauss(0.04, 0.03) for x in df[df['country_txt'] == c]['latitude']],
                               name=c,
                               hoverinfo='text',
                               marker={'size': 9, 'opacity': 0.65, 'line': {'width': .2, 'color': '#cccccc'}},
                               hovertext=df[df['country_txt'] == c]['city'].astype(str) + ', ' + df[df['country_txt'] == c]['country_txt'].astype(str)+ '<br>' +
                                         [dt.datetime.strftime(d, '%d %b, %Y') for d in df[df['country_txt'] == c]['date']] + '<br>' +
                                         'Perpetrator: ' + df[df['country_txt'] == c]['gname'].astype(str) + '<br>' +
                                         'Target: ' + df[df['country_txt'] == c]['target1'].astype(str) + '<br>' + 
                                         'Deaths: ' + df[df['country_txt'] == c]['nkill'].astype(str) + '<br>' +
                                         'Injured: ' + df[df['country_txt'] == c]['nwound'].astype(str) + '<br><br>' + 
                                         ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else '' for x in df[df['country_txt'] == c]['summary']])
                 for c in countries],
        'layout': go.Layout(title='Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
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

@app.callback(Output('top_countries_attacks', 'figure'),
             [Input('years_attacks', 'value')])
def top_countries_count(years):
    df_top_countries = terrorism[terrorism['iyear'].between(years[0], years[1])]
    df_top_countries = df_top_countries.groupby(['country_txt'], as_index=False)['nkill'].agg(['count', 'sum'])
    df = df_top_countries.sort_values(['count']).tail(20)
    return {
        'data': [go.Bar(x=df['count'],
                        y=df.index,
                        orientation='h',
                        constraintext='none',
                        text=df_top_countries.sort_values(['count']).tail(20).index,
                        textposition='outside')],
        'layout': go.Layout(title='Number of Terrorist Attacks ' + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#eeeeee',
                            paper_bgcolor='#eeeeee',
                            font={'family': 'Palatino'},
                            height=700,
                            yaxis={'visible': False})
    }
    
@app.callback(Output('top_countries_deaths', 'figure'),
             [Input('years_deaths', 'value')])
def top_countries_deaths(years):
    df_top_countries = terrorism[terrorism['iyear'].between(years[0], years[1])]
    df_top_countries = df_top_countries.groupby(['country_txt'], as_index=False)['nkill'].agg(['count', 'sum'])
    
    return {
        'data': [go.Bar(x=df_top_countries.sort_values(['sum']).tail(20)['sum'],
                        y=df_top_countries.sort_values(['sum']).tail(20).index,
                        orientation='h',
                        constraintext='none',
                        showlegend=False, 
                        text=df_top_countries.sort_values(['sum']).tail(20).index,
                        textposition='outside')],
        'layout': go.Layout(title='Total Deaths from Terrorist Attacks ' + '  ' + ' - '.join([str(y) for y in years]),
                            plot_bgcolor='#eeeeee',
                            font={'family': 'Palatino'},
                            paper_bgcolor='#eeeeee',
                            height=700,
                            yaxis={'visible': False})
    }