from email import message
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from helpers.key_finder import api_key
from helpers.api_call import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


########### Define a few variables ######

tabtitle = 'Movies'
sourceurl = 'https://www.kaggle.com/tmdb/tmdb-movie-metadata'
sourceurl2 = 'https://developers.themoviedb.org/3/getting-started/introduction'
githublink = 'https://github.com/austinlasseter/tmdb-rf-classifier'

########### Define sentiment analyzing function ######
def sentiment_analysis(sentence):
    sid = SentimentIntensityAnalyzer()

    sentiment_dict = sid.polarity_scores(sentence)

    # positive score >= 0.05
    # neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
    # negative sentiment: compound score <= -0.05
    compound = sentiment_dict['compound']
    if compound >= 0.05:
        sentiment = 'joyful!'
    elif compound > -0.05:
        sentiment = 'lacking emotion'
    else:
        sentiment = 'terrifyingly negative'

    message=f'According to Vader, this movie is {sentiment}'
    return message



########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout

app.layout = html.Div(children=[
    dcc.Store(id='tmdb-store', storage_type='session'),
    dcc.Store(id='summary-store', storage_type='session'),
    html.Div([
        html.H1(['Movie Reviews']),
        html.Div([
            html.Div([
                html.Div('Randomly select a movie summary'),
                html.Button(id='eek-button', n_clicks=0, children='API call', style={'color': 'rgb(255, 255, 255)'}),
                html.Div(id='movie-title', children=[]),
                html.Div(id='movie-release', children=[]),
                html.Div(id='movie-overview', children=[]),
                html.Div(id='review-sentiment', children=[])

            ], style={ 'padding': '12px',
                    'font-size': '22px',
                    # 'height': '400px',
                    'border': 'thick red solid',
                    'color': 'rgb(255, 255, 255)',
                    'backgroundColor': '#536869',
                    'textAlign': 'left',
                    },
            className='six columns'),

        ], className='twelve columns'),
        html.Br(),

    ], className='twelve columns'),


        # Output
    html.Div([
        # Footer
        html.Br(),
        html.A('Code on Github', href=githublink, target="_blank"),
        html.Br(),
        html.A("Data Source: Kaggle", href=sourceurl, target="_blank"),
        html.Br(),
        html.A("Data Source: TMDB", href=sourceurl2, target="_blank"),
    ], className='twelve columns'),



    ]
)

########## Callbacks

# TMDB API call
@app.callback(Output('tmdb-store', 'data'),
              [Input('eek-button', 'n_clicks')],
              [State('tmdb-store', 'data')])
def on_click(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks==0:
        data = {'title':' ', 'release_date':' ', 'overview':' '}
    elif n_clicks>0:
        data = api_pull(random.choice(ids_list))
    return data

@app.callback([Output(component_id='movie-title', component_property='children'),
                Output(component_id='movie-release', component_property='children'),
                Output(component_id='movie-overview', component_property='children'),
                Output(component_id='review-sentiment', component_property='children')
                ],
              [Input('tmdb-store', 'modified_timestamp')],
              [State('tmdb-store', 'data')])
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate
    else:
        message=''
        if len(data['overview']) > 1:
            message = sentiment_analysis(data['overview'])
        return data['title'], data['release_date'], data['overview'], message


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
