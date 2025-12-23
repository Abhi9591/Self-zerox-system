# Self Xerox Kiosk System

A complete kiosk system for self-service xerox machines, including a backend API, Kiosk interface, Admin dashboard, and Mobile upload interface.

## Prerequisites

Before running the application, ensure you have the following installed:
- **Python 3.10+**
- **PostgreSQL**: Running on `localhost:5432` (or as configured in `.env`)
- **MinIO**: Running on `localhost:9000` (or as configured in `.env`)
- **PDF Printer**: A printer named "PDF_Printer" (or as configured in `.env`)

## Project Structure

- `backend/`: FastAPI application, database models, and routes.
- `frontend/kiosk/`: Interface for the Kiosk machine.
- `frontend/admin/`: Administrator dashboard.
- `frontend/mobile/`: Mobile interface for document upload.

## Step-by-Step Setup

### 1. Backend Setup

Open your terminal and navigate to the `backend` directory:

```bash
cd backend
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create or update the `.env` file in the `backend` directory with your local settings (Database, S3/MinIO, Printer).

#### Database Setup
Run the following commands to initialize the database and seed default data:

```bash
# Setup PostgreSQL tables
python setup_postgres.py

# Seed default data (Admin user, Machines, etc.)
python seed_db.py
```

### 2. Running the Server

Start the FastAPI server using Uvicorn:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be accessible at `http://localhost:8000`.

## Accessing the Interfaces

Once the server is running, you can access the different parts of the system:

- **Kiosk Interface**: [http://localhost:8000/kiosk/](http://localhost:8000/kiosk/)
- **Admin Dashboard**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
  - **Login**: `admin` / `password`
- **Mobile Upload**: [http://localhost:8000/mobile/upload.html](http://localhost:8000/mobile/upload.html)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Automatic Setup (Windows)

For Windows users, you can use the provided batch file to install dependencies, setup the database, and start the server automatically:

```bash
cd backend
run.bat
```
