import streamlit as st
import requests

# Constants
SERP_API_KEY = "d2fbac5d8025840daf9af009d957a230a40936e7eddbe3b88ecbddd821688cfb"

st.set_page_config(page_title="Google Maps", layout="wide")
st.title("🖼️ Google Maps Photo Gallery (Interactive Card View)")

# City Dropdown List
cities = [
    "Riyadh, Saudi Arabia",
    "Jeddah, Saudi Arabia",
    "Dammam, Saudi Arabia",
    "Khobar, Saudi Arabia",
    "Dhahran, Saudi Arabia",
    "Mecca, Saudi Arabia",
    "Medina, Saudi Arabia",
    "Tabuk, Saudi Arabia",
    "Abha, Saudi Arabia",
    "Khamis Mushait, Saudi Arabia",
    "Najran, Saudi Arabia",
    "Al Ahsa, Saudi Arabia",
    "Hail, Saudi Arabia",
    "Jazan, Saudi Arabia",
    "Al Baha, Saudi Arabia",
    "Al Qassim, Saudi Arabia",
    "Arar, Saudi Arabia",
    "Sakakah, Saudi Arabia",
    "Yanbu, Saudi Arabia",
    "Taif, Saudi Arabia"
]

# UI Inputs
query = st.text_input("Enter Search Query", "مزايا لخدمات العمالة المنزلية")
location = st.selectbox("Select Location", cities)
num_results = st.number_input("Number of Results to Retrieve", min_value=1, max_value=20, value=5)

run_button = st.button("🔍 Search & Show Gallery")

# Search and Photo Functions
def search_places(query, location, limit=5):
    search_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps",
        "q": query,
        "location": location,
        "num": limit,
        "api_key": SERP_API_KEY
    }
    response = requests.get(search_url, params=params).json()
    return response.get("local_results", [])

def get_photos_by_data_id(data_id):
    photo_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps_photos",
        "data_id": data_id,
        "api_key": SERP_API_KEY
    }
    response = requests.get(photo_url, params=params).json()
    return response.get("photos", [])

# Execution Logic
if run_button:
    with st.spinner("🔄 Fetching places and images..."):
        places = search_places(query, location, num_results)

        if not places:
            st.error("❌ No places found.")
        else:
            image_cards = []

            for place in places:
                place_name = place.get("title")
                data_id = place.get("data_id")
                if not data_id:
                    continue
                maps_link = f"https://www.google.com/maps?cid={data_id}"
                photos = get_photos_by_data_id(data_id)
                if photos:
                    for i, photo in enumerate(photos):
                        thumbnail = photo.get("thumbnail", "")
                        if thumbnail:
                            image_cards.append({
                                "Place Name": place_name,
                                "Image URL": thumbnail,
                                "Map Link": maps_link,
                                "Unique Key": f"{data_id}_{i}"
                            })

            if not image_cards:
                st.warning("⚠️ No photos found.")
            else:
                st.markdown("## 🖼️ Interactive Photo Cards")
                cols = st.columns(3)
                for idx, card in enumerate(image_cards):
                    col = cols[idx % 3]
                    with col:
                        st.markdown(f"**📍 {card['Place Name']}**")
                        st.markdown(f"[🌍 View on Google Maps]({card['Map Link']})", unsafe_allow_html=True)
                        with st.expander("👁️ View Photo", expanded=False):
                            st.image(card["Image URL"], use_container_width=True)
