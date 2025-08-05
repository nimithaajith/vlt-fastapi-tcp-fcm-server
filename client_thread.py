#device threads

import threading
from datetime import datetime,timedelta
from models import *
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import List
from pyfcm import FCMNotification
FCM_API_KEY = "YOUR_FCM_SERVER_KEY"  # Replace with your actual Firebase Server Key
push_service = FCMNotification(FCM_API_KEY)

class ClientThread(threading.Thread):
    def __init__(self,conn,addr):
        self.conn=conn
        self.addr=addr
        self.imei=''
        threading.Thread.__init__(self)

    # get sub packet type
    def get_packet_type(self,packetcode):
        if packetcode == 'NR':
            return 'normal'
        elif packetcode == 'EA':
            return 'EmergencyAlert'
        elif packetcode == 'EO':
            return 'EmergencyAlertOFF'
        elif packetcode == 'TA' or packetcode == 'DT':
            return 'TamperAlert'
        elif packetcode == 'HP':
            return 'HealthPacket'
        elif packetcode == 'IN':
            return 'IgnitionON'
        elif packetcode == 'IF':
            return 'IgnitionOFF'
        elif packetcode == 'BF':
            return 'Vehicle Battery Disconnect'
        elif packetcode == 'BR':
            return 'Vehicle Battery Reconnect'
        elif packetcode == 'BL':
            return 'Internal Battery Low'
        elif packetcode == 'BC':
            return 'Internal Battery Charged'
        elif packetcode == 'HB':
            return 'Harsh Breaking'
        elif packetcode == 'HA':
            return 'Harsh Acceleration'
        elif packetcode == 'RT':
            return 'Rash Turning'
        elif packetcode == 'OS':
            return 'Overspeed'
        elif packetcode == 'CFG' or packetcode == 'PC' or packetcode == 'OT':
            return 'Over the air Update'
        elif packetcode == 'TILT' or packetcode == 'CO':
            return 'Collision Alert'
        else:
            return 'pvt'

    def insert_to_database(self,db:Session,packet_type:str,data_list:List,device_msg:str):        
        
        if packet_type == 'login' or packet_type == 'health':
            try:
                formated_date=str(datetime.now())[:19].replace('T',' ')
                ctime=datetime.strptime(formated_date,"%Y-%m-%d %H:%M:%S")                
                data_rec=DeviceData(                    
                    imei = self.imei,
                    message = device_msg,
                    message_type=packet_type,
                    received_at = ctime                     
                ) 
                print("object created for  device data table::",data_rec)
                db.add(data_rec)     
                db.commit()           
                print("record created in device data table::",data_rec)
            except Exception as e:
                print("record creation failed in Devicedata_AIS:::::",e)
        elif packet_type == 'pvt': 

            #prepare ctime and convert to date           
            msg_date=data_list[9]
            formated_date=str(msg_date[4:])+"-"+str(msg_date[2:4])+"-"+msg_date[:2]
            msg_time=data_list[10]
            formated_date=formated_date+" "+msg_time[:2]+":"+msg_time[2:4]+":"+msg_time[4:]
            print("formatted date:",formated_date)
            ctime=datetime.strptime(formated_date,"%Y-%m-%d %H:%M:%S")

            #packet type details
            other_info =self.get_packet_type(data_list[3])
            packet_info= packet_type + ":" + other_info
            # print(">>>>>OTHERINFO>>>>>",packet_info)
            
            try:
                formated_date=str(datetime.now())[:19].replace('T',' ')
                systemtime=datetime.strptime(formated_date,"%Y-%m-%d %H:%M:%S")
                data_rec=DeviceData(                    
                    imei = self.imei,
                    message = device_msg,
                    message_type=packet_type,
                    received_at = ctime                   
                    
                )
                db.add(data_rec)     
                db.commit() 
                print("record created in device data table")
                device = db.query(DeviceTable).filter(DeviceTable.imei == self.imei).first()
                previous_data=device.live_data
                device.live_data=device_msg
                device.live_data_type=packet_type
                device.timestamp=systemtime
                db.commit()
                if data_list[3] == 'IN':
                    userkey=device.fcm_token
                    if userkey:
                        result = push_service.notify_single_device(
                        registration_id=userkey,
                        message_title="Ignition status update",
                        message_body=f"Ignition ON for your vehicle No : {data_list[1]}"
                    )
                    print("Ignition on notification send to user")
            except Exception as e:
                print("record creation failed in Devicedata",e)
            

           
        elif packet_type == 'emergency':
            msg_date=data_list[4]
            formated_date=str(msg_date[4:8])+"-"+str(msg_date[2:4])+"-"+msg_date[:2]
            
            formated_date=formated_date+" "+msg_date[8:10]+":"+msg_date[10:12]+":"+msg_date[12:]
            print("formatted date:",formated_date)
            try:
                formated_date1=str(datetime.now())[:19].replace('T',' ')
                systemtime=datetime.strptime(formated_date1,"%Y-%m-%d %H:%M:%S")
                if data_list[1]=='SEM':
                    other_info="Stop Emergency msg"
                else:
                    other_info="Emergency msg"
                data_rec=DeviceData(                    
                    imei = self.imei,
                    message = device_msg,
                    message_type=packet_type,
                    received_at = ctime  
                )
                db.add(data_rec)     
                db.commit() 
                 
                print("record created in device data table::",data_rec)
            except Exception as e:
                print("record creation failed in Devicedata_AIS::::",e)
            
            
            
    


    



    #######################
    #Device Thread start function
    #######################    
    def run(self):
        db:Session =SessionLocal()
        try:
            print("#############################################################")
            print("________________________NEW DEVICE THREAD STARTS________________________________ ")
            print(str(datetime.now()+timedelta(hours=5,minutes=30))[:19])
            HEADER = 1024
            FORMAT = "utf-8"
            print(f"[NEW CONNECTION] Connected to{self.addr} ")
            connected = True
            count = 0
            
            print("Active threads :",threading.active_count())
            while connected:            
                device_msg = self.conn.recv(HEADER)
                if not device_msg:                
                    break
                if not device_msg.startswith(b'$'):
                    connected = False
                    print("Invalid Message>>>",device_msg)                
                    break 
                count=count+1          
                
                msg=str(datetime.now()+timedelta(hours=5,minutes=30))[:19]+" ::  "+str(device_msg)
                ## need to save the device message to db
                print("__________________________TIME__________________________")
                print(str(datetime.now()+timedelta(hours=5,minutes=30))[:19])
                print(count,": [NEW MESSAGE]->",device_msg)

                #sample device messages 
                # //$LGN,KL09A12,866772041471415,FV1.0,AIS140           
                # $LGN,OD00AB1234,866772041471415,FIRMWAREVER1.0,AIS140,30.10145,78.28998,DDE3220E*
                # $PVT,VNDR,FIRMWAREVER1.0,NR,1,L,860260051760232,PB01BV2345,1,14122022,172946,31.589618,N,75.875231,E,0,117.58,39,286.7,0.42,0.43,BHARAT,0,1,12.2,4.1,0,C,12,404,53,16C7,E4C2,2138,700000,29,2137,700000,21,2136,700000,21,968A,70000,19,0000,0000,00,0,492894,00AC*
                

                device_msg_in_utf8 =device_msg.decode("ascii")
                print("TO STRING::::",device_msg_in_utf8)
                data=[]
                data = device_msg_in_utf8.split(',')
                header = data[0]
                print("Message list:::",data)
                if header == '$EPB':
                    if not self.imei:
                        connected = False
                        #login packet should be the first one
                        break                  
                    packettype='emergency'
                    print("Emergency>>>>>>>>>")
                    self.conn.send(b'$YES')
                    self.insert_to_database(db,packettype,data,device_msg_in_utf8) 

                elif header == '$LGN':
                    packettype='login'
                    self.imei=data[2]
                    self.conn.send(b'$YES')
                    #insert to database
                    self.insert_to_database(db,packettype,data,device_msg_in_utf8)
                    
                elif header == '$PVT' and self.imei:
                    if not self.imei:
                        connected = False
                        #login packet should be the first one
                        break 
                    packettype='pvt'
                    # self.conn.send(b'$YES')
                    self.insert_to_database(db,packettype,data,device_msg_in_utf8)                
                
                #$HEL,VENDORID,FIRMWAREVER1.0,866772012345678,70,65,90,2,10,0011,00*
                elif header == '$HEL'and self.imei:
                    if not self.imei:
                        #login packet should be the first one
                        connected = False
                        break 
                    packettype='health'
                    self.conn.send(b'$YES')
                    self.insert_to_database(db,packettype,data,device_msg_in_utf8)
                elif self.imei:
                    self.conn.send(b'$YES')
                    
                elif not self.imei :
                    connected = False
                    print("Missing login info,ending connection...")
                    print("Try to connect again....")
                    count = count-1
                    break    
        except Exception as e:
            if 'Connection reset by peer' in str(e) :
                print('connection to device is lost.....Ending communication....')
            else:
                print("exception......in run...:: ",e) 
        finally:
            db.close()
            print('connection to db closed.')
            self.conn.close()  
            print('connection to device closed.')
            



