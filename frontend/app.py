import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="RentMachine", layout="wide")

st.title("AWS EC2 RentMachine")

# Sidebar for Navigation
page = st.sidebar.selectbox("Navigation", ["User Dashboard", "Admin Panel"])

if page == "User Dashboard":
    st.header("My Instances")
    
    # Mock User ID for demo
    user_id = st.text_input("Enter User ID", value="user_123")
    
    if st.button("Refresh"):
        pass # Just re-runs script
    
    # In a real app, we would fetch instances by user_id from API.
    # But current API doesn't support filtering by user_id yet. 
    # Let's add that or just mock it for now.
    st.info("Fetching instances functionality to be implemented in API.")

    st.subheader("Rent New Instance")
    region = st.selectbox("Region", ["us-east-1", "us-west-1", "eu-central-1"])
    
    if st.button("Deploy New Instance"):
        with st.spinner("Deploying..."):
            try:
                res = requests.post(f"{API_URL}/deploy", json={"user_id": user_id, "region": region})
                if res.status_code == 200:
                    data = res.json()["data"]
                    st.success(f"Deployed! Instance ID: {data['instance_id']}")
                    st.json(data)
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

elif page == "Admin Panel":
    st.header("Admin Panel")
    
    st.subheader("Add AWS Account")
    with st.form("add_account"):
        access_key = st.text_input("Access Key")
        secret_key = st.text_input("Secret Key", type="password")
        regions = st.multiselect("Regions", ["us-east-1", "us-west-1", "eu-central-1"], default=["us-east-1"])
        quota = st.number_input("Quota", min_value=1, value=10)
        submitted = st.form_submit_button("Add Account")
        
        if submitted:
            payload = {
                "access_key": access_key,
                "secret_key": secret_key,
                "regions": regions,
                "total_quota": quota
            }
            try:
                res = requests.post(f"{API_URL}/admin/accounts", json=payload)
                if res.status_code == 200:
                    st.success("Account Added!")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
