# 🚀 Asynchronous Email Campaign System

This project is a high-performance **Email Marketing & Subscription System**. It allows users to subscribe or unsubscribe via APIs and schedules bulk marketing emails to be sent automatically at any future time.

Built using **FastAPI**, **Celery (with Redis)**, and **Dockerized SQLite**.

## 🛠 Main Features
* **User Management:** Quick endpoints to Subscribe or Unsubscribe users.
* **Smart Campaign Scheduler:** Schedules future emails. The backend automatically calculates execution delays.
* **Bug-Free Design:** Fully resolves critical Timezone offset errors (Naive vs Aware) and async-to-sync worker blocking.

## 🏗 Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** SQLite3 (Runs inside Docker environment)
* **Task Queue & Broker:** Celery + Redis
* **Email Service:** fastapi-mail (Configured for Mailtrap Sandbox testing)

## 🚀 How to Setup and Run (Quick Start)

### Step 1: Clone the Project
```bash
git clone https://github.com
cd "email-manager-api"
```

### Step 2: Install Project Dependencies
Run the following command to install all necessary libraries exactly listed inside your `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Step 3: Start Redis Server (Broker)
Run the official production-ready Redis image inside a lightweight Docker container:
```bash
docker run -d -p 6379:6379 --name email_redis redis
```

### Step 4: Run the Celery Worker
Open a new terminal window and start the background worker:
```bash
celery -A app.my_worker worker --loglevel=info
```

### Step 5: Run the FastAPI App
Open another terminal window and start the main server:
```bash
uvicorn app.main:app --reload
```
Now, open your browser and go to: **http://127.0.0** to test all APIs directly!

## 🔌 API Endpoints Reference

| Endpoint | Method | Description | Example Payload |
| :--- | :--- | :--- | :--- |
| `/subscribe/` | POST | Adds a new active user to the database | `{"name": "Ali", "email": "ali@example.com"}` |
| `/unsubscribe/` | POST | Deactivates a user from receiving emails | `{"email": "ali@example.com"}` |
| `/campaign/` | POST | Saves a marketing campaign draft | `{"subject": "Sale", "body": "50% off", "scheduleTime": "2026-12-25T10:00:00", "status": "draft"}` |
| `/campaign/send` | POST | Schedules and sends emails to active users | Uses Celery countdown based on scheduleTime |
| `/clear-database/` | DELETE | Wipes all data from User & Campaign tables | *No body required* |

## ⚠️ Important Troubleshooting (Windows & Local Machine Bugs)

If you are running this project on a local Windows machine without a full Docker environment, you will likely face setup issues where **Celery tasks get stuck and nothing prints in the terminal**. Here is the exact fix:

### 1. The Redis Windows Issue
Redis does not officially support Windows. *❌ Avoid:* Old GitHub repositories (like microsoftarchive/redis) that provide `.msi` files. They are completely outdated, deprecated, and cause security bugs.  
*✔️ Solution:* Always run Redis via **Docker** using the command in Step 3. It takes 2 seconds and runs the official Linux image perfectly.

### 2. Celery "Tasks Not Executing/Printing" Bug on Windows
Windows lacks Unix-style process-forking, so running the standard Celery command will receive tasks but **never execute them**.  
*✔️ Solution 1 (Fastest):* Add the single pool flag to your command to force execution:
```bash
celery -A app.my_worker worker --loglevel=info --pool=solo
```
*✔️ Solution 2:* Install eventlet pool support via pip:
```bash
pip install eventlet
celery -A app.my_worker worker --loglevel=info -P eventlet
```

## ⚙️ Testing Note
This system uses **Mailtrap Sandbox** credentials hardcoded inside the worker file for safe integration testing. Outgoing emails will securely appear in your virtual Mailtrap dashboard instead of real customer spam folders.
