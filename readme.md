# 🧮 Operations Persistence Engine

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-black?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

A robust RESTful API Calculator built with **Flask**, designed to demonstrate Microservices architecture and Database Polymorphism. The system performs mathematical operations and persists the history logs into either **PostgreSQL** or **MongoDB** based on dynamic runtime configuration.

---

## 🚀 Key Features

* **Microservices Architecture:** Fully containerized environment using Docker & Docker Compose.
* **Dual Persistence Layer:** Seamlessly switches between SQL (PostgreSQL) and NoSQL (MongoDB) storage.
* **Factory Design Pattern:** Smart handling of database connections and query execution.
* **Calculation Modes:**
    * **Independent:** Simple, stateless calculation (e.g., `4 + 2`).
    * **Stack-Based:** LIFO (Last-In, First-Out) stack operations.
* **Health Checks:** Built-in endpoints to monitor system status.

---

## 🛠️ Tech Stack

* **Server:** Python, Flask
* **Databases:** PostgreSQL (Relational), MongoDB (Document-based)
* **Containerization:** Docker, Docker Compose
* **Version Control:** Git

---

## 📂 Project Structure

```text
Operations-Persistence-Engine/
├── databases/              # DB logic & Drivers
│   ├── db_manager.py       # Factory pattern implementation
│   ├── mongo_driver.py     # MongoDB connection handler
│   └── postgres_driver.py  # PostgreSQL connection handler
├── server.py               # Main Flask Application
├── Dockerfile              # App container configuration
├── docker-compose.yml      # Orchestration of Server + DBs
├── requirements.txt        # Python dependencies
└── submission.json         # Submission artifact