from fastapi import FastAPI
from celery import Celery
from app.my_worker import sender_bot
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone


import sqlite3

app = FastAPI()


con = sqlite3.connect("tutorial.db")
cur = con.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS User (
    Email TEXT PRIMARY KEY,
    Email_Status TEXT,
    Name TEXT
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS Campaign (
    Subject TEXT,
    Body TEXT,
    ScheduleTime TEXT,
    Status TEXT
)
""")
con.commit()
con.close()


class User(BaseModel):
    name: str
    email: EmailStr


class User_unsub(BaseModel):
    email: EmailStr


class Campaign(BaseModel):
    subject: str
    body: str
    scheduleTime: datetime
    status: str


@app.post("/subscribe/")
def subscribe(user_info: User):
    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO User (Email, Email_Status, Name) VALUES (?, 'active', ?)",
            (user_info.email, user_info.name),
        )

        con.commit()
    except sqlite3.IntegrityError as e:
        return {"Alert": "User already exists!"}
    finally:
        con.close()

    return {"Message": "successfull"}


@app.post("/unsubscribe/")
def un_subscribe(user_unsub: User_unsub):
    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute("SELECT EMAIL FROM USER WHERE Email = ?", (user_unsub.email,))
        user = cur.fetchone()
        if user is None:

            return {
                "Alert": f"a user with the name of'{user_unsub.email}' is not found"
            }

        cur.execute(
            "UPDATE User  Set Email_Status ='deactivate' where  Email  = ?",
            (user_unsub.email,),
        )
        con.commit()
        return {"Message": "User successfully deactivated"}

    finally:
        con.close()


@app.post("/campaign/")
def campaignModel(campaign_data: Campaign):
    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Campaign (Subject, Body, ScheduleTime,Status) VALUES (?, ?, ?,?)",
            (
                campaign_data.subject,
                campaign_data.body,
                campaign_data.scheduleTime,
                campaign_data.status,
            ),
        )
        con.commit()
        return {"Message": "campaign"}
    finally:
        con.close()


@app.post("/campaign/send")
def campaign_sending(campaign_data: Campaign):
    active_users = []
    time_str = ""
    delay_seconds = 0

    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute("SELECT Subject, Body FROM Campaign ORDER BY ROWID DESC LIMIT 1")
        latest_campaign = cur.fetchone()
        if latest_campaign is None:
            return {"message": "Error"}
        db_subject = latest_campaign[0]
        db_body = latest_campaign[1]
        cur.execute("SELECT Email, Name FROM User WHERE Email_Status IN ('active')")

        active_users = cur.fetchall()
        current_time = datetime.now(timezone.utc)
        schedule_time = campaign_data.scheduleTime
        print(delay_seconds)
               

        if schedule_time.tzinfo is None:
            schedule_time = schedule_time.replace(tzinfo=timezone.utc)
        else:
            schedule_time = schedule_time.astimezone(timezone.utc)

        if schedule_time < current_time:
            return {"error": "make your schedule for future"}
        time_str = campaign_data.scheduleTime.strftime("%Y-%m-%d %H:%M:%S")
        delay_seconds = int((campaign_data.scheduleTime - current_time).total_seconds())

    except Exception as e:
        return {"message": e}

    finally:
        con.close()

    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Campaign (Subject, Body, ScheduleTime, Status) VALUES (?, ?, ?, ?)",
            (campaign_data.subject, campaign_data.body, time_str, campaign_data.status),
        )

        con.commit()

    except Exception as e:
        return {"error": e}

    finally:
        con.close()

    if not active_users:
        return {"message": "there is no active user"}
    for user in active_users:
        user_email = user[0]
        user_name = user[1]
        sender_bot.apply_async(
            args=[user_name,user_email, campaign_data.subject, campaign_data.body], 
            countdown=delay_seconds
        )

    return {
        "Message": "Campaign scheduled and emails sent successfully!",
        "Scheduled For": time_str,
    }


@app.delete("/clear-database/")
def clear_database():
    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()

        cur.execute("DELETE FROM User;")
        cur.execute("DELETE FROM Campaign;")

        con.commit()
        return {"Message": "data delete!"}
    except Exception as e:
        return {"Error": str(e)}
    finally:
        con.close()
