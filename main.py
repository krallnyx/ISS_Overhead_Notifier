import requests
from datetime import datetime
import smtplib
from email.message import EmailMessage

MY_LAT = 51.4014  # Your latitude
MY_LONG = 1.3231  # Your longitude


class ISSOverhead:
    def __init__(self):
        self.parameters = {
            "lat": MY_LAT,
            "lng": MY_LONG,
            "formatted": 0,
        }
        self.iss_latitude = 0
        self.iss_longitude = 0
        self.time_now = 0.0
        # time_now, sunrise and sunset are used as floats, minutes aren't base 100 but still based 60 so it's not
        # meant to be used !
        # it just doesn't matter in our case as it's only used to compare values
        self.sunrise = 0.0
        self.sunset = 0.0
        self.smtp_server = "smtp.email.com"
        self.email = "email@email.com"
        self.password = ""
        self.msg = EmailMessage()

    def check_night(self):
        if self.sunrise < self.time_now < self.sunset:
            print("It's daytime")
            return False
        return True

    def check_iss_in_sky(self):
        print(f"my latitude: {MY_LAT}, ISS latitude: {self.iss_latitude}")
        print(f"my longitude: {MY_LONG}, ISS longitude: {self.iss_longitude}")
        if MY_LAT+5 > self.iss_latitude > MY_LAT-5:
            if MY_LONG+5 > self.iss_longitude > MY_LONG-5:
                print("ISS in the sky")
                return True
        return False

    def send_email(self):
        self.msg.set_content("The International Space Station is currently visible in your night sky!\nLook up!")
        self.msg['Subject'] = "ISS visible"
        self.msg['From'] = self.email
        self.msg['To'] = self.email
        with smtplib.SMTP(self.smtp_server) as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            connection.send_message(self.msg)
        print("Email sent")

    def request_apis(self):

        response = requests.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
        data = response.json()

        self.iss_latitude = float(data["iss_position"]["latitude"])
        self.iss_longitude = float(data["iss_position"]["longitude"])

        # Your position is within +5 or -5 degrees of the ISS position.
        in_sky = self.check_iss_in_sky()

        response = requests.get("https://api.sunrise-sunset.org/json", params=self.parameters)
        response.raise_for_status()
        data = response.json()
        # as said in the __init__ method, we build WRONG times, using a flot with minutes still base 60
        # it doesn't matter for us as it's only used to compare them
        self.sunrise = float(f'{data["results"]["sunrise"].split("T")[1].split(":")[0]}.'
                             f'{data["results"]["sunrise"].split("T")[1].split(":")[1]}')
        self.sunset = float(f'{data["results"]["sunset"].split("T")[1].split(":")[0]}.'
                            f'{data["results"]["sunset"].split("T")[1].split(":")[1]}')

        self.time_now = float(f'{datetime.now().hour}.{datetime.now().minute}')

        night = self.check_night()

        if night and in_sky:
            self.send_email()


if __name__ == '__main__':
    iss_overhead = ISSOverhead()
    iss_overhead.request_apis()


