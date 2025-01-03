import streamlit as st
import requests
import pandas as pd
import io
from premai import Prem
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# PREM API Credentials
PREM_API_KEY = os.getenv("PREM_SAAS_API_KEY")
PREM_PROJECT_ID = os.getenv("PREM_PROJECT_ID")

# Initialize Prem client
prem_client = Prem(api_key=PREM_API_KEY)

# Mock API URL
MOCK_API_URL = "https://my.api.mockaroo.com/health.json?key=92050340"

# Function to fetch health data from Mockaroo API
def fetch_mock_health_data():
    try:
        response = requests.get(MOCK_API_URL)
        if response.status_code == 200:
            # Parse the CSV content into a pandas DataFrame
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            # Randomly select one row to simulate real-time health data
            selected_row = df.sample().iloc[0]
            return {"steps": selected_row["steps"], "calories": selected_row["calories"]}
        else:
            st.error(f"Failed to fetch mock health data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to detect slacking
def detect_slacking(data):
    steps = data.get("steps", 0)
    calories = data.get("calories", 0)

    # Example thresholds
    slacking_detected = steps < 5000 or calories < 2000
    return slacking_detected, steps, calories

# Function to get motivational suggestions from PREM API
def get_prem_suggestions(message):
    messages = [
        {"role": "user", "content": message}
    ]
    try:
        response = prem_client.chat.completions.create(
            project_id=PREM_PROJECT_ID,
            messages=messages,
            max_tokens=500,
            model="gpt-4o-mini",
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error using PREM API: {e}")
        return "Could not generate suggestions at this time."

# Streamlit App
def main():
    st.title("AI Nutritionist - Mockaroo Integration")
    st.write("A simple and effective AI nutritionist app using Mockaroo API for health data!")

    # Fetch health data from Mockaroo API
    st.header("Health Data")
    data = fetch_mock_health_data()

    if data:
        slacking_detected, steps, calories = detect_slacking(data)

        st.write(f"**Steps Today**: {steps}")
        st.write(f"**Calories Burned Today**: {calories}")

        if slacking_detected:
            st.error("Slacking Detected! You're below your activity goals.")
            message = f"I have taken {steps} steps and burned {calories} calories today. What can I do to improve?"
            suggestions = get_prem_suggestions(message)
            st.info("AI Suggestions:")
            st.write(suggestions)
        else:
            st.success("Great job! You're meeting your activity goals.")
            message = f"I have taken {steps} steps and burned {calories} calories today. What should I keep doing to stay on track?"
            suggestions = get_prem_suggestions(message)
            st.info("AI Motivational Message:")
            st.write(suggestions)

    # Educational Tip
    st.header("Daily Tip")
    if st.button("Get Today's Tip"):
        tip = get_prem_suggestions("Give me a motivational tip for staying healthy.")
        st.success(f"Tip: {tip}")

if __name__ == "__main__":
    main()


