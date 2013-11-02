"""
<A basic resource allocation program written for a Morgan Stanley Hackathon>
    Copyright (C) 2013  Team Midas

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json, urllib, urllib2
import math
import operator
import requests

url = 'http://hermes.wha.la/api/hermes'
token = 'f6ead613-de05-4a51-bda4-76ae2448c1b8'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
pAP = 0
pEU = 0
pNA = 0
hAP = []
hEU = []
hNA = []

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

CR = AutoVivification()

#JSON parsing functions
def getCostIncured(payout):
    return payout['ServerState']['CostIncured']

def getServerCost(payout):
    return payout['ServerState']['CostPerServer']

def getDQTime(payout):
    return payout['ServerState']['DisqualifyTimeInMilliSeconds']

def getInfrastructureUpgrades(payout):
    return payout['ServerState']['InfraStructureUpgradeLevels']

def getInfrastructureState(payout):
    return payout['ServerState']['InfraStructureUpgradeState']

def getPlayFileName(payout):
    return payout['ServerState']['InfraStructureUpgradeState']

def getProfitAccumulated(payout):
    return payout['ServerState']['ProfitAccumulated']

def getResearchUpgrades(payout):
    return payout['ServerState']['ResearchUpgradeLevels']

def getResearchUpgardeState(payout):
    return payout['ServerState']['ResearchUpgradeState']

def getServerTiers(payout):
    return payout['ServerState']['ServerTiers']

def getWebServers(payout):
    return getServerTiers(payout)['WEB']
 
def getWebRegions(payout):
    return getWebServers(payout)['ServerRegions']

def getWebNodeCount(payout, region):
    return getWebRegions(payout)[region]['NodeCount']

def getJavaServers(payout):
    return getServerTiers(payout)['JAVA']

def getJavaRegions(payout):
    return getJavaServers(payout)['ServerRegions']

def getJavaNodeCount(payout, region):
    return getJavaRegions(payout)[region]['NodeCount']

def getDBServers(payout):
    return getServerTiers(payout)['DB']

def getDBRegions(payout):
    return getDBServers(payout)['ServerRegions']

def getDBNodeCount(payout, region):
    return getDBRegions(payout)[region]['NodeCount']

def getTurnNo(payout):
    return payout['ServerState']['TurnNo']

def getTransactionTime(payout):
    return payout['ServerState']['TransactionTime']

def getWebTransactions(payout, region):
    return getWebRegions(payout)[region]['NoOfTransactionsInput']

def printWebTransactions(payout):
    AP = getWebTransactions(payout, 'AP')
    EU = getWebTransactions(payout, 'EU')
    NA = getWebTransactions(payout, 'NA')
    addHistory('AP', AP)
    addHistory('EU', EU)
    addHistory('NA', NA)
    print "Asia: " + str(AP)
    print "Europe: " + str(EU)
    print "North America: " + str(NA)

def setNodes(tier, region, count):
    CR['Servers'][tier]['ServerRegions'][region]['NodeCount'] = count

def clearCR():
    CR = {}

def addHistory(region, num):
    global hAP
    global hEU
    global hNA
    temp = []

    if(region == 'AP'):
        temp = hAP
    elif(region == 'EU'):
        temp = hEU
    else:
        temp = hNA

    if(len(temp) < 5):
        temp.append(num)
    else:
        temp = temp[1:]
        temp.append(num)

    if(region == 'AP'):
        hAP = temp
    elif(region == 'EU'):
        hEU = temp
    else:
        hNA = temp

"""
    if (len(temp) < 3):
        return 0
"""

def calcChange(region):
    global pAP
    global pEU
    global pNA
    global hAP
    global hEU
    global hNA
    dx = 0
    dx2 = 0
    temp = []
    
    if(region == 'AP'):
        temp = hAP
    elif(region == 'EU'):
        temp = hEU
    else:
        temp = hNA

    if(len(temp) < 5):
        return 0

    #lagrange save for maybe later use
#    p = (temp[0] * 8) + (temp[1] * -15) + (temp[2] * 16) + (temp[3] * -6) + (temp[4] * 2)
    
#    print "PREDICTIONS FOR " + region + " IS: " + str(p)

#Control functions
def nextTurn():
    data = {'Command': 'PLAY', 'Token': token}
    return requests.post(url, data=json.dumps(data), headers=headers)

def init():
    data = {'Command': 'INIT', 'Token': token}
    r = requests.post(url, data=json.dumps(data), headers=headers)
#    payout = r.json()

#    turn = getTurnNo(payout)
#    print "CURRENT TURN IS: " + str(turn)

#    print "# of EU Servers: " + json.dumps(getWebNodeCount(payout, 'EU'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': {'Servers': {'WEB': {'ServerRegions': {'EU': {'NodeCount': '-1'}}}}}}
    setNodes('WEB', 'EU', -1)
    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': CR}
    r = requests.post(url, data=json.dumps(data), headers=headers)


def main():
    init()
    r = nextTurn()

    while(1):
        payout = r.json()
        clearCR()

        turn = getTurnNo(payout)

        print ""
        print "CURRENT TURN IS: " + str(turn)

        printWebTransactions(payout)
        print ""
#        print "HISTORY OF ASIA: " + str(hAP)
#        print "HISTORY OF EUROPE: " + str(hEU)
#        print "HISTORY OF AMERICA: " + str(hNA)
#        calcChange('AP')
#        calcChange('EU')
#        calcChange('NA')
#        print ""

        r = nextTurn()
        raw_input("Press Enter to continue...")

main()
