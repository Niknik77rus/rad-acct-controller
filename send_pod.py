import os

pod_users = open('blocked_users.py')
for line in pod_users:
    info_pod = line.split()
    #print info_pod[0]
    pod_command =  "echo \"User-Name = " + info_pod[0] + ", Acct-Session-Id = " + info_pod[1] + ", NAS-IP-Address = " + info_pod[2] + ", Framed-IP-Address = " + info_pod[3] + "\" | /usr/bin/radclient " + info_pod[2] + ":3799 disconnect SECRET"
    print pod_command
    os.system(pod_command)
