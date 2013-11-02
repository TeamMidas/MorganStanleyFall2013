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

def sumWebTransactions(payout):
    AP = getWebTransactions(payout, 'AP')
    EU = getWebTransactions(payout, 'EU')
    NA = getWebTransactions(payout, 'NA')
    print "Asia: " + str(AP)
    print "Europe: " + str(EU)
    print "North America: " + str(NA)

def setNodes(tier, region, num):
    return {'Command': 'CHNG', 'Token': token, 'ChangeRequest': {'Servers': {tier: {'ServerRegions': {region: {'NodeCount': num}}}}}}


#Control functions
def nextTurn():
    data = {'Command': 'PLAY', 'Token': token}
    return requests.post(url, data=json.dumps(data), headers=headers)

def init():
    data = {'Command': 'INIT', 'Token': token}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    payout = r.json()

    turn = getTurnNo(payout)
    print "CURRENT TURN IS: " + str(turn)

    print "# of EU Servers: " + json.dumps(getWebNodeCount(payout, 'EU'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
    
#    data = {'Command': 'CHNG', 'Token': token, 'ChangeRequest': {'Servers': {'WEB': {'ServerRegions': {'EU': {'NodeCount': '-1'}}}}}}
    data = setNodes('WEB', 'EU', -1)
    r = requests.post(url, data=json.dumps(data), headers=headers)

def main():
    init()
    r = nextTurn()

    while(1):
        payout = r.json()

        print "# of EU Servers: " + json.dumps(getWebNodeCount(payout, 'EU'), sort_keys=True, indent=4, separators=(',', ': ')) + "\n"
        turn = getTurnNo(payout)

        print ""
        print "CURRENT TURN IS: " + str(turn)
#    print json.dumps(payout, sort_keys=True, indent=4, separators=(',', ': '))

        sumWebTransactions(payout)
        print ""
        r = nextTurn()
        raw_input("Press Enter to continue...")

main()
