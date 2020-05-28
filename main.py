# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

#################Data

country = 'Brazil'

df = pd.read_csv('covid19_data.csv')
df = df.set_index(df.date)
country_options = df['Country_Region'].unique()

#################Dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#333333',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height': '100vh'}, children=[
    html.H1(
        children='COVID19 Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='For educational purpose only', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div(style={'backgroundColor': colors['background'], 'width': '25%', 'margin': '20px'}, children=[
        dcc.Dropdown(
                id="country",
                options=[{
                    'label': i,
                    'value': i
                } for i in country_options],
                value='All countries')
    ]),

    dcc.Graph(
        id='total-confirmed-graph'
    )
])

@app.callback(
    dash.dependencies.Output('total-confirmed-graph', 'figure'),
    [dash.dependencies.Input('country', 'value')])
def update_graph(country):
    if country == "All countries" or country == None:
        df_plot = df[['Confirmed', 'Deaths', 'Recovered']].groupby('date').sum()
    else:
        df_plot = df[df['Country_Region'] == country][['Confirmed', 'Deaths', 'Recovered']].groupby('date').sum()

    trace1 = go.Scatter(x=df_plot.index, y=df_plot['Confirmed'], name='Confirmed')
    trace2 = go.Scatter(x=df_plot.index, y=df_plot['Deaths'], name='Deaths')
    trace3 = go.Scatter(x=df_plot.index, y=df_plot['Recovered'], name='Recovered')

    return {
        'data': [trace1, trace2, trace3],
        'layout': {
                'paper_bgcolor': colors['background'],
                'plot_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }}
    }

if __name__ == '__main__':
    app.run_server(debug=True)