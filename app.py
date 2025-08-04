import streamlit as st
from openai import OpenAI
client = OpenAI(api_key="MY_API_KEY")
from datetime import datetime
import requests
#st.set_page_config(page_title="BreatheClean.AI", page_icon="🌿", layout="wide")
# Set up the app
st.set_page_config(page_title="BreatheClean.AI", page_icon="🌿")



# Style overrides
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f9f8;
    }
    h1, h2, h3 {
        color: #1c6758;
    }
    .card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f9f8;
    }
    h1, h2, h3 {
        color: #1c6758;
    }
    .card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    /* Highlight the text input box */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 2px solid #4caf50;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        color: #333;
        transition: border-color 0.3s ease-in-out;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2e7d32;
        outline: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 BreatheClean.AI 🌿")
st.subheader("Smart Allergy & Air Quality Forecast App")
st.write("Welcome to your global environmental health companion.")
# User input
city = st.text_input("Enter your city or zip code:", "New York")

# Current date
now = datetime.now()
st.write(f"📅 Today is: {now.strftime('%A, %B %d, %Y')} at {now.strftime('%I:%M %p')}")


# OpenWeatherMap API key
api_key = "MY_API_KEY"  # Replace with your real key

# Function to get weather, air quality, and location name
def get_weather_data(city, api_key):
    try:
        if city.isdigit() and len(city) == 5:
            # ZIP code mode (U.S. only)
            geo_url = f"http://api.openweathermap.org/geo/1.0/zip?zip={city},US&appid={api_key}"
            geo_response = requests.get(geo_url).json()

            if "lat" not in geo_response:
                return None, None, "Unknown Location"

            lat = geo_response['lat']
            lon = geo_response['lon']
            location_name = f"{geo_response.get('name', '')}, {geo_response.get('state', '') or geo_response.get('country', '')}"
        else:
            # Global city mode
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
            geo_response = requests.get(geo_url).json()

            if not geo_response or "lat" not in geo_response[0]:
                return None, None, "Unknown Location"

            lat = geo_response[0]['lat']
            lon = geo_response[0]['lon']
            name = geo_response[0].get("name", "")
            state = geo_response[0].get("state", "")
            country = geo_response[0].get("country", "")
            location_name = f"{name}, {state or country}" if name else "Unknown Location"

        # Weather & Air Quality API calls
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

        weather_data = requests.get(weather_url).json()
        air_data = requests.get(air_url).json()

        return weather_data, air_data, location_name, country

    except Exception as e:
        print("Error:", e)
        return None, None, "Unknown Location"

    
def get_local_time(lat, lon, timezone_api_key):
    url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_api_key}&format=json&by=position&lat={lat}&lng={lon}"
    response = requests.get(url).json()
    return response.get("formatted", None)
    
def estimate_pollen_risk(temp_celsius, plant_names):
    high_pollen_plants = ["Ambrosia", "Betula", "Quercus", "Poaceae", "Artemisia"]
    count = sum(any(p in plant for p in high_pollen_plants) for plant in plant_names)

    if temp_celsius >= 25 and count >= 3:
        return "🔴 High – Warm temperatures and multiple pollen-heavy plants"
    elif temp_celsius >= 15 and count >= 1:
        return "🟠 Moderate – Mild weather with some allergy plants"
    else:
        return "🟢 Low – Not ideal conditions for pollen spread"

def get_native_plants(country_code, month=None):
    gbif_url = "https://api.gbif.org/v1/occurrence/search"
    params = {
        "country": country_code,
        "taxonKey": 7707728,  # Tracheophyta (vascular plants)
        "hasCoordinate": "true",
        "limit": 10
    }

    if month:
        params["month"] = month

    try:
        response = requests.get(gbif_url, params=params)
        data = response.json()
        return data.get("results", [])
    except:
        return []


# Fetch and display data
if city:
    weather, air, location_name, country_code = get_weather_data(city, api_key)
    # Add your TimeZoneDB API key here
timezone_api_key = "MY_API_KEY"  # Replace with your key

# Only fetch local time if weather is available
if weather:
    lat = weather['coord']['lat']
    lon = weather['coord']['lon']
    local_time = get_local_time(lat, lon, timezone_api_key)
    if local_time:
        st.write(f"📅 Local time in {location_name}: {local_time}")
    else:
        st.write("🕒 Couldn't fetch local time.")


    st.write(f"📍 Showing results for: **{location_name}**")
    st.markdown("### ☁️ Forecast Summary")

    if weather:
        temp = weather['main']['temp']
        desc = weather['weather'][0]['description'].title()
        st.write(f"**Temperature:** {temp}°C")
        st.write(f"**Condition:** {desc}")
    else:
        st.warning("Couldn't get weather data.")

    if air:
        pm25 = air['list'][0]['components']['pm2_5']
        st.write(f"**Air Quality (PM2.5):** {pm25} μg/m³")

        if pm25 > 35:
            st.error("Air quality is poor. Avoid outdoor activity.")
        elif pm25 > 15:
            st.warning("Moderate air quality. Sensitive people should be cautious.")
        else:
            st.success("Air quality is good!")

        # 🌼 Smart Tip Section
   
        st.markdown("### 🌼 Daily Health Tip")
        if pm25 > 35:
            st.error("🔴 Tip: Air quality is very poor. Stay indoors and wear a mask if going out.")
        elif "dust" in desc.lower():
            st.warning("🟠 Tip: Dusty conditions — wear sunglasses and use antihistamines if needed.")
        elif temp > 30:
            st.warning("🟠 Tip: High heat may worsen allergy symptoms. Stay hydrated!")
        elif "rain" in desc.lower():
            st.info("🌧️ Tip: Rain may wash away pollen, but mold risk rises. Watch indoor humidity.")
        else:
            st.success("✅ Tip: Great day to enjoy the outdoors, but carry medication if you're sensitive.")

        # ⬇️ Place native plant section here
        # 🌿 Native Plants Section
        st.markdown("### 🌿 Native Plants in This Region")

        month = now.month  # Current month

        if country_code:
            plants = get_native_plants(country_code, month)
            st.write(f"🔍 Found {len(plants)} raw plant records from GBIF.")
            if plants:
                seen = set()
                plant_names = []

                for plant in plants:
                    name = plant.get("scientificName")
                    kingdom = plant.get("kingdom")

                    # Log skipped results
                    if kingdom != "Plantae":
                        st.write(f"❌ Skipped non-plant: {name or 'Unnamed'}")
                        continue

                    # Skip duplicates and blanks
                    if not name or name in seen:
                        continue
                    seen.add(name)

                    # Collect valid plant names
                    plant_names.append(name)

                # 🔠 Sort alphabetically
                plant_names.sort()

                # Display
                for name in plant_names:
                    st.write(f"- 🌱 **{name}**")
                    # 🌾 Pollen Spread Risk Section (optional)
            if weather:
                temp = weather['main']['temp']
                pollen_risk = estimate_pollen_risk(temp, plant_names)
                st.markdown("### 🌾 Pollen Spread Risk Meter")

                # Score logic (adjust as needed)
                if "High" in pollen_risk:
                    st.progress(100)
                    st.error("🔴 High – Warm temperatures and multiple pollen-heavy plants")
                elif "Moderate" in pollen_risk:
                    st.progress(60)
                    st.warning("🟠 Moderate – Mild weather with some allergy plants")
                else:
                    st.progress(20)
                    st.success("🟢 Low – Not ideal conditions for pollen spread")


            else:
                st.info("No native plant data available for this region right now.")
        else:
            st.warning("Could not determine country code for native plant lookup.")

st.markdown("---")
st.header("🤖 Ask Our AI Health Assistant")
user_question = st.text_input("Ask anything about air quality, plants, or allergies:")


if user_question:
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful environmental health assistant."},
                {"role": "user", "content": user_question}
            ]
        )
        answer = response.choices[0].message.content
        st.success(answer)       
        

