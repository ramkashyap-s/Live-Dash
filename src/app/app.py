from src.database.database_operations import DatabaseOperations
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.graph_objs import *
import pandas as pd
from datetime import datetime, timedelta

# ToDO refactor this file

db = DatabaseOperations()
con = db.get_connection()

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


app = dash.Dash(
    'streaming-twitch-app',
    external_stylesheets=external_css
)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H2("Twitch Stats Streaming"),
    ], className='banner'),
    html.Div([
        html.Div([
            html.H3(" (Number of comments)")
        ], className='Title'),
        html.Div([
            dcc.Graph(id='num-comments'),
        ], className='twelve columns num-comments'),
        dcc.Interval(id='num-comments-update', interval=1000, n_intervals=0),
    ], className='row num-comments-row')], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})


@app.callback(Output('num-comments', 'figure'), [Input('num-comments-update', 'n_intervals')])
def gen_num_comments(interval):
    now = datetime.now()
    prev = now - timedelta(seconds=120)

    df = pd.read_sql_query("SELECT channel_name, metric_name, metric_value from stats where channel_name = '{0}' "
                           "AND end_time > '{1}' AND end_time <= '{2}';".format('#elded', prev, now), con)
    trace = Scatter(
        y=df['metric_value'],
        line=Line(
            color='#42C4F7'
        ),
        hoverinfo='skip',
        mode='lines'
    )

    layout = Layout(
        height=350,
        xaxis=dict(
            range=[0, 120],
            showgrid=False,
            showline=False,
            zeroline=False,
            fixedrange=True,
            tickvals=[0, 30, 60, 90, 120],
            ticktext=['120', '90', '60', '30', '0'],
            title='Time Elapsed (sec)'
        ),
        yaxis=dict(
            range=[min(0, min(df['metric_value'])),
                   # max(30, max(df['metric_value'])+max(df['metric_value']))],
                   max(30, 10 + max(df['metric_value']))],
            showline=False,
            fixedrange=True,
            zeroline=False,
            nticks=max(6, round(df['metric_value'].iloc[-1]/10))
        ),
        margin=Margin(
            t=45,
            l=50,
            r=50
        )
    )

    return Figure(data=[trace], layout=layout)



if __name__ == '__main__':
    app.run_server()