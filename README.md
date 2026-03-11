# AI Risk Manager

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-orange)

AI Risk Manager is an intelligent financial analytics platform designed to help businesses identify financial risks, analyze operational data, and forecast future financial trends using machine learning.

The system processes financial datasets such as clients, invoices, and transactions, then automatically generates insights including client risk scores, financial forecasts, and analytical dashboards.

---

# 🚀 Features

* 📊 Financial Data Analysis
* ⚠️ Automated Risk Detection
* 📈 Revenue Forecasting
* 🧠 Machine Learning–based Risk Prediction
* 📂 CSV Dataset Upload & Processing
* 📉 Interactive Financial Dashboards
* 👥 Client Behavior Analysis

---

# 🧠 Machine Learning Model

The system uses machine learning to analyze financial behavior and detect potential business risks.

### Capabilities

* Predict high-risk clients
* Detect abnormal financial patterns
* Analyze payment behavior
* Forecast future financial metrics

The trained model is stored locally and used for prediction during runtime.

---

# 🏗️ System Architecture

```mermaid
flowchart LR

A[User Uploads Financial Data] --> B[FastAPI Backend]
B --> C[Data Validation & Processing]
C --> D[Feature Engineering]
D --> E[Machine Learning Model]
E --> F[Risk Prediction & Forecasting]
F --> G[Interactive Dashboard]
```

---

# 🖥️ Screenshots

### Dashboard

<img src="screenshots/dashboard.png" width="800">

### Client Risk Analysis

<img src="screenshots/clients.png" width="800">

### Financial Forecast

<img src="screenshots/forecast.png" width="800">

*(Add screenshots to a folder named `screenshots` in the repo)*

---

# 🎬 Demo

<img src="demo/demo.gif" width="800">

*(Optional: Add a demo GIF showing dashboard interaction)*

---

# 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* FastAPI
* Python

### Machine Learning

* Scikit-learn
* Pandas
* NumPy

### Visualization

* Chart.js

---

# 📂 Project Structure

```
AI-Risk-Manager
│
├── core
│   ├── api.py
│   ├── business_risk.py
│   ├── forecast.py
│   ├── ingestion.py
│   ├── validator.py
│   └── visualizer.py
│
├── frontend
│   ├── dashboard.html
│   ├── forecast.html
│   ├── clients.html
│   ├── upload.html
│   ├── script.js
│   └── style.css
│
├── data
│   ├── clients.csv
│   ├── invoices.csv
│   └── transactions.csv
│
├── models_saved
│   └── churn_model.pkl
│
├── train_model.py
├── main.py
└── README.md
```

---

# ⚙️ Installation

### Clone the repository

```
git clone https://github.com/krishanudeka/AI-Risk-Manager.git
cd AI-Risk-Manager
```

---

### Install dependencies

```
pip install -r requirements.txt
```

---

### Run the backend server

```
uvicorn main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

# 📊 How the System Works

1. User uploads financial CSV datasets.
2. Backend validates and processes the data.
3. Feature engineering extracts relevant financial indicators.
4. Machine learning model predicts risk scores.
5. Results are visualized through dashboards.

---

# 🔮 Future Improvements

* Real-time financial monitoring
* Deep learning forecasting models
* Anomaly detection for fraud detection
* Cloud deployment
* Role-based authentication
* API integrations with accounting software

---

# 👨‍💻 Author

**Krishanu Deka**

GitHub
https://github.com/krishanudeka

---

# ⭐ Support

If you found this project useful, consider giving it a star ⭐ on GitHub.
