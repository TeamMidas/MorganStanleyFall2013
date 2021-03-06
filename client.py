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

#projected Demands for the next minute
pAP = 0 
pEU = 0 
pNA = 0 

#history of actual demands, goes back 4 minutes
hAP = [] 
hEU = [] 
hNA = []

#prediction error
difAP = 0
difNA = 0
difEU = 0

#ChangeRequests
CR = {}

trend = 0

#Database migration
preferredR = 'EU'
migration = 0
oldregion = 'EU'

#upgrades
expendedmoney = 0
upInfra = 2
upTech = 0

#database change rate normalizing
turncount = 0
idealDB = 0
nextTurn = 12

goingUpWeb = {'AP': {}, 'EU': {}, 'NA': {}}
goingUpJava = {'AP': {}, 'EU': {}, 'NA': {}}
goingUpData = {'AP': {}, 'EU': {}, 'NA': {}}

goingDownJava = {'AP': {}, 'EU': {}, 'NA': {}}
goingDownData = {'AP': {}, 'EU': {}, 'NA': {}}

downID = 1
upID = 1

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

def getResearchUpgradeLevels(payout):
    return payout['ServerState']['ResearchUpgradeLevels']

def getResearchUpgradeState(payout):
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

def getJavaCapacity(payout):
    return getJavaServers(payout)['ServerPerformance']['CapactityLevels'][0]['UpperLimit']

def getDBServers(payout):
    return getServerTiers(payout)['DB']

def getDBRegions(payout):
    return getDBServers(payout)['ServerRegions']

def getDBNodeCount(payout, region):
    return getDBRegions(payout)[region]['NodeCount']

def getDBCapacity(payout):
    return getDBServers(payout)['ServerPerformance']['CapactityLevels'][0]['UpperLimit']

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
    global CR

    if(len(CR) == 0):
        CR['Servers'] = {}
    if tier not in CR['Servers']:
        CR['Servers'][tier] = {}
    if(len(CR['Servers'][tier]) == 0):
        CR['Servers'][tier]['ServerRegions'] = {}
    if region not in CR['Servers'][tier]['ServerRegions']:
        CR['Servers'][tier]['ServerRegions'][region] = {}
    CR['Servers'][tier]['ServerRegions'][region]['NodeCount'] = count

def upgradesInfrastructure(infrastructure):
    CR['UpgradeInfrastructure'] = infrastructure

def upgradesResearch(research):
    CR['UpgradeToResearch'] = research

def upgradeLogic(payout):
    global upTech
    global upInfra
    global expendedmoney

    cash = getProfitAccumulated(payout)
    if(upTech >= 2):
        return 0 

#    if(getInfrastructureState(payout)['Key'] != 'LEVEL2' and upInfra > 1):
#        upgradesInfrastructure('true')
#        upInfra = upInfra - 1
#        return 1

    if(cash > 90000 and upTech == 0):
        upgradesResearch("GRID")
        upTech = 1
        expendedmoney = expendedmoney + 150000
        return 1

    if(upTech == 1 and turncount <= 5000):
        if(getResearchUpgradeState(payout)["GRID"] == -1 and cash > 90000):
            upgradesResearch("GREEN")
            upTech = 2
            expendedmoney = 400000
            return 1

        if(getResearchUpgradeState(payout)["GRID"] <= 1000 and cash > 150000 + expendedmoney):
            upgradesResearch("GREEN")
            upTech = 2
            expendedmoney = 8000000
            return 1

        if(getResearchUpgradeState(payout)["GRID"] <= 2000 and cash > 250000 + expendedmoney):
            upgradesResearch("GREEN")
            upTech = 2
            expendedmoney = 8000000
            return 1

        if(getResearchUpgradeState(payout)["GRID"] > 2000 and cash > 550000 + expendedmoney):
            upgradesResearch("GREEN")
            upTech = 2
            expendedmoney = 12000000
            return 1

    return 0

def clearCR():
    global CR
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
    global trend
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

def webLogic(payout, region):
    global upID
    global downID
    expected = 0
    if(region == 'AP'):
        expected = pAP
    elif(region == 'EU'):
        expected = pEU
    else:
        expected = pNA

    online = getWebNodeCount(payout, region)
    serverValue = getWebCapacity(payout)
    capacity = online * serverValue
    difference = expected - capacity
    needed = 0

    #print "REGION: " + region + " DIFFERENCE: " + str(difference) + " CAPACITY: " + str(capacity)
    #print ""
    if(difference > 0):
        needed = int(difference / serverValue)
        if(needed > 0):
            #print "WEB ADDED: " + str(needed)
            setNodes('WEB', region, needed)
            while(needed > 0):
                goingUpWeb[region][upID] = 2
                upID = upID+1
                needed = needed-1
            return 1
    elif(difference < 0):
        needed = int(difference / serverValue)
        if(online + needed <= 1):
             return 0
        if(needed < 0):
            #print "WEB REMOVED: " + str(needed)
            setNodes('WEB', region, needed)
            return 1
    return 0

def javaLogic(payout, region):
    global upID
    global downID
    expected = 0
    if(region == 'AP'):
        expected = pAP
    elif(region == 'EU'):
        expected = pEU
    else:
        expected = pNA

    online = getJavaNodeCount(payout, region)
    serverValue = getJavaCapacity(payout)
    capacity = online * serverValue
    difference = expected - capacity
    needed = 0

   # print "JAVA REGION: " + region + " DIFFERENCE: " + str(difference) + " CAPACITY: " + str(capacity)
   # print ""
    if(difference > 0):
        needed = int(difference / serverValue) - (len(goingUpJava[region]))

        if(needed > 0):
            #print "JAVA ADDED: " + str(needed)
            setNodes('JAVA', region, needed)
            while(needed > 0):
                goingUpJava[region][upID] = 4
                upID = upID+1
                needed = needed-1
            return 1
    elif(difference < 0):
        needed = int(difference / serverValue) + (len(goingDownJava[region]))
        if(online + needed <= 1):
             return 0
        if(needed < 0):
            #print "JAVA REMOVED: " + str(needed)
            while(needed < 0):
                setNodes('JAVA', region, needed)
                goingDownJava[region][upID] = 1
                downID = downID+1
                needed = needed+1
            return 1
    return 0

def dataLogic(payout):
    global upID
    global downID
    global preferredR
    global migration
    global oldregion
    global idealDB
    global nextTurn

    expected = 0

    region = preferredR

    serverValue = int(getDBCapacity(payout) * 1.25)

    if(migration > 0):
        print "CURRENTLY MIGRATING"
        migration = migration - 1
        return dataMove(payout)

    if(pNA > serverValue * 4 and hNA[4] > serverValue * 3 and pEU < serverValue * 3):
        preferredR = 'NA'
    elif((pEU > serverValue * 4 and hEU[4] > serverValue * 3 and pNA < 400 and hNA[4] < 600 and hNA[3] < 600 ) or (pAP > serverValue * 4 and hAP[4] > serverValue * 3 and pEU > serverValue * 3 and hEU[4] > serverValue * 4 and pNA < serverValue * 2 and hNA[4] < serverValue * 2)):
        preferredR = 'EU'

    #start of migration to new main area
    if(preferredR != region):
        temp = getDBNodeCount(payout, region)
        setNodes('DB', preferredR, temp)
        while(temp > 0):
            goingUpData[region][upID] = 8
            upID = upID+1
            temp = temp-1
        migration = 10
        oldregion = region
        return 1

    expected = pAP + pEU + pNA
    online = getDBNodeCount(payout, region)
    capacity = online * serverValue
    difference = expected - capacity
    needed = int(difference / serverValue)

    #attempt to stop the database size swinging
    if(turnCount == nextTurn):
        nextTurn = nextTurn + 4
        temp = 1 + int (((pAP + pNA + pEU) + (hAP[4] + hNA[4] + hEU[4]) + (hAP[3] + hNA[3] + hEU[3]) + (hAP[2] + hNA[2] + hEU[2]))/4)
        if(abs(idealDB - temp) > (idealDB / 5)):
            idealDB = int(idealDB * 1.2)
        else:
            idealDB = temp
            
    if(online + len(goingUpData[region]) < (idealDB * 0.8)):
        needed = int(idealDB * 0.9) - online - len(goingUpData(region))
        setNodes('DB', region, needed)
        while(needed > 0):
            goingUpData[region][upID] = 8
            upID = upID+1
            needed = needed-1
        return 1

#    print "DATA REGION: " + region + " SERVER SIZE: " + str(serverValue) + " DIFFERENCE: " + str(difference) + " CAPACITY: " + str(capacity) + " needed: " + str(needed)
#    print ""

    if(abs(difference) > (serverValue * 1.1)):
        if(difference > 0):
            if(needed > 0 and needed - len(goingUpData[region]) > 0):
                print "ADDED: " + str(needed)
                setNodes('DB', region, needed)
                while(needed > 0):
                    goingUpData[region][upID] = 8
                    upID = upID+1
                    needed = needed-1
                return 1
        else:
            if(needed < 0 and online + needed - len(goingDownData[region]) > idealDB):
                print "REMOVED: " + str(needed)
                while(needed < 0):
                    setNodes('DB', region, needed)
                    goingDownData[region][downID] = 2
                    downID = downID+1
                    needed = needed+1
            return 1
    return 0

def dataMove(payout):
    global downID
    if(migration == 2):
        temp = getDBNodeCount(payout, oldregion)
        setNodes('DB', oldregion, temp * -1)
        while( temp > 0):
            goingDownData[oldregion][upID] = 2
            downID = downID+1
            temp = temp-1
        return 1
    else:
        return 0

#Control functions
def nextTurn():
    data = {'Command': 'PLAY', 'Token': token}
    return requests.post(url, data=json.dumps(data), headers=headers)

def init():
    data = {'Command': 'INIT', 'Token': token}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    payout = r.json()

def tickDown():
    popKey = {}
    for i in goingUpWeb:
        for j in goingUpWeb[i]:
            if (goingUpWeb[i][j] <= 0):
                popKey[i] = j
            else:
                goingUpWeb[i][j] = goingUpWeb[i][j] - 1

    for i in popKey:
        goingUpWeb[i].pop(j, None)

    popKey = {}
    for i in goingUpJava:
        for j in goingUpJava[i]:
            if (goingUpJava[i][j] <= 0):
                popKey[i] = j
            else:
                goingUpJava[i][j] = goingUpJava[i][j] - 1

    for i in popKey:
        goingUpJava[i].pop(j, None)

    popKey = {}
    for i in goingUpData:
        for j in goingUpData[i]:
            if (goingUpData[i][j] <= 0):
                popKey[i] = j
            else:
                goingUpData[i][j] = goingUpData[i][j] - 1


    for i in popKey:
        goingUpData[i].pop(j, None)

    popKey = {}
    for i in goingDownJava:
        for j in goingDownJava[i]:
            if (goingDownJava[i][j] <= 0):
                popKey[i] = j
            else:
                goingDownJava[i][j] = goingDownJava[i][j] - 1

    for i in popKey:
        goingDownJava[i].pop(j, None)

    popKey = {}
    for i in goingDownData:
        for j in goingDownData[i]:
            if (goingDownData[i][j] <= 0):
                popKey[i] = j
            else:
                goingDownData[i][j] = goingDownData[i][j] - 1

    for i in popKey:
        goingDownData[i].pop(j, None)

def main():
    global difAP
    global difEU
    global difNA
    global CR
    global turnCount

    avgAP = 0.0
    avgEU = 0.0
    avgNA = 0.0

    init()
    r = nextTurn()

    while(1):
        payout = r.json()
        turnCount = getTurnNo(payout)
        turn = getTurnNo(payout)
        tickDown()

        print ""
        print "CURRENT TURN IS: " + str(turn)
        print "TIME IS: " + getTransactionTime(payout)
        print "Money earned so far: " + str(getProfitAccumulated(payout))
        print "Money earned this turn: " + str(getProfitEarned(payout))
        print ""
        printWebTransactions(payout)
        print ""

        print "# of AP WEB Servers: " + str(getWebNodeCount(payout, 'AP'))
        print "# of EU WEB Servers: " + str(getWebNodeCount(payout, 'EU'))
        print "# of NA WEB Servers: " + str(getWebNodeCount(payout, 'NA'))
        print "# of AP JAVA Servers: " + str(getJavaNodeCount(payout, 'AP'))
        print "# of EU JAVA Servers: " + str(getJavaNodeCount(payout, 'EU'))
        print "# of NA JAVA Servers: " + str(getJavaNodeCount(payout, 'NA'))
        print "# of AP DATA Servers: " + str(getDBNodeCount(payout, 'AP'))
        print "# of EU DATA Servers: " + str(getDBNodeCount(payout, 'EU'))
        print "# of NA DATA Servers: " + str(getDBNodeCount(payout, 'NA'))
        print ""

        #gathers data about my predictions
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
            #print "Highest mistake ASIA: " + str(difAP)
            #print "Highest mistake EUROPE: " + str(difEU)
            #print "Highest mistake AMERICA: " + str(difNA)
            #print ""

#        print "HISTORY OF ASIA: " + str(hAP)
#        print "HISTORY OF EUROPE: " + str(hEU)
#        print "HISTORY OF AMERICA: " + str(hNA)
        calcChange('AP')
        calcChange('EU')
        calcChange('NA')
        print ""
        
        if(turn > 6):
            z = webLogic(payout, 'AP') 
            z = z + webLogic(payout, 'EU')
            z = z + webLogic(payout, 'NA')
            z = z + javaLogic(payout, 'AP')
            z = z + javaLogic(payout, 'EU')
            z = z + javaLogic(payout, 'NA')
            z = z + dataLogic(payout)
            z = z + upgradeLogic(payout)
            if(z > 0):
                data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': CR}
                #print data
                r = requests.post(url, data=json.dumps(data), headers=headers)
                clearCR()
                #print r.text

        #print "ASIA WEB SERVERS: " + str(goingUpWeb['AP'])
        #print "EUROPE WEB SERVERS: " + str(goingUpWeb['EU'])
        #print "AMERICA WEB SERVERS: " + str(goingUpWeb['NA'])
        #print "ASIA JAVA SERVERS: " + str(goingUpJava['AP'])
        #print "EUROPE JAVA SERVERS: " + str(goingUpJava['EU'])
        #print "AMERICA JAVA SERVERS: " + str(goingUpJava['NA'])
        #print "ASIA JAVA SERVERS DOWN: " + str(goingDownJava['AP'])
        #print "EUROPE JAVA SERVERS DOWN: " + str(goingDownJava['EU'])
        #print "AMERICA JAVA SERVERS DOWN: " + str(goingDownJava['NA'])
        #print "ASIA DATA SERVERS: " + str(goingUpData['AP'])
        #print "EUROPE DATA SERVERS: " + str(goingUpData['EU'])
        #print "AMERICA DATA SERVERS: " + str(goingUpData['NA'])
        #print "ASIA DATA SERVERS DOWN: " + str(goingDownData['AP'])
        #print "EUROPE DATA SERVERS DOWN: " + str(goingDownData['EU'])
        #print "AMERICA DATA SERVERS DOWN: " + str(goingDownData['NA'])
        #print ""
        #print 'RESEARCH: ' + json.dumps(getResearchUpgradeState(payout), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"

        r = nextTurn() #ALWAYS KEEP
        
        #if(turn > 123456 ):
        #    raw_input("Press Enter to continue...")

main()
