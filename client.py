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

url = "http://hermes.wha.la/api/hermes"
data = {'Command': 'INIT', 'Token': 'f6ead613-de05-4a51-bda4-76ae2448c1b8', 'ChangeRequest': 'null'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print r.text
