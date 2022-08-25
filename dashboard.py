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
from folium.plugins import MarkerCluster
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, State

pd.set_option('display.max_columns', None)

# Reading in the data with the proper encoding
data = pd.read_csv('gt_data.csv', encoding='ISO-8859-1')


columns = ['iyear', 'imonth', 'iday', 'country_txt', 'region_txt', 'provstate','city', 'latitude', 'longitude', 
           'suicide', 'attacktype1_txt', 'targtype1_txt', 'target1', 'gname', 'motive', 'weaptype1_txt', 'propvalue', 'nkill', 'nwound']

df = data[columns].rename(columns = {'iyear':'year', 'imonth':'month', 'iday':'day', 'country_txt':'country', 'region_txt':'region', 'provstate':'state',
                'attacktype1_txt':'attack_type', 'target1':'target', 'nkill':'killed', 'nwound':'wounded', 'gname':'group',
                'targtype1_txt':'target_type', 'weaptype1_txt':'weapon_type', 'propvalue' : 'property_value'})


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
                        style = {'fontSize' : 55, 'font-family' : 'monospace', 'font-weight' : 'bold', 'textAlign' : 'center', 'marginTop' : 15, 'marginBottom' : 15}
                       ),
                
                html.P(
                    children = 'This dashboard contains a wide variety of analsis on global terrorism over the last 50 years, with the main features being plots and charts describing the data. The goal is to try to better understand methods of terror, groups behind these attacks, where these attacks are occuring, and the numbers associated with those attacks.',
                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'margin-left': '30px', 'margin-right' : '30px', 'marginBottom' : 15}
                )
            ]
        ),
        
        html.H4('High-Level Data Overview',
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
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '50px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a region',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'region',
                                    options = pd.unique(df['region']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-left': '20px', 'margin-right' : '20px'}
                        ), 
                        
                        html.Div(
                            children = [
                                html.P(
                                    children = 'Select a country',
                                    style = {'fontSize' : 17, 'font-family' : 'monospace', 'textAlign' : 'center', 'color' : 'black', 'marginBottom' : 10}
                                ),

                                dcc.Dropdown(
                                    id = 'country',
                                    options = pd.unique(df['country']),
                                    value = None,
                                    search_value = '',
                                    style = {'marginBottom' : 5, 'font-family' : 'monospace', 'fontSize' : 16}
                                )
                            ], style={'display': 'inline-block', 'width': '50%', 'margin-right' : '50px'}
                        ), 
                        
                    ], style = dict(display='flex')
                ),
                
                html.Div(
                    children = [
                        dcc.Graph(id = 'stacked-bar', style={'marginTop' : 10, 'margin-left': '95px', 'width' : '90%'})
                    ]
                )   
            ]
        )
    ]
)



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
        
    if (country is not None) and region is None:
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
                      hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13)) 

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
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13)) 
        return fig
    
    if column == 'Target Type': 
        df_filtered = df[['year', 'target_type', 'wounded', 'killed']][(df['attack_type'] != 'Unknown')]
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
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "white", font_color = 'black', font_size = 13)) 
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
                          hovermode = 'x unified', hoverlabel=dict(bgcolor = "black", font_color = 'white', font_size=13)) 
        return fig
        
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)