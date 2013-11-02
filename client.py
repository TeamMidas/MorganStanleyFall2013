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
highTurn = 0

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

    dx = temp[4] - temp[3]
    dx2 = dx - temp[3] - temp[2]

    p = calcNext(temp, dx, dx2)

    if(region == 'AP'):
        pAP = p
        print "PREDICTED FOR ASIA IS: " + str(p)
    elif(region == 'EU'):
        pEU = p
        print "PREDICTED FOR EUROPE IS: " + str(p)
    else:
        pNA = p
        print "PREDICTED FOR AMERICA IS: " + str(p)

def calcNext(history, dx, dx2):
    current = history[4]
    trend = findTrend(history)
    ans = 0
    if(dx * dx2 < 0 and abs(dx) < 20):
        if(dx > 0):
            ans = current + int(1.125 * dx)
        else:
            ans = current - int(1.125 * dx)

    if(trend == 1 or trend == -1):
        ans = current

    if(trend == 2 or trend == -2):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.125 * dx)
            else:
                ans = current - int(.5 * dx)
        else:
            if (dx < 0):
                ans = current - int(1.125 * dx)
            else:
                ans = current + int(.5 * dx)

    if(trend == 3 or trend == -3):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.25 * dx)
            else:
                ans = current - int(.25 * dx)
        else:
            if(dx < 0):
                ans = current - int(1.25 * dx)
            else:
                ans = current + int(.25 * dx)

    if(trend == 4 or trend == -4):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.5 * dx)
            else:
                ans = current - (.125 * dx)
        else:
            if (dx < 0 ):
                ans = current - int(1.5 * dx)
            else:
                ans = current + int(.125 * dx)

    return ans

def findTrend(a):
    i = 0
    if(a[4] > a[3]):
        i = 1
        while(i < 4 and a[len(a) - i - 1] > a[len(a)- i - 2]):
            i=i+1
    else:
        i = -1
        while(i > -5 and a[len(a) - 1 + i] < a[len(a) - 2 + i]):
            i = i-1
    
    return i

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
    global highTurn
    difAP = 0
    difEU = 0
    difNA = 0
    init()
    r = nextTurn()

    while(1):
        payout = r.json()
        if(highTurn > getTurnNo(payout)):
            print "CURRENT TURN IS: " + str(getTurnNo(payout))
            break
        clearCR()
        highTurn = getTurnNo(payout)
        turn = getTurnNo(payout)
        print ""
        print "CURRENT TURN IS: " + str(turn)
        print getTransactionTime(payout)
        printWebTransactions(payout)
        print ""
        
        if(turn > 10):
            if(difAP < abs(hAP[4]-pAP)):
                difAP = abs(hAP[4] - pAP)
            if(difEU < abs(hEU[4] - pEU)):
                difEU = abs(hEU[4]-pEU)
            if(difNA < abs(hNA[4] - pNA)):
                difNA = abs(hNA[4] - pNA)
            print "Highest mistake ASIA: " + str(difAP)
            print "Highest mistake EUROPE: " + str(difEU)
            print "Highest mistake AMERICA: " + str(difNA)

        print ""
#        print "HISTORY OF ASIA: " + str(hAP)
#        print "HISTORY OF EUROPE: " + str(hEU)
#        print "HISTORY OF AMERICA: " + str(hNA)
        calcChange('AP')
        calcChange('EU')
        calcChange('NA')
        print ""

        r = nextTurn()
        #raw_input("Press Enter to continue...")

main()
