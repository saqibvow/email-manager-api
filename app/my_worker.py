from celery import Celery
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from asgiref.sync import async_to_sync 


app = Celery('worker', broker="redis://email_redis:6379/0", backend="redis://email_redis:6379/0")
app.conf.timezone = 'Asia/Karachi' 
app.conf.enable_utc = False 


conf = ConnectionConfig(
    MAIL_USERNAME = "d2d93b85f63e54",
    MAIL_PASSWORD = "6774436064ef2e",
    MAIL_FROM = "danny77@ethereal.email",
    MAIL_PORT = 587,
    MAIL_SERVER = "sandbox.smtp.mailtrap.io",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
  

@app.task(rate_limit='1/s')
def sender_bot(user_name,user_email, db_subject, db_body): 
    try:
        message = MessageSchema(
            subject=db_subject,
            recipients=[user_email],
            body=db_body,
            subtype="plain"
        )
        fm = FastMail(conf)
        async_to_sync(fm.send_message)(message)
        return f"Email sent to {user_email}"
    except Exception as e:
        print(f"DEBUG - Pydantic Validation Error Details: {str(e)}")
        raise e