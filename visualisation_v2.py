import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

db_path = "./data/bougival/database/Bougival_database.csv"

# Lecture des données

# data = """
# date,suncycle_type,suncycle_day,label_0,label_1,label_2,label_3,label_4,label_5,label_6,label_7,label_8,label_9,label_10,date_min,date_max,dist_tw_rising,dist_tw_setting,moon_phase,temperature_2m,relative_humidity_2m,precipitation,rain,cloud_cover,et0_fao_evapotranspiration,soil_temperature_0_to_7cm,soil_moisture_0_to_7cm
# 2023-04-18 08:00:00,daylight,2023-04-18 00:00:00,0.0,0.0,3.0,2.0,1.0,0.0,0.0,0.0,0.0,10.0,23.0,2023-04-18 08:50:00,2023-04-18 08:59:00,12146.082404,-39908.568601,26.244555555555557,9.5195,86.15349,0.0,0.0,1.8,0.13027237,8.919499,0.345
# 2023-04-18 09:00:00,daylight,2023-04-18 00:00:00,9.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,6.0,7.0,2023-04-18 09:00:00,2023-04-18 09:59:00,15746.082404,-36308.568601,26.244555555555557,11.3195,77.460175,0.0,0.0,21.300001,0.21205097,10.2195,0.344
# 2023-04-18 10:00:00,daylight,2023-04-18 00:00:00,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,2023-04-18 10:00:00,2023-04-18 10:59:00,19346.082404,-32708.568601,26.244555555555557,12.7695,67.345795,0.1,0.1,51.0,0.28168085,11.4695,0.343
# 2023-04-18 11:00:00,daylight,2023-04-18 00:00:00,17.0,8.0,11.0,22.0,6.0,0.0,6.0,44.0,11.0,36.0,34.0,2023-04-18 11:00:00,2023-04-18 11:59:00,22946.082404,-29108.568601,26.244555555555557,13.4695,58.011547,0.1,0.1,18.0,0.30232328,12.3195,0.343
# """

# df = pd.read_csv(pd.compat.StringIO(data))

df = pd.read_csv(db_path)

# Création de l'application Dash
app = dash.Dash(__name__)

# Définition des options de sélection de label
label_options = [{'label': col, 'value': col} for col in df.columns if col.startswith('label')]

# Mise en page de l'application
app.layout = html.Div([
    dcc.Dropdown(
        id='label-dropdown',
        options=label_options,
        value=label_options[0]['value']
    ),
    dcc.Graph(id='graph_count'),
])

# Définition de la fonction de mise à jour du graphique en fonction de la sélection de label
@app.callback(
    Output('combined-graph', 'figure'),
    [Input('label-dropdown', 'value')]
)
def update_graph(selected_label):
    # Calcul du comptage des labels par type de cycle solaire
    label_counts = df.groupby(['date', 'suncycle_type'])[selected_label].sum().reset_index()

    # Création du graphique du comptage des labels par type de cycle solaire
    fig = make_subplots(rows=2, cols=1, subplot_titles=(f'Comptage du label {selected_label} en fonction du temps par type de cycle solaire', 'Données météo'), shared_xaxes=True)

    for suncycle_type, data_group in label_counts.groupby('suncycle_type'):
        fig.add_trace(go.Scatter(x=data_group['date'], y=data_group[selected_label], mode='lines', name=suncycle_type, legendgroup=suncycle_type), row=1, col=1)
    
    # Ajouter les données météorologiques dans le subplot en bas
    weather_data = df[['date', 'temperature_2m', 'relative_humidity_2m', 'precipitation', 'rain', 'cloud_cover']]
    for column in weather_data.columns[1:]:
        fig.add_trace(go.Scatter(x=weather_data['date'], y=weather_data[column], mode='lines', name=column, legendgroup='weather'), row=2, col=1)
    
    # Mise à jour des légendes pour chaque subplot
    fig.update_layout(legend=dict(orientation="h"), legend_tracegroupgap=200)
    
    fig.update_layout(height=800)
    
    return fig

# Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True)