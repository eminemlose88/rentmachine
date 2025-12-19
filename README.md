# RentMachine: AWS Multi-Account EC2 Management System

This system automates the management and distribution of AWS EC2 instances across multiple accounts. It features automated deployment, monitoring, and self-healing capabilities.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **Database**: MongoDB (Motor/AsyncIO)
- **Scheduling**: APScheduler (In-process)
- **Cloud Provider**: AWS (Boto3)

## Prerequisites

- Python 3.9+
- MongoDB (Local or Atlas)
- AWS Accounts (Access Key & Secret Key)

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```ini
    MONGODB_URL=mongodb://localhost:27017
    DATABASE_NAME=rentmachine
    SECRET_KEY=your-secret-key
    ```

3.  **Run Backend**
    ```bash
    uvicorn backend.app.main:app --reload
    ```
    API Docs: http://localhost:8000/docs

4.  **Run Frontend**
    ```bash
    streamlit run frontend/app.py
    ```
    UI: http://localhost:8501

## Features

- **Automated Deployment**: Dispatches EC2 instances across available AWS accounts.
- **Auto-Replenishment**: Automatically detects prematurely terminated instances and re-deploys them.
- **Account Management**: Handles AWS credentials and quotas.
- **Monitoring**: Periodically checks instance status and updates public IP.
- **User Data Injection**: Sets root password and enables SSH access automatically.

## Project Structure

```
rentmachine/
├── backend/
│   ├── app/
│   │   ├── api/          # API Routes
│   │   ├── core/         # Config & Security
│   │   ├── db/           # Database Connection & Models
│   │   ├── services/     # Business Logic (AWS, Account, Monitor)
│   │   └── main.py       # App Entry Point
├── frontend/
│   └── app.py            # Streamlit Dashboard
├── scripts/              # Utilities
└── requirements.txt
```
