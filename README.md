# Global Terrorism Over The Last 50 Years

### Context
The Global Terrorism Database (GTD) is an open-source database including information on terrorist attacks around the world from 1970 through 2017. The GTD includes systematic data on domestic as well as international terrorist incidents that have occurred during this time period and now includes more than 180,000 attacks. The database is maintained by researchers at the National Consortium for the Study of Terrorism and Responses to Terrorism (START), headquartered at the University of Maryland.


### Objective
The main two goals of this analytics project are:
  1. Getting a data-driven understanding of global terrorism from the last five decades
  2. Building new and strengthening existing data visualization skills, with an emphasis on geospatial charts

**To see the full notebook in action, since it doesn't render within the repo, click [HERE](https://nbviewer.org/github/tenzin-choezin/global-terrorism/blob/main/analysis.ipynb)!**
  
### Analytics Dashboard Preview
![](homepage/homepage.gif)
![](homepage/homepage2.png)
![](homepage/homepage3.png)
![](homepage/homepage4.png)


## Usage
### Install Dependencies

```shell
import numpy as np  
import pandas as pd 
import warnings
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import geopandas as gpd
import json
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, State
```

You probably want to install them with `pip` or `conda`.


### Getting the data
The main dataset is too large to include in this repo. To find it, click [HERE](https://www.kaggle.com/datasets/START-UMD/gtd?datasetId=504&searchQuery=plotly) to download and upload to your own workspace! For the geospatial data files used, click [here](https://github.com/tenzin-choezin/global-terrorism/tree/main/data). It's stoerd in the **data** folder in this repo.

### Running the application
```shell
python dashboard.py
```

-----------------
<p align="left">
    <img src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white">
    <img src="https://img.shields.io/badge/numpy-%23F7931E.svg?style=for-the-badge&logo=numpy&logoColor=white">
    <img src="https://img.shields.io/badge/plotly-%037FFC.svg?style=for-the-badge&logo=plotly&logoColor=white">
    <img src="https://img.shields.io/badge/vscode-%23190458.svg?style=for-the-badge&logo=visualstudio&logoColor=white">
     <img src="https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white">
    <img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white">
</p>

### Technologies used
* Python libraries - numpy, pandas, plotly, dash, geopandas, folium
* Version control - git 

### Tools and Services : 
* IDE - Vs code, Jupyter Lab
* Application deployment - Local server
* Code repository - GitHub
-----------------
