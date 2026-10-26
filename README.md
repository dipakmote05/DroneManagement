# 🚁 Drone Mission Platform

A web-based platform for managing drone service requests, assigning operators, coordinating missions, and viewing drone telemetry and location data. The project uses a **Flask REST API** for the backend and a **Streamlit** interface for client and operator workflows.

## ✨ Features

- **Role-based access:** Separate client and operator experiences.
- **Authentication:** Signup/login flows with JWT-protected API routes.
- **Drone service requests:** Clients can request services such as mapping, surveillance, and healthcare.
- **Operator workflow:** Operators can view pending requests and accept or reject them.
- **Mission management:** Mission pages support ready and active mission workflows.
- **Drone telemetry:** Backend routes handle telemetry and provide the latest stored data.
- **Location tracking:** Client pages can display target/drone coordinates on a map when location data is available.
- **Background telemetry polling:** A scheduler periodically calls the telemetry storage endpoint.
- **Email/SMS OTP utilities:** Optional helpers are included for email and Twilio SMS verification.

> **Note:** Actual live flight control, camera streaming, GPS hardware integration, and third-party authentication depend on the connected hardware/services and configuration. A dashboard or telemetry endpoint alone does not guarantee a physical drone is connected.

## 🧰 Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Python, Streamlit, Requests, Pandas |
| Backend | Python, Flask, Flask-CORS, Flask-SQLAlchemy |
| Database | MySQL via PyMySQL |
| Authentication | JWT; optional Google OAuth token verification |
| Optional messaging | SMTP email, Twilio SMS |
| API style | REST endpoints under `/api/...` |

## 📁 Project Structure

```text
drone-mission-platform-main/
├── backend/
│   ├── app.py                 # Flask application and API registration
│   ├── config.py              # Application/database configuration
│   ├── requirements.txt       # Backend Python dependencies
│   ├── auth/                  # Authentication, JWT, OTP helpers and routes
│   ├── database/              # Database setup
│   ├── drone/                 # Drone control, navigation, sensors and telemetry
│   ├── mission/               # Mission routes, state and capture logic
│   ├── orders/                # Drone service request/order logic
│   ├── users/                 # User routes and models
│   ├── utils/                 # Geo, email OTP and SMS OTP helpers
│   └── telemetry_scheduler.py # Periodic telemetry-store requests
├── frontend streamlite/
│   ├── app.py                 # Streamlit entry/router
│   └── pages/
│       ├── login_app.py
│       ├── signup_app.py
│       ├── client_dashboard.py
│       ├── new_request_page.py
│       ├── track_drone.py
│       ├── track_simple.py
│       ├── operator_dashboard.py
│       ├── requests_page.py
│       └── mission_page.py
└── docs/                      # Architecture/API documentation (if populated)
```

## ✅ Prerequisites

- Python 3.10 or newer recommended
- MySQL Server
- `pip` and Python virtual environment support
- Git (optional)

## ⚙️ Setup and Installation

### 1. Extract the project and enter its directory

```bash
unzip drone-mission-platform-main.zip
cd drone-mission-platform-main
```

If you already cloned/downloaded the project, enter the extracted project folder instead.

### 2. Create and activate a virtual environment

**Ubuntu/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

The current `requirements.txt` may not list every package imported by the project. If you see `ModuleNotFoundError`, install the missing package in the active virtual environment. Common project imports include:

```bash
pip install flask flask-cors flask-sqlalchemy pymysql python-dotenv requests pandas streamlit PyJWT google-auth twilio
```

Return to the project root when you need to start the frontend:

```bash
cd ..
```

### 4. Configure MySQL

Start MySQL on Ubuntu:

```bash
sudo systemctl start mysql
sudo systemctl status mysql
```

Open the MySQL shell:

```bash
sudo mysql
```

Create a database and a dedicated database user. Choose your own secure password:

```sql
CREATE DATABASE drone_platform;
CREATE USER 'drone_user'@'localhost' IDENTIFIED BY 'replace_with_a_strong_password';
GRANT ALL PRIVILEGES ON drone_platform.* TO 'drone_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure environment variables

Create a `.env` file inside the `backend/` directory. The backend loads environment variables through `python-dotenv`.

```env
SECRET_KEY=replace_with_a_long_random_secret
DATABASE_URL=mysql+pymysql://drone_user:replace_with_a_strong_password@localhost/drone_platform

# Optional: configure these only if using email OTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_app_password

# Optional: configure these only if using Twilio SMS
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE=your_twilio_phone_number
```

Use URL-encoding for special characters in database passwords. Never commit `.env`, real credentials, OTPs, or API secrets to Git.

The Google authentication helper currently contains a placeholder client ID. Configure it with your own Google OAuth client ID before using that flow.

### 6. Start the Flask backend

From the project root:

```bash
cd backend
python app.py
```

The API runs on:

```text
http://127.0.0.1:5000
```

Check the health endpoint in a browser or with curl:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "OK",
  "message": "Drone backend running"
}
```

The application creates its SQLAlchemy tables during startup. Ensure the MySQL database exists and the configured user has the required permissions.

### 7. Start the Streamlit frontend

Open a **second terminal**, activate the same virtual environment, and run:

```bash
cd "drone-mission-platform-main/frontend streamlite"
streamlit run app.py
```

If you are already in the project root, use:

```bash
cd "frontend streamlite"
streamlit run app.py
```

Streamlit will print a local address, usually `http://localhost:8501`. Open that address in your browser.

The frontend currently calls the backend at `http://127.0.0.1:5000`. If you change the backend host or port, update the API base URLs in the frontend files as well.

## 🧭 Typical Workflow

1. Create an account or sign in.
2. A client can select a service, enter the target latitude/longitude, select an operator, and submit a request.
3. An operator opens the requests page and accepts or rejects pending requests.
4. The operator uses Mission Control to work with a ready or active mission.
5. The client dashboard/tracking page displays available request status and location/telemetry information.

Available screens and actions depend on the current database state and which backend endpoints are operational.

## 🔌 API Overview

The Flask app registers these route groups:

| Prefix | Purpose |
|---|---|
| `/health` | Backend health check |
| `/api/auth` | Authentication |
| `/api/users` | User-related operations |
| `/api/orders` | Drone service requests and order lifecycle |
| `/api/drone` | Drone telemetry and drone operations |
| `/api/mission` | Mission operations |

For exact endpoint paths, request bodies, and authorization requirements, inspect the route files under `backend/auth/`, `backend/users/`, `backend/orders/`, `backend/drone/`, and `backend/mission/`.

Protected routes may require a bearer token in the request header:

```http
Authorization: Bearer <your_jwt_token>
```

## 🛠️ Troubleshooting

- **MySQL connection error:** Confirm MySQL is running, the database exists, and `DATABASE_URL` matches your database credentials.
- **`ModuleNotFoundError`:** Activate your virtual environment and install the missing dependency.
- **Frontend cannot connect to backend:** Start Flask first and check that the frontend API URL matches the backend address.
- **401/403 API response:** Sign in again and check that the JWT is valid and the account has the required role.
- **No drone location or telemetry:** Check the telemetry endpoints, database records, scheduler logs, and any configured hardware/sensor integration.
- **Email/SMS OTP fails:** Verify the relevant SMTP/Twilio environment variables and account configuration.
- **Google login fails:** Replace the placeholder Google client ID with a configured OAuth client ID.

## 🔐 Security Notes

- Replace development secrets with strong, private values.
- Do not use default/demo database passwords in production.
- Keep `.env` out of version control.
- Use HTTPS and production-grade server configuration before deployment.
- Validate and authorize every API request; do not rely only on frontend role checks.
- Review OTP expiry, rate limiting, token expiry, and credential handling before deploying publicly.
- Run the telemetry scheduler as a single controlled process in production to avoid duplicate polling loops when multiple workers are started.

## 🚧 Future Improvements

- Add automated backend and API tests.
- Add deployment instructions and production configuration.
- Document each API endpoint with sample request/response payloads.
- Add robust hardware integration and explicit drone connection status.
- Add mission history, telemetry charts, and stronger error reporting.
- Add configuration for the backend API URL instead of hard-coding it in frontend pages.

## 📄 License

No license is specified in the provided project files. Add a license file before redistributing or publishing the project.
