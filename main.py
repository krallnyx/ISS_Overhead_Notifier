import requests
from datetime import datetime

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
        self.time_now = 0
        self.sunrise = 0
        self.sunset = 0

    def check_night(self):
        if int(self.sunrise[0]) <= self.time_now.hour:
            if int(self.sunrise[1]) <= self.time_now.minute:
                print("the sun has already risen today")
                if int(self.sunset[0]) >= self.time_now.hour:
                    if int(self.sunset[1]) >= self.time_now.minute:
                        # the sun hasn't set yet, it's daytime
                        return True
        return False

    def check_iss_in_sky(self):
        if MY_LAT+5 > self.iss_latitude > MY_LAT-5:
            if MY_LONG+5 > self.iss_longitude > MY_LONG-5:
                return True
        return False

    def send_email(self):
        pass

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
        self.sunrise = data["results"]["sunrise"].split("T")[1].split(":")[:2]
        self.sunset = data["results"]["sunset"].split("T")[1].split(":")[:2]

        self.time_now = datetime.now()

        night = self.check_night()

        # If the ISS is close to my current position
        # and it is currently dark
        # Then send me an email to tell me to look up.
        if night and in_sky:
            self.send_email()


if __name__ == '__main__':
    iss_overhead = ISSOverhead()
    iss_overhead.request_apis()


