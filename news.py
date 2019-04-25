import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import schedule
import time
import pickle
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup

pd.set_option('display.max_colwidth', 200)

def fetch_news():
    try:
        vect=pickle.load(open(r'news_vect_pickle.p', 'rb'))
        model=pickle.load(open(r'news_model_pickle.p', 'rb'))
        
        scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(r'/home/mb45296/Descargas/perax-855b9ddcb8c9.json', scope)

        gc = gspread.authorize(credentials)
        ws = gc.open_by_url("https://docs.google.com/spreadsheets/d/1WVPZJpecZOCYQ-JOub5gzakdCo4tHpNKeR4vmSej8x0/edit#gid=0")#gc.open("newstories")
        sh = ws.sheet1
        zd = list(zip(sh.col_values(1),sh.col_values(2), sh.col_values(3)))
        zf = pd.DataFrame(zd, columns=['title','urls','html'])
        
        zf.replace('', pd.np.nan, inplace=True)
        #print(zf)
        zf.dropna(inplace=True)
        #print(zf)
        #print(sh.col_values(1))
#zf
        def get_text(x):
            soup = BeautifulSoup(x, 'lxml')
            text = soup.get_text()
            return text

        zf.loc[:,'text'] = zf['html'].map(get_text)
        #print(vect.fit_transform(zf['text']))
        tv = vect.transform(zf['text'])
        #print(model.predict(tv))
        res=model.predict(tv)
        #print(tv)
        

        rf=pd.DataFrame(res,columns=['wanted'])
        #print(rf)
        rez=pd.merge(rf,zf,left_index=True,right_index=True)
        

        news_str=''
        for t,u in zip(rez[rez['wanted']=='y']['title'],rez[rez['wanted']=='y']['urls']):
            news_str=news_str+t+'\n'+u+'\n'



        payload={'value1':news_str}
        r=requests.post("https://maker.ifttt.com/trigger/news2/with/key/oWiucRhd2I9z6g7oSAVqOy_jtcc_sVly1EimStbt7mr",data=payload)

        #clean ws
        #lenv=len(sh.col_values(1))
        #cell_list=sh.range('A1:F'+str(lenv))
        #for cell in cell_list:
        #    cell.value=""
        #sh.update_cells(cell_list)

        print(r.text)

    except:
        print("failed")





#schedule.every(60).minutes.do(fetch_news)

#while 1:
#   schedule.run_pending()
#   time.sleep(1)
