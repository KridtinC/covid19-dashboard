# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import date, timedelta
import datetime as dt

#################Data

location = pd.read_csv('covid19_location.csv')
df = pd.read_csv('covid19_data.csv')
df = df.set_index(df.date)
country_options = df['Country_Region'].unique()
today_stats = df[df['date'] == (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')]
scale = 5000

#################Dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#333333',
    'text': '#7FDBFF',
    'red': '#db1600',
    'green': '#33eb00',
    'white': '#ffffff'
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

            html.Div(children='For educational purpose only', style={
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
                html.Div(style={'backgroundColor': colors['background'], 'margin': '20px', 'display': 'inline-block'}, children=[
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
                

                html.Div(style={'backgroundColor': colors['background'], 'margin': '20px', 'display': 'inline-block'}, children=[
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
                
                html.Div(style={'backgroundColor': colors['background'], 'margin': '20px', 'display': 'inline-block'}, children=[
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
        
        html.Div(style={'backgroundColor': colors['background'], 'margin': '10px', 'display': 'inline-block'}, children=[
            dcc.Graph(
                id='total-confirmed-graph'
            )
        ]),

        html.Div(style={'backgroundColor': colors['background'], 'margin': '10px', 'display': 'inline-block'}, children=[
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
                'paper_bgcolor': colors['background'],
                'plot_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }}
    }
    fig_daily = {
        'data': [daily],
        'layout': {
                'title': "Number of infected daily",
                'paper_bgcolor': colors['background'],
                'plot_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }}
    }

    return fig_map, fig_graph, fig_daily, '{:,}'.format(int(total_confirmed)), '{:,}'.format(int(total_deaths)), '{:,}'.format(int(total_recovered))

if __name__ == '__main__':
    app.run_server(debug=True)