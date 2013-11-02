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
from pylab import *

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
difAP = 0
difNA = 0
difEU = 0
fig = plt.figure()

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

def getProfitConstant(payout):
    return payout['ServerState']['ProfitConstant']

def getProfitAccumulated(payout):
    return payout['ServerState']['ProfitAccumulated']

def getProfitEarned(payout):
    return payout['ServerState']['ProfitEarned']

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

def getWebCapacity(payout):
    return getWebServers(payout)['ServerPerformance']['CapactityLevels'][0]['UpperLimit']

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

"""
This should give upgrades
To set nodes and do upgrades do:
    setNodes(tier, region, count)
    upgrades(infrastructure, research)
    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': CR}
    r = requests.post(url, data=json.dumps(data), headers=headers)
"""

def upgrades(infrastructure, research):
    CR['Servers']['UpgradeInfrastructure'] = infrastructure
    CR['Servers']['UpgradeToResearch'] = research

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
    
    spike = spikeDetection(temp, region)
    if(spike > 0):
        if(spike > 10):
            p = temp[4]
        else:
            #v = 2**spike
            v = math.log(spike) * 1.5
            if(temp[4] - temp[3] > 0):
                p = temp[4] + int((temp[4] - temp[3]) * v)
            else:
                p = temp[4] - int(((temp[4] - temp[3]) * -1) * v)
    else:
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
            ans = current + int(1.06 * dx)
        else:
            ans = current - int(1.06 * dx)

    if(trend == 1 or trend == -1):
        ans = current

    if(trend == 2 or trend == -2):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.125 * dx)
            else:
                ans = current - int(.875 * dx)
        else:
            if (dx < 0):
                ans = current - int(1.125 * dx)
            else:
                ans = current + int(.875 * dx)

    if(trend == 3 or trend == -3):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.25 * dx)
            else:
                ans = current - int(.75 * dx)
        else:
            if(dx < 0):
                ans = current - int(1.25 * dx)
            else:
                ans = current + int(.75 * dx)

    if(trend == 4 or trend == -4):
        if(trend > 0):
            if(dx > 0):
                ans = current + int(1.5 * dx)
            else:
                ans = current - (.5 * dx)
        else:
            if (dx < 0 ):
                ans = current - int(1.5 * dx)
            else:
                ans = current + int(.5 * dx)

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
    
def spikeDetection(a, region):
    temp = 0
    if(region == 'AP'):
        temp = pAP
    elif(region == 'EU'):
        temp = pEU
    else:
        temp = pNA

    if(abs(a[4] - temp) > 300):
        if(abs(a[4] - a[3]) < 200):
            return int(a[4] * 0.5)
        elif(abs(a[3] - a[2]) < 200):
                 return int(a[4] * 0.8)
        else:
            return a[4]

    i = 1
    if (abs(a[4] - temp) > 80):
        while(i < 4 and a[4-i]-a[3-i] > 60):
            i=i+1
        return i
    else:
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
    payout = r.json()

#    turn = getTurnNo(payout)
#    print "CURRENT TURN IS: " + str(turn)

#    print "# of EU Servers: " + json.dumps(getWebNodeCount(payout, 'EU'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': {'Servers': {'WEB': {'ServerRegions': {'EU': {'NodeCount': '-1'}}}}}}


#    print json.dumps(getInfrastructureUpgrades(payout), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#    print json.dumps(getWebCapacity(payout), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#    print json.dumps(payout['ServerState'], sort_keys=True, indent=4, separators=(',', ': ')) + "\n"

    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': CR}
    r = requests.post(url, data=json.dumps(data), headers=headers)

def main():
    global highTurn
    global difAP
    global difEU
    global difNA
    avgAP = 0.0
    avgEU = 0.0
    avgNA = 0.0
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
        print "TIME IS: " + getTransactionTime(payout)
        print ""
        printWebTransactions(payout)
        print ""

        print "Money earned so far: " + str(getProfitAccumulated(payout))
        print "Money earned this turn: " + str(getProfitEarned(payout))
        print ""

        if(turn > 10):
            if(difAP < abs(hAP[4]-pAP)):
                difAP = abs(hAP[4] - pAP)
            if(difEU < abs(hEU[4] - pEU)):
                difEU = abs(hEU[4]-pEU)
            if(difNA < abs(hNA[4] - pNA)):
                difNA = abs(hNA[4] - pNA)
            avgAP = (((avgAP * (turn - 11)) + abs(hAP[4] - pAP)) / (turn - 10))
            avgEU = (((avgEU * (turn - 11)) + abs(hEU[4] - pEU)) / (turn - 10))
            avgNA = (((avgNA * (turn - 11)) + abs(hNA[4] - pNA)) / (turn - 10))
            print "Average Mistake ASIA: " + str(avgAP)
            print "Average Mistake EUROPE: " + str(avgEU)
            print "Average Mistake AMERICA: " + str(avgNA)
            print ""
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

        #plots (turn, profit) as scatter plot
#        plt.axis([0,turn+10,0,3000])
#        Profit = getProfitEarned(payout)
#        plt.scatter(turn, Profit, color='green')


        plt.axis([0,turn+10,0,500])
        TransNA = getWebTransactions(payout, 'NA')
        TransEU = getWebTransactions(payout, 'EU')
        TransAP = getWebTransactions(payout, 'AP')


        plt.scatter(turn, TransNA, color='red')
        plt.scatter(turn, TransEU, color='blue')
        plt.scatter(turn, TransAP, color='orange')
        
        #this is for live plotting only
#        plt.pause(0.00000000000000000000000000000000000000000001)
#        plt.draw()


#        print 'DB NODES IN NA: ' + json.dumps(getDBNodeCount(payout, 'NA'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#        print 'DB NODES IN EU: ' + json.dumps(getDBNodeCount(payout, 'EU'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
#        print 'DB NODES IN AP: ' + json.dumps(getDBNodeCount(payout, 'AP'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"

        r = nextTurn()
#        if(turn > 2400):
#            plt.show()
        raw_input("Press Enter to continue...")

main()
