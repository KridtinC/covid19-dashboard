# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import date, timedelta
import datetime as dt
import requests as rq
from datetime import date, timedelta
from io import StringIO
import math
import numpy as np
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

def load_data():
    global location, df, country_options, today_stats, scale
    location = pd.read_csv('covid19_location.csv')
    df = pd.read_csv('covid19_data.csv')
    df = df.set_index(df.date)
    country_options = df['Country_Region'].unique()
    today_stats = df[df['date'] == (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')]
    scale = 5000
    print("Updated")

def to_dt(date_str):
    return dt.datetime.strptime(date_str, '%Y-%m-%d')

def update_data():
    df_from_each_file = list()
    date_i = dt.date(2020, 1, 22)
    while date_i != date.today():
        res = rq.get('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + date_i.strftime('%m-%d-%Y') + '.csv')
        res_str = res.content.decode('utf-8')
        res_str = res_str.replace('Province/State', 'Province_State').replace('Country/Region', 'Country_Region').replace('Last Update', 'Last_Update').replace('Latitude', 'Lat').replace('Longitude', 'Long_')
        res_str_IO = StringIO(res_str)
        df = pd.read_csv(res_str_IO, delimiter=',', quotechar='"')
        df['date'] = date_i
        df_from_each_file.append(df)
        date_i = date_i + timedelta(days=1)

    concatenated_df   = pd.concat(df_from_each_file, ignore_index=True)
    # concatenated_df['date'] = concatenated_df.apply(lambda x: to_dt(x['date']), axis = 1)
    concatenated_df = concatenated_df.set_index(concatenated_df.date)
    concatenated_df.to_csv('covid19_data.csv', index=False)

    load_data()


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", hours=1)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

#################Data

load_data()

#################Dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'red': '#db1600',
    'green': '#33eb00',
    'white': '#ffffff',
    'black': '#333333'
}

border_style = {'backgroundColor': colors['black'],
    'padding': '10px',
    'margin': '10px', 
    'display': 'inline-block',
    'border-style': 'ridge',
    'border-color': '#666666'
}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height': '100vh'}, children=[
    html.Div(style={'backgroundColor': colors['background'], 'justify-content': 'center', 'display': 'flex'}, children=[
        html.Div(style={'backgroundColor': colors['background'], 'margin': '20px', 'display': 'inline-block'}, children=[
            html.H1(
                children='COVID19 Dashboard',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'padding': '5px',
                    'font-weight': 'bold'
                }
            ),

            html.Div(children='For educational purpose only, see source code at https://github.com/KridtinC/covid19-dashboard', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

            html.Div(style={'backgroundColor': colors['background'], 'justify-content': 'center', 'display': 'flex'}, children=[
                html.Div(style={'backgroundColor': colors['background'], 'width': '50%', 'margin': '20px'}, children=[
                    html.H6(
                            children='Select country',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),

                    dcc.Dropdown(
                            id="country",
                            options=[{
                                'label': i,
                                'value': i
                            } for i in country_options],
                            value='All countries')
                ])
            ]),

            

            html.Div(style={'backgroundColor': colors['background'], 'margin': '10px', 'justify-content': 'center', 'display': 'flex'}, children=[
                html.Div(style=border_style, children=[
                    html.H4(
                        children='TOTAL CONFIRMED',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),

                    html.H1(
                        id='total_confirmed',
                        style={
                            'textAlign': 'center',
                            'color': colors['red'],
                            'font-weight': 'bold'
                        }
                    )
                ]),
                

                html.Div(style=border_style, children=[
                    html.H4(
                        children='TOTAL DEATHS',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),

                    html.H1(
                        id='total_deaths',
                        style={
                            'textAlign': 'center',
                            'color': colors['white'],
                            'font-weight': 'bold'
                        }
                    )
                ]),
                
                html.Div(style=border_style, children=[
                    html.H4(
                        children='TOTAL RECOVERED',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),

                    html.H1(
                        id='total_recovered',
                        style={
                            'textAlign': 'center',
                            'color': colors['green'],
                            'font-weight': 'bold'
                        }
                    )
                ]),
                
            ])
        ]),

        html.Div(style={'backgroundColor': colors['background'], 'margin': '20px', 'display': 'inline-block'}, children=[
            dcc.Graph(
                id='total-confirmed-map'
            )
        ])
    ]),

    html.Div(style={'backgroundColor': colors['background'], 'justify-content': 'center', 'display': 'flex'}, children=[
        
        html.Div(style=border_style, children=[
            dcc.Graph(
                id='total-confirmed-graph'
            )
        ]),

        html.Div(style=border_style, children=[
            dcc.Graph(
                id='total-confirmed-daily'
            )
        ])
    ])

    
])

@app.callback(
    [dash.dependencies.Output('total-confirmed-map', 'figure'),
    dash.dependencies.Output('total-confirmed-graph', 'figure'),
    dash.dependencies.Output('total-confirmed-daily', 'figure'),
    dash.dependencies.Output('total_confirmed', 'children'),
    dash.dependencies.Output('total_deaths', 'children'),
    dash.dependencies.Output('total_recovered', 'children')],
    [dash.dependencies.Input('country', 'value')])
def update_graph(country):
    if country == "All countries" or country == None:
        df_plot = df[['Confirmed', 'Deaths', 'Recovered']].groupby('date').sum()
        loc_lat = 25
        loc_lng = 0
        zoom = 0
    else:
        df_plot = df[df['Country_Region'] == country][['Confirmed', 'Deaths', 'Recovered']].groupby('date').sum()
        loc_lat = location[location['Country_Region'] == country].drop_duplicates().reset_index()['Lat'][0]
        loc_lng = location[location['Country_Region'] == country].drop_duplicates().reset_index()['Long_'][0]
        zoom = 4

    total_confirmed = df_plot.tail(1)['Confirmed']
    total_deaths = df_plot.tail(1)['Deaths']
    total_recovered = df_plot.tail(1)['Recovered']

    trace1 = go.Scatter(x=df_plot.index, y=df_plot['Confirmed'], name='Confirmed')
    trace2 = go.Scatter(x=df_plot.index, y=df_plot['Deaths'], name='Deaths')
    trace3 = go.Scatter(x=df_plot.index, y=df_plot['Recovered'], name='Recovered')

    daily = go.Bar(x=df_plot.index, y=df_plot['Confirmed'] - df_plot['Confirmed'].shift(1).fillna(value=0))

    fig_map = go.Figure(data=go.Scattermapbox(
        lon = today_stats['Long_'],
        lat = today_stats['Lat'],
        text = today_stats['Country_Region'],
        mode = 'markers',
        marker = go.scattermapbox.Marker(
            color = colors['red'],
            size = today_stats['Confirmed']/scale
            )
        ),
        layout = go.Layout(
            paper_bgcolor= colors['background'],
            plot_bgcolor= colors['background'],
            font= {
                    'color': colors['text']
                },
            mapbox_style="carto-darkmatter",
            mapbox=dict(
                bearing=0,
                center=dict(
                    lat=loc_lat,
                    lon=loc_lng
                ),
                pitch=0,
                zoom=zoom
            ),
            margin=dict(t=0, b=0, l=0, r=0)
        )
    )

    fig_graph = {
        'data': [trace1, trace2, trace3],
        'layout': {
                'title': "Total number of infected",
                'paper_bgcolor': colors['black'],
                'plot_bgcolor': colors['black'],
                'font': {
                    'color': colors['text']
                }}
    }
    fig_daily = {
        'data': [daily],
        'layout': {
                'title': "Number of infected daily",
                'paper_bgcolor': colors['black'],
                'plot_bgcolor': colors['black'],
                'font': {
                    'color': colors['text']
                }}
    }

    return fig_map, fig_graph, fig_daily, '{:,}'.format(int(total_confirmed)), '{:,}'.format(int(total_deaths)), '{:,}'.format(int(total_recovered))

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=80)