import requests
import json
import sys
import argparse
import re
import os
import datetime

#colors..
run         = '\033[93m[~]\033[0m'
good        = '\033[92m[+]\033[0m'
bad         = '\033[91m[-]\033[0m'
info        = '\033[93m[!]\033[0m'
red         = '\033[91m'
end         = '\033[0m'
que = '\033[94m[?]\033[0m'
G = '\033[92m'
Y = '\033[93m' # yellow
B = '\033[94m'
#headers
headers = {
    'Accept': 'application/json',
    'Connection' : 'Keep-Alive',
}
#ripe.net api url
API_URL = 'http://rest.db.ripe.net/'
now = datetime.datetime.now()
hash_exportname = now.strftime("%d%b%M%S")


def banner():
    print("""
%s ___________   _____       _   _               %s_   %s          
|_   _|%s ___%s \ |  __ \     | | | |            %s (_)%s            
  | | | %s|_/%s / | |  \/ __ _| |_| |__   ___ _ __ _ _ __   __ _ 
  | | |  __/  | | __ /%s _%s` | __| '_ \ / _ \ '__| | '_ \ /%s _%s` |
 _| |_| |     | |_\ \ %s(_|%s | |_| | | |  __/ |  | | | | | %s(_|%s |
 \___/\_|      \____/\__,_|\__|_| |_|\___|_|  |_|_| |_|\__, |
                                        %s@Omarbenabdejlil%s__/ |
                                                       |___/ 
    %s""" % (B,Y,B,Y,B,Y,B,Y,B,Y,B,Y,B,Y,B,Y,B,Y,B,end))

banner()

#arg message error
def parser_error(errmsg):
    print("Usage: python " + sys.argv[0] + " [Options] use -h for help")
    print("Error: " + errmsg)
    sys.exit()

#args module
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u google.com")
    parser.error = parser_error
    parser._optionals.title = "\nOPTIONS"
    parser.add_argument('-i', '--ip', help="ip target",dest='ARG_IP')
    parser.add_argument('-f', '--file', help="specify input file of ipaddresses",dest='input_file')
    parser.add_argument('-e', '--export', help="export data.",dest='export_file',action='store_true')
    return parser.parse_args()

# Assign arguments
args = parse_args()
ARG_IP = args.ARG_IP
ARG_FILE = args.input_file
ARG_EXPORT = args.export_file

# get information from ripe !!!-> using ripe api.
def ipGathering(ip):
    endpoint = 'search?source=ripe&query-string='+ip+''
    coordination = requests.get(API_URL+endpoint,headers=headers).json()
    qs_array = coordination['parameters']['query-strings']['query-string']
    print('\n%s------------------------------------------- %s' % (G,end))
    if (len(qs_array) > 0):
        for i in range(len(qs_array)):
            print('\n%s Target : %s ' % (que,qs_array[i]['value']))
            print('\n%s------------------------------------------- %s' % (G,end))
    else:
        print('%s No Target Found.' % bad)
    attributes_array = coordination['objects']['object']
    for i in range(len(attributes_array)):
        datainc = attributes_array[i]['attributes']['attribute']
        for c in range(len(datainc)):
            print('%s %s : %s ' % (good,datainc[c]['name'],datainc[c]['value']))
    if ARG_EXPORT:
        exporter(ip)
    print('%s-------------------------------------------\n %s' % (G,end))

# method validateIP : !!!-> using regular expression when adding ip argument.
def validateIp(ip):
    regx = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    rec = re.compile(regx)
    matchip = rec.match(ip)
    if matchip == None:
        print('%s %s Not IPAddress format.'% (bad,ip))
    else:
        ipGathering(ip)

# method importer to import ip addresses from file.
def importer(file):
    if os.path.exists(file):
        with open(ARG_FILE,'r') as ipaddresses:
            ip_array = [ip.strip('\n') for ip in ipaddresses]
        try:
            for ip in ip_array:
                ipGathering(ip)
                if ARG_EXPORT:
                    exporter(ip)
        except Exception as error_:
            print('error : '+ str(error_))
    else:
        print('%s file not found.' % bad)

# method exporter to export data into a file
def exporter(ip):
    filename = 'exported/'+hash_exportname+'_log'
    if not os.path.exists('exported'):
        os.mkdir('exported')
        print('%s exported directory created.' % run)
    endpoint = 'search?source=ripe&query-string='+ip+''
    coordination = requests.get(API_URL+endpoint,headers=headers).json()
    qs_array = coordination['parameters']['query-strings']['query-string']
    with open(filename, 'a+') as savefile:
        if (len(qs_array) > 0):
            for i in range(len(qs_array)):
                savefile.write('\n\n******************\n'+qs_array[i]['value']+'\n******************\n')
    savefile.close()
    with open(filename, 'a+') as savefile:    
        attributes_array = coordination['objects']['object']
        for i in range(len(attributes_array)):
            datainc = attributes_array[i]['attributes']['attribute']
            for c in range(len(datainc)):
                savefile.write(''+datainc[c]['name']+':'+datainc[c]['value']+'\n')
    savefile.close()
    print('%s %s %s %s has been updated.\n' % (info,G,filename,end))

#main
if __name__ == "__main__":
    if ARG_FILE:
        print('\n%s Process Running...' % run)
        importer(ARG_FILE)

    elif ARG_IP:
        print('\n%s Process Running...' % run)
        validateIp(ARG_IP)
    else:
        print('%s No target found use -h for help' % bad)