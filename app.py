# app.py (With Robust Initialization)
import streamlit as st
import requests
from deep_translator import GoogleTranslator

# --- DATA AND LOGIC ---
SDG_DATA = {
    "SDG 7": {"title": "Affordable and Clean Energy", "keywords": ["energy", "renewable", "solar", "wind", "clean power", "electricity", "grid", "hydro", "geothermal"]},
    "SDG 9": {"title": "Industry, Innovation, and Infrastructure", "keywords": ["innovation", "infrastructure", "technology", "startup", "industrial", "internet", "manufacturing", "entrepreneurship"]},
    "SDG 11": {"title": "Sustainable Cities and Communities", "keywords": ["cities", "urban", "sustainability", "community", "housing", "transport", "public spaces", "smart city", "resilience"]},
    "SDG 12": {"title": "Responsible Consumption and Production", "keywords": ["sustainability", "recycling", "circular economy", "efficiency", "waste", "supply chain", "production", "consumption"]},
    "SDG 13": {"title": "Climate Action", "keywords": ["climate", "emissions", "renewable", "carbon footprint", "greenhouse gas", "adaptation", "fossil fuels"]},
}

# --- HELPER FUNCTIONS ---
def translate_to_english(text, source_lang='no', target_lang='en'):
    if not text: return ""
    try: return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        st.warning(f"Translation failed: {e}. Using original text.")
        return text

def fetch_brreg_data(org_nr):
    if not org_nr.isdigit() or len(org_nr) != 9: return "Error: Please enter a valid 9-digit organisation number."
    url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org_nr}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        name = data.get("navn", "Name not found.")
        description_no = " ".join(data["vedtektsfestetFormaal"]) if "vedtektsfestetFormaal" in data and data["vedtektsfestetFormaal"] else "No official purpose found."
        description_en = translate_to_english(description_no)
        website = data.get("hjemmeside", "Not available")
        sector = data.get("naeringskode1", {}).get("beskrivelse", "Not available")
        employees = data.get("antallAnsatte", 0)
        return {"name": name, "description_no": description_no, "description_en": description_en, "website": website, "sector": sector, "employees": employees}
    except requests.exceptions.HTTPError as e:
        return f"Error: Organisation number not found or API error ({e.response.status_code})."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the API. {e}"

# --- UPDATED: Robust State Management Initialization ---
# We now initialize every key the app will use with a default value.
# This prevents AttributeError crashes.
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
    st.session_state.org_nr = ""
    st.session_state.startup_name = ""
    st.session_state.business_description = ""
    st.session_state.website = ""
    st.session_state.sector = ""
    st.session_state.employees = 0
    st.session_state.mapped_sdgs = {}
    st.session_state.prioritized_sdgs = []
    st.session_state.goals_and_kpis = {}
    st.session_state.integration_plan = {}
    st.session_state.reporting_framework = "Not Selected"

# --- APP LAYOUT AND PAGES ---
st.set_page_config(page_title="SDG Startup Tool", layout="wide")
st.sidebar.title("🚀 SDG Tool Navigation")

# ==============================================================================
# PAGE 1: SIMPLIFIED SETUP PAGE
# ==============================================================================
if not st.session_state.setup_complete:
    st.title("Welcome to the SDG Startup Tool")
    st.write("Enter your company's Norwegian Organisation Number to begin.")

    def start_analysis():
        if st.session_state.org_nr:
            with st.spinner("Fetching and translating data..."):
                fetched_data = fetch_brreg_data(st.session_state.org_nr)
                if isinstance(fetched_data, dict):
                    st.session_state.startup_name = fetched_data['name']
                    st.session_state.business_description = fetched_data['description_en']
                    st.session_state.website = fetched_data['website']
                    st.session_state.sector = fetched_data['sector']
                    st.session_state.employees = fetched_data['employees']
                    st.session_state.setup_complete = True
                else:
                    st.error(fetched_data)
        else:
            st.warning("Please enter an Organisation Number.")

    st.text_input("Norwegian Organisation Number", key="org_nr")
    st.caption("Enter the 9-digit number without any spaces or letters.")
    st.button("Find Company & Start Analysis", on_click=start_analysis)

# ==============================================================================
# MAIN APPLICATION PAGES
# ==============================================================================
else:
    page = st.sidebar.radio(
        "Choose a step:",
        ["🏠 Home", "1. Map SDGs", "2. Prioritize SDGs", "3. Set Goals & KPIs",
         "4. Integrate Strategy", "5. Select Framework", "6. Generate Report"]
    )
    
    st.title(f"SDG Tool for: {st.session_state.startup_name}")
    st.markdown("---")
    
    if page == "🏠 Home":
        st.header("Company Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="👥 Number of Employees", value=st.session_state.employees)
        with col2:
            st.markdown(f"**🌐 Website:** [{st.session_state.website}](http://{st.session_state.website})")
        st.markdown(f"** sectoral Activity Sector:** {st.session_state.sector}")
        st.subheader("Business Description (for SDG Mapping)")
        st.info(f"*{st.session_state.business_description}*")

    elif page == "1. Map SDGs":
        st.header("1. SDG Mapping & Relevance Assessment")
        description_words = st.session_state.business_description.lower().split()
        mapped = {}
        for code, data in SDG_DATA.items():
            if any(keyword in description_words for keyword in data["keywords"]):
                mapped[code] = data["title"]
        st.session_state.mapped_sdgs = mapped
        if not st.session_state.mapped_sdgs:
            st.warning("No relevant SDGs found based on your business description.")
        else:
            st.success(f"Found {len(st.session_state.mapped_sdgs)} relevant SDGs:")
            for code, title in st.session_state.mapped_sdgs.items():
                st.markdown(f"- **{code}:** {title}")

    elif page == "2. Prioritize SDGs":
        st.header("2. Prioritization & Impact Analysis")
        if not st.session_state.mapped_sdgs:
            st.warning("Please run Step 1 to map your SDGs first.")
        else:
            scored_sdgs = []
            description_words = st.session_state.business_description.lower().split()
            for code, title in st.session_state.mapped_sdgs.items():
                relevance = sum(1 for keyword in SDG_DATA[code]["keywords"] if keyword in description_words)
                opportunity = len(title) % 5
                total_score = relevance + opportunity
                scored_sdgs.append((total_score, code, title))
            scored_sdgs.sort(reverse=True)
            st.session_state.prioritized_sdgs = scored_sdgs
            st.write("Here are your relevant SDGs, prioritized by a simulated impact score:")
            for i, (score, code, title) in enumerate(st.session_state.prioritized_sdgs):
                st.metric(label=f"{i+1}. {code}", value=title, delta=f"Score: {score}")

    elif page == "3. Set Goals & KPIs":
        st.header("3. Goal Setting & KPIs")
        if not st.session_state.mapped_sdgs:
            st.warning("Please run Step 1 to map your SDGs first.")
        else:
            sdg_options = list(st.session_state.mapped_sdgs.keys())
            selected_sdg = st.selectbox("Select an SDG to set a goal for:", options=sdg_options)
            goal = st.text_input(f"Enter a specific goal for {selected_sdg}:")
            kpi = st.text_area(f"Enter the KPI to measure this goal:")
            if st.button("Save Goal"):
                st.session_state.goals_and_kpis[selected_sdg] = {"goal": goal, "kpi": kpi}
                st.success(f"Goal for {selected_sdg} has been saved!")
            if st.session_state.goals_and_kpis:
                st.write("---")
                st.subheader("Saved Goals:")
                for code, data in st.session_state.goals_and_kpis.items():
                    st.markdown(f"**{code}** | **Goal:** {data['goal']} | **KPI:** {data['kpi']}")

    elif page == "4. Integrate Strategy":
        st.header("4. Integration Tools")
        if not st.session_state.goals_and_kpis:
            st.warning("Please set at least one goal in Step 3 first.")
        else:
            goal_options = list(st.session_state.goals_and_kpis.keys())
            selected_goal = st.selectbox("Select a goal to integrate:", options=goal_options)
            department = st.text_input("Which department is responsible? (e.g., R&D)")
            action_item = st.text_area("What is the specific action item for them?")
            if st.button("Save Integration"):
                st.session_state.integration_plan[selected_goal] = {"department": department, "action_item": action_item}
                st.success(f"Integration plan for {selected_goal} has been saved!")
            if st.session_state.integration_plan:
                st.write("---")
                st.subheader("Saved Integration Plans:")
                for code, data in st.session_state.integration_plan.items():
                    st.markdown(f"**{code} Goal -> Department: {data['department']}** | **Action:** {data['action_item']}")

    elif page == "5. Select Framework":
        st.header("5. Customizable Frameworks")
        frameworks = ["GRI", "IRIS", "B Corp", "SDG Compass"]
        selected_framework = st.selectbox("Select a reporting framework:", options=frameworks)
        st.session_state.reporting_framework = selected_framework
        st.success(f"Reporting framework set to: {st.session_state.reporting_framework}")

    elif page == "6. Generate Report":
        st.header("📄 Final SDG Impact Report")
        st.subheader("1. Relevant SDGs")
        if st.session_state.mapped_sdgs:
            for code, title in st.session_state.mapped_sdgs.items(): st.markdown(f"- **{code}:** {title}")
        else: st.info("Not yet defined.")
        st.subheader("2. Prioritized Impact Areas")
        if st.session_state.prioritized_sdgs:
            for _, code, title in st.session_state.prioritized_sdgs: st.markdown(f"- {code}: {title}")
        else: st.info("Not yet defined.")
        st.subheader("3. Goals and KPIs")
        if st.session_state.goals_and_kpis:
            for code, data in st.session_state.goals_and_kpis.items():
                st.markdown(f"**{code}**")
                st.markdown(f"  - **Goal:** {data['goal']}")
                st.markdown(f"  - **KPI:** {data['kpi']}")
        else: st.info("Not yet defined.")
        st.subheader("4. Strategy Integration")
        if st.session_state.integration_plan:
            for code, data in st.session_state.integration_plan.items():
                st.markdown(f"**{data['department']} Department**")
                st.markdown(f"  - **Action for {code}:** {data['action_item']}")
        else: st.info("Not yet defined.")
        st.subheader("5. Reporting Framework Alignment")
        st.markdown(f"- **Framework:** {st.session_state.reporting_framework}")
