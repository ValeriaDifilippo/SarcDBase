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

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dash app creation for the analysis_genes page
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), on_bad_lines='skip')
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter='\t', dtype=str)
        else:
            return html.Div(['Unsupported file format'])
        return df
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return html.Div([f'There was an error processing this file: {e}'])

def save_to_file(df, file_key):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.csv')
    df.to_csv(file_path, index=False)
    session[file_key] = file_path  # Store the path in a session key
    return file_path

def load_from_file(file_path):
    return pd.read_csv(file_path)

def create_dash_table(df):
    return html.Div([
        dag.AgGrid(
            id='ag-grid',
            columnDefs=[{'headerName': i, 'field': i} for i in df.columns],
            rowData=df.to_dict('records'),
            defaultColDef={'sortable': True, 'filter': True, 'resizable': True},
            style={'height': 'calc(100vh - 150px)', 'width': '100%'},
            dashGridOptions={'pagination': False},
        )
    ])

def create_dash_analysis_who(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/analysis/genes/')
    dash_app.layout = html.Div([
        dcc.Upload(
            id='upload-data-sv',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'backgroundColor': '#f0f5f9', 'color': '#283593',
                'border': '1px solid #b0bec5', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px', 'cursor': 'pointer'
            },
            multiple=False
        ),
        html.Div(id='output-data-upload-sv'),
    ])

    @dash_app.callback(
        Output('output-data-upload-sv', 'children'),
        Input('upload-data-sv', 'contents'),
        State('upload-data-sv', 'filename')
    )
    def update_output_sv(contents, filename):
        file_key = 'file_path_sv'  # Unique session key for this Dash app
        if contents is not None:
            df = parse_contents(contents, filename)
            if isinstance(df, pd.DataFrame):
                save_to_file(df, file_key)
                return create_dash_table(df)
            else:
                return html.Div(['Failed to process file. Please check the file format.'])
        elif file_key in session:
            df = load_from_file(session[file_key])
            return create_dash_table(df)
        return html.Div('No data uploaded yet.')

    return dash_app
