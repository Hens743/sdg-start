import streamlit as st
import requests # New library for making API calls

# --- Data and Logic ---

# Expanded SDG_DATA dictionary for better matching
SDG_DATA = {
    "SDG 7": {
        "title": "Affordable and Clean Energy",
        "keywords": ["energy", "renewable", "solar", "wind", "clean power", "electricity", "grid", "hydro", "geothermal"]
    },
    "SDG 9": {
        "title": "Industry, Innovation, and Infrastructure",
        "keywords": ["innovation", "infrastructure", "technology", "startup", "industrial", "internet", "manufacturing", "entrepreneurship"]
    },
    "SDG 11": {
        "title": "Sustainable Cities and Communities",
        "keywords": ["cities", "urban", "sustainability", "community", "housing", "transport", "public spaces", "smart city", "resilience"]
    },
    "SDG 12": {
        "title": "Responsible Consumption and Production",
        "keywords": ["sustainability", "recycling", "circular economy", "efficiency", "waste", "supply chain", "production", "consumption"]
    },
    "SDG 13": {
        "title": "Climate Action",
        "keywords": ["climate", "emissions", "renewable", "carbon footprint", "greenhouse gas", "adaptation", "fossil fuels"]
    },
}

# --- NEW: Function to fetch data from Brønnøysundregistrene ---
def fetch_brreg_data(org_nr):
    """Fetches business description from the Brønnøysundregistrene API."""
    if not org_nr.isdigit() or len(org_nr) != 9:
        return "Error: Please enter a valid 9-digit organisation number."

    url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org_nr}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # The 'formal' (purpose) is often nested. We look for it.
            purpose = data.get("formal", {}).get("virksomhet", "No official purpose found.")
            return purpose if purpose else "No official purpose found."
        elif response.status_code == 404:
            return "Error: Organisation number not found."
        else:
            return f"Error: API returned status code {response.status_code}."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the API. {e}"

# --- State Management ---
if 'startup_name' not in st.session_state:
    st.session_state.startup_name = ""
    st.session_state.org_nr = ""
    st.session_state.business_description = ""
    st.session_state.mapped_sdgs = {}
    st.session_state.prioritized_sdgs = []
    st.session_state.goals_and_kpis = {}
    st.session_state.integration_plan = {}
    st.session_state.reporting_framework = "Not Selected"
    st.session_state.setup_complete = False

# --- App Layout and Pages ---

st.set_page_config(page_title="SDG Startup Tool", layout="wide")
st.sidebar.title("🚀 SDG Tool Navigation")

if not st.session_state.setup_complete:
    st.title("Welcome to the SDG Startup Tool")
    st.write("Enter your startup's details manually or fetch them from Brønnøysundregistrene.")

    # --- NEW: Updated setup section with API integration ---
    st.session_state.startup_name = st.text_input("Startup Name", st.session_state.startup_name)
    st.session_state.org_nr = st.text_input("Norwegian Organisation Number (9 digits)", st.session_state.org_nr)

    if st.button("🤖 Fetch Information from Brønnøysundregistrene"):
        with st.spinner("Fetching data..."):
            fetched_description = fetch_brreg_data(st.session_state.org_nr)
            if "Error:" not in fetched_description:
                st.session_state.business_description = fetched_description
                st.success("Information fetched successfully!")
            else:
                st.error(fetched_description)

    st.info(
        "**How to write a good description:** Use clear keywords about your industry, "
        "products, and services (e.g., 'solar energy', 'recycling technology', 'sustainable housing')."
    )
    st.session_state.business_description = st.text_area(
        "Business Description (fetched data can be edited here)",
        st.session_state.business_description, height=150
    )

    if st.button("Save and Continue"):
        if st.session_state.startup_name and st.session_state.business_description:
            st.session_state.setup_complete = True
            st.rerun()
        else:
            st.error("Please ensure Startup Name and Business Description are filled in.")
else:
    # The rest of the app pages remain the same as before
    page = st.sidebar.radio(
        "Choose a step:",
        ["🏠 Home", "1. Map SDGs", "2. Prioritize SDGs", "3. Set Goals & KPIs",
         "4. Integrate Strategy", "5. Select Framework", "6. Generate Report"]
    )
    st.title(f"SDG Tool for: {st.session_state.startup_name}")
    st.markdown("---")
    
    # ... (The code for the different pages from the previous version goes here) ...
    # ... (This part is unchanged) ...
    if page == "🏠 Home":
        st.header("Welcome!")
        st.write("You can navigate through the different steps using the menu on the left.")
        st.info(f"**Current Business Description:** *'{st.session_state.business_description}'*")

    elif page == "1. Map SDGs":
        st.header("1. SDG Mapping & Relevance Assessment")
        st.write("This step maps your business description to relevant SDGs.")
        
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
                    st.markdown(f"**{code}**")
                    st.markdown(f"- **Goal:** {data['goal']}")
                    st.markdown(f"- **KPI:** {data['kpi']}")

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
                    st.markdown(f"**{code} Goal -> Department: {data['department']}**")
                    st.markdown(f"- **Action:** {data['action_item']}")

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
