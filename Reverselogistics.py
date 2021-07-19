
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import googlemaps

import json
import geopandas as gpd
import pyproj
import plotly.graph_objs as go

st.title('Reverse Logistics')
st.markdown('Welcome to **Reverse Logistis** app, here we will try to make your company save C02 costs and money')

st.header('Write tender template file route')

file_root = st.text_area("File route", height=20)
# excel table read
# file_root = 'C:/Users/ramon/Anaconda3/envs/TFM2/TFM/Reverse_Logistics_Template.xlsx'
tender = pd.read_excel(file_root)
tender.head()


# Side Bar


st.sidebar.header('Reverse Logistics Selections')


#Countries SB
country_exports = tender.groupby('Origin_Country').sum()
country_exports = country_exports.rename({'Volume': 'Export_Volume'}, axis=1)
country_imports = tender.groupby('Destination_Country').sum()
country_imports = country_imports.rename({'Volume': 'Import_Volume'}, axis=1)
Countries = pd.concat([country_exports, country_imports], axis = 1, join = 'inner')
Countries.reset_index(level=0, inplace=True)
Countries = Countries.rename({'index': 'Country'}, axis=1)
country_selection = st.sidebar.selectbox('Country', sorted(Countries['Country']) )

#Port SB
port_exports = tender[tender['Origin_Country']==country_selection].groupby('Origin_Port').sum()
port_exports = port_exports.rename({'Volume': 'Export_Volume'}, axis=1)
port_imports = tender[tender['Destination_Country']==country_selection].groupby('Destination_Port').sum()
port_imports = port_imports.rename({'Volume': 'Import_Volume'}, axis=1)
Ports = pd.concat([port_exports, port_imports], axis = 1, join = 'inner')
Ports.reset_index(level=0, inplace=True)
Ports = Ports.rename({'index': 'Port'}, axis=1)
port_selection = st.sidebar.selectbox('Port', sorted(Ports['Port']) )

#City SB

city_exports = tender[(tender['Origin_Country']==country_selection) & (tender['Origin_Port']==port_selection)].groupby('Origin_City').sum()
city_imports = tender[(tender['Destination_Country']==country_selection) & (tender['Destination_Port']==port_selection)].groupby('Destination_City').sum()
Cities = pd.concat([city_exports, city_imports], axis = 1, join = 'inner')
Cities.reset_index(level=0, inplace=True)
Cities = Cities.rename({'index': 'City'}, axis = 1)
city_selection = st.sidebar.selectbox('City', sorted(Cities['City']) )


#Customer Histogram
st.title('Volume by Customer')
volume_by_customer = tender.groupby("Customer").sum()
volume_by_customer.reset_index(level=0, inplace=True)
x = volume_by_customer['Customer'].values
y = volume_by_customer['Volume'].values
fig, ax = plt.subplots(figsize=(7,6))
plt.bar(x, y)
plt.xlabel("Customer")
plt.ylabel("Sum of Volume")
plt.title("Tender Volume by Customer")
st.pyplot(fig)



#TOP 10 Exporting Countries
st.title('TOP 10 Exporting countries')
volume_by_origin = tender.groupby("Origin_Country").sum().sort_values('Volume', ascending=False)
volume_by_origin = volume_by_origin.head(10)
volume_by_origin.reset_index(level=0, inplace=True)
x = volume_by_origin['Origin_Country'].values
y = volume_by_origin['Volume'].values
fig, ax = plt.subplots(figsize=(7,6))
plt.bar(x, y)
plt.xlabel("Origin Cuountry")
plt.ylabel("Sum of Volume")
plt.title("Tender Volume by Origin Country")
st.pyplot(fig)


#TOP 10 Importing Countries
st.title('TOP 10 Importing countries')
volume_by_destination = tender.groupby("Destination_Country").sum().sort_values('Volume', ascending=False)
volume_by_destination = volume_by_destination.head(10)
volume_by_destination.reset_index(level=0, inplace=True)
x = volume_by_destination['Destination_Country'].values
y = volume_by_destination['Volume'].values
fig, ax = plt.subplots(figsize=(7,6))
plt.bar(x, y)
plt.xlabel("Destination_Cuountry")
plt.ylabel("Sum of Volume")
plt.title("Tender Volume by Destination Country")
st.pyplot(fig)

#Exports & Imports
st.title('Imports and Exports from selection')

exports_with_imports = Countries[Countries['Country']==country_selection]
fig, ax = plt.subplots()
exports_with_imports.plot.bar(x = 'Country', y = ['Export_Volume', 'Import_Volume'], rot = 40, ax = ax)
for p in ax.patches: 
    ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()))

st.pyplot(fig)

#Ports with Imports and Exports Values
st.title('Imports and Exports from selection by Port')
#let's create 2 data frames with the selected Country
reverse_logistics_origin = tender[tender['Origin_Country']==country_selection]
reverse_logistics_destination = tender[tender['Destination_Country']==country_selection]

#Creating 2 dataframes for imports and exports grouped by ports
reverse_ports_Origin = reverse_logistics_origin.groupby(['Origin_Port']).sum()
reverse_ports_Origin = reverse_ports_Origin.rename({'Volume': 'Export_Volume'}, axis=1)

reverse_ports_Destination = reverse_logistics_destination.groupby(['Destination_Port']).sum()
reverse_ports_Destination = reverse_ports_Destination.rename({'Volume': 'Import_Volume'}, axis=1)

#Combining both dataframes
total_by_port = pd.concat([reverse_ports_Origin, reverse_ports_Destination], axis=1, join='inner')
total_by_port.reset_index(level=0, inplace=True)
total_by_port = total_by_port.rename({'index': 'Port'}, axis=1)

# Let's see a graph
st.title('Imports and Exports from City') 
fig, ax = plt.subplots()
total_by_port.plot.bar(x = 'Port', y = ['Export_Volume', 'Import_Volume'], rot = 40, ax = ax)
for p in ax.patches: 
    ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()))
st.pyplot(fig)

#The same for cities
reverse_logistics_origin_city = tender[(tender['Origin_Country']==country_selection) & (tender['Origin_Port']==port_selection)]
reverse_logistics_destination_city = tender[(tender['Destination_Country']==country_selection) & (tender['Destination_Port']==port_selection)]
reverse_cities_Origin = reverse_logistics_origin_city.groupby(['Origin_City']).sum()
reverse_cities_Origin = reverse_cities_Origin.rename({'Volume': 'Export_Volume'}, axis=1)
reverse_cities_Destination = reverse_logistics_destination_city.groupby(['Destination_City']).sum()
reverse_cities_Destination = reverse_cities_Destination.rename({'Volume': 'Import_Volume'}, axis=1)

total_by_city = pd.concat([reverse_cities_Origin, reverse_cities_Destination], axis=1, join='inner')
total_by_city.reset_index(level=0, inplace=True)
total_by_city = total_by_city.rename({'index': 'City'}, axis=1)



# Let's see a graph again for cities
fig, ax = plt.subplots()
total_by_city.plot.bar(x = 'City', y = ['Export_Volume', 'Import_Volume'], rot = 40, ax = ax)
for p in ax.patches: 
    ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()))
st.pyplot(fig)


#REVERSE LOGISTICS OUTPUT

#Let's create one dataframe with the final rows to be combined

st.title('REVERSE LOGISTICS OUTPUT')
st.text('Lanes to be combined')
Origins = tender[tender['Origin_City']==city_selection]
Origins = Origins[Origins['Origin_Port']==port_selection]

Destinations = tender[tender['Destination_City']==city_selection]
Destinations = Destinations[Destinations['Destination_Port']==port_selection]

final_reverse = Origins.merge(Destinations, how='outer')
st.dataframe(final_reverse)


#The total amount to combine in this case will be the minimum volume from the selected city or to the selected city
st.text('Containers to be combined (single count)')
volume_to_reverse = final_reverse[final_reverse['Origin_City']==city_selection]
total_export = volume_to_reverse['Volume'].sum()
volume_to_reverse = final_reverse[final_reverse['Destination_City']==city_selection]
total_import = volume_to_reverse['Volume'].sum()
total_to_combine = (total_export, total_import)
final_number = min(total_to_combine)
final_number


selected_city1 = city_selection + ', ' + country_selection
selected_port1 = port_selection + ', ' + ' Port, ' + country_selection

# Let's find the coordenates
API_KEY = 'AIzaSyCb3tyT9hP3P5dpMSuOSJ51p_4i5d7-SqM'
map_client = googlemaps.Client(API_KEY)


origin_location = (map_client.geocode(selected_city1)[0]['geometry']['location']['lat'], map_client.geocode(selected_city1)[0]['geometry']['location']['lng'])
port_location = (map_client.geocode(selected_port1)[0]['geometry']['location']['lat'], map_client.geocode(selected_port1)[0]['geometry']['location']['lng'])

#Quick function to convert miles to km:

def convert_distance(miles):
    km = miles * 1.6 
    return km

total_distance1 = map_client.directions(origin_location, port_location, mode='driving')
total_distance2 = total_distance1[0]['legs'][0]['distance']['text']
total_distance3 = [int(s) for s in total_distance2.split() if s.isdigit()]
total_distance = total_distance3[0]
total_distance = convert_distance(total_distance)

#One Way trips from city to port and viceversa
st.text('One Way trips from city to port and viceversa')
trips = final_number * 4
trips

#Trips with reverse_logistics
st.text('Trips with reverse_logistics')
trips_reverse = trips/2
trips_reverse

#Km saved
st.text('KM saved')
km_saved = trips_reverse
km_saved

#C02 without applying reverse
st.text('C02 not applying RL')
C02 = trips*total_distance
C02

st.text('C02 saved applying RL')
C02_saved = C02/2
C02_saved

st.text('Summary')
final = pd.DataFrame(columns=['C02 gr saved', 'KM saved'])
final.loc[0] = [C02_saved, km_saved]
final