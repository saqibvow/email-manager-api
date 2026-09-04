from fastapi import FastAPI
from pydantic import BaseModel
from worker import send_email_task

app = FastAPI()

user_db =[]
campaign_db = []

class User(BaseModel):
    name:  str
    email: str
    status:bool = True

class Campaign(BaseModel):
    subject: str
    body: str
    scheduleTime: str
    status: str


@app.post("/subscribe/")

def subscribe(user_info:User):
    user_data = user_info.model_dump()
    user_db.append(user_data)
    return {"message": "Subscribed successfully", "user": user_data}


@app.post("/unsubscribe/")
def un_subscribe(user_info:User):
    user_email = user_info.model_dump()

    for user in user_db:
        if user["email"] == user_info.email:
            user["status"] = False
            return {"message": "Unsubscribed successfully", "user": user}
    else:
        return {"message":"account not found"}


@app.post("/campaign/")
def campaignModel(campaign_data:Campaign):
    campaign_Dict = campaign_data.model_dump()
    campaign_db.append(campaign_Dict)
    return{"message":"campaign saved in database successfully","data":campaign_Dict}
@app.get("/campaignchecking/")
def campaign_checking():
    return{"campaign":campaign_db}

@app.post("/campaign/send")
def campaign_sending():
    send_email_task.delay(user_db,campaign_db)
    return {"message":"data recived successfully"}
   

           










