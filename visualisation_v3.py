import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

df = pd.read_csv("./data/bougival/database/bougival_db_complet.csv")
# phch_ponct = pd.read_csv("./data/")

# Création de l'application Dash
app = dash.Dash(__name__)

# Options de sélection de label
label_options = [{'label': col, 'value': col} for col in df.columns if col.startswith('label')]

# Options de sélection de données météo
weather_options = [{'label': col, 'value': col} for col in ['temperature_2m','relative_humidity_2m', 'precipitation', 'rain', 'cloud_cover','et0_fao_evapotranspiration', 'soil_temperature_0_to_7cm','soil_moisture_0_to_7cm']]

# Options de sélection de paramètres phisico-chimiques
physicochem_options = [{'label': col, 'value': col} for col in ['turbidite', 'temperature', 'pH', 'oxygene','conductivite']]

# Mise en page de l'application
app.layout = html.Div([
    html.Div([
        html.Label('Sélectionnez le label :'),
        dcc.Dropdown(id='label-dropdown', options=label_options, value=label_options[0]['value'])
    ]),
    html.Div([
        dcc.Graph(id='label-graph')
    ]),
    html.Div([
        html.Label('Sélectionnez les données météo :'),
        dcc.Dropdown(id='weather-dropdown', options=weather_options, value=[weather_options[0]['value']], multi=True)
    ]),
    html.Div([
        dcc.Graph(id='weather-graph')
    ]),
    html.Div([
        html.Label('Sélectionnez les paramètres physico-chimiques :'),
        dcc.Dropdown(id='physicochem-dropdown', options=physicochem_options, value=[physicochem_options[0]['value']], multi=True)
    ]),
    html.Div([
        dcc.Graph(id='physicochem-graph')
    ]),
])

# Définition des fonctions de mise à jour des graphiques en fonction des sélections
@app.callback(
    Output('label-graph', 'figure'),
    [Input('label-dropdown', 'value')]
)
def update_label_graph(selected_label):
    return {
        'data': [go.Scatter(x=df[df['suncycle_type'] == suncycle_type]['date'], y=df[df['suncycle_type'] == suncycle_type][selected_label], mode='lines', name=suncycle_type) for suncycle_type in df['suncycle_type'].unique()],
        'layout': go.Layout(title=f'Comptage du label {selected_label} au cours du temps', xaxis_title='Date', yaxis_title='Comptage')
    }

@app.callback(
    Output('weather-graph', 'figure'),
    [Input('weather-dropdown', 'value')]
)
def update_weather_graph(selected_weather):
    data = [go.Scatter(x=df['date'], y=df[col], mode='lines', name=col) for col in selected_weather]
    return {
        'data': data,
        'layout': go.Layout(title='Données météo au cours du temps', xaxis_title='Date', yaxis_title='Valeur')
    }

@app.callback(
    Output('physicochem-graph', 'figure'),
    [Input('physicochem-dropdown', 'value')]
)
def update_physicochem_graph(selected_physicochem):
    data = [go.Scatter(x=df['date'], y=df[col], mode='lines', name=col) for col in selected_physicochem]
    return {
        'data': data,
        'layout': go.Layout(title='Paramètres phisico-chimiques au cours du temps', xaxis_title='Date', yaxis_title='Valeur')
    }

# Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True)