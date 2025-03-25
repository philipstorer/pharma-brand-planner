# app.py
import streamlit as st
import pandas as pd
import openai
import requests
from bs4 import BeautifulSoup

# === CONFIG ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
st.set_page_config(page_title="Pharma Brand Planner", layout="wide")

# === LOAD EXCEL FILE ===
@st.cache_data
def load_data():
    xls = pd.ExcelFile("SI Tool.xlsx")
    tab1 = xls.parse('Tab 1')
    tab2 = xls.parse('Tab 2')
    tab3 = xls.parse('Tab 3')
    tab4 = xls.parse('Tab 4')
    return tab1, tab2, tab3, tab4

tab1, tab2, tab3, tab4 = load_data()

# === STEP 1: Select Product Lifecycle ===
st.sidebar.title("Brand Planning Tool")
st.header("Step 1: Select Where You Are in the Product Lifecycle")

product_lifecycle_options = list(tab1.iloc[0, 1:].dropna())
product_lifecycle = st.radio("Choose one:", product_lifecycle_options)

# === STEP 2: Select Strategic Imperatives ===
st.header("Step 2: Select Strategic Imperatives")
selected_col_idx = tab1.iloc[0].tolist().index(product_lifecycle)
strategic_rows = tab1.iloc[1:]
strategic_imperatives = strategic_rows[strategic_rows.iloc[:, selected_col_idx] == 'x']["Strategic Imperatives"].dropna().tolist()
selected_si = st.multiselect("Choose relevant imperatives:", strategic_imperatives)

# === STEP 3: Product Differentiators ===
st.header("Step 3: Select Product Differentiators")
categories = tab2.columns.tolist()
selected_category = st.selectbox("Choose a differentiator category:", categories)
options = tab2[selected_category].dropna().tolist()
selected_diff = st.multiselect("Select differentiators from this category:", options)

# === STEP 4: Optional Brand Tone ===
st.header("Step 4: Select Optional Brand Tone")
brand_tones = tab3.iloc[:, 0].dropna().tolist()
selected_tone = st.multiselect("Choose brand tone(s):", brand_tones)

# === STEP 5: Select Strategic Objective ===
st.header("Step 5: Select Strategic Objective")
objectives = tab4.columns[1:].tolist()
selected_objectives = st.multiselect("Select your strategic objectives:", objectives)

# === STEP 6: Generate Tactics ===
if st.button("Generate Tactics Plan"):
    st.subheader("Tactics Aligned to Your Strategic Imperatives")
    output_df = pd.DataFrame()
    output_df = pd.DataFrame()

    
for si in selected_si:
    matches = tab4[tab4['Strategic Challenge'] == si]
    if not matches.empty:
        for obj in selected_objectives:
            if obj in matches.columns:
                tactics = matches[obj].dropna().tolist()
                for tactic in tactics:
                    if pd.isna(tactic):
                        continue

                    # AI prompt to describe tactic
                    prompt = f"""
                    You are a pharmaceutical marketing strategist. Write a short 3-4 sentence rationale describing why the following tactic: '{tactic}' aligns with the selected strategic imperative: '{si}', the differentiator(s): {', '.join(selected_diff)}, and the tone(s): {', '.join(selected_tone)}.
                    """
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.6
                        )
                        desc = response['choices'][0]['message']['content']
                    except Exception as e:
                        desc = f"AI description not available: {e}"

                    est_time = "4–6 weeks"
                    est_cost = "$15,000–$25,000"                    row_df = pd.DataFrame([{
                        "Strategic Imperative": si,
                        "Tactic": tactic,
                        "AI Description": desc,
                        "Est. Timing": est_time,
                        "Est. Cost": est_cost
                    }])
                    output_df = pd.concat([output_df, row_df], ignore_index=True)

                if pd.isna(tactic):
                    continue

                # AI prompt to describe tactic
                prompt = f"""
                You are a pharmaceutical marketing strategist. Write a short 3-4 sentence rationale describing why the following tactic: '{tactic}' aligns with the selected strategic imperative: '{si}', the differentiator(s): {', '.join(selected_diff)}, and the tone(s): {', '.join(selected_tone)}.
                """
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6
                    )
                    desc = response['choices'][0]['message']['content']
                except Exception as e:
                    desc = f"AI description not available: {e}"

                est_time = "4–6 weeks"
                est_cost = "$15,000–$25,000"                    row_df = pd.DataFrame([{
                        "Strategic Imperative": si,
                        "Tactic": tactic,
                        "AI Description": desc,
                        "Est. Timing": est_time,
                        "Est. Cost": est_cost
                    }])
                    output_df = pd.concat([output_df, row_df], ignore_index=True)

    if output_df.empty:
        st.warning("No tactics were found based on your selected imperatives and objectives.")
    else:
        st.dataframe(output_df)

    # === STEP 7: Messaging Ideas ===
        st.subheader("5 Key Messaging Ideas")

    if not selected_si or not selected_diff or not selected_tone:
        st.warning("Please make sure you've selected strategic imperatives, differentiators, and tone before generating messaging ideas.")
    else:
        msg_prompt = f"""
        Based on the strategic imperatives: {', '.join(selected_si)},
        product differentiators: {', '.join(selected_diff)},
        and tone: {', '.join(selected_tone)},
        generate 5 pharma marketing message ideas.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": msg_prompt}],
                temperature=0.7
            )
            ideas = response['choices'][0]['message']['content']
            st.markdown(ideas)
        except Exception as e:
            st.error(f"Message generation failed: {e}")}.
    """
    try:
        response2 = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": concept_prompt}],
            temperature=0.7
        )
        st.markdown(response2['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"Campaign concept generation failed: {e}")

    # === STEP 9: Competitive Insights ===
    st.subheader("Competitive Intelligence")
    drug_name = st.text_input("Enter your drug name to generate competitive insights:")
    if st.button("Get Competitive Insights"):
        search_url = f"https://www.google.com/search?q={drug_name}+site:drugs.com"
        st.info(f"Searching online for competitors to {drug_name}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")

            count = 0
            for link in links:
                href = link.get("href")
                if href and "drugs.com" in href and "/compare/" in href:
                    name = href.split("compare/")[-1].replace("+vs+", " vs ")
                    st.write(f"**Competitor Comparison Found:** {name}")
                    count += 1
                    if count > 2:
                        break

            if count == 0:
                st.write("No direct competitors found.")

        except Exception as e:
            st.error(f"Error during competitor search: {e}")
