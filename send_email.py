import smtplib
from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email: EmailStr


def send(rec_email: UserModel, student_name: str):
    text = (f"Subject: Important Update on Your Academic Progress\n"
            f"Content-Type: text/plain; charset=utf-8\n\n"
            f"Dear {student_name},\n"
            f"I hope you're doing well! As we approach finals, "
            f"I encourage you to reflect on your progress and focus on areas for improvement. "
            f"Support is available—feel free to reach out for extra help or tutoring.\n"
            f"Keep pushing forward—your hard work matters! \n\nBest, NYU")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('artemlytvyn2007@gmail.com', "tcng qihn fnyc qivn")  # Ensure app password is used
    server.sendmail('artemlytvyn2007@gmail.com', rec_email.email, text.encode('utf-8'))
    print("✅ Mail has been sent successfully.")
    server.quit()

