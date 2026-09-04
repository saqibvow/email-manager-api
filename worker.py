from celery import Celery
import mailtrap as mt

app = Celery('worker', broker='redis://127.0.0.1:6379/0')


app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_transport_options={'global_keyprefix': 'celery', 'protocol': 2},
    redis_backend_transport_options={'protocol': 2},
    task_default_queue='celery', # Explicitly queue ka naam set kar diya
)


@app.task(name="worker.send_email_task") 
def send_email_task(user_db,campaign_db):
    if not campaign_db:
        print("check your campaign")
        return
    emails_sent = 0
    client = mt.MailtrapClient(token="0cee05861ec677484aa421b70eec27df")
    
    for campaign in campaign_db:
        # FastAPI se status String "True" ya Boolean True dono aa sakta hai, hum dono check karenge
        if campaign.get("status") == "True" or campaign.get("status") is True:
            for sub_user in user_db:
                # FastAPI mein User status Boolean True hai, use check karenge
                if sub_user.get("status") is True or sub_user.get("status") == "True":
                    
                    # Mail object (FastAPI ke fields 'subject' aur 'body' ke sath)
                    mail = mt.Mail(
                        sender=mt.Address(email="hello@saqibvowmail.com", name="Mailtrap Test"),
                        to=[mt.Address(email=sub_user.get("email"))],
                        subject=campaign.get("subject", "No Subject"), # FastAPI ka subject
                        text=campaign.get("body", "No Body Content"),  # FastAPI ka body
                        category="FastAPI Integration",
                    )
                    
    
                    client = mt.MailtrapClient(token="0cee05861ec677484aa421b70eec27df")
                    response = client.send(mail)
            return f"SUCCESS: Total {emails_sent} emails sent for active campaigns!"

                    



    
    