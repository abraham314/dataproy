import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os
import time
import math
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import schedule
import time
import requests, sys

APIKEY = 'oWiucRhd2I9z6g7oSAVqOzQ1LEFSm9Mpc_zVCnQdZQO'
EVENT = 'sms'



def checa_vuelos():
    url ="https://www.google.co.in/flights#flt=MEX.PVR.2019-08-29*PVR.MEX.2019-09-01;c:MXN;e:1;sd:1;t:f"


    if os.name == "nt":
       driverPath = '/home/mb45296/WhatsApp-Chatbot/driver/chromedriver_2.24.exe'
       dataPath = "Data"
    else:
       driverPath = "/home/mb45296/WhatsApp-Chatbot/driver/chromedriver"
       dataPath = "Data/ChatBot"


    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + dataPath)
    driver = webdriver.Chrome(chrome_options=options, executable_path=driverPath)
    #driver.implicitly_wait(30)
	#driver = webdriver.Chrome()
    driver.get(url)
    #driver.implicitly_wait(20)

    wait= WebDriverWait(driver, 20)
    #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'span.flt-subhead1 gws-flights-results__price')))

    s = BeautifulSoup(driver.page_source,"lxml") 

    driver.quit()

    best_price_tags = s.findAll('div',"flt-subhead1 gws-flights-results__price gws-flights-results__cheapest-price")+s.findAll('div', 'flt-subhead1 gws-flights-results__price')
    best_prices = []
    for tag in best_price_tags:
        best_prices.append(int(tag.text.replace('$','').replace(',','')))
 

    best_price = best_prices[0]

    fares = pd.DataFrame(sorted(set(best_prices)), columns=['price'])#.sort_values('price')
    px = [x for x in fares['price']]
    ff = pd.DataFrame(px, columns=['fare']).reset_index()

    X = StandardScaler().fit_transform(ff)
    db = DBSCAN(eps=.5, min_samples=1).fit(X)

    labels = db.labels_
    clusters = len(set(labels))

    pf = pd.concat([ff, pd.DataFrame(db.labels_,columns=['cluster'])], axis=1)
    rf=pf.groupby('cluster')['fare'].agg(['min','count']).sort_values('min',ascending=True)

    if clusters>1 and ff['fare'].min()==rf.iloc[0]['min']: #and rf.iloc[0]['count']<rf['count'].quantile(.7):
       return(best_price)
    else:
       return(-1)



    #while 1:
       #schedule.run_pending()
       #time.sleep(1)   

data = {
   #'value1': sys.argv[1], 
   'value1': sys.argv[1],
   'value2': checa_vuelos()
}

resp = requests.post('https://maker.ifttt.com/trigger/'+EVENT+'/with/key/'+APIKEY,data=data)

schedule.every(2).minutes.do(checa_vuelos)
while 1:
   schedule.run_pending()
   time.sleep(1)   



