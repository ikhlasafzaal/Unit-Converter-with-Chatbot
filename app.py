import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Function to load CSS from a file
def load_css():
    with open("styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the CSS
load_css()

# Streamlit Sidebar
#st.sidebar.title("Unit Converter")

# Define conversion categories
conversions = {
    "length": {"meter": 1, "kilometer": 0.001, "mile": 0.000621371, "yard": 1.09361},
    "weight": {"gram": 1, "kilogram": 0.001, "pound": 0.00220462, "ounce": 0.035274},
    "temperature": lambda value, from_unit, to_unit: 
        (value * 1.8 + 32 if from_unit == "celsius" and to_unit == "fahrenheit" else
         (value - 32) / 1.8 if from_unit == "fahrenheit" and to_unit == "celsius" else value),
    "area": {"square_meter": 1, "square_kilometer": 0.000001, "square_mile": 3.861e-7, "acre": 0.000247105},
    "volume": {"liter": 1, "milliliter": 1000, "cubic_meter": 0.001, "gallon": 0.264172}
}

# Streamlit UI Title
st.title(" 🎨 Unit Converter With Chatbot")

# Category selection
category = st.selectbox("Select Category", list(conversions.keys()))

# Units selection for the chosen category
from_unit = st.selectbox("From Unit", list(conversions[category]) if category != "temperature" else ["celsius", "fahrenheit"])
to_unit = st.selectbox("To Unit", list(conversions[category]) if category != "temperature" else ["celsius", "fahrenheit"])

# Input value from the user
value = st.number_input("Enter Value", min_value=0.0, step=0.1)

# Conversion logic with Gemini API
def handle_conversion(query):
    try:
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# Local conversion logic
def convert_locally(value, from_unit, to_unit):
    if category == "temperature":
        return conversions[category](value, from_unit, to_unit)
    else:
        return value * (conversions[category][to_unit] / conversions[category][from_unit])

# Buttons for conversion
if st.button("Convert with LLM"):
    query = f"Convert {value} {from_unit} to {to_unit}."
    result = handle_conversion(query)
    st.success(result)

if st.button("Convert Without LLM"):
    try:
        result = convert_locally(value, from_unit, to_unit)
        st.success(f"Converted Value: {result} {to_unit}")
    except Exception as e:
        st.error(f"Conversion error: {e}")

# Simple Chatbot Interface
st.subheader(" 🧑‍🚀 Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# User input for the chatbot
user_input = st.text_input("Ask something...")

if st.button("Send"):
    if user_input:
        st.session_state.messages.append(f"You: {user_input}")
        response = handle_conversion(user_input)
        st.session_state.messages.append(f"Bot: {response}")

# Display chat messages
for msg in st.session_state.messages:
    if "You" in msg:
        st.markdown(f'<div class="stMessage stUserMessage">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stMessage stBotMessage">{msg}</div>', unsafe_allow_html=True)
