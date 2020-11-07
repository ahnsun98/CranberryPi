import os
import subprocess
import time
from datetime import datetime
import Adafruit_DHT as dht
import requests
import cv2
import numpy as np
import threading
import boto3

it = 0 #it : indoor temp
pn = 0 #pn : person num

up = "python3 irrp.py -p -g23 -fairconup"
down = "python3 irrp.py -p -g23 -faircondown"
onoff = "python3 irrp.py -p -g23 -fairconpower"

s3 = boto3.client('s3',
   aws_access_key_id='AKIA25U5UVIVIAR6IMUW',
   aws_secret_access_key='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'


cam = cv2.VideoCapture(0,cv2.CAP_V4L)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

arr = ""
myfile = ""

def print_real():
    ret, img = cam.read()
    now = datetime.now()
    realti = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)
    filename1 ='image/'+realti+'.jpg'
    filename2 =realti+'.jpg'
    cv2.imwrite("image/"+realti+".jpg",img)

    bucket_name='objectdetection7220'
    s3.upload_file(filename1,bucket_name,filename2)

def gpn():
    for object in s3.list_objects(Bucket='objectdetection7220-1')['Contents']:
        s3.download_file('objectdetection7220-1', object['Key'], object['Key'])
        arr=object['Key']
    myfile=open(arr,'r',encoding='utf-8')
    mystring=myfile.read()

    return int(mystring) 

def check_hour():
  now = datetime.now()
  return now.hour
  
def switch(x):
    return({11,12,1,2:'heat', 5,6,7,8:'cool'}.get(x,'default'))

def check_temp():
    _,it = dht.read_retry(dht.DHT11,14)

def set_temp(st,tmp):
    if(st<tmp):
        while(st==tmp):
            if(os.system(up) != 0): '''up'''
                print('up error')
                break
             print('temp on')
            st++
    if(tmp<st):
        while(st==tmp):
            if(os.system(down) != 0): '''down'''
                print('down error')
                break
            print('temp down')
            st--

#pn : person num
#it : indoor temp
#st : setted temp
#s : state
#sys : cool or heat
'''starting off'''

def main(month, init_temp):
    sys=switch(month)
    s=0 #off
    st=init_temp 
    forBreak=False '''for error handle'''
    while True:
        hour=check_hour()
        if(hour=='12' or hour=='17'):
          continue
        print_real()
        time.slep(3)
        pn=gpn()
        time.sleep(2)
        check_temp()
        if(sys=='cool'):
            print('Start Cooling Control!')
            print('======================')
            while True:
                if(s==1 and (it<24 or pn==0)):
                    if(os.system(onoff) != 0): '''off'''
                        print('onoff error')
                        forBreak=True
                        break
                    print('off')
                    s=0
                else:    
                    if(it<=26): '''꺼져있을 때 는 처음상황에서는 26도 보다 크면 on'''
                        continue                
                    if(s==0 and (it==24 and 20<pn)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            forBreak=True
                            break
                        print('on')
                        s=1
                        '''set temp 24'''
                        set_temp(st,24)
                    else if(s==0 and (it==25 and 10<pn)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            forBreak=True
                            break
                        print('on')
                        s=1
                        if(10<pn<=20):
                            '''set temp 25'''
                            set_temp(st,25)
                        if(20<pn<=30):
                            '''set temp 24'''
                            set_temp(st,24)
                    else if(s==0 and (it>=26)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            break
                        print('on')
                        s=1
                        if(0<pn<=10):
                            '''set temp 26'''
                            set_temp(st,26)
                        if(10<pn<=20):
                            '''set temp 25'''
                            set_temp(st,25)
                        if(20<pn<=30):
                            '''set temp 24'''
                            set_temp(st,24) 
                    else:
                        continue

        if(sys=='heat'):
            print('Start Heating Control!')
            print('======================')
            while True:
                if(s==1 and (it>20 or pn==0)):
                    if(os.system(onoff) != 0): '''off'''
                        print('onoff error')
                        forBreak=True
                        break
                    print('off')
                    s=0
                else:    
                    if(it>=18): '''꺼져있을 때 켜는 처음상황에서는 18도 보다 작으면 on'''
                        continue
                    if(s==0 and (it==20 and pn<=10)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            forBreak=True
                            break
                        print('on')
                        s=1
                        '''set temp 20'''
                        set_temp(st,20)
                    else if(s==0 and (it==19 and pn<=20)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            forBreak=True
                            break
                        print('on')
                        s=1
                        if(0<pn<=10):
                            '''set temp 20'''
                            set_temp(st,20)
                        if(10<pn<=20):
                            '''set temp 19'''
                            set_temp(st,19)
                    else if(s==0 and (it<=18)):
                        if(os.system(onoff) != 0): '''on'''
                            print('onoff error')
                            forBreak=True
                            break
                        print('on')
                        s=1
                        if(0<pn<=10):
                            '''set temp 20'''
                            set_temp(st,20)
                        if(10<pn<=20):
                            '''set temp 19'''
                            set_temp(st,19)
                        if(20<pn<=30):
                            '''set temp 18'''
                            set_temp(st,18) 
                    else:
                        continue
        else:
            print("There's no need for cooling and heating!")
        if(forBreak==True):
            break
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='control Air Conditioner')
    parser.add_argument("--input_month",help=" ")
    parser.add_argument("--input_initial_temp",help=" ")
    args=parser.parse_args()
    input_month=args.input_month
    input_initial_temp=args.input_initial_temp
    main(month, input_initial_temp)