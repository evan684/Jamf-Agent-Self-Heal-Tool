#!/usr/bin/env python3

import requests
import argparse
import os
import getpass
import sys

jamfURL = "https://jamf.example.com:8443"


def create_parser():
    parser = argparse.ArgumentParser(description="This tool is used to pull jamf advanced searches into reports and email them.")
    parser.add_argument('--nosslverify', '-k', required=False, action='store_true', help="Disables SSL checking")
    parser.add_argument('--prompt', '-p',  required=False, action='store_true',help="Prompts for username and password instead of using enviroment variable.")
    parser.add_argument('--serial', '-s', required=False, help="Allows you to pass in a serial to be processed with out the need to enter it in a prompt.")
    parser.add_argument('-yes', '-y', action='store_true', help="Bypasses confirmation prompt.")
    return parser

#Arg Collection
parser = create_parser()
args = parser.parse_args()

# SSL Check Status
if args.nosslverify == True:
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    ssl_verification = False
else:
    ssl_verification = True

def prompt_for_creds():
    global username
    global password
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")


def ask_to_continue():
    i = 0
    while i < 2:
        answer = input("Would you like to continue with this device? (yes or no): ")
        if any(answer.lower() == f for f in ["yes", 'y']):
            continuePrompt = "Yes"
            break
        elif any(answer.lower() == f for f in ['no', 'n']):
            continuePrompt = "No"
            break
        else:
            i += 1
            if i < 2:
                print('Please enter yes or no.')
            else:
                continuePrompt = "None"
    return continuePrompt

def check_website(website, ssl):
    """
    Checks status of entered website and will exist script if connection fails.
    """
    try: 
        requests.get(website, verify=ssl).status_code
    except requests.exceptions.SSLError:
        print("The site returned an SSL error. Verifiy your url is correct. If needed pass in a --nosslverify or -k flag to skip ssl verification. This will reduce security.")
        sys.exit()
    except:
        print("A connection error occurred. Make sure you have the correct URL and port if needed.")
        sys.exit()
    else:
        pass

def jamf_auth(jamfurl, ssl, u, p):
    """
    Handles Jamf bearer auth returns token and expeiration as global vars to be used elseware in script.
    """
    authURL="/api/v1/auth/token"
    global token
    global tokenExpiration
    try:
        req = requests.post(jamfurl + authURL, verify=ssl, auth=(u, p), headers={"accept":"application/json"})
        data = req.json()
        token = data['token']
        tokenExpiration = data['expires']
    except:
        print("Error: Authentication failed.")
        sys.exit()

def jamf_invalidate_token(jamfurl, ssl, token):
    """
    invalidates bearer token.
    """
    apiurl = "/api/v1/auth/invalidate-token"
    req = requests.post(jamfurl + apiurl, verify=ssl, headers={"accept":"*/*", "Authorization":"Bearer " + token})

def jamf_search_computer_by_serial(jamfurl, ssl, serial, token):
    computerSerialNumberSearch = "/JSSResource/computers/serialnumber/"
    try: 
        req = requests.get(jamfurl + computerSerialNumberSearch + serial, verify=ssl, headers={"accept":"application/json", "Authorization":"Bearer " + token})
        if req.status_code == 404:
            print("The serial number returned with 404 not found error. Please double check the serial number.")
            sys.exit()
    except:
        print("Error: A connection error occurred.")
        sys.exit()
    else:
        data = req.json()
        print(f"Computer Name: {data['computer']['general']['name']} Id: {data['computer']['general']['id']}")
        print(f"Last Check In: {data['computer']['general']['last_contact_time']}")
        print(f"Assigned User: {data['computer']['location']['username']}")
        deviceID = data['computer']['general']['id']
        return deviceID

def jamf_send_framework_reinstall_command(jamfurl, ssl, deviceid, token):
    apiurl = "/api/v1/jamf-management-framework/redeploy/"
    try:
        req = requests.post(jamfurl + apiurl + str(deviceid), verify=ssl, headers={"accept":"application/json", "Authorization":"Bearer " + token})
    except:
        print("Error: A connection error occurred.")
        sys.exit()
    else:
        data = req.json()
        sentdeviceid = data['deviceId']
        sentcommandUUID = data['commandUuid']
        print(f"Command sent to device id: {sentdeviceid} and returned a sucess code with command UUID: {sentcommandUUID}" )


### Work starts here
prompt_for_creds()

#Verifiy we can connect to website.
check_website(jamfURL, ssl_verification)

#prompt for user auth if needed.
jamf_auth(jamfURL, ssl_verification, username, password)

#search computer serial. Prompt for serial if none are passed in.
if args.serial:
    deviceSerial = str(args.serial)
else:
    deviceSerial = input("Enter Serial Number: ")
deviceID = jamf_search_computer_by_serial(jamfURL, ssl_verification, deviceSerial, token)

# prompt user to contunie if bypass is not passed in.
if args.yes:
    continuePrompt = "Yes"
else:
    continuePrompt = ask_to_continue()

#send jamf framework reinstall command.
if continuePrompt == "Yes":
    jamf_send_framework_reinstall_command(jamfURL, ssl_verification, deviceID, token)
elif continuePrompt == "No":
    jamf_invalidate_token(jamfURL, ssl_verification, token)
    print("User opted to cancel operation, exiting script.")
else:
    print("No option selected exiting script.") 
    
