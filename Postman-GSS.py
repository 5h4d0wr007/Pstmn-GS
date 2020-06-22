#!/usr/bin/python
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ORANGE = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
org = raw_input("Enter name of the Organization to audit: ")
emailUser = raw_input("Enter your Email address: ")
emailPassword = raw_input("Enter your password: ")
githubToken = raw_input("Enter your Github personal access token: ")
emailSend = raw_input("Enter Email address of the Security Team: ")
subject = 'Automated GitHub Audit Report'
print(bcolors.ORANGE+'''                                                                                              
    ____                __                            __        __                 
   / __ \ ____   _____ / /_ ____ ___   ____ _ ____   / /____ _ / /_   _____        
  / /_/ // __ \ / ___// __// __ `__ \ / __ `// __ \ / // __ `// __ \ / ___/______  
 / ____// /_/ /(__  )/ /_ / / / / / // /_/ // / / // // /_/ // /_/ /(__  )/_____/ 
/_/     \____//____/ \__//_/ /_/ /_/ \__,_//_/ /_//_/ \__,_//_.___//____/        
    
   ______ _  __   __  __        __           _____                                       
  / ____/(_)/ /_ / / / /__  __ / /_         / ___/ _____ ____ _ ____   ____   ___   _____
 / / __ / // __// /_/ // / / // __ \ ______ \__ \ / ___// __ `// __ \ / __ \ / _ \ / ___/
/ /_/ // // /_ / __  // /_/ // /_/ //_____/___/ // /__ / /_/ // / / // / / //  __// /    
\____//_/ \__//_/ /_/ \__,_//_.___/       /____/ \___/ \__,_//_/ /_//_/ /_/ \___//_/ 

''' + bcolors.ENDC)
today = date.today()
msg = MIMEMultipart()
msg['From'] = emailUser
msg['To'] = emailSend
msg['Subject'] = subject
body = 'Hi Security Team, Please find attached the report generated from GitHub scan on '+ str(today)
msg.attach(MIMEText(body,'plain'))
with open("/tmp/output.log", "a") as output:
    print(bcolors.OKGREEN + "[+] Cloning the repositories" + bcolors.ENDC)
    print(bcolors.OKGREEN + "[+] Scanning all org repositories now. This may take a while so please be patient" + bcolors.ENDC)
    callDockerRun = "docker run -it abhartiya/tools_gitallsecrets -token="+githubToken+" -org="+org+" -orgOnly"
    #print(callDockerRun)
    dockerRun = subprocess.call(callDockerRun, shell=True, stdout=output, stderr=output) 
    if (dockerRun == 0):
        print(bcolors.OKGREEN + "[+] Finished scanning all repositories" + bcolors.ENDC)
        fetchID = subprocess.check_output("docker ps -alq",shell=True) 
        newFetchID = fetchID.rstrip("\n")
	args = "docker cp {}:/root/results.txt .".format(newFetchID)
        finalCommand = subprocess.call(args,shell=True, stdout=output, stderr=output)
        if (finalCommand == 0):
            print(bcolors.OKGREEN + "[+] Combining the output into one file" + bcolors.ENDC)
	    filename='results.txt'
            attachment  =open(filename,'rb')
	    part = MIMEBase('application','octet-stream')
	    part.set_payload((attachment).read())
	    encoders.encode_base64(part)
	    part.add_header('Content-Disposition',"attachment; filename= "+filename)
	    msg.attach(part)
	    text = msg.as_string()
	    server = smtplib.SMTP('smtp.gmail.com',587)
	    server.starttls()
	    server.login(emailUser,emailPassword)
	    server.sendmail(emailUser,emailSend,text)
	    server.quit()
	    print(bcolors.OKGREEN + "[+] Result sent to the Security Team via email" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "[-] Combining the output failed" + bcolors.ENDC)
   	    print(bcolors.FAIL + "[-] Quitting..." + bcolors.ENDC)
    else:
	print(bcolors.FAIL + "[-] Docker run failed" + bcolors.ENDC)
        print(bcolors.FAIL + "[-] Quitting..." + bcolors.ENDC)
