import streamlit as st
import pandas as pd 
import folium
from streamlit_folium import st_folium 
import plotly.express as px
import geopandas as  gpd
from folium.plugins import MiniMap, Geocoder, Search

st.set_page_config(
    page_title="Nakuru County Tourism"
)

@st.cache_data
def get_data():
    url = "https://raw.githubusercontent.com/nangami29/FinalYear-project/main/nakuru_tourist_attractions.csv"
    geo_url = "https://raw.githubusercontent.com/nangami29/FinalYear-project/main/KENYAcounties.geojson"

    try:
        df=pd.read_csv(url, encoding='ISO-8859-1')
        gdf=gpd.read_file(geo_url)
        return df, gdf 
    except Exception as e:
        st.error(f"Data loading failed: {e}")
        return None, None
    
data, geodata=get_data()
required_columns = ['Attraction', 'Latitude', 'Longitude', 'Description']
missing_cols = [col for col in required_columns if col not in data.columns]

if missing_cols:
    st.error(f"The data is missing expected columns: {missing_cols}")
    st.stop()


if data is None or geodata is None:
    st.error("Data is missing or could not be loaded.")
    st.stop()
    
attraction_to_county = {
    "Lake Nakuru National Park": "Nakuru",
    "Menengai Crater": "Nakuru",
    "Lake Naivasha": "Nakuru",
    "Hell’s Gate National Park": "Nakuru",
    
}

def get_centre_boundary(attraction_name):
    county_name = attraction_to_county.get(attraction_name)
    if not county_name:
        return None
    county_bounds = geodata[geodata['NAME_1'] == county_name]
    if county_bounds.empty:
        st.warning(f"No boundary data found for {county_name}")
        return None
    return county_bounds


#st.write(data.columns)
#st.write("Available GeoJSON names:", geodata['NAME_1'].unique())

# Header
st.title("NAkuru County Tourism sector")
st.write(" Select a centre to view its geographical information and description")

# tourist centre attractions selection
print(f"Value of data: {data}")
if data is not None:
    print(f"Columns in data: {data.columns}")
centre= st.selectbox(label="Select Centre", options=list(data['Attraction'].unique()), key="selected_centre")
#selected_centre=get_centre_boundary(centre=centre)

if centre:
    centre_data=data[data['Attraction'] ==centre].iloc[0]
    
    col1, col2=st.columns([3,  2])

    with col1:
        st.subheader('No. of visitors over Selected Years')
        years=["Visitor_Statistics(2020)", "Visitor_Statistics(2021)", 
               "Visitor_Statistics(2022)", "Visitor_Statistics(2023)"]

        selected_years=st.multiselect(label="Select Visitor " \
        "Years", options= years, default=years[:4])

#create a dataframe and pass it to plotly
        attraction_data={
            "Year":[year.split()[0] for year in selected_years],
            "Visitors":[centre_data[year] for year in selected_years]
        }

        visitors_df=pd.DataFrame(attraction_data)
        #Display the chart
        fig=px.bar(visitors_df, x="Year", y="Visitors", title=f"No of Visitors of{centre} over the selected years")
        st.plotly_chart(fig, use_container_width=True)

    if centre_data is not None:
                st.subheader("County Statistics")
                st.subheader("Location on Map")

                # Create map centered on the attraction
                m = folium.Map(location=[centre_data["Latitude"], centre_data["Longitude"]], zoom_start=12)
                
                # Add marker for the attraction
                folium.Marker(
                    [centre_data["Latitude"], centre_data["Longitude"]],
                    tooltip=centre_data["Attraction"]
                ).add_to(m)

                # Prepare popup content with hotel and description info
                popup_html = f"""
                <h4>{centre_data['Attraction']}</h4>
                <p><b>Description:</b> {centre_data['Description']}</p>
                <p><b>Nearby Hotels:</b> {centre_data.get('Nearby_Hotels_Lodges')}</p>
                <p><b>Entrance Fee (Citizens):</b> Ksh {centre_data.get('Entrace_fee(citizens)Kshs')}</p>
                <p><b>Entrance Fee (Residents):</b> Ksh {centre_data.get('Residents', 'N/A')}</p>
                <p><b>Entrance Fee(Non-Residents):</b>USD {centre_data.get('Non_Residents(USD)')}</p>
                """

                # Create popup
                popup = folium.Popup(popup_html, max_width=300)

                # Add marker with icon and popup
                folium.Marker(
                    location=[centre_data["Latitude"], centre_data["Longitude"]],
                    tooltip="Click for more info",
                    popup=popup,
                    icon=folium.Icon(icon="info-sign", color="blue")
                ).add_to(m)


                

                # Add county boundary
                centre_boundary = get_centre_boundary(centre_data["Attraction"])
                if centre_boundary is not None:
                    folium.GeoJson(centre_boundary, name='County Boundary').add_to(m)

                    

                Geocoder().add_to(m)
                MiniMap(
                    position='topright',
                    toggle_display=True,
                ).add_to(m)


                # Display the map
                st_folium(m, width=700, height=500, use_container_width=True)


            
else:
    st.write("Select a centre to view its data")


