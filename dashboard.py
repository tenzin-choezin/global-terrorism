import numpy as np  
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import geopandas as gpd
import folium
import json
from folium.plugins import MarkerCluster
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, State

pd.set_option('display.max_columns', None)

pd.set_option('display.max_columns', None)

# Reading in the data with the proper encoding
data = pd.read_csv('gt_data.csv', encoding='ISO-8859-1')


columns = ['iyear', 'imonth', 'iday', 'country_txt', 'region_txt', 'provstate','city', 'latitude', 'longitude', 
           'suicide', 'attacktype1_txt', 'targtype1_txt', 'target1', 'gname', 'motive', 'weaptype1_txt', 'propvalue', 'nkill', 'nwound']

df = data[columns].rename(columns = {'iyear':'year', 'imonth':'month', 'iday':'day', 'country_txt':'country', 'region_txt':'region', 'provstate':'state',
                'attacktype1_txt':'attack_type', 'target1':'target', 'nkill':'killed', 'nwound':'wounded', 'gname':'group',
                'targtype1_txt':'target_type', 'weaptype1_txt':'weapon_type', 'propvalue' : 'property_value'})


# GEOPANDAS DATA
geo_all = gpd.read_file('countries.geojson').rename(columns = {'ADMIN' : 'country'})[['country', 'geometry']]
geo_us = gpd.read_file('us.geojson').rename(columns = {'NAME' : 'country'})[['country', 'geometry']]
geo_all = pd.concat([geo_all, geo_us], ignore_index = True)


# COUNTRY COORDINATES
country2coordinates = pd.read_csv('country_coordinates.csv').iloc[:, 1:4]
data_scatter = df[(~df['killed'].isnull()) & (~df['wounded'].isnull())][['country', 'year', 'region', 'state', 'city', 'latitude', 'longitude', 
                                                                         'attack_type', 'target_type', 'weapon_type', 'group', 'killed', 'wounded']]


app = dash.Dash()
server = app.server
app.title = 'Global Terrorism Analytics'

column_options = ['Attack Type', 'Weapon Type', 'Target Type', 'Terrorist Group']


app.layout = html.Div(
    id = 'root',
    children = [
        
        html.Div(
            id = 'Header',
            children = [
                html.H4('Global Terrorism Analytics',
                        style = {'fontSize' : 65, 'font-family' : 'monospace', 'font-weight' : 'bold', 'textAlign' : 'center', 'marginTop' : 15, 'marginBottom' : 15}
                       ),
                
                html.P(
                    children = 'This dashboard contains a wide variety of analysis on global terrorism over the last 50 years, with the main features being plots and charts describing the data. The goal is to try to better understand methods of terror, groups behind these attacks, where these attacks are occuring, and the numbers associated with those attacks.',
                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'margin-left': '30px', 'margin-right' : '30px', 'marginBottom' : 15}
                )
            ]
        ),
        
        html.H4('Overview of Historical Numbers',
                style = {'fontSize' : 36, 'font-family' : 'monospace', 'font-weight' : 'bold', 'textAlign' : 'center', 'marginTop' : 25, 'marginBottom' : 0}
               ),
        
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a column to aggregate',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'column',
                                    options = column_options,
                                    value = None,
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '33%', 'margin-left': '150px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a region',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'region',
                                    options = sorted(pd.unique(df['region'])),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '33%', 'margin-left': '20px', 'margin-right' : '20px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a country',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'country',
                                    options = sorted(pd.unique(df['country'])),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '33%', 'margin-right' : '150px'}
                        ), 
                        
                    ], style = dict(display='flex')
                ),
                
                html.Div(
                    children = [
                        dcc.Graph(id = 'stacked-bar', style={'marginTop' : 10, 'margin-left': '95px', 'width' : '90%', 'marginBottom' : 15})
                    ]
                )     
            ]
        ),
        
        html.H4('Terrorism Methodology Breakdown',
                style = {'fontSize' : 36, 'font-family' : 'monospace', 'font-weight' : 'bold', 'textAlign' : 'center', 'marginTop' : 25, 'marginBottom' : 0}
               ),
        
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a column to aggregate',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'column-agg',
                                    options = column_options,
                                    value = 'Attack Type',
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '125px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a geographic type to aggregate',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-agg',
                                    options = ['Region', 'Country'],
                                    value = 'Region',
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px'}
                        ),    
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a start year',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'start-year',
                                    options = pd.unique(df['year']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                                
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px', 'margin-right' : '20px'}
                        ),
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select an end year',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'end-year',
                                    options = pd.unique(df['year']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                                
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-right' : '125px'}
                        )
                        
                    ], style = dict(display='flex')
                ),
                
                html.Div(
                    children = [
                        dcc.Graph(id = 'by-area', style={'marginTop' : 10, 'margin-left': '25px', 'width' : '53%', 'marginBottom' : 15}),
                        dcc.Graph(id = 'bubble', style={'marginTop' : 10, 'margin-left': '0px', 'margin-right' : '25px', 'width' : '47%', 'marginTop' : 10, 'marginBottom' : 15})
                        
                    ], style = dict(display='flex')
                )
                
            ]
        ),
        
        
        html.H4('Geospatial Analysis',
                style = {'fontSize' : 36, 'font-family' : 'monospace', 'font-weight' : 'bold', 'textAlign' : 'center', 'marginTop' : 25, 'marginBottom' : 0}
               ),
        
        # MAP STARTS HERE
        html.Div(
            children = [
                html.Div(
                    children = [
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a metric to color by',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-type',
                                    options = ['Most Common', 'Most Fatal'],
                                    value = 'Most Common',
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '75px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a column to aggregate',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'agg-type',
                                    options = column_options,
                                    value = 'Attack Type',
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a region',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-region',
                                    options = sorted(pd.unique(df['region'])),
                                    value = 'North America',
                                    clearable = False,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a country',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-country',
                                    options = sorted(pd.unique(df['country'])),
                                    value = None,
                                    clearable = True,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a start year',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-start',
                                    options = pd.unique(df['year']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                                
                            ], style={'display': 'inline-block', 'width': '35%', 'margin-left': '20px'}
                        ),
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select an end year',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'geo-end',
                                    options = pd.unique(df['year']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                                
                            ], style={'display': 'inline-block', 'width': '35%', 'margin-left' : '20px', 'margin-right' : '75px'}
                        )
                        
                    ], style = dict(display='flex')
                ),
                
               html.Div(
                    children = [
                        dcc.Graph(id = 'geo-chart', style={'marginTop' : 10, 'margin-left': '15px', 'width' : '50%', 'marginBottom' : 15}),
                        dcc.Graph(id = 'geo-chart2', style={'marginTop' : 10, 'margin-left': '0px', 'margin-right' : '15px', 'width' : '50%', 'marginTop' : 10, 'marginBottom' : 15})
                        
                    ], style = dict(display='flex')
                )
                
            ]
        )    
        
    ]
)



@app.callback(
    Output('country', 'options'),
    [Input('region', 'value')]
)
def country_update(region):
    if region is not None:
        filtered = df[df['region'] == region]
        countries = [{'label':i,'value':i} for i in sorted(filtered["country"].unique())]
        return countries
    else:
        countries = [{'label':i,'value':i} for i in sorted(df["country"].unique())]
        return countries
    
    
@app.callback(
    Output('end-year', 'options'),
    [Input('start-year', 'value')]
)
def end_yr_update(start):
    if start is not None:
        filtered = df[df['year'] >= start]
        years = [{'label':i,'value':i} for i in filtered["year"].unique()]
        return years
    else:
        years = [{'label':i,'value':i} for i in df["year"].unique()]
        return years
 
    
@app.callback(
    Output('start-year', 'options'),
    [Input('end-year', 'value')]
)
def start_yr_update(end):
    if end is not None:
        filtered = df[df['year'] <= end]
        years = [{'label':i,'value':i} for i in filtered["year"].unique()]
        return years
    else:
        years = [{'label':i,'value':i} for i in df["year"].unique()]
        return years
    
# UTILITY FUNCTION
def get_target_type(attack):
    if attack in ['Business', 'Journalists & Media', 'NGO']:
        return 'Business'
    elif attack in ['Government (General)', 'Government (Diplomatic)']:
        return 'Government'
    elif attack in ['Private Citizens & Property', 'Tourists']:
        return 'Individuals'
    elif attack == 'Educational Institution':
        return 'Education'
    elif attack in ['Religious Figures/Institutions', 'Abortion Related']:
        return 'Religion'
    elif attack in ['Airports & Aircraft', 'Maritime', 'Transportation']:
        return 'Transportation'
    elif attack in ['Food or Water Supply', 'Telecommunication', 'Utilities']:
        return 'Infrastructure'
    elif attack in ['Unknown', 'Other']:
        return 'Other'
    else:
        return attack
    
@app.callback(
    Output('stacked-bar', 'figure'),
    [Input('region', 'value'),
     Input('country', 'value'),
     Input('column', 'value')
    ]
)
def barchart_update(region, country, column, df = df):
    if (region is not None) and country is None:
        df = df[df['region'] == region]
        
    if ((country is not None) and (region is None)) or ((region is not None) and (country is not None)):
        df = df[df['country'] == country]
            
    df_filtered = df[['year', 'attack_type', 'wounded', 'killed']][(df['attack_type'] != 'Unknown')]
    by_region = df_filtered.groupby(['year', 'attack_type']).agg({'attack_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
    by_region = by_region.rename(columns = {
        'attack_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'attack_type' : 'Attack Type'})

    # getting attack type percentages by year
    attack_props = []
    death_props = []
    wounded_props = []
    for year in sorted(pd.unique(by_region['year'])):
        attack_props += by_region[by_region['year'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
        death_props += by_region[by_region['year'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
        wounded_props += by_region[by_region['year'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
    by_region['attack_prop'] = attack_props
    by_region['death_prop'] = death_props
    by_region['wounded_prop'] = wounded_props

    # getting text for each bar
    attack_text = []
    for i in range(len(by_region)):
        attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                           + '<br>' 
                           + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                           + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

    by_region['attack_text'] = attack_text

    fig = px.bar(by_region, x = 'year', y = 'attacks', color = 'Attack Type', template = 'plotly_dark',
                 text = 'attack_text', height = 600, labels={'year' : 'Year', 'attacks' : '# of Attacks'})

    fig.update_traces(hovertemplate = '%{text}', textposition = "none")

    fig.update_xaxes(showspikes=True, spikecolor="red", spikemode = 'across', spikethickness=3)

    fig.update_layout(title = {'text' : 'Numbers per Attack Type by Year', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                      hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13),
                     xaxis=dict(rangeslider=dict(visible=True)))

    if column == 'Weapon Type':
        df_filtered = df[['year', 'weapon_type', 'wounded', 'killed']][(df['weapon_type'] != 'Unknown')]
        by_region = df_filtered.groupby(['year', 'weapon_type']).agg({'weapon_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_region = by_region.rename(columns = {
            'weapon_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'weapon_type' : 'Weapon Type'})

        by_region['Weapon Type'] = by_region['Weapon Type'].apply(lambda x: 
                                                                  'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)

        # getting attack type percentages by year
        attack_props = []
        death_props = []
        wounded_props = []
        for year in sorted(pd.unique(by_region['year'])):
            attack_props += by_region[by_region['year'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
            death_props += by_region[by_region['year'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
            wounded_props += by_region[by_region['year'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
        by_region['attack_prop'] = attack_props
        by_region['death_prop'] = death_props
        by_region['wounded_prop'] = wounded_props

        # getting text for each bar
        attack_text = []
        for i in range(len(by_region)):
            attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                               + '<br>' 
                               + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                               + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

        by_region['attack_text'] = attack_text

        fig = px.bar(by_region, x = 'year', y = 'attacks', color = 'Weapon Type', template = 'plotly_dark',
                     text = 'attack_text', height = 600, labels={'year' : 'Year', 'attacks' : '# of Attacks'})

        fig.update_traces(hovertemplate = '%{text}', textposition = "none")

        fig.update_xaxes(showspikes=True, spikecolor="white", spikemode = 'across', spikethickness=3)

        fig.update_layout(title = {'text' : 'Numbers per Weapon Type by Year', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13),
                          xaxis=dict(rangeslider=dict(visible=True)))
        return fig
    
    if column == 'Target Type': 
        df_filtered = df[['year', 'target_type', 'wounded', 'killed']][(df['target_type'] != 'Unknown')]
        df_filtered['target_type'] = df_filtered['target_type'].apply(get_target_type)
        by_region = df_filtered.groupby(['year', 'target_type']).agg({'target_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_region = by_region.rename(columns = {
            'target_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'target_type' : 'Target Type'})

        # getting attack type percentages by year
        attack_props = []
        death_props = []
        wounded_props = []
        for year in sorted(pd.unique(by_region['year'])):
            attack_props += by_region[by_region['year'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
            death_props += by_region[by_region['year'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
            wounded_props += by_region[by_region['year'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
        by_region['attack_prop'] = attack_props
        by_region['death_prop'] = death_props
        by_region['wounded_prop'] = wounded_props

        # getting text for each bar
        attack_text = []
        for i in range(len(by_region)):
            attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                               + '<br>' 
                               + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                               + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

        by_region['attack_text'] = attack_text

        fig = px.bar(by_region, x = 'year', y = 'attacks', color = 'Target Type', template = 'plotly_dark',
                     text = 'attack_text', height = 600, labels={'year' : 'Year', 'attacks' : '# of Attacks'})

        fig.update_traces(hovertemplate = '%{text}', textposition = "none")

        fig.update_xaxes(showspikes=True, spikecolor="white", spikemode = 'across', spikethickness=3)

        fig.update_layout(title = {'text' : 'Numbers per Target Type by Year', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "white", font_color = 'black', font_size = 13),
                          xaxis=dict(rangeslider=dict(visible=True)))
        return fig
    
    if column == 'Terrorist Group':
        df_filtered = df[['year', 'group', 'wounded', 'killed']][(df['group'] != 'Unknown')]
        by_region = df_filtered.groupby(['year', 'group']).agg({'group' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_region = by_region.rename(columns = {
            'group' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'group' : 'Group'})
        by_region = by_region.sort_values(by = ['year', 'attacks', 'killed'], ascending = [True, False, False]).groupby(['year']).head(10).reset_index(drop = True)

        # getting attack type percentages by year
        attack_props = []
        death_props = []
        wounded_props = []
        for year in sorted(pd.unique(by_region['year'])):
            attack_props += by_region[by_region['year'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
            death_props += by_region[by_region['year'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
            wounded_props += by_region[by_region['year'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
        by_region['attack_prop'] = attack_props
        by_region['death_prop'] = death_props
        by_region['wounded_prop'] = wounded_props

        # getting text for each bar
        attack_text = []
        for i in range(len(by_region)):
            attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                               + '<br>' 
                               + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                               + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

        by_region['attack_text'] = attack_text

        fig = px.bar(by_region, x = 'year', y = 'attacks', color = 'Group', template = 'plotly_dark',
                     text = 'attack_text', height = 600, labels={'year' : 'Year', 'attacks' : '# of Attacks'})

        fig.update_traces(hovertemplate = '%{text}', textposition = "none")

        fig.update_xaxes(showspikes=True, spikecolor="red", spikemode = 'across', spikethickness=3)

        fig.update_layout(title = {'text' : 'Numbers per Top 10 Groups by Year', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13),
                          xaxis=dict(rangeslider=dict(visible=True)))
        return fig
        
    return fig




@app.callback(
    Output('by-area', 'figure'),
    [Input('geo-agg', 'value'),
     Input('column-agg', 'value'),
     Input('start-year', 'value'),
     Input('end-year', 'value')
    ]
)
def area_bar_update(area, column, start, end, df = df):
    if (start is not None):
        df = df[df['year'] >= start]
    if end is not None:
        df = df[df['year'] <= end]
    
    if area == 'Region':
        if column == 'Attack Type':
            df_filtered = df[['region', 'attack_type', 'wounded', 'killed']][(df['attack_type'] != 'Unknown')] #& condition]
            by_region = df_filtered.groupby(['region', 'attack_type']).agg({'attack_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'attack_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'attack_type' : 'Attack Type'})
            title_text = column

        if column == 'Weapon Type':
            df_filtered = df[['region', 'weapon_type', 'wounded', 'killed']][(df['weapon_type'] != 'Unknown')]
            by_region = df_filtered.groupby(['region', 'weapon_type']).agg({'weapon_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'weapon_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'weapon_type' : column})
            by_region[column] = by_region['Weapon Type'].apply(lambda x: 
                                                                      'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)
            title_text = column
        
        if column == 'Target Type':
            df_filtered = df[['region', 'target_type', 'wounded', 'killed']][(df['target_type'] != 'Unknown')]
            df_filtered['target_type'] = df_filtered['target_type'].apply(get_target_type)
            by_region = df_filtered.groupby(['region', 'target_type']).agg({'target_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'target_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'target_type' : column})
            title_text = column


        if column == 'Terrorist Group':
            df_filtered = df[['region', 'group', 'wounded', 'killed']][(df['group'] != 'Unknown')]
            by_region = df_filtered.groupby(['region', 'group']).agg({'group' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'group' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'group' : column})
            by_region = by_region.sort_values(by = ['region', 'attacks', 'killed'], ascending = [True, False, False]).groupby(['region']).head(10).reset_index(drop = True)
            title_text = 'Top 10 Groups'

        # getting attack type percentages by year
        attack_props = []
        death_props = []
        wounded_props = []
        for year in sorted(pd.unique(by_region['region'])):
            attack_props += by_region[by_region['region'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
            death_props += by_region[by_region['region'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
            wounded_props += by_region[by_region['region'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
        by_region['attack_prop'] = attack_props
        by_region['death_prop'] = death_props
        by_region['wounded_prop'] = wounded_props


            # getting text for each bar
        attack_text = []
        for i in range(len(by_region)):
            attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                               + '<br>' 
                               + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                               + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

        by_region['attack_text'] = attack_text

        fig = px.bar(by_region, x = 'region', y = 'attacks', color = column, template = 'plotly_dark',
                     text = 'attack_text', height = 600, labels={'region' : 'Region', 'attacks' : '# of Attacks'})

        fig.update_traces(hovertemplate = '%{text}', textposition = "none")

        fig.update_xaxes(showspikes=True, spikecolor="red", spikemode = 'across', spikethickness=3)

        fig.update_layout(title = {'text' : 'Numbers per ' + title_text +  ' by Region', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13))

        return fig
    
    
    if area == 'Country':
        if column == 'Attack Type':
            df_filtered = df[['country', 'attack_type', 'wounded', 'killed']][(df['attack_type'] != 'Unknown')]
            by_region = df_filtered.groupby(['country', 'attack_type']).agg({'attack_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'attack_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'attack_type' : 'Attack Type'})
            filtered = by_region.groupby(['country']).sum().reset_index().sort_values(by = 'attacks', ascending = False).head(20)['country'].to_list()
            by_region = by_region[by_region['country'].isin(filtered)]
            title_text = column
            
        if column == 'Weapon Type':
            df_filtered = df[['country', 'weapon_type', 'wounded', 'killed']][(df['weapon_type'] != 'Unknown')]
            by_region = df_filtered.groupby(['country', 'weapon_type']).agg({'weapon_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'weapon_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'weapon_type' : 'Weapon Type'})

            by_region['Weapon Type'] = by_region['Weapon Type'].apply(lambda x: 
                                                                      'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)
            filtered = by_region.groupby(['country']).sum().reset_index().sort_values(by = 'attacks', ascending = False).head(20)['country'].to_list()
            by_region = by_region[by_region['country'].isin(filtered)]
            title_text = column
            
        if column == 'Target Type':
            df_filtered = df[['country', 'target_type', 'wounded', 'killed']][(df['target_type'] != 'Unknown')]
            df_filtered['target_type'] = df_filtered['target_type'].apply(get_target_type)
            by_region = df_filtered.groupby(['country', 'target_type']).agg({'target_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'target_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'target_type' : 'Target Type'})
            filtered = by_region.groupby(['country']).sum().reset_index().sort_values(by = 'attacks', ascending = False).head(20)['country'].to_list()
            by_region = by_region[by_region['country'].isin(filtered)]
            title_text = column
            
        if column == 'Terrorist Group':
            df_filtered = df[['country', 'group', 'wounded', 'killed']][(df['group'] != 'Unknown')]
            by_region = df_filtered.groupby(['country', 'group']).agg({'group' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
            by_region = by_region.rename(columns = {
                'group' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'group' : 'Group'})
            by_region = by_region.sort_values(by = ['country', 'attacks', 'killed'], ascending = [True, False, False]).groupby(['country']).head(10).reset_index(drop = True)

            filtered = by_region.groupby(['country']).sum().reset_index().sort_values(by = 'attacks', ascending = False).head(20)['country'].to_list()
            by_region = by_region[by_region['country'].isin(filtered)]
            title_text = 'Top 10 Groups'
            column = 'Group'
            
        # getting attack type percentages by year
        attack_props = []
        death_props = []
        wounded_props = []
        for year in sorted(pd.unique(by_region['country'])):
            attack_props += by_region[by_region['country'] == year][['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks'].to_list()
            death_props += by_region[by_region['country'] == year][['killed']].apply(lambda x: round(x / sum(x), 4) * 100)['killed'].to_list()
            wounded_props += by_region[by_region['country'] == year][['wounded']].apply(lambda x: round(x / sum(x), 4) * 100)['wounded'].to_list()
        by_region['attack_prop'] = attack_props
        by_region['death_prop'] = death_props
        by_region['wounded_prop'] = wounded_props

        # getting text for each bar
        attack_text = []
        for i in range(len(by_region)):
            attack_text.append(by_region['attacks'].values[i].astype(str) + ' Attacks (' +  by_region['attack_prop'].values[i].astype(float).astype(str)[:4] + '%)'
                               + '<br>' 
                               + by_region['killed'].values[i].astype(str) + ' Killed (' +  by_region['death_prop'].values[i].astype(float).astype(str)[:4] + '%), '
                               + by_region['wounded'].values[i].astype(str) +' Injured (' +  by_region['wounded_prop'].values[i].astype(float).astype(str)[:4] + '%)')

        by_region['attack_text'] = attack_text

        fig = px.bar(by_region, x = 'country', y = 'attacks', color = column, template = 'plotly_dark',
                     text = 'attack_text', height = 600, labels={'country' : 'Country', 'attacks' : '# of Attacks'})

        fig.update_traces(hovertemplate = '%{text}', textposition = "none")

        fig.update_xaxes(showspikes=True, spikecolor="white", spikemode = 'across', spikethickness=3)

        fig.update_layout(title = {'text' : 'Numbers per ' + title_text +  ' by Country (Top 20)', 'x' : 0.45, 'y' : 0.94, 'font_size' : 18}, 
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13))
        
        return fig  
    
    
@app.callback(
    Output('bubble', 'figure'),
    [Input('column-agg', 'value'),
     Input('start-year', 'value'),
     Input('end-year', 'value')
    ]
)
def bubble_update(column, start, end, df = df):
    if (start is not None):
        df = df[df['year'] >= start]
    if end is not None:
        df = df[df['year'] <= end]
        
    if column == 'Attack Type':
        df_filtered = df[df['attack_type'] != 'Unknown'][['year', 'attack_type', 'killed', 'wounded']]
        df_grouped = df_filtered.groupby(['attack_type']).agg({'year' : 'size', 'killed' : 'sum', 
                                                   'wounded' : 'sum'}).reset_index().rename(columns = {'year' : 'attacks'}).astype({'killed' : int, 'wounded' : int})
        df_sorted = df_grouped.sort_values(by = ['attacks'], ascending = False)
        df_sorted['attack_prop'] = df_sorted[['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks']
        df_sorted['attack_size'] = [x * 5 if x < 3 else x for x in df_sorted['attack_prop'].to_list()]
        df_sorted = df_sorted.rename(columns = {'attack_type' : 'Attack Type'})
        
    if column == 'Weapon Type':
        df_filtered = df[df['weapon_type'] != 'Unknown'][['year', 'weapon_type', 'killed', 'wounded']]
        df_grouped = df_filtered.groupby(['weapon_type']).agg({'year' : 'size', 'killed' : 'sum', 
                                                           'wounded' : 'sum'}).reset_index().rename(columns = {'year' : 'attacks'}).astype({'killed' : int, 'wounded' : int})
        df_sorted = df_grouped.sort_values(by = ['attacks'], ascending = False)
        df_sorted['attack_prop'] = df_sorted[['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks']
        df_sorted['attack_size'] = [x * 5 if x < 3 else x for x in df_sorted['attack_prop'].to_list()]
        df_sorted = df_sorted.rename(columns = {'weapon_type' : 'Weapon Type'})
        df_sorted['Weapon Type'] = df_sorted['Weapon Type'].apply(lambda x: 
                                                                  'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)
        
    if column == 'Target Type':
        df_filtered = df[df['target_type'] != 'Unknown'][['year', 'target_type', 'killed', 'wounded']]
        df_filtered['target_type'] = df_filtered['target_type'].apply(get_target_type)
        df_grouped = df_filtered.groupby(['target_type']).agg({'year' : 'size', 'killed' : 'sum', 
                                                           'wounded' : 'sum'}).reset_index().rename(columns = {'year' : 'attacks'}).astype({'killed' : int, 'wounded' : int})
        df_sorted = df_grouped.sort_values(by = ['attacks'], ascending = False)
        df_sorted['attack_prop'] = df_sorted[['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks']
        df_sorted['attack_size'] = [x * 5 if x < 3 else x for x in df_sorted['attack_prop'].to_list()]
        df_sorted = df_sorted.rename(columns = {'target_type' : 'Target Type'})

        
    if column == 'Terrorist Group':
        df_filtered = df[df['group'] != 'Unknown'][['year', 'group', 'killed', 'wounded']]
        df_grouped = df_filtered.groupby(['group']).agg({'year' : 'size', 'killed' : 'sum', 
                                                           'wounded' : 'sum'}).reset_index().rename(columns = {'year' : 'attacks'}).astype({'killed' : int, 'wounded' : int})
        df_sorted = df_grouped.sort_values(by = ['attacks'], ascending = False)[:15]
        df_sorted['attack_prop'] = df_sorted[['attacks']].apply(lambda x: round(x / sum(x), 4) * 100)['attacks']
        df_sorted['attack_size'] = [x * 5 if x < 3 else x for x in df_sorted['attack_prop'].to_list()]
        df_sorted = df_sorted.rename(columns = {'group' : 'Group'})
        column = 'Group'
        
    attack_text = []
    for i in range(len(df_sorted)):
        attack_text.append(df_sorted[column].values[i] + ' (' + df_sorted['attack_prop'].values[i].astype(float).astype(str)[:4]
                           + '%)<br>' + df_sorted['killed'].values[i].astype(str) + ' Killed, '
                           + df_sorted['wounded'].values[i].astype(str) + ' Injured')

    df_sorted['attack_text'] = attack_text

    fig = px.scatter(df_sorted, x = "wounded", y="killed", text = 'attack_text',
                     size="attack_size", color= column, hover_name = column,
                     log_x = True, log_y = True, size_max = 55)

    fig.update_traces(mode='markers', marker=dict(sizemode='area', line_width=3), hovertemplate= column + ': %{text}')

    fig.update_layout(
        title = {'text' : 'Total Number of Attacks v. Total Number of Casualties by ' + column,
                 'x' : 0.44},
        height = 600,
        xaxis=dict(
            title = '# of Attacks',
            gridcolor = 'white',
            gridwidth = 2,
        ),
        yaxis=dict(
            title = '# Casualties',
            gridcolor = 'white',
            gridwidth = 2,
        ),
        paper_bgcolor = 'rgb(243, 243, 243)',
        plot_bgcolor = 'rgb(243, 243, 243)',

        hoverlabel=dict(
            bgcolor = "white",
            font_size=14
        )
    )
    
    return fig



# UTILITY FUNCTION
def get_coordinates(region):
    if region == 'South Asia':
        lat, long, zoom = 25.0376, 76.4563, 3
    elif region == 'Eastern Europe':
        lat, long, zoom = 63.507956, 91.406424, 1.25
    elif region == 'Middle East & North Africa':
        lat, long, zoom =  30.195786, 26.317865, 2.5
    elif region == 'Western Europe':
        lat, long, zoom = 58.256917, 10.694426, 2.5
    elif region == 'Sub-Saharan Africa':
        lat, long, zoom = -2.284266, 13.438434, 2.25
    elif region == 'Central America & Caribbean':
        lat, long, zoom = 15.248292, -78.782581, 3.75
    elif region == 'South America':
        lat, long, zoom = -20.501867, -57.351585, 2
    elif region == 'Central Asia':
        lat, long, zoom = 45.4507, 68.8319, 3.25
    elif region == 'Australasia & Oceania':
        lat, long, zoom = -26.107551, 137.331159, 2.5
    elif region == 'Southeast Asia':
        lat, long, zoom = 7.448598, 110.389588, 3
    elif region == 'North America':
        lat, long, zoom = 54.5260, -105.2551, 1.75
    elif region == 'East Asia':
        lat, long, zoom = 34.159897, 110.762998, 2.5
    return lat, long, zoom


@app.callback(
    Output('geo-country', 'options'),
    [Input('geo-region', 'value')]
)
def update_geo_country(region):
    if region is not None:
        filtered = df[df['region'] == region]
        countries = [{'label':i,'value':i} for i in sorted(filtered["country"].unique())]
        return countries
    else:
        countries = [{'label':i,'value':i} for i in sorted(df["country"].unique())]
        return countries
    
@app.callback(
    Output('geo-end', 'options'),
    [Input('geo-start', 'value')]
)
def update_geo_end(start):
    if start is not None:
        filtered = df[df['year'] >= start]
        years = [{'label':i,'value':i} for i in filtered["year"].unique()]
        return years
    else:
        years = [{'label':i,'value':i} for i in df["year"].unique()]
        return years
 
    
@app.callback(
    Output('geo-start', 'options'),
    [Input('geo-end', 'value')]
)
def update_geo_start(end):
    if end is not None:
        filtered = df[df['year'] <= end]
        years = [{'label':i,'value':i} for i in filtered["year"].unique()]
        return years
    else:
        years = [{'label':i,'value':i} for i in df["year"].unique()]
        return years
    
    
@app.callback(
    Output('geo-chart', 'figure'),
    [Input('geo-type', 'value'),
     Input('agg-type', 'value'),
     Input('geo-region', 'value'),
     Input('geo-start', 'value'),
     Input('geo-end', 'value')
    ]
)
def geochart_update(metric, aggregate, region, start, end, df = df):
    if (start is not None):
        df = df[df['year'] >= start]
    if end is not None:
        df = df[df['year'] <= end]
        
    if aggregate == 'Attack Type':
        df_filtered = df[['country', 'region', 'attack_type', 'wounded', 'killed']][(df['attack_type'] != 'Unknown')]
        by_country = df_filtered.groupby(['country', 'attack_type']).agg({'region' : 'first', 'attack_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_country = by_country.rename(columns = {
            'attack_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'attack_type' : 'Attack Type'})
        color = aggregate
    
    if aggregate == 'Weapon Type':
        df_filtered = df[['country', 'region', 'weapon_type', 'wounded', 'killed']][(df['weapon_type'] != 'Unknown')]
        by_country = df_filtered.groupby(['country', 'weapon_type']).agg({'region' : 'first', 'weapon_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_country = by_country.rename(columns = {
            'weapon_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'weapon_type' : 'Weapon Type'})
        by_country['Weapon Type'] = by_country['Weapon Type'].apply(lambda x: 
                                                                  'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)
        color = aggregate
        
    if aggregate == 'Target Type':
        df_filtered = df[['country', 'region', 'target_type', 'wounded', 'killed']][(df['target_type'] != 'Unknown')]
        df_filtered['target_type'] = df_filtered['target_type'].apply(get_target_type)
        by_country = df_filtered.groupby(['country', 'target_type']).agg({'region' : 'first', 'target_type' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_country = by_country.rename(columns = {
            'target_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'target_type' : 'Target Type'})
        color = aggregate
        
    if aggregate == 'Terrorist Group':
        df_filtered = df[['country', 'region', 'group', 'wounded', 'killed']][(df['group'] != 'Unknown')]
        by_country = df_filtered.groupby(['country', 'group']).agg({'region' : 'first', 'group' : 'size', 'killed' : 'sum', 'wounded' : 'sum'})
        by_country = by_country.rename(columns = {
            'group' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'group' : 'Group'})     
        color = 'Group'
        
        
    if metric == 'Most Common':
        by_metric = by_country.sort_values(by = ['country', 'attacks'], ascending = [True, False]).groupby(['country']).head(1).reset_index(drop = True)
    else:
        by_metric = by_country.sort_values(by = ['country', 'killed'], ascending = [True, False]).groupby(['country']).head(1).reset_index(drop = True)
        
    # getting text for each bar
    attack_text = []
    for i in range(len(by_metric)):
        attack_text.append(by_metric['attacks'].values[i].astype(str) + ' Attacks, ' #+ '<br>' 
                           + by_metric['killed'].values[i].astype(str) + ' Killed, ' #+ '<br>' 
                           + by_metric['wounded'].values[i].astype(str) +' Injured')

    by_metric['Info'] = attack_text

    w_geo = by_metric.merge(geo_all, how = 'inner', on = 'country').rename(columns = {'country' : 'Country'})
    w_geo = w_geo[w_geo['region'] == region] 

    geo_data = geo_all[geo_all['country'].isin(w_geo['Country'].to_list())]
    geojson = json.loads(geo_data.to_json())

    coordinates = get_coordinates(region)
    lat, long, zoom = coordinates[0], coordinates[1], coordinates[2]

    fig = px.choropleth_mapbox(w_geo, geojson = geojson, color = color,
                               locations = "Country", featureidkey = "properties.country",
                               hover_data = ["Info"],
                               center = {"lat" : lat, "lon" : long}, mapbox_style = "carto-positron", zoom = zoom)
    fig.update_layout(margin={"r" : 0,"t" : 0,"l" : 0,"b" : 0}, height = 550,  
                      legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01,bgcolor="black", bordercolor="white",
                                  borderwidth=1.5, font=dict(color="white")))
    return fig



@app.callback(
    Output('geo-chart2', 'figure'),
    [Input('geo-type', 'value'),
     Input('agg-type', 'value'),
     Input('geo-region', 'value'),
     Input('geo-country', 'value'),
     Input('geo-start', 'value'),
     Input('geo-end', 'value')
    ]
)
def geochart2_update(metric, aggregate, region, country, start, end, df = data_scatter):
    if (start is not None):
        df = df[df['year'] >= start]
    if end is not None:
        df = df[df['year'] <= end]
        
    if aggregate == 'Attack Type':
        data = df[df['attack_type'] != 'Unknown']
        by_city = data.groupby(['country', 'city', 'attack_type']).agg({'region' : 'first', 'latitude' : 'first', 'longitude' : 'first', 'attack_type' : 'size', 
                                                                        'killed' : 'sum', 'wounded' : 'sum'})
        by_city = by_city.rename(columns = {
            'attack_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'attack_type' : 'Attack Type'})
        color = aggregate
        
    if aggregate == 'Weapon Type':
        data = df[df['weapon_type'] != 'Unknown']
        by_city = data.groupby(['country', 'city', 'weapon_type']).agg({'region' : 'first', 'latitude' : 'first', 'longitude' : 'first', 'weapon_type' : 'size', 
                                                                        'killed' : 'sum', 'wounded' : 'sum'})
        by_city = by_city.rename(columns = {
            'weapon_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'weapon_type' : 'Weapon Type'})
        by_city['Weapon Type'] = by_city['Weapon Type'].apply(lambda x: 
                                                                  'Vehicle (Non-Explosive)' if x == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)' else x)  
        color = aggregate
        
    if aggregate == 'Target Type':
        data = df[df['target_type'] != 'Unknown']
        data['target_type'] = data['target_type'].apply(get_target_type)
        by_city = data.groupby(['country', 'city', 'target_type']).agg({'region' : 'first', 'latitude' : 'first', 'longitude' : 'first', 'target_type' : 'size', 
                                                                        'killed' : 'sum', 'wounded' : 'sum'})
        by_city = by_city.rename(columns = {
            'target_type' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'target_type' : 'Target Type'})
        color = aggregate
    
    if aggregate == 'Terrorist Group':
        data = df[df['group'] != 'Unknown']
        by_city = data.groupby(['country', 'city', 'group']).agg({'region' : 'first', 'latitude' : 'first', 'longitude' : 'first', 'group' : 'size', 
                                                                        'killed' : 'sum', 'wounded' : 'sum'})
        by_city = by_city.rename(columns = {
            'group' : 'attacks'}).reset_index().astype({'killed' : int, 'wounded' : int}).rename(columns = {'group' : 'Group'})
        color = 'Group'

    # for the default region. when region is not none
    by_metric = by_city[by_city['region'] == region]
    coordinates = get_coordinates(region)
    lat, long, zoom = coordinates[0], coordinates[1], coordinates[2]
    
    if country is not None:
        by_metric = by_city[by_city['country'] == country]
        coordinates = country2coordinates[country2coordinates['country'] == country]
        lat, long, zoom = coordinates.latitude.values[0], coordinates.longitude.values[0], 3.5
         
    if metric == 'Most Common':
        by_metric = by_metric.sort_values(by = ['country', 'city', 'attacks'], ascending = [True, True, False]).groupby(['country', 'city']).head(1).reset_index(drop = True)
    else:
        by_metric = by_metric.sort_values(by = ['country', 'city', 'killed'], ascending = [True, True, False]).groupby(['country', 'city']).head(1).reset_index(drop = True)
    
    # getting text for each bar
    attack_text = []
    for i in range(len(by_metric)):
        attack_text.append(by_metric['attacks'].values[i].astype(str) + ' Attacks, ' 
                           + by_metric['killed'].values[i].astype(str) + ' Killed, '
                           + by_metric['wounded'].values[i].astype(str) +' Injured')
    by_metric['Info'] = attack_text

    fig = px.scatter_mapbox(by_metric,
                            lat= 'latitude',
                            lon= 'longitude',
                            mapbox_style = "carto-darkmatter",
                            color = color,
                            hover_name = 'city',
                            hover_data = {'latitude' : False, 'longitude' : False, 'Info' : True},
                            template = 'plotly_dark',
                            zoom=3,
                            height = 550)
    
    fig.update_layout(margin={"r" : 0,"t" : 0,"l" : 0,"b" : 0}, height = 550, mapbox=dict(
            center=dict(lat=lat, lon=long), pitch=0, zoom = zoom), legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01,bgcolor="black", bordercolor="white",
                                  borderwidth=2.5, font=dict(color="white")))
    
    return fig



if __name__ == '__main__':
    app.run_server(debug = True)