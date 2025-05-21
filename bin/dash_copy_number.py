from flask import Flask, render_template, session
from dash import Dash, dcc, html, Input, Output, State, callback
import pandas as pd
import os
import uuid
import base64
import io
import dash_ag_grid as dag
import plotly.express as px
import datetime

# Function to parse the contents of the uploaded file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), on_bad_lines='skip')
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter='\t', low_memory=False)
        else:
            return html.Div(['Unsupported file format'])
        return df
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return html.Div([f'There was an error processing this file: {e}'])

# Function to create the Dash app for the copy number page
def create_dash_copy_number(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/visualization/copy_number/')
    
    dash_app.layout = html.Div([
        html.Div([
            html.H2("How this page works:", style={'textAlign': 'center', 'margin-bottom': '10px'}),
            html.Ul([
                html.Li(" Upload the file"),
                html.Li(" Generate the plot"),
                html.Li(" Analyse")
            ], style={'fontSize': '18px', 'lineHeight': '1.6', 'listStyleType': 'decimal', 'margin': '0', 'padding': '0 20px'})
        ], style={'padding': '20px', 'backgroundColor': '#f0f5f9', 'borderRadius': '5px', 'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)', 'margin-bottom': '20px'}),
        
        html.Div(id='upload-status', style={'margin-bottom': '10px'}),  # Message for upload status
        html.Div([
            dcc.Upload(
                id='upload-data-cn',
                children=html.Div([
                    html.H4('Select Files', style={'color': 'white', 'margin': '0', 'lineHeight': '60px'})
                ]),
                style={
                    'width': '200px',  # Smaller width
                    'height': '60px',  # Smaller height
                    'lineHeight': '60px',  # Center text vertically
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'borderColor': '#283593',  # Blue border color
                    'backgroundColor': '#283593',  # Blue background color
                    'textAlign': 'center',  # Center text horizontally
                    'margin': '20px',
                    'cursor': 'pointer',
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
                    'display': 'inline-block',  # Aligns the upload area inline
                    'position': 'relative'
                },
                multiple=False
            ),
        ], style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center'}),
        html.Div(id='plot-status'),  # Message for plot status
        dcc.Dropdown(id='chromosome-dropdown', placeholder="Select a chromosome", style={'width': '50%'}),
        html.Button('Generate Plot', id='generate-plot-button', n_clicks=0),
        html.Div(id='plot-output')  # Div for displaying the plot
    ])
    
    @dash_app.callback(
        Output('chromosome-dropdown', 'options'),
        Output('upload-status', 'children'),  # Output for upload status message
        Input('upload-data-cn', 'contents'),
        State('upload-data-cn', 'filename')
    )
    def update_dropdown(contents, filename):
        if contents is not None:
            df = parse_contents(contents, filename)
            if isinstance(df, pd.DataFrame):
                options = [{'label': str(chr), 'value': str(chr)} for chr in df['chromosome'].unique()]
                upload_message = 'The table is now uploaded. Choose your chromosome and generate the plot.'
                return options, upload_message
            else:
                return [], 'Failed to process file. Please check the file format.'
        return [], ''  # No message if no file is uploaded

    @dash_app.callback(
        Output('plot-status', 'children'),
        Output('plot-output', 'children'),
        Input('generate-plot-button', 'n_clicks'),
        State('upload-data-cn', 'contents'),
        State('upload-data-cn', 'filename'),
        State('chromosome-dropdown', 'value')
    )
    def generate_scatter_plot(n_clicks, contents, filename, selected_chr):
        if n_clicks > 0:
            if contents is None:
                return 'Upload a file.', ''  # No plot generated if no file is uploaded

            if selected_chr is None:
                return 'Please select a chromosome.', ''  # No plot generated if no chromosome is selected

            # Display "please wait" message
            plot_status = 'The plot is generating, please wait...'
            
            # Process and generate the plot
            df = parse_contents(contents, filename)
            df_filtered = df[df['chromosome'] == selected_chr]
            scatter_plot = px.scatter(df_filtered, x="start", y="log2", color='color', symbol='gene')
            scatter_plot.add_hline(y=0)
            scatter_plot.update_layout(showlegend=False)
            
            # Replace the message with the plot
            plot_output = dcc.Graph(figure=scatter_plot)
            return plot_status, plot_output

        return '', ''  # No messages if no button is clicked

    return dash_app

