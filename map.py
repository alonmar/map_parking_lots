# Import necessary libraries
import geopandas as gpd
import folium
from folium.plugins import Draw, HeatMap, Geocoder
from streamlit_folium import folium_static as st_folium
import streamlit as st
from folium import GeoJsonPopup
from utils import get_buffer

# Set Streamlit page layout to wide
st.set_page_config(layout="wide")

# Load restaurant data from a GeoJSON file
gdf = gpd.read_file("miami_restaurants.geojson")

# Load parking lot data from a GeoJSON file
lots_geo = gpd.read_file("puntos.geojson")

# Process parking lots
lots_geo["id"] = range(1, len(lots_geo) + 1)

# Calculate environmental value by creating a buffer around parking lots
lots_geo_buffer = get_buffer(lots_geo, radio=500)

# Perform spatial join to count restaurants within the buffer zones
conteo_restaurantes_inside_lotes = gpd.sjoin(
    lots_geo_buffer, gdf, how="inner", predicate="intersects"
)

# Group by parking lot ID and count the number of restaurants
conteo_restaurantes_lotes = (
    conteo_restaurantes_inside_lotes.groupby("id").size().reset_index()
)
conteo_restaurantes_lotes.columns = ["id", "restaurantes"]

# Merge the count data back into the parking lot GeoDataFrame
lots_geo = lots_geo.merge(conteo_restaurantes_lotes, on="id", how="left")
lots_geo["Value"] = lots_geo["restaurantes"] * 1700

# Assign colors and classes based on the number of restaurants
lots_geo["color"] = [
    "green" if i > 20 else "red" if i < 10 else "blue" for i in lots_geo["restaurantes"]
]
lots_geo["Class"] = [
    "Top" if i > 20 else "Bottom" if i < 10 else "Middle"
    for i in lots_geo["restaurantes"]
]

# Create a popup for the parking lots
popup = GeoJsonPopup(
    fields=["id", "Class", "Value"],
    aliases=["id_parking_lot: ", "Class: ", "Value: "],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

# Load new parking lot data from a GeoJSON string
new_lots = """{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-80.136852,25.792318]}},{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-80.222511,25.764958]}},{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[-80.199509,25.799737]}}]}"""
new_lots_geo = gpd.read_file(new_lots)

# Process new parking lots
new_lots_geo["id"] = range(1, len(new_lots_geo) + 1)
new_lots_geo["latitude"] = new_lots_geo.geometry.y
new_lots_geo["longitude"] = new_lots_geo.geometry.x

# Calculate environmental value for new parking lots
new_lots_geo_buffer = get_buffer(new_lots_geo, radio=500)

# Perform spatial join to count restaurants within the buffer zones of new lots
conteo_restaurantes_inside_nuevos_lotes = gpd.sjoin(
    new_lots_geo_buffer, gdf, how="inner", predicate="intersects"
)
conteo_restaurantes_newlotes = (
    conteo_restaurantes_inside_nuevos_lotes.groupby("id").size().reset_index()
)
conteo_restaurantes_newlotes.columns = ["id", "restaurantes"]
new_lots_geo = new_lots_geo.merge(conteo_restaurantes_newlotes, on="id", how="left")
new_lots_geo["Value"] = new_lots_geo["restaurantes"] * 1700

# Create a popup for the new parking lots
popup_lotes = GeoJsonPopup(
    fields=["id", "Value"],
    aliases=["Simulation: ", "Value: "],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)

# Prepare heatmap data from restaurant locations
heat_data = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry]

# Build the map centered on Miami
m = folium.Map(location=[25.7617, -80.1918], zoom_start=12)

# Add parking lot GeoJSON data to the map
folium.GeoJson(
    lots_geo,
    name="Parking lot",
    marker=folium.Marker(icon=folium.Icon(icon="fa fa-car", prefix="fa")),
    style_function=lambda feature: {
        "markerColor": feature["properties"]["color"],
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.6,
    },
    popup=popup,
).add_to(m)
folium.GeoJson(lots_geo_buffer, name="Parking lot buffer").add_to(m)

# Add new parking lot GeoJSON data to the map
folium.GeoJson(
    new_lots_geo,
    name="New lot",
    marker=folium.Marker(icon=folium.Icon(icon="fa fa-car", prefix="fa")),
    style_function=lambda feature: {
        "markerColor": "black",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.6,
    },
    show=False,
    popup=popup_lotes,
).add_to(m)
folium.GeoJson(
    new_lots_geo_buffer,
    name="New lot buffer",
    show=False,
).add_to(m)

# Add geocoder to the map
Geocoder(add_marker=False).add_to(m)

# Add drawing control to the map
Draw(export=False).add_to(m)

# Add heatmap to the map
HeatMap(heat_data).add_to(
    folium.FeatureGroup(name="Heat Map", float=0, show=False).add_to(m)
)

# Add layer control to the map
folium.LayerControl().add_to(m)

# Display the map in Streamlit
result = st_folium(
    m,
    height=700,
    width=1000,
)

# Create two columns in Streamlit to display dataframes
col1, col2 = st.columns(2)

# Display the processed parking lot data in the first column
col1.write("Dataset:")
col1.dataframe(
    lots_geo.drop(columns=["geometry", "color"]).rename(
        columns={"id": "id_parking_lot", "Count": "environment_score", "Value": "sales"}
    )
)

# Display the processed new parking lot data in the second column
col2.write("Dataset new Lots:")
col2.dataframe(
    new_lots_geo[
        [
            "id",
            "restaurantes",
            "latitude",
            "longitude",
            "Value",
        ]
    ].rename(
        columns={
            "id": "id_new_parking_lot",
            "Value": "sales forecast",
            "restaurantes": "Count",
        }
    )
)