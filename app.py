import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
import os

from ai_service_openrouter import get_wellness_advice

import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

st.set_page_config(
    page_title="Employee Burnout Coach",
    page_icon="🔥",
    layout="wide"
)

@st.cache_resource
def load_model():
    try:
        with open('employee_burnout_model.pkl', 'rb') as file:
            data = pickle.load(file)
        return data['model'], data['columns']
    except FileNotFoundError:
        st.error("Model file not found. Please ensure 'employee_burnout_model.pkl' is in the same directory.")
        return None, None

model, model_columns = load_model()


# --- Helper Functions ---
def prepare_input_data(user_inputs, expected_columns):
    input_df = pd.DataFrame([user_inputs])

    input_df['Date of Joining'] = pd.to_datetime(input_df['Date of Joining'])
    input_df['Days_Since_Joining'] = (datetime.now() - input_df['Date of Joining']).dt.days
    input_df = input_df.drop('Date of Joining', axis=1)

    # One-hot encode categorical features
    input_df = pd.get_dummies(input_df, columns=['Gender', 'Company Type', 'WFH Setup Available'], drop_first=True)

    final_df = pd.DataFrame(0, index=[0], columns=expected_columns)
    
    # Update with actual values from input_df
    for col in input_df.columns:
        if col in final_df.columns:
            final_df[col] = input_df[col].values
    
    final_df = final_df.infer_objects(copy=False)
    final_df = final_df[expected_columns]

    return final_df

def get_risk_category(score):
    """Categorizes the burnout score."""
    if score < 0.4:
        return "Low", "💚"
    elif score < 0.7:
        return "Moderate", "💛"
    else:
        return "High", "❤️"

st.title("🧠 Your Personal AI Burnout Coach")
st.markdown("Enter your current work metrics in the sidebar to get a burnout risk assessment and personalized coaching advice.")

with st.sidebar:
    st.header("📊 Your Work Metrics")
    st.markdown("Adjust the sliders and options below to reflect your current work situation.")

    date_of_joining = st.date_input(
        "Date of Joining",
        datetime(2022, 1, 1),
        help="Select the date you started your current role. This helps calculate your tenure, a factor in burnout risk."
    )
    gender = st.selectbox(
        "Gender",
        ["Male", "Female"],
        help="Select your gender."
    )
    company_type = st.selectbox(
        "Company Type",
        ["Service", "Product"],
        help="Select whether your company primarily offers services or products."
    )
    wfh_available = st.selectbox(
        "WFH Setup Available",
        ["Yes", "No"],
        help="Indicate if you have the option to work from home."
    )
    designation = st.slider(
        "Job Designation Level", 0, 5, 2,
        help="Your job level or seniority, where 0 is entry-level and 5 is senior leadership."
    )
    resource_allocation = st.slider(
        "Resource Allocation (Projects)", 1, 10, 3,
        help="How many projects or major tasks are you currently handling? A higher number can indicate a heavier workload."
    )
    mental_fatigue = st.slider(
        "Mental Fatigue Score", 0.0, 10.0, 5.0, 0.5,
        help="Your self-assessed level of mental exhaustion. 0 means you feel sharp and focused, while 10 means you feel completely drained."
    )

    analyze_button = st.button("Analyze & Get Advice", type="primary", use_container_width=True)


if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

if analyze_button and model is not None:
    st.session_state.analysis_done = True
    st.session_state.messages = []

    user_data_input = {
        'Date of Joining': date_of_joining,
        'Gender': gender,
        'Company Type': company_type,
        'WFH Setup Available': wfh_available,
        'Designation': float(designation),
        'Resource Allocation': float(resource_allocation),
        'Mental Fatigue Score': mental_fatigue
    }

    input_df_final = prepare_input_data(user_data_input, model_columns)
    burnout_prediction = model.predict(input_df_final)[0]

    risk_category, emoji = get_risk_category(burnout_prediction)
    st.session_state.user_data = {
        **user_data_input,
        'burn_rate': burnout_prediction,
        'risk_category': risk_category,
        'emoji': emoji,
        'Days_Since_Joining': (datetime.now() - datetime.combine(date_of_joining, datetime.min.time())).days
    }
    
    with st.spinner("Your AI coach is analyzing your results..."):
        initial_advice = get_wellness_advice(st.session_state.user_data)
    
    st.session_state.initial_advice = initial_advice
    # Add initial advice as the first message in the chat
    st.session_state.messages.append({"role": "assistant", "content": initial_advice})


if st.session_state.analysis_done:
    data = st.session_state.user_data
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Your Burnout Risk Analysis")
        st.metric(
            label="Predicted Burnout Score",
            value=f"{data['burn_rate']:.2f} / 1.0",
            help="This score predicts your risk of burnout on a scale from 0 (low) to 1 (high)."
        )
        st.markdown(f"### Risk Category: **{data['risk_category']} {data['emoji']}**")
        with st.expander("See your input data"):
            st.write(data)

    with col2:
        st.subheader("Chat with Your AI Coach")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a follow-up question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking..."):
                try:
                    full_response = get_wellness_advice({
                        **st.session_state.user_data,
                        "follow_up_question": prompt
                    })
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"An error occurred with the AI chat service: {e}")
                    full_response = "I'm sorry, I'm having trouble connecting right now. Please try again later."
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            st.rerun()

else:
    st.info("Please enter your daily stats in the sidebar and click 'Analyze & Get Advice' to begin.")

