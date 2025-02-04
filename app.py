import os
import sys
import requests
import dash
import pandas as pd
import plotly.express as px
from flask import Flask
from dash import dcc, html
from dash.dependencies import Input, Output
from routes.continent import bp as continent_bp
from routes.country import bp as country_bp
from routes.pandemic import bp as pandemic_bp
from routes.pandemic_country import bp as pandemic_country_bp
from routes.daily_pandemic_country import bp as daily_pandemic_country_bp

sys.path.append(os.path.join(os.path.dirname(__file__), 'load'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'etl'))

def create_app():
    app = Flask(__name__)

    app.register_blueprint(continent_bp)
    app.register_blueprint(country_bp)
    app.register_blueprint(pandemic_bp)
    app.register_blueprint(pandemic_country_bp)
    app.register_blueprint(daily_pandemic_country_bp)

    dash_app = dash.Dash(__name__, server=app, url_base_pathname='/')

    dash_app.layout = html.Div([

        
        html.Nav([html.H2("Pandemic Statistics Dashboard", style={'color': 'white', 'margin': '0', 'padding': '10px', 'textAlign': 'center'})],
                 style={'backgroundColor': 'rgba(0, 0, 0, 0)', 'padding': '10px'}),

        
        html.Div([
            
            html.Div([
                html.Label("Select Country", style={'fontSize': '18px', 'fontWeight': 'bold','color': 'white'}),
                dcc.Dropdown(id='country-dropdown', options=[], value=None,
                             style={'width': '100%', 'fontFamily': 'Arial, sans-serif', 'borderRadius': '8px', 'border': '1px solid #ddd'}),
            ], style={'width': '15%', 'padding': '10px'}),

            
            html.Div([
                html.Label("Select Pandemic", style={'fontSize': '18px', 'fontWeight': 'bold','color': 'white'}),
                dcc.Dropdown(id='pandemic-dropdown', options=[], value=None,
                             style={'width': '100%', 'fontFamily': 'Arial, sans-serif', 'borderRadius': '8px', 'border': '1px solid #ddd'}),
            ], style={'width': '15%', 'padding': '10px'}),

           
            html.Div([
                html.Label("Select Date Range", style={'fontSize': '18px', 'fontWeight': 'bold','color': 'white'}),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date="2020-01-01",
                    end_date="2025-01-01",
                    display_format='YYYY-MM-DD',
                    style={
                        'width': '100%',
                        'fontFamily': 'Arial, sans-serif',
                        'border': '1px solid #ddd',
                        'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.12)',
                        'fontSize': '5px',
                        'display': 'flex',
                        'justifyContent': 'space-between',
                    },
                    
                ),
            ], ),

        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px', 'backgroundColor': 'rgba(0, 0, 0, 0)', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),

        
        html.Div(id='cards-container', style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'justifyContent': 'center', 'margin': '20px auto'}),
        dcc.Graph(id='continent-pie-chart', style={'width': '50%', 'margin': '40px'}),
        dcc.Graph(id='recovery-trend', style={'width': '50%', 'margin': '40px','Color': 'black'})
        
    ], style={
        'backgroundImage': 'url(https://mediclinic.scene7.com/is/image/mediclinic/hirslanden-corona-virus-teaser:1-1?_ck=1616227095797&wid=1050&hei=1050&dpr=off)',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center center',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': 'rgba(0, 0, 0, 0)'
    })

   
    def get_countries():
        response = requests.get('http://127.0.0.1:5000/country')
        return response.json() if response.status_code == 200 else []
    def get_continents():
        response = requests.get('http://127.0.0.1:5000/continent')
        return response.json() if response.status_code == 200 else []

    def get_pandemics():
        response = requests.get('http://127.0.0.1:5000/pandemic')
        return response.json() if response.status_code == 200 else []

    def get_daily_pandemic(id_country, id_pandemic):
        response = requests.get(f'http://127.0.0.1:5000/daily_pandemic_country/{id_country}/{id_pandemic}')
        return response.json() if response.status_code == 200 else []
    def get_pandemic_by_continent():
        response = requests.get(f'http://127.0.0.1:5000/pandemic_country/continent')
        return response.json() if response.status_code == 200 else []

   
    @dash_app.callback(
        Output('country-dropdown', 'options'),
        Input('country-dropdown', 'value')
    )
    def update_dropdown(value):
        countries = get_countries()
        return [{'label': country[1], 'value': country[0]} for country in countries]

    @dash_app.callback(
        Output('pandemic-dropdown', 'options'),
        Input('pandemic-dropdown', 'value')
    )
    def update_pandemic_dropdown(value):
        pandemics = get_pandemics()
        return [{'label': pandemic['name'], 'value': pandemic['id_pandemic']} for pandemic in pandemics]

    @dash_app.callback(
        Output('cards-container', 'children'),
        [Input('country-dropdown', 'value'),
         Input('pandemic-dropdown', 'value')]
    )
    def update_cards(country_id, pandemic_id):
        if not country_id or not pandemic_id:
            return html.P("Veuillez sélectionner un pays et une pandémie.", style={'textAlign': 'center', 'color': 'white'})

        response = requests.get(f'http://127.0.0.1:5000/pandemic_country/{country_id}/{pandemic_id}')
        if response.status_code == 200:
            data = response.json()
            cards = [
                html.Div([html.H3("Total Deaths"), html.P(f"{data.get('total_deaths', 0)}")],
                         style={'border': '1px solid #d04e47', 'padding': '10px', 'width': '200px', 'backgroundColor': 'rgba(0, 0, 0, 0)','backdrop-filter': 'blur(50px)', 'borderRadius': '10px', 'textAlign': 'center', 'color': '#e67e22','font-weight': 'bold','font-size': '20px'}),
                html.Div([html.H3("Total Cases"), html.P(f"{data.get('total_confirmed', 0)}")],
                         style={'border': '1px solid #e67e22', 'padding': '10px', 'width': '200px', 'backgroundColor': 'rgba(0, 0, 0, 0)','backdrop-filter': 'blur(50px)', 'borderRadius': '10px', 'textAlign': 'center', 'color': '#5b8fd4','font-weight': 'bold','font-size': '20px'}),
                html.Div([html.H3("Total Recovered"), html.P(f"{data.get('total_recovered', 0)}")],
                         style={'border': '1px solid #2ecc71', 'padding': '10px', 'width': '200px', 'backgroundColor': 'rgba(0, 0, 0, 0)','backdrop-filter': 'blur(50px)','borderRadius': '10px', 'textAlign': 'center', 'color': '#27ae60','font-size': '20px','font-weight': 'bold'})
            ]
            return cards
        return html.P("Données non trouvées.", style={'textAlign': 'center', 'color': 'black'})

    @dash_app.callback(
        Output('recovery-trend', 'figure'),
        [Input('country-dropdown', 'value'),
         Input('pandemic-dropdown', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date')]
    )
    def update_recovery_graph(country_id, pandemic_id, start_date, end_date):
        if not country_id or not pandemic_id:
            return px.line(title="Sélectionnez un pays et une pandémie")

        data = get_daily_pandemic(country_id, pandemic_id)
        if not data:
            return px.line(title="Aucune donnée disponible")

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        if 'daily_new_cases' not in df_filtered.columns:
            return px.line(title="Données manquantes")

        fig = px.line(df_filtered, x='date', y='daily_new_cases',
                      title="Évolution du Nombre de Cas Quotidiens",
                      labels={'daily_new_cases': 'Cas quotidiens', 'date': 'Date'},
                      markers=True)

        fig.update_traces(line=dict(color='blue', width=2), marker=dict(size=6, color='red'))
        fig.update_layout(
          
           plot_bgcolor='rgba(0, 0, 0, 0)',  # Couleur du fond du graphique
           paper_bgcolor='rgba(0, 0, 0, 0)',  # Couleur de fond du cadre
           font=dict(color='white'),
           xaxis=dict(gridcolor='gray', color='white'),
           yaxis=dict(gridcolor='gray', color='white')
        )
        return fig
        
    
    @dash_app.callback(
       Output('continent-pie-chart', 'figure'),
       [Input('country-dropdown', 'value')]
    )
    def update_continent_pie_chart(country_id):
        continents = get_pandemic_by_continent()  

        if not continents:
            return px.pie(title="Aucune donnée disponible")
    
    
        continent_names = [continent['continent'] for continent in continents]
        continent_cases = [continent.get('cases', 0) for continent in continents]
    
        fig = px.pie(
          names=continent_names,
          values=continent_cases,
          title="Répartition des Cas par Continent"
        )
      
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        fig.update_layout(
          plot_bgcolor='blue', 
          paper_bgcolor='blue',
          font=dict(color='white')
        )
        return fig


    return app

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()
