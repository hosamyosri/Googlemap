import streamlit as st
import requests
import pandas as pd
from io import StringIO

# List of SerpAPI keys to try
SERP_API_KEYS = [
    "e99c480e6a906850d705d7e0fc33122864744a65",  # Primary
    "e75a04722079702cc1f6be18fc26398f0b325682c92bb26d4d7578958153c038"   # Secondary
]

# Helper function to make a request using available API keys
def serpapi_request(url, params):
    for key in SERP_API_KEYS:
        params["api_key"] = key
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if "error" not in data:
                return data
        except Exception:
            continue
    return {"error": "All API keys failed."}

# UI setup
st.set_page_config(page_title="🔎 Google Maps Toolkit", layout="wide")
st.sidebar.title("📂 Navigation")
app = st.sidebar.radio("Select a tool:", ("🖼️ Photo Gallery", "📝 Review Finder"))

cities = [
    "Riyadh, Saudi Arabia", "Jeddah, Saudi Arabia", "Dammam, Saudi Arabia", "Khobar, Saudi Arabia",
    "Dhahran, Saudi Arabia", "Mecca, Saudi Arabia", "Medina, Saudi Arabia", "Tabuk, Saudi Arabia",
    "Abha, Saudi Arabia", "Khamis Mushait, Saudi Arabia", "Najran, Saudi Arabia", "Al Ahsa, Saudi Arabia",
    "Hail, Saudi Arabia", "Jazan, Saudi Arabia", "Al Baha, Saudi Arabia", "Al Qassim, Saudi Arabia",
    "Arar, Saudi Arabia", "Sakakah, Saudi Arabia", "Yanbu, Saudi Arabia", "Taif, Saudi Arabia"
]

# === PHOTO GALLERY ===
if app == "🖼️ Photo Gallery":
    st.title("🖼️ Google Maps Photo Gallery")
    query = st.text_input("Search Query", "مزايا لخدمات العمالة المنزلية")
    location = st.selectbox("City", cities)
    num_results = st.number_input("Number of Places", min_value=1, max_value=20, value=5)
    run_button = st.button("🔍 Search Photos")

    def search_places(query, location, limit):
        return serpapi_request(
            "https://serpapi.com/search.json",
            {"engine": "google_maps", "q": query, "location": location, "num": limit}
        ).get("local_results", [])

    def get_photos_by_data_id(data_id):
        return serpapi_request(
            "https://serpapi.com/search.json",
            {"engine": "google_maps_photos", "data_id": data_id}
        ).get("photos", [])

    if run_button:
        with st.spinner("Fetching images..."):
            image_cards = []
            places = search_places(query, location, num_results)
            for place in places:
                data_id = place.get("data_id")
                if not data_id:
                    continue
                place_name = place.get("title")
                maps_link = f"https://www.google.com/maps?cid={data_id}"
                photos = get_photos_by_data_id(data_id)
                for i, photo in enumerate(photos):
                    thumb = photo.get("thumbnail")
                    if thumb:
                        image_cards.append({
                            "Place Name": place_name,
                            "Image URL": thumb,
                            "Map Link": maps_link,
                            "Key": f"{data_id}_{i}"
                        })
            if image_cards:
                st.markdown("## Results")
                cols = st.columns(3)
                for idx, card in enumerate(image_cards):
                    with cols[idx % 3]:
                        st.markdown(f"**📍 {card['Place Name']}**")
                        st.markdown(f"[🌍 View]({card['Map Link']})", unsafe_allow_html=True)
                        st.image(card["Image URL"], use_container_width=True)
                df = pd.DataFrame(image_cards)
                csv = df.to_csv(index=False)
                st.download_button("⬇️ Download CSV", data=csv, file_name="photo_gallery.csv", mime="text/csv")
            else:
                st.warning("No photos found.")

# === REVIEW FINDER ===
elif app == "📝 Review Finder":
    st.title("📝 Google Maps Review Finder")
    city = st.selectbox("City", cities)
    keyword = st.text_input("Keyword to Match in Reviews", "خدمات عامة")
    language = st.selectbox("Language", ["ar", "en"], index=0)
    sort_by = st.selectbox("Sort Reviews By", ["qualityScore", "newestFirst", "ratingHigh", "ratingLow"])
    max_places = st.slider("Number of Places", 1, 10, 5)
    max_reviews = st.slider("Max Reviews per Place", 1, 20, 10)

    if st.button("🔎 Start Review Search"):
        st.info(f"Searching for '{keyword}' in {city}...")

        search_data = serpapi_request(
            "https://serpapi.com/search",
            {"engine": "google_maps", "q": keyword, "location": city, "hl": language}
        )

        if "local_results" not in search_data:
            st.error("No results found.")
        else:
            for place in search_data["local_results"][:max_places]:
                name = place.get("title")
                address = place.get("address", "N/A")
                rating = place.get("rating", "N/A")
                place_id = place.get("place_id")
                link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

                st.subheader(f"🏢 [{name}]({link})")
                st.caption(f"📍 {address} | ⭐ {rating}")

                review_data = serpapi_request(
                    "https://serpapi.com/search",
                    {
                        "engine": "google_maps_reviews",
                        "place_id": place_id,
                        "hl": language,
                        "sort_by": sort_by,
                        "num": max_reviews
                    }
                )

                matches = []
                for rev in review_data.get("reviews", []):
                    snippet = rev.get("snippet", "")
                    extracted = rev.get("extracted_snippet", {}).get("original", "")
                    if keyword in snippet or keyword in extracted:
                        matches.append({
                            "User": rev["user"]["name"],
                            "Rating": rev["rating"],
                            "Date": rev["date"],
                            "Review": snippet,
                            "Link": rev.get("link", "")
                        })

                if matches:
                    df = pd.DataFrame(matches)
                    st.success(f"✅ {len(df)} matching reviews found.")
                    st.dataframe(df)
                    csv = df.to_csv(index=False)
                    st.download_button("⬇️ Download Reviews", data=csv, file_name="matched_reviews.csv", mime="text/csv")
                else:
                    st.warning("No matching reviews found.")
