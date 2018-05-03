import requests
import pymysql.cursors
import time
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from data import *
# Connect to the database
conn = pymysql.connect(host=sqlhostname,
                             user=sqluser,
                             password=sqlpassword,
                             db=sqldbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def CreateNeededTable():
    global conn
    cursor = conn.cursor()
    query = "CREATE TABLE IF NOT EXISTS `messages`(  `datanumber` int NOT NULL AUTO_INCREMENT,`id` text NOT NULL, PRIMARY KEY (datanumber)) ENGINE=MEMORY;"
    cursor.execute(query)

def saveMessageId(x):
    global conn
    cursor = conn.cursor()
    query = "INSERT INTO `messages` (`id`) VALUES (%s)"
    cursor.execute(query, (str(x)))

def checkMessageId(x):
    global conn
    cursor = conn.cursor()
    query = "SELECT * FROM `messages` WHERE id = '" + str(x) + "'"
    cursor.execute(query)
    row = cursor.fetchone()
    if row == None:
       print "Uploading New Message..."
       print "Message: " + str(x)
       saveMessageId(x)
       if printMessageById(x) != False:
           name, text = printMessageById(x)
           SendText(str(name), str(text))

def printMessageById(idnumber):
    global apikey
    global token
    texttypes = ["mentionedOnCard"]
    querystring = {"key":apikey,"token":token}
    url = "https://api.trello.com/1/notifications/" + str(idnumber)
    response = requests.request("GET", url, params=querystring).json()

    if response["type"] in texttypes:
        name = response["memberCreator"]["fullName"]
        text = response["data"]["text"]
        return str(name), str(text)
    else:
        return False

def CheckMessages():
    global username
    url = "https://api.trello.com/1/members/" + username + "/notifications?fields=name,url&key=" + str(apikey) + "&token=" + str(token)
    request = requests.get(url).json()

    for i in range(0,len(request)):
        try:
          request[i]["id"]
        except NameError:
          print "well, it WASN'T defined after all!"
        else:
          checkMessageId(request[i]["id"])

def SendText(name, message):
    global phonenumber
    driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
    driver.get("http://www.24sms.net/")
    driver.find_element_by_name('SendFrom').send_keys(str(name))
    driver.find_element_by_name('SendTo').send_keys(str(phonenumber))
    driver.find_element_by_name("Msg").send_keys(str(message))
    driver.find_element_by_xpath("//input[@type='submit']").click()


CreateNeededTable()
CheckMessages()
