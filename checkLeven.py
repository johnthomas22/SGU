import json,  urllib.request, smtplib, pickle, os
from datetime import datetime
#https://www2.sepa.org.uk/hydrodata/api/Level15/477620

#
#
#

def main():
    #open and read the file after the appending:
    try:
       f = open("/home/john/lastreading.txt", "r")
       result = float(f.read())
    except:
       result = 0

    print("Last Result = ", result)

    file_name = '/home/john/checkLeven.pickled'
    parameters = pickle.load(open(file_name, 'rb'))

    email_address_from = parameters['email_address_from']
    email_address_to = parameters['email_address_to']
    email_password = parameters['email_password']

    print('email_address_from =', email_address_from)
    print('email_address_to =', email_address_to)
    #print('email_password =', email_password)

    with urllib.request.urlopen("https://www2.sepa.org.uk/hydrodata/api/Level15/477620") as url:
        data = json.load(url)
    last = data[-1]
    #
    # 2023-01-01T18:45:00
    #
    limit = 1.4
    lasttime = datetime.strptime(last["Timestamp"], "%Y-%m-%dT%H:%M:%S").timestamp()
    lasttimets = datetime.fromtimestamp(lasttime)
    lasttimestr = lasttimets.strftime("%d/%m/%Y %H:%M:%S")

    if float(last["Value"]) > limit and float(last["Value"]) > result:
       print('Increase detected...')
       f = open("/home/john/lastreading.txt", "w")
       f.write(last["Value"])
       f.close()
       with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(email_address_from, email_password )
        connection.sendmail(from_addr=email_address_from, to_addrs=email_address_to,
        msg="subject:Loch Leven Sluice water level is RED \n\n SEPA's sensors indicated the water level is " + last["Value"] + " at " + lasttimestr + "\n Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details.")
    else:
        print('Nothing to do here...')

    if float(last["Value"]) < limit:
       try:
          os.remove("/home/john/lastreading.txt") 
          print('Deleted last reading file')
          with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
              connection.login(email_address_from, email_password )
              connection.sendmail(from_addr=email_address_from, to_addrs=email_address_to,
              msg="subject:Loch Leven Sluice water level \n\n SEPA's sensors indicated the water level has fallen below RED level to " + last["Value"] + " at " + lasttimestr + "\n Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details.")
       except:
           print("lastreading.txt not found")

    print("SEPA's sensors indicated the water level is " + last["Value"] + " at " + lasttimestr + "\n Check https://www2.sepa.org.uk/WaterLevels/default.aspx?sd=t&lc=477620 for details.")

if __name__ == "__main__":
    main()
