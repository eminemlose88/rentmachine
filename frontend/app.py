import streamlit as st
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Since we are running in the same container/network, we use localhost
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="RentMachine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .sidebar .sidebar-content {
        background: #ffffff
    }
    .stButton>button {
        width: 100%;
    }
    .status-running {
        color: #0f9d58;
        font-weight: bold;
    }
    .status-pending {
        color: #f4b400;
        font-weight: bold;
    }
    .status-terminated {
        color: #db4437;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 RentMachine Dashboard")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["My Instances", "Deploy New", "Admin Panel"])

st.sidebar.markdown("---")
st.sidebar.caption("RentMachine v1.0")

if page == "My Instances":
    st.header("📋 My Instances")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_id = st.text_input("User ID", value="user_123", help="Simulating login")
    with col2:
        st.write("") # Spacer
        st.write("") # Spacer
        if st.button("🔄 Refresh"):
            st.rerun()

    try:
        res = requests.get(f"{API_URL}/instances", params={"user_id": user_id})
        if res.status_code == 200:
            instances = res.json()
            if instances:
                # Prepare data for DataFrame
                data = []
                for inst in instances:
                    status_icon = "⚪"
                    if inst['status'] == 'running': status_icon = "🟢"
                    elif inst['status'] == 'pending': status_icon = "🟡"
                    elif inst['status'] == 'terminated': status_icon = "🔴"
                    
                    data.append({
                        "ID": inst.get('instance_id', 'N/A'),
                        "Region": inst.get('region', 'N/A'),
                        "Public IP": inst.get('public_ip', 'Pending...'),
                        "Password": inst.get('initial_password', '******'),
                        "Status": f"{status_icon} {inst.get('status', 'unknown').upper()}",
                        "Launch Time": inst.get('launch_time', '').split('T')[0]
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(
                    df, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Public IP": st.column_config.TextColumn("Public IP", help="Connect via SSH"),
                        "Password": st.column_config.TextColumn("Password", help="Root password"),
                    }
                )
            else:
                st.info("No instances found. Go to 'Deploy New' to rent one!")
        else:
            st.error(f"Failed to fetch instances. API Error: {res.status_code}")
    except Exception as e:
        st.error(f"Could not connect to backend. Is it running? Error: {e}")

elif page == "Deploy New":
    st.header("⚡ Deploy New Instance")
    
    with st.container():
        st.markdown("### Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", value="user_123")
            region = st.selectbox("Region", ["us-east-1", "us-west-1", "eu-central-1", "ap-northeast-1"])
        
        with col2:
            instance_type = st.selectbox("Instance Type", ["t2.micro (1 vCPU, 1GB RAM)", "t3.small (2 vCPU, 2GB RAM)"])
            duration = st.slider("Duration (Hours)", 1, 24, 1)

        st.markdown("### Summary")
        st.info(f"You are about to deploy a **{instance_type.split(' ')[0]}** instance in **{region}** for **{user_id}**.")
        
        if st.button("🚀 Launch Instance", type="primary"):
            with st.status("Processing deployment...", expanded=True) as status:
                st.write("🔍 Checking account availability...")
                time.sleep(1)
                st.write("📡 Contacting AWS API...")
                
                try:
                    res = requests.post(f"{API_URL}/deploy", json={"user_id": user_id, "region": region})
                    if res.status_code == 200:
                        data = res.json()["data"]
                        st.write("✅ Instance launched successfully!")
                        status.update(label="Deployment Complete!", state="complete", expanded=False)
                        
                        st.success(f"Instance Created! ID: `{data['instance_id']}`")
                        st.balloons()
                        
                        st.markdown("### 📝 Next Steps")
                        st.markdown(f"""
                        1. Go to **My Instances** to check the status.
                        2. Wait for the **Public IP** to be assigned (approx. 30s).
                        3. SSH into your machine using `root` and the generated password.
                        """)
                    else:
                        status.update(label="Deployment Failed", state="error")
                        st.error(f"Deployment failed: {res.text}")
                except Exception as e:
                    status.update(label="Connection Error", state="error")
                    st.error(f"Error connecting to backend: {e}")

elif page == "Admin Panel":
    st.header("🛠️ Admin Panel")
    
    password = st.text_input("Admin Password", type="password")
    if password == "admin123":  # Simple auth for demo
        tab1, tab2 = st.tabs(["Add Account", "System Logs"])
        
        with tab1:
            st.subheader("Add AWS Account")
            with st.form("add_account"):
                access_key = st.text_input("AWS Access Key ID")
                secret_key = st.text_input("AWS Secret Access Key", type="password")
                regions = st.multiselect("Allowed Regions", ["us-east-1", "us-west-1", "eu-central-1"], default=["us-east-1"])
                quota = st.number_input("Max Instances Quota", min_value=1, value=10)
                
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
                            st.success(f"Account added successfully! ID: {res.json()['id']}")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
        
        with tab2:
            st.write("System logs will appear here (Not implemented in this demo).")
    else:
        if password:
            st.error("Invalid password")
        else:
            st.info("Please enter admin password to proceed.")
