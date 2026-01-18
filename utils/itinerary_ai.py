import os
import json
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
from bs4 import BeautifulSoup  

# --- Load environment ---
load_dotenv()
env_path = Path(__file__).parent.parent / ".env"  # adjust as needed
load_dotenv(dotenv_path=env_path)

# --- Load API key ---
try:
    API_KEY = st.secrets["groq"]["api_key"]
except Exception:
    API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("Groq API Key not found! Add it to .env or Streamlit secrets.")

# --- Initialize Groq client ---
def get_groq_client():
    try:
        return Groq(api_key=API_KEY)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        return None

client = get_groq_client()


# -------------------- AI Suggestions --------------------
def get_ai_suggestions(budget, interests, country=None):
    """
    Suggest 3 student-friendly destinations using Groq AI.
    """
    if not client:
        return "Error: Groq API Key missing."

    country_context = f"in {country}" if country and country != "Anywhere" else "anywhere in the world"
    prompt = f"""
    Suggest 3 student-friendly travel destinations {country_context} for a budget of {budget}.
    User Interests: {', '.join(interests)}

    Output as Markdown numbered list:
    1. **City, Country**: Why it's good (1 sentence)
    2. ...
    3. ...
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting suggestions: {e}"


# -------------------- Itinerary Prompt --------------------
def _build_itinerary_prompt(city, days, budget_info, interests, travel_type):
    """
    Constructs a detailed prompt for generating a day-wise student itinerary.
    """
    currency = budget_info.get('currency', 'INR')
    breakdown_str = "\n".join([f"- {k}: {v} {currency}" for k, v in budget_info['breakdown'].items()])

    prompt = f"""
You are an expert AI Travel Planner for STUDENTS.

Create a {days}-day itinerary for {city}.

Context:
- Travelers: {budget_info.get('travelers', 1)}
- Total Budget: {budget_info.get('total', 0)} {currency}
- Interests: {', '.join(interests)}
- Style: {travel_type}

Budget Guidelines:
{breakdown_str}

REAL HOTEL SEARCH:
- Suggest REAL, high-rated student accommodations in {city}.
- If Budget: Suggest hostels like Zostel, goStops, or The Hosteller.
- If Standard/Luxury: Suggest real 3-4 star budget hotels.
- Format links as: <a href='https://www.google.com/search?q={city}+hotel+[Name]' target='_blank'>[Hotel Name]</a>.

MATH VALIDATION RULES:
1. Every activity/meal/stay MUST have a <span class='price-tag'>Cost: [Amount] {currency}</span>.
2. Sum of all price-tags MUST equal the total_cost field in JSON.

FORMATTING RULES:
- Wrap each day in <div class='day-card'>.
- Prepend each day with <h3>Day X</h3> (X = day number) — even if only one activity.
- Use <div class='segment'> for Morning, Afternoon, Evening and bold these three words <strong>...</strong>.
- End with a <div class='cost-summary'> table.
- The Total row should be bold using <strong>...</strong>.



OUTPUT FORMAT: JSON only
{{
    "html": "...",
    "locations": ["Specific Landmark 1", "Specific Landmark 2"],
    "total_cost": {budget_info.get('total', 0)},
    "currency": "{currency}"
}}
"""
    return prompt


# -------------------- Generate Itinerary --------------------
def generate_itinerary(city, days, budget_info, interests, travel_type):
    """
    Generates a student-friendly itinerary using Groq AI.
    Returns JSON with keys: html, locations, total_cost, currency
    """
    if not client:
        return json.dumps({
            "html": "<p>Error: Groq API Key not found.</p>",
            "locations": [],
            "total_cost": 0,
            "currency": budget_info.get('currency', 'INR')
        })

    prompt = _build_itinerary_prompt(city, days, budget_info, interests, travel_type)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,  # low temperature for deterministic output
            max_tokens=6000,
            response_format={"type": "json_object"}
        )

        result = chat_completion.choices[0].message.content

        # -------------------- Post-process HTML to ensure Day numbers --------------------
        try:
            data = json.loads(result)
            html_text = data.get("html", "")
            soup = BeautifulSoup(html_text, "html.parser")
            day_cards = soup.find_all("div", class_="day-card")
            for i, day_div in enumerate(day_cards, start=1):
                if not day_div.find("h3"):
                    day_div.insert(0, soup.new_tag("h3"))
                    day_div.h3.string = f"Day {i}"
            data["html"] = str(soup)
            return json.dumps(data)
        except Exception:
            # fallback: return raw result if parsing fails
            return result

    except Exception as e:
        return json.dumps({
            "html": f"<div class='error'>Error: {str(e)}</div>",
            "locations": [],
            "total_cost": 0,
            "currency": budget_info.get('currency', 'INR')
        })
