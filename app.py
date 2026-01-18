import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# New streamlined imports
from utils.travel_utils import (
    calculate_budget_split, 
    get_currency_for_country, 
    COUNTRY_CURRENCY_MAP
)
from utils.itinerary_ai import generate_itinerary
from utils.maps import create_map

# Generate the country list dynamically from your mapping keys
COUNTRIES = sorted(list(COUNTRY_CURRENCY_MAP.keys()))

# --- Configuration & Setup ---
def configure_page():
    st.set_page_config(
        page_title="AI Travel Planner",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def load_custom_styles():
    """Reads the external CSS file and injects it into the app."""
    try:
        # Path to your styles.css file
        with open("utils/styles.css", "r") as f:
            external_css = f.read()
    except FileNotFoundError:
        external_css = ""

    st.markdown(f"""
        <style>
        {external_css}
        
        /* App-specific layout overrides */
        .block-container {{ padding-top: 0rem !important; }}
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        
        .landing-container {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        /* Ensure AI HTML content container takes full width */
        .stMarkdown div {{ width: 100%; }}
        </style>
    """, unsafe_allow_html=True)



# --- Callbacks ---
def handle_plan_click():
    """Callback to trigger state change before rerun."""
    st.session_state.itinerary_generated = True

def handle_reset_click():
    """Callback to reset the app."""
    st.session_state.itinerary_generated = False
    st.session_state.itinerary_data = None

# ----------------- Main Application -----------------
def main():
    configure_page()
    load_custom_styles()

    # --- Session State Initialization ---
    if "itinerary_generated" not in st.session_state:
        st.session_state.itinerary_generated = False
    if "itinerary_data" not in st.session_state:
        st.session_state.itinerary_data = None

    # ----------------- UI: Input Form -----------------
    if not st.session_state.itinerary_generated:
        st.markdown('<div class="landing-container"><h1>✈️ AI Student Travel Assistant</h1><p>Smart, budget-friendly itineraries in seconds.</p></div>', unsafe_allow_html=True)


        col_l, col_center, col_r = st.columns([1, 2, 1])
        with col_center:
            # Country & City
            country = st.selectbox("Select Country", COUNTRIES, index=COUNTRIES.index("India") if "India" in COUNTRIES else 0)
            city = st.text_input("City (Optional)", placeholder="e.g. Mumbai, Goa")

            # Budget & Duration
            c1, c2 = st.columns(2)
            with c1: budget = st.number_input("Budget", min_value=1000, step=1000, value=5000)
            with c2: days = st.number_input("Days", min_value=1, max_value=30, value=3)

            # Travelers & Style
            travelers = st.slider("Travelers", 1, 10, 1)
            travel_type = st.radio("Travel Style", ["Budget", "Standard", "Luxury"], horizontal=True)

            interests = st.multiselect("Interests", ["Culture", "Food", "Adventure", "Relaxation", "Nightlife","History","Museums"], default=["Food"])

            # IMPORTANT: The button uses on_click to hide this page immediately
            st.button("Plan My Trip 🎒✈️", on_click=handle_plan_click)

            # Store temporary inputs in session state to pass to AI during next run
            st.session_state.temp_inputs = {
                "place": city if city else country,
                "days": days,
                "budget": budget,
                "travelers": travelers,
                "interests": interests,
                "travel_type": travel_type,
                "currency": get_currency_for_country(country)
            }

    # ----------------- UI: Results Display -----------------
    else:
        # 1. AI Generation Logic (Only runs once)
        if st.session_state.itinerary_data is None:
            with st.spinner("🤖 AI is packing your backpack with the best deals...!!"):
                inputs = st.session_state.temp_inputs
                
                # Split budget
                budget_data = calculate_budget_split(
                    float(inputs['budget']), int(inputs['days']), 
                    inputs['interests'], int(inputs['travelers']), inputs['currency']
                )

                try:
                    response = generate_itinerary(
                        inputs['place'], inputs['days'], budget_data, 
                        inputs['interests'], inputs['travel_type']
                    )
                    st.session_state.itinerary_data = json.loads(response)
                    st.session_state.budget_data = budget_data
                    
                    # Map Logic
                    locations = st.session_state.itinerary_data.get("locations", [])
                    st.session_state.map_obj = create_map(inputs['place'], locations)
                except Exception as e:
                    st.error(f"Error: {e}")
                    if st.button("Try Again"):
                        handle_reset_click()
                        st.rerun()

        # 2. Render Results
        if st.session_state.itinerary_data:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.title(f"📍 Trip to {st.session_state.temp_inputs['place']}")
            with col_b:
                st.button("⬅️ New Plan", on_click=handle_reset_click)

            display_results(
                st.session_state.itinerary_data,
                st.session_state.get('map_obj'),
                st.session_state.get('budget_data'),
                st.session_state.temp_inputs['currency']
            )

# ----------------- Helper: Display Tabs -----------------
# Update display_results to fix the "None" error shown in your screenshot
def display_results(data, map_obj, budget_data, currency):
    tab1, tab2, tab3 = st.tabs(["📝 Itinerary", "🗺️ Map", "💰 Budget Breakdown"])

    with tab1:
        # Fallback for total_cost to prevent showing 'None'
        total = data.get('total_cost')
        total_str = f"{total}" if total is not None else "Calculating..."
        st.info(f"💡 Estimated Total: {total_str} {currency}")
        st.markdown(data.get("html", ""), unsafe_allow_html=True)

    with tab2:
        if map_obj:
            map_html = map_obj.get_root().render()
            components.html(map_html, height=500)
        else:
            st.warning("Map couldn't be loaded for this location.")

    with tab3:
        st.subheader("Budget Allocation")
        if budget_data:
            df = pd.DataFrame([budget_data['breakdown']]).melt(var_name="Category", value_name="Amount")
            st.bar_chart(df.set_index("Category"))
            st.table(df)

if __name__ == "__main__":
    main()
