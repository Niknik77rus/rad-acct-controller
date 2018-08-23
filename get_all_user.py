from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import sys
import get_all_user_config

def get_all_users():
    cnx = mysql.connector.connect(user='radius', password='ohRmAEwh',
                              host='127.0.0.1',
                              database='radius',
                              use_pure=False)
    cursor = cnx.cursor()
    allusers = "select username, planName, lastbill, nextbill from userbillinfo where username in (select username from radusergroup where groupname<>'daloRADIUS-Disabled-Users' and priority=0);"
    cursor.execute(allusers)
    allusers_info = list(cursor.fetchall())
    cursor.close()
    cnx.close()
    print(allusers_info)
    return allusers_info

def write_info_pod(info_pod_list):
    with open("blocked_users.py", "w") as pod_file:
        for item in info_pod_list:
            res_str = item[0] + ' ' +  item[1]  + ' ' + item[2]  + ' ' + item[3]
            pod_file.write(res_str + '\n')


def get_vol_user(allusers_info):
    vol_user_list = []
    cnx = mysql.connector.connect(user='radius', password='ohRmAEwh',
                              host='127.0.0.1',
                              database='radius',
                              use_pure=False)
    cursor = cnx.cursor()
    for i in range (len(allusers_info)):
        info_pod_list = []
        get_quota = ("select planTrafficTotal from billing_plans where planName=\'" + allusers_info[i][1]+ "\';")
        cursor.execute(get_quota)
        qouta_sql = cursor.fetchall()
        quota = int(qouta_sql[0][0]) // 1024 // 1024
        print(quota)
        vol_user = ("select sum(acctoutputoctets + acctinputoctets) from radacct where username=%s and acctstarttime between %s and %s;")
        username = allusers_info[i][0]
        starttime = allusers_info[i][2]
        endtime = allusers_info[i][3]
        cursor.execute(vol_user, (username, starttime, endtime))
        res_vol_user = cursor.fetchall()
        if res_vol_user[0][0] == None:
            print('None', username, 'no acct in this period')
        else:
            res_mb = res_vol_user[0][0] // 1024 // 1024
            print(username, res_mb)
            vol_user = [username, res_mb]
            vol_user_list.append(vol_user)
            if res_mb < quota:
                print(username, 'has a valid prof')

            else:
                print(username, 'need to be blocked')
                upd_ug_pri = ("update radusergroup set priority=20 where username=\'" + username + "\' and groupname<>'daloRADIUS-Disabled-Users';")
                username = allusers_info[i][0]
		#COMMENTED FOR TESTS
                #cursor.execute(upd_ug_pri)
                #cnx.commit()
                ins_ug_dis = ("INSERT INTO radusergroup values (\'" + allusers_info[i][0] + "\', \'daloRADIUS-Disabled-Users\', 0);")
                #cursor.execute(ins_ug_dis)
                #cnx.commit()
                get_info_pod = ("select username, acctsessionid, nasipaddress, framedipaddress from radacct  where username=\'" + allusers_info[i][0] + "\' and acctstoptime is NULL")
                cursor.execute(get_info_pod)
                info_pod = cursor.fetchall()
		info_pod_list.append(info_pod[0])
                print("TEST INFO POD", info_pod) 
	
    write_info_pod(info_pod_list)	
    cursor.close()
    cnx.close()
    write_info_pod(info_pod_list)
    print(info_pod_list)
    #print(vol_user_list)
    #return vol_user_list

get_vol_user(get_all_users())


