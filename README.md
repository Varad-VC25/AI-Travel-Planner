<div align="center">

# 🧳 AI-Powered Student Travel Planner

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Groq AI](https://img.shields.io/badge/Powered%20By-Groq%20Llama%203-orange?style=for-the-badge)](https://groq.com/)
</div>
An AI-driven travel planner for students, generating personalized and budget-friendly itineraries with real-time location data and map visualizations.

---

## 🌍 Overview

AI Travel Planner is a Streamlit-based travel planning app that uses AI (Groq LLM) to generate smart, student-friendly itineraries.

Enter your destination, travel days, budget, type of travel, and interests — the app generates:

- Detailed day-wise itinerary  
- Morning / Afternoon / Evening segments  
- Cost-tag breakdown matching your total budget  
- Student-friendly hotel suggestions  
- List of important places  
- Interactive route map with markers  

All generated dynamically using AI + Folium (OpenStreetMap).

---

## 🚀 Features

### ✨ AI Features
- Generates complete student itineraries
- Validates budget mathematically (sum of cost tags)
- Produces HTML output with styled cards, segments, and tables

### 🗺 Interactive Maps 
- Uses Folium + OpenStreetMap
- Auto-geocodes each location using Nominatim (OSM)
- Draws routes between itinerary locations using OSRM
- Adds markers automatically
- Displays distance & estimated travel time

### 💰 Budget Tools
- Intelligent category split (stay/food/transport/activities/misc)
- Adjusts based on interests (adventure, food, culture)
- Shows bar chart + table

### 🎨 Custom UI
- Modern glass-UI theme
- Animated buttons
- Styled itinerary cards
- Responsive layout

---

### 🛠️ Tech Stack
| Layer           | Technology     | Purpose                 |
| --------------- | -------------- | ----------------------- |
| Frontend        | Streamlit      | Interactive web UI      |
| AI Engine       | Groq (Llama-3) | Ultra-fast AI inference |
| Mapping         | Folium         | Interactive maps        |
| Data Processing | Pandas         | Budget & logic handling |
| Styling         | CSS            | Custom UI design        |

---

### 🚀 Getting Started
### Prerequisites

Python 3.8+

Groq API Key (Free): https://console.groq.com/

### 📥 Installation

1️⃣ Clone the Repository

git clone https://github.com/Varad-VC25/AI-Travel-Planner.git
cd AI-Travel-Planner


2️⃣ Install dependencies

pip install -r requirements.txt


3️⃣ Add your API key

Create .streamlit/secrets.toml

GROQ_API_KEY="your_api_key_here"


4️⃣ Run the app

streamlit run app.py

---

## 📸 Screenshots

### 🏠 Home / Input Page
![Home Screen](assets/home.png)

---

### 🤖 AI Generated Itinerary
![Generated Itinerary](assets/output.png)

---

### 💸 Budget Summary
![Budget Summary](assets/budget.png)

---

### 🗺️ Map View 
![Map View](assets/map.png)


