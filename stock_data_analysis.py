# -*- coding: utf-8 -*-
"""Stock_Data_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZSLfnZYYfiIWSky8H02dDuzY4nqzq4Fc
"""

!pip install yfinance
!pip install bs4

#importing libraries
import pandas as pd
import numpy as np

import yfinance as yf
import requests
from bs4 import BeautifulSoup

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_graph(stock_data, revenue_data, stock):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Historical Share Price ($)", "Historical Revenue ($)"), vertical_spacing = .5)
    fig.add_trace(go.Scatter(x=pd.to_datetime(stock_data.Date, infer_datetime_format=True), y=stock_data.Close.astype("float"), name="Share Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=pd.to_datetime(revenue_data.Date, infer_datetime_format=True), y=revenue_data.Revenue.astype("float"), name="Revenue"), row=2, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Revenue ($ Millions)", row=2, col=1)
    fig.update_layout(showlegend=False, height=1000, title=stock, xaxis_rangeslider_visible=True)
    fig.show()

# Using the Ticker function to create a ticker object.
# ticker symbol of tesla is TSLA
tesla_data = yf.Ticker('TSLA')

# history function helps to extract stock information.
# setting period parameter to max to get information for the maximum amount of time.
tsla_data = tesla_data.history(period='max')

# Resetting the index
tsla_data.reset_index(inplace=True)

# display the first five rows
tsla_data.head()

from google.colab import files
tsla_data.to_csv('data.csv') 
files.download('data.csv')
data = pd.read_csv('/content/data.csv')

# using requests library to download the webpage
url='https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue'

# Save the text of the response
html_text = requests.get(url).text

# Parse the html data using beautiful_soup.
soup=BeautifulSoup(html_text, 'html5lib')

# Using beautiful soup extract the table with Tesla Quarterly Revenue.
# creating new dataframe
tsla_revenue = pd.DataFrame(columns=["Date", "Revenue"])

tables = soup.find_all('table')
table_index=0

for index, table in enumerate(tables):
    if ('Tesla Quarterly Revenue'in str(table)):
        table_index=index
        
for row in tables[table_index].tbody.find_all("tr"):
    col = row.find_all("td")
    if (col!=[]):
        date =col[0].text
        # to remove comma and dollar sign
        revenue =col[1].text.replace("$", "").replace(",", "")
        tsla_revenue=tsla_revenue.append({'Date':date,'Revenue':revenue},
                                           ignore_index=True)

# displaying dataframe
tsla_revenue

tsla_revenue = tsla_revenue[tsla_revenue['Revenue']!='']
tsla_revenue

plot_graph(tsla_data, tsla_revenue, 'Tesla Historical Share Price & Revenue')

#Fisher Transformation
from matplotlib import pyplot as plt
import math
Op = data['Open']
Hh = data['High']
Lw = data['Low']
Ce = data['Close']
date = data['Date']
Avg= (Lw + Hh)/2
max= np.max(Avg)
min= np.min(Avg)
S = np.zeros((Avg.size))

for i in range(1,Avg.size):
      S[i] = 0.33*2*((Avg[i]-min)/(max-min) -0.5)+ S[i-1]*0.67
fisch_value= np.zeros((S.size))
for i in range(1,S.size):
      fisch_value[i]=0.5*math.log((1+S[i])/(1-S[i])) + 0.5*fisch_value[i-1]
plt.plot(date, fisch_value, label="Fischer Value")



plt.legend()
plt.title('Fisher value with opening and closing values')
plt.xlabel('Dates')
plt.ylabel('Prices over time')
plt.savefig("Fisher.png")
plt.show()

#Average Directional Index (ADI)

plusDM = np.zeros((Op.size))
minusDM = np.zeros((Op.size))

for i in range(1, len(Op)):
 plusDM[i]= Hh[i]-Hh[i-1]
 if plusDM[i] < 0:
    plusDM[i]=0

 minusDM[i]=Lw[i-1]-Lw[i]
 if minusDM[i] < 0:
    minusDM[i] = 0

 if plusDM[i]>minusDM[i]:
   minusDM[i]=0
 elif plusDM[i]<minusDM[i]: 
   plusDM[i] =0

Delta = np.zeros((Op.size))
A=np.zeros((Op.size))
B= np.zeros((Op.size))
TR= np.zeros((Op.size))

for i in range(1,Op.size):
    Delta[i]= Hh[i]-Lw[i]
    A[i] = Hh[i]-Ce[i-1]
    B[i] = Ce[i-1]-Lw[i] 

TR= np.maximum(A,B,Delta)

plusDI= ((plusDM)/(TR))*100
minusDI=((minusDM)/(TR))*100


DIdiff= abs(plusDI - minusDI)
DIsum= abs(plusDI + minusDI)

DX = np.zeros(Op.size)

for i in range(0,Op.size):
    if DIsum[i]==0:
      DX[i]=0
    else:
      DX[i]= (DIdiff[i]/DIsum[i])*100

from matplotlib import rcParams
rcParams['figure.figsize'] = 500,40
plt.plot(date, DX, label="Average Directional Index")
plt.plot(date, plusDI, label="Positive Directional Index")
plt.plot(date, minusDI, label="Negative Directional Index")

plt.legend()
plt.title('ADX with Negative and Positive Directional values')
plt.xlabel('Dates')
plt.ylabel('Prices over time')
plt.savefig("ADI.png")
plt.show()

import numpy as np  
import pandas as pd  
from pandas_datareader import data as wb  
import matplotlib.pyplot as plt  
from scipy.stats import norm

timesteps = 30
starting_price = 600
volatility = 2
max_simulations = 1000


simulation_df = pd.DataFrame()
for x in range(max_simulations):
  price_lists = []
  price = starting_price
  price_lists.append(price)
  count=0
   
  for y in range(timesteps):
    if count==29:
      break
    price= price_lists[count]*(1+(np.random.normal(0,volatility))/100)
    price_lists.append(price)
    count+=1
  simulation_df[x]=price_lists
fig=plt.figure()
plt.plot(simulation_df)
plt.xlabel("days")
plt.ylabel("prices")
fig.suptitle('Monte Carlo Simulation')
plt.savefig("monte_carlo.png")

