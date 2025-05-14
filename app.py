import streamlit as st
import requests

# Constants
SERP_API_KEY = "dd947c3d9f56e4a248956a548fabfd8b644743e68bed96a2a578873385e1411b"

st.set_page_config(page_title="Google Maps", layout="wide")
st.title("🖼️ Google Maps Photo Gallery (Interactive Card View)")

# City Dropdown List
cities = [
    "Riyadh, Saudi Arabia", "Jeddah, Saudi Arabia", "Dammam, Saudi Arabia", "Khobar, Saudi Arabia",
    "Dhahran, Saudi Arabia", "Mecca, Saudi Arabia", "Medina, Saudi Arabia", "Tabuk, Saudi Arabia",
    "Abha, Saudi Arabia", "Khamis Mushait, Saudi Arabia", "Najran, Saudi Arabia", "Al Ahsa, Saudi Arabia",
    "Hail, Saudi Arabia", "Jazan, Saudi Arabia", "Al Baha, Saudi Arabia", "Al Qassim, Saudi Arabia",
    "Arar, Saudi Arabia", "Sakakah, Saudi Arabia", "Yanbu, Saudi Arabia", "Taif, Saudi Arabia"
]

# UI Inputs
query = st.text_input("Enter Search Query", "مزايا لخدمات العمالة المنزلية")
location = st.selectbox("Select Location", cities)
num_results = st.number_input("Number of Places to Search", min_value=1, max_value=20, value=5)
max_api_calls = st.number_input("Maximum API Calls Allowed", min_value=1, max_value=100, value=20)

run_button = st.button("🔍 Search & Show Gallery")

# SerpAPI Functions
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
        api_calls_used = 0
        image_cards = []

        # Count the initial place search as 1 API call
        api_calls_used += 1
        if api_calls_used > max_api_calls:
            st.warning("⚠️ API call limit reached before even starting.")
        else:
            places = search_places(query, location, num_results)

            if not places:
                st.error("❌ No places found.")
            else:
                for place in places:
                    if api_calls_used >= max_api_calls:
                        st.warning("⚠️ Stopped: Reached maximum allowed API calls.")
                        break

                    place_name = place.get("title")
                    data_id = place.get("data_id")
                    if not data_id:
                        continue

                    maps_link = f"https://www.google.com/maps?cid={data_id}"

                    # Count this photo-fetching API call
                    api_calls_used += 1
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
                    st.warning("⚠️ No photos found or API limit blocked photo results.")
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

    st.info(f"📊 Total API calls used: {api_calls_used} / {max_api_calls}")
