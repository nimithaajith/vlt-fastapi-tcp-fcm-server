#device threads

import threading
from datetime import datetime,timedelta
from models import *
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import List
from pyfcm import FCMNotification
FCM_API_KEY = "YOUR_FCM_SERVER_KEY"  # Replace with your actual Firebase Server Key
push_service = FCMNotification(api_key=FCM_API_KEY)

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
            

            # try:
            #     live_rec=Livedata_AIS.objects.filter(imei=self.imei)
            #     if live_rec.exists():
            #         live_rec=live_rec[0]
            #         try:
            #             # UPDATING ALERTS
            #             #1.overspeed alert status
            #             if float(data_list[15]) >60 :
            #                 live_rec.overspeed = formated_date
                        
            #             #2.emergency alert status
                        
            #             if data_list[4] == "10" or other_info=="EmergencyAlert":                            
            #                 live_rec.emergency = ctime
            #             elif data_list[4] == "11" or other_info=="EmergencyAlertOFF":                            
            #                 live_rec.emergency = "Normal"                          

            #             #3.main battery alert status
            #             if data_list[4] == "3" or other_info=="Vehicle Battery Disconnect":
            #                 live_rec.main_battery ='Disconnect '+ctime
            #             elif data_list[4] == "6" or other_info=="Vehicle Battery Reconnect":
            #                 live_rec.main_battery = 'Connect '+ctime 

            #             #4.Internal battery alert status
            #             if data_list[4] == "4" or other_info=="Internal Battery Low":
            #                 live_rec.internal_battery ='Low '+ctime
            #             elif data_list[4] == "5" or other_info=="Internal Battery Charged":
            #                 live_rec.internal_battery = 'Charged '+ctime 
                        
            #             #5.GPS box alert status
            #             if data_list[4] == "9":
            #                 live_rec.gps_box = ctime
                        
            #             #6.parameter change over air alert status
            #             if data_list[4] == "12" or other_info=="Over the air Update":
            #                 live_rec.para_change =ctime
            #             #other warning alert status
            #             if data_list[4] == "13" or other_info=="Harsh Breaking":
            #                 live_rec.harsh_breaking =ctime                        
            #             if data_list[4] == "14" or other_info=="Harsh Acceleration":
            #                 live_rec.harsh_acc =ctime
            #             if data_list[4] == "15" or other_info=="Rash Turning":
            #                 live_rec.rash_turn =ctime
            #             if data_list[4] == "16" or other_info=="TamperAlert":
            #                 live_rec.tampered =ctime
            #             if data_list[4] == "19" or other_info=="Collision Alert":
            #                 live_rec.collision =ctime
            #             if data_list[4] == "20" or other_info=="Overspeed":
            #                 live_rec.overspeed =ctime
            #             if data_list[26] == "1":
            #                 live_rec.sos =ctime                         
            #             live_rec.device_data =device_msg
            #             live_rec.ctime=ctime
            #             live_rec.systemtime=systemtime
            #             live_rec.packet_type=packet_type
            #             live_rec.other_info=other_info
                        
            #             live_rec.save()
            #             print("live updated")
            #         except Exception as e:
            #             print("live rec delete exception, ::",e)
            #     else:
            #         #alerts
            #         if float(data_list[15]) >60 :
            #                 overspeed = ctime 
            #         elif data_list[4] == "20" or other_info=="Overspeed":
            #             overspeed =ctime
            #         else:
            #             overspeed ="Normal"                                     
            #         if data_list[4] == "10" or other_info=="EmergencyAlert":                            
            #             emergency = ctime
            #         else:                            
            #             emergency = "Normal" 
            #         if data_list[4] == "3" or other_info=="Vehicle Battery Disconnect":
            #             main_battery ='Disconnect '+ctime
            #         elif data_list[4] == "6" or other_info=="Vehicle Battery Reconnect":
            #             main_battery = 'Connect '+ctime 
            #         else:
            #             main_battery ="Normal"
            #         if data_list[4] == "4" or other_info=="Internal Battery Low":
            #             internal_battery ='Low '+ctime
            #         elif data_list[4] == "5" or other_info=="Internal Battery Charged":
            #             internal_battery = 'Charged '+ctime 
            #         else:
            #             internal_battery ='Normal'
                    
            #         if data_list[4] == "9":
            #             gps_box ='Opened '+ctime
            #         else:
            #             gps_box ="Normal"
            #         if data_list[4] == "12" or other_info=="Over the air Update":
            #             para_change =ctime
            #         else:
            #             para_change ="Normal"
            #         if data_list[4] == "13" or other_info=="Harsh Breaking":
            #             harsh_breaking =ctime  
            #         else:
            #             harsh_breaking ="Normal"                     
            #         if data_list[4] == "14" or other_info=="Harsh Acceleration":
            #             harsh_acc =ctime
            #         else:
            #             harsh_acc ="Normal"
            #         if data_list[4] == "15" or other_info=="Rash Turning":
            #             rash_turn =ctime
            #         else:
            #             rash_turn ="Normal"
            #         if data_list[4] == "16" or other_info=="TamperAlert":
            #             tampered =ctime
            #         else:
            #             tampered ="Normal"
            #         if data_list[4] == "19" or other_info=="Collision Alert":
            #             collision =ctime
            #         else:
            #             collision ="Normal"
            #         if data_list[26] == "1":
            #             sos =ctime
            #         else:
            #             sos="Normal"
            #         data_rec=Livedata_AIS.objects.create(
            #             imei = self.imei,
            #             device_data = device_msg,
            #             ctime = ctime,
            #             systemtime = systemtime,
            #             packet_type = packet_type,
            #             overspeed = overspeed,
            #             emergency = emergency,
            #             collision=collision,
            #             rash_turn=rash_turn,
            #             harsh_acc=harsh_acc,
            #             harsh_breaking=harsh_breaking,
            #             gps_box=gps_box,
            #             para_change=para_change,
            #             tampered=tampered,
            #             internal_battery=internal_battery,
            #             main_battery=main_battery,
            #             other_info=other_info,
            #             sos=sos
            #         )                 
            #     print("record created in live  table::")
            # except Exception as e:
            #     print("record creation failed in Livedata_AIS:::",e)
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
            
            
            # try:
            #     live_rec=Livedata_AIS.objects.filter(imei=self.imei)
            #     if live_rec.exists():
            #         live_rec=live_rec[0]
            #         try:
            #             if data_list[1]=='EMR':
            #                 live_rec.emergency = formated_date
            #             elif data_list[1]=='SEM':
            #                 live_rec.emergency = 'Normal'
            #             live_rec.save()    
            #         except Exception as e:
            #             print("record update failed in Livedata_AIS:::",)
            #     else:
            #         print("No Live rec for this imei")        
            # except Exception as e:
            #     print("Live record fetch issue:::",e)  
    


    



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
            



