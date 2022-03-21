from smtplib import *
from datetime import *
from random import *

my_email = "dalkomcandy1009@gmail.com"
your_email = "gyumin1009@naver.com"
password = "qkrrbals!1"

dt = datetime.now()

def quotes():
    data = open(r'C:\Code\Python\Projects\smtplib\mail\quotes.txt','r') 
    quote = choice(data.readlines()).strip()
    with SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user = my_email, password = password)
        connection.sendmail(from_addr = my_email, 
                            to_addrs = your_email, 
                            msg = f"Subject:Today's Quote\n\n{quote}")

if dt.weekday() != 0:
    quotes()
