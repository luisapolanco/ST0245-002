import geopandas as gpd
import pandas as pd
import sys
from heapq import heapify, heappush
import matplotlib.pyplot as plt
import networkx as nx
from shapely import wkt

edges = pd.read_csv('/content/calles_de_medellin_con_acoso.csv', sep=';')
edges['geometry'] = edges['geometry'].apply(wkt.loads)
edges = gpd.GeoDataFrame(edges)

area = pd.read_csv('/content/poligono_de_medellin.csv', sep=';')
area['geometry'] = area['geometry'].apply(wkt.loads)
area = gpd.GeoDataFrame(area)

#AVERAGE OF HARASSMENT RISK IN FIELDS WITH N/A

edges['harassmentRisk'].fillna(edges['harassmentRisk'].mean(), inplace = True)
edges["harassmentRisk * length"] = edges["harassmentRisk"] * edges["length"]
edges

#ALL THE STREETS WITH TWO DIRECTIONS

two_directions = edges.rename(columns = {'origin': 'destination', 'destination': 'origin'})
two_directions = two_directions[two_directions['oneway'] == True]
two_directions = two_directions[['name', 'origin', 'destination', 'length', 'oneway', 'harassmentRisk', 'geometry','harassmentRisk * length' ]]

#JOIN BOTH DATAFRAMES

two_directions = two_directions[['name', 'origin', 'destination','length',  'harassmentRisk', 'geometry', 'harassmentRisk * length' ]]
edgesWithoutOneWay = edges[['name', 'origin', 'destination','length',  'harassmentRisk', 'geometry', 'harassmentRisk * length']]

data = edgesWithoutOneWay.to_numpy().tolist() + two_directions.to_numpy().tolist()

data_pandas = [edgesWithoutOneWay, two_directions]

streets = pd.concat(data_pandas)

streets 

#CONVERT DATAFRAME TO A DICTIONARY

hash_table = dict()

for elemento in range (len(data)):
  if data[elemento][1] in hash_table:
    info_list = [data[elemento][2], data[elemento][3], data[elemento][4], data[elemento][6]]
    hash_table[data[elemento][1]].append(info_list)
  else:
    info_list = [data[elemento][2], data[elemento][3], data[elemento][4], data[elemento][6]] 
    hash_table[data[elemento][1]]= [info_list]



#IMPLEMENTATION OF THE ALGORITHM WITH NETWORKX LIBRARY

##THE SHORTEST PATH

shortPathWithLessHarassment = nx.from_pandas_edgelist(edges, source="origin", target="destination", edge_attr="harassmentRisk * length")

djk_path = nx.dijkstra_path(shortPathWithLessHarassment, source='(-75.5762232, 6.266327)', target='(-75.5832559, 6.2601878)', weight=True)

#DRAW SHORT PATH WITH TOTAL DISTANCE AND AVERAGE OF HARASSMENT RISK 

listLengthOrigins = []
for i in range(len(djk_path) -2):
  listLengthOrigins.append(djk_path[i])

listLengthDestinations = []
for i in range(1, len(djk_path) -1):
  listLengthDestinations.append(djk_path[i])

totalDistance = 0
totalhrisk = 0

for i in range( len(listLengthOrigins)):
  element = streets[(streets['origin'] == listLengthOrigins[i]) & (streets['destination'] == listLengthDestinations[i])]
  length = element['length'].values
  hrisk = element['harassmentRisk'].values
  totalDistance += length
  totalhrisk  += hrisk
  

print("Menor distancia: " , totalDistance)
print("Menor riesgo de acoso: " , totalhrisk/len(listLengthOrigins))


fig, ax = plt.subplots(figsize =(12,8))

area.plot(ax=ax, facecolor='black')

edges.plot(ax=ax, linewidth=1, edgecolor='dimgray')

for i in range(len(listLengthOrigins)):
  dist = edges[(edges['origin'] == listLengthOrigins[i]) & (edges['destination'] == listLengthDestinations[i])]
  dist.plot(ax = ax, linewidth=5, edgecolor= 'yellow')

plt.tight_layout()
plt.show()


#IMPLEMENTATION OF THE DIJKSTRA ALGORITHM

#NOTE: THIS ALGORITHM CURRENTLY IS NOT FUNCTIONAL BECAUSE
# IT DOESN'T SEARCH BETWEEN ALL THE POSSIBLE DESTINATIONS,
# BUT IT TRIES TO FIND THE WAY FROM THE DERIVATIVES OF THE ORIGIN.

def dijkstra(hash_data, origin, destination):
    inf = sys.maxsize
    node_data = dict()
    for i in hash_data.keys():
        node_data[i] = {'cost': inf, 'pred': []}

    node_data[origin]['cost'] = 0
    visited = []
    temp = origin
    for i in range(len(hash_data) - 1):
        if temp not in visited:
            visited.append(temp)
            min_heap = []
            for j in hash_data[temp]:

                if j[0] not in visited:
                    cost = node_data[temp]['cost'] + j[1]
                    if cost < node_data[j[0]]['cost']:
                        node_data[j[0]]['cost'] = cost
                        node_data[j[0]]['pred'] = node_data[temp]['pred'] + list([temp])
                        print(node_data[j[0]]['pred'])
                    heappush(min_heap, (node_data[j[0]]['cost'], j[0]))
        heapify(min_heap)
        if min_heap == []:
            break
        else:
            temp = min_heap[0][1]
    print("Shortest distance: " + str(node_data[destination]['cost']))
    print("Shortest path: " + str(node_data[destination]['pred'] + list([destination])))