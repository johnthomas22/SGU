import json
import smtplib
import pickle
import os
import requests
from datetime import datetime

URL = "https://www2.sepa.org.uk/hydrodata/api/Level15/477620"
LIMIT = 1.4


def main():
    # open and read the file after the appending:
    try:
        with open("/home/john/lastreading.txt", "r") as f:
            result = float(f.read())
    except Exception:
        result = 0.0

    print("Last Result = ", result)

    file_name = "/home/john/checkLeven.pickled"
    with open(file_name, "rb") as pickle_f:
        parameters = pickle.load(pickle_f)

    email_address_from = parameters["email_address_from"]
    email_address_to = parameters["email_address_to"]
    email_password = parameters["email_password"]

    print(f"{email_address_from=}")
    print(f"{email_address_to=}")
    # print('email_password =', email_password)

    data = requests.get(URL).json()
    last = data[-1]

    lasttime = datetime.strptime(last["Timestamp"], "%Y-%m-%dT%H:%M:%S").timestamp()
    lasttimets = datetime.fromtimestamp(lasttime)
    lasttimestr = lasttimets.strftime("%d/%m/%Y %H:%M:%S")

    if float(last["Value"]) >= LIMIT and float(last["Value"]) > last_reading:
        print("Increase detected...")
        with open("/home/john/lastreading.txt", "w") as f:
            f.write(last["Value"])
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
            connection.login(email_address_from, email_password)
            connection.sendmail(
                from_addr=email_address_from,
                to_addrs=email_address_to,
                msg=f"""Subject: Loch Leven Sluice water level is RED

SEPA's sensors indicated the water level is {last['Value']} at {lasttimestr}
Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details.""",
            )
    else:
        print("Nothing to do here...")

    if float(last["Value"]) < LIMIT:
        try:
            os.remove("/home/john/lastreading.txt")
            print("Deleted last reading file")
        except Exception:
            print("lastreading.txt not found")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
            connection.login(email_address_from, email_password)
            connection.sendmail(
                from_addr=email_address_from,
                to_addrs=email_address_to,
                msg=f"""subject:Loch Leven Sluice water level

SEPA's sensors indicated the water level has fallen below RED level to {last['Value']} at {lasttimestr}
Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details.""",
            )

    print(
        f"""SEPA's sensors indicated the water level is {last['Value']} at {lasttimestr}
Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details."""
    )


if __name__ == "__main__":
    main()
