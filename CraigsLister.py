#!/usr/bin/python

'''
Author: Christopher Mertin
Date: July 15, 2015

Released under the GNU public license

This is a simple program I made to find Craigslist listings for apartments or
rooms that are available in Salt Lake City, Utah. It searches for it based on
a price range you define and when it finds that price it sends you an email
to the listing page. It searches the listings every 30 minutes as to not stress
the servers, give people reasonable time to make a new post, and to give you
a little break to do other things. If you want to use it, be sure to change
the parameters in the SendEmail function so that it has your gmail username,
password, and the email address to send it to. 

If your gmail account is failing to connect, try allowing "less secure apps"
to access your gmail account 
(https://www.google.com/settings/security/lesssecureapps) and also there is
an "unlock captcha fix at (https://accounts.google.com/displayunlockcaptcha).
On top of this, check your email and see if Google has notified you saying they
blocked an unknown app from accessing your account. You may have to follow the
link in that email to verify that it was you.

This should not violate any of Craigslist policies as it is the same as 
refreshing your web browser on the website. This program simply parses 
(ie "reads") the site for you once every 30 minutes.
'''

from __future__ import print_function
import time
from datetime import datetime
import smtplib
import urllib2
import StringIO
import os.path

# Makes searching a list for a term easy so that it won't produce an error
# when what you're searching isn't in the list
def FindList(myList, search):
    try:
        return myList.index(search)
    except:
        return -1

# Searches and parses the Craigslist site for new listings within your range
def NewListings(city, rooms, apartments, min_price, max_price):
    # Opens and cleans up the webpage for your search
    craigslistURL = urllib2.urlopen("http://" + city + ".craigslist.org/search/hhh?min_Price=" + 'min_price' + "&max_price=" + 'max_price').read()
    craigslist_HTML = StringIO.StringIO(craigslistURL)
    craigslist_HTML = craigslist_HTML.readlines()
    
    for i in xrange(0, len(craigslist_HTML)):
        craigslist_HTML[i] = craigslist_HTML[i].strip()
        
    looking_for = ["/apa/", "/roo/"]
    listings_index = Find(craigslist_HTML, "<p class=\"row\"")
    listings = craigslist_HTML[listings_index]
    
    for i in xrange(0, len(listings)):
        # Check to see if in houses/apartments for rent
        if FutureIndex(listings, i, looking_for[0]):
            if FindList(apartments, listings[i:i+20]) == -1:
                url = "http://" + city + ".craigslist.org" + listings[i:i+20]
                SendEmail(url, city)
                apartments.append(listings[i:i+20])
        # Check to see if listed rooms for rent
        elif FutureIndex(listings, i, looking_for[1]):
            if FindList(rooms, listings[i:i+20]) == -1:
                url = "http://" + city + ".craigslist.org" + listings[i:i+20]
                SendEmail(url, city)
                rooms.append(listings[i:i+20])

# Search an array for a substring in the list, return -1 if it's not in there
def Find(array, string, start=0):
    for i in xrange(start, len(array)):
        if array[i].find(string)!=-1:
            return i
    return None # or -1

# Emails the user the url that the new listing was found at, writes it to a file
# instead if the email fails to send and notifies the user of successful and
# failed email attempts, along with a time stamp.
def SendEmail(url, city):
    logfile = "CL_" + city + ".log"
    gmail_user = "user@gmail.com"
    gmail_pwd = "password"
    FROM = "user@gmail.com"
    TO = ["any_email@domain.com"] #must be a list
    SUBJECT = "New craigslist listing available!"
    TEXT = url
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print("[" + time + "] " + "Successfully sent mail:\n\t" + url)
        with open(logfile, "a") as myfile:
            myfile.write("[" + time + "] " + "Successfully sent mail:\n\t" + url + "\n")
    except:
        print("[" + time + "] " + "Failed to send mail:\n\t" +  url)
        with open(logfile, "a") as myfile:
            myfile.write("[" + time + "] " + "Failed to send mail:\n\t" +  url + "\n")
             
# Starts at a pre-defined index and checks to see if the next "N" indexes agree
# with the substring that you're looking for to get the index of where the 
# substring starts at
def FutureIndex(array, index, substring):
    for i in xrange(0, len(substring)):
        if array[index+i] != substring[i]:
            return False
    return True

# Beginning of the main program
city = "SaltLakeCity" # Needs to be no spaces and as it's displayed at
                      # http://CITYNAME.craigslist.org/ when you visit the site
rooms_file = "CL_" + city + "_rooms.dat"
apts_file = "CL_" + city + "_apts.dat"
logfile = "CL_" + city + ".log"
min_price = 0 # Minimum price of the listings you're looking for
max_price = 1400 # Maximum price of the listings
rooms = []
apartments = []

print("Note: If an email fails to send, it will be saved in ", end="")
print("\"" + logfile + "\"\n      as well as be displayed in the terminal.")
print("Note: To close the program, execute \"Ctrl+C\" on your keyboard")
print("\nBeginning searches...\n")

if os.path.isfile(rooms_file):
    with open(rooms_file) as myfile:
        for line in myfile:
            rooms.append(line.strip())

if os.path.isfile(apts_file):
    with open(apts_file) as myfile:
        for line in myfile:
            apartments.append(line.strip())
while True: # Want to run continuously
    NewListings(city, rooms, apartments, min_price, max_price)

    with open(rooms_file, "w") as myfile:
        for i in xrange(0, len(rooms)):
            myfile.write(rooms[i] + "\n")
            
    with open(apts_file, "w") as myfile:
        for i in xrange(0, len(apartments)):
            myfile.write(apartments[i] + "\n")
    time.sleep(60*30) # Want to limit to every 30 minutes to not stress servers

