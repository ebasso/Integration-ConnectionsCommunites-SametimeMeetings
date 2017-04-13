# -*- coding: utf-8 -*-
#
# Before run:
#
# > pip install requests
#
#
import sys, time, json, re, base64
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

CONNECTIONS_HOST = 'https://connections.<COMPANY>.com'
CONNECTIONS_USERNAME = 'wsadmin'
CONNECTIONS_ENCODED_PASSWORD = '<REPLACE_HERE>'

MEETINGS_HOST = 'https://stmeetings.<COMPANY>.com'
MEETINGS_USERNAME = 'wsadmin'
MEETINGS_ENCODED_PASSWORD = '<REPLACE_HERE>'

# Disable Warnings from Untrusted TLs keys
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ConnectionsCommunities:

    def __init__(self,hostname=None,loginname=None,password=None):
        self.hostname = hostname
        self.loginname = loginname
        self.password = password
        self.auth = HTTPBasicAuth(loginname, password)

    def doGet(self,url,headers,auth):
        r = requests.get(url=url,headers=headers,auth=auth, verify=False)
        if (r.status_code != 200):
            print 'requests.get -> %s = %s\n' % (r.url, r)
            return None;
        return r.content

    def parseOpensearch(self,content):

        opensearch = {
            'totalResults': 0,
            'startIndex': 0,
            'itemsPerPage': 0,
            'pages': 0
        }

        root = ET.fromstring(content)

        temp = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
        if (temp is None):
            return opensearch
        totalResults = int(temp.text)

        temp = root.find("{http://a9.com/-/spec/opensearch/1.1/}startIndex")
        if (temp is None):
            return opensearch
        startIndex = int(temp.text)

        temp = root.find("{http://a9.com/-/spec/opensearch/1.1/}itemsPerPage")
        if (temp is None):
            return opensearch
        itemsPerPage = int(temp.text)

        pages = totalResults / itemsPerPage
        if ((totalResults % itemsPerPage) != 0):
            pages = pages + 1

        opensearch = {
            'totalResults': totalResults,
            'startIndex': startIndex,
            'itemsPerPage': itemsPerPage,
            'pages': pages
        }
        return opensearch

    def parseCommunities(self,content,communities):

        root = ET.fromstring(content)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        for entry in entries:
            communityUuid = entry.find('{http://www.ibm.com/xmlns/prod/sn}communityUuid').text
            title = entry.find('{http://www.w3.org/2005/Atom}title').text

            community = {
            'uuid': communityUuid,
            'title': title.encode("utf-8")
            }
            communities.append(community)

    def listAll(self):
        communities = []

        url = self.hostname + '/communities/service/atom/communities/all?page=1'
        headers = { 'Content-Type': 'atom/xml'}

        feedCommunities = self.doGet(url=url,headers=headers,auth=self.auth)
        if (feedCommunities is None):
            return None

        opensearch = self.parseOpensearch(feedCommunities)
        if (opensearch['pages'] == 0):
            return None
        print url
        self.parseCommunities(feedCommunities,communities)

        max = opensearch['pages']+1
        for page in range(2,max):
            url = self.hostname + '/communities/service/atom/communities/all?page=' + str(page);
            if (page % 10 == 0):
                print url
            feedCommunities = self.doGet(url=url,headers=headers,auth=self.auth)
            if (feedCommunities is None):
                return None
            self.parseCommunities(feedCommunities,communities)
        print url
        return communities

    def getCommunityOwners(self,communityUuid):
        url = self.hostname + '/communities/service/atom/community/members?communityUuid=' + communityUuid
        headers = { 'Content-Type': 'atom/xml'}

        feedMembers = self.doGet(url=url,headers=headers,auth=self.auth)
        if (feedMembers is None):
            return None

        members = self.parseMembers(feedMembers)
        if (members is None):
            return None

        owners = []
        for m in members:
            if m['role'] == 'owner':
                owners.append(m['email'])
        return owners

    def parseMembers(self,feed):
        members = []
        root = ET.fromstring(feed)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        for entry in entries:
            contributor = entry.find('{http://www.w3.org/2005/Atom}contributor')
            t_email= contributor.find('{http://www.w3.org/2005/Atom}email')

            if (t_email is not None):
                email = t_email.text
                #print email

                role = entry.find('{http://www.ibm.com/xmlns/prod/sn}role').text
                #print role
                member = {
                'email': email,
                'role': role
                }
                members.append(member)
        return members

class CommunityBookmarks:

    def __init__(self,hostname=None,loginname=None,password=None):
        self.hostname = hostname
        self.loginname = loginname
        self.password = password
        self.auth=HTTPBasicAuth(loginname, password)

    def create(self,xml_data,communityUuid=None):

        if (communityUuid is None) :
            return None

        headers = { 'Content-Type': 'application/atom+xml;charset=UTF-8'}
        url = self.hostname + '/communities/service/atom/community/bookmarks?communityUuid=' + communityUuid


        res = requests.post(url=url,headers=headers,auth=self.auth,verify=False,data=xml_data)
        if (res.status_code != 201):
            print 'CommunityBookmarks.create -> %s = %s\n' % (res.url, res)
            #print res.content

        return res

    def read(self,referenceId=None,communityUuid=None):

        if (communityUuid is None) :
            return None

        headers = { 'Content-Type': 'application/atom+xml;charset=UTF-8'}
        url = self.hostname + '/communities/service/atom/community/bookmarks?communityUuid=' + communityUuid + '&referenceId=' + referenceId

        res = requests.get(url=url,headers=headers,auth=self.auth,verify=False)
        if (res.status_code != 200):
            print 'CommunityBookmarks.read -> %s = %s\n' % (res.url, res)
            print res.content
            return None;

        return res.content

    def update(self,xml_data,referenceId=None,communityUuid=None):

        if (communityUuid is None) :
            return None

        headers = { 'Content-Type': 'application/atom+xml;charset=UTF-8'}
        url = self.hostname + '/communities/service/atom/community/bookmarks?communityUuid=' + communityUuid + '&referenceId=' + referenceId

        res = requests.put(url=url,headers=headers,auth=self.auth,verify=False,data=xml_data)
        if (res.status_code != 201):
            print 'CommunityBookmarks.update -> %s = %s\n' % (res.url, res)
            print res.content
            return None;

        return res.content

    def delete(self,referenceId=None,communityUuid=None):

        if (communityUuid is None) :
            return None

        headers = { 'Content-Type': 'application/atom+xml;charset=UTF-8'}
        url = self.hostname + '/communities/service/atom/community/bookmarks?communityUuid=' + communityUuid + '&referenceId=' + referenceId

        res = requests.delete(url=url,headers=headers,auth=self.auth,verify=False)
        if (res.status_code != 200):
            print 'CommunityBookmarks.delete -> %s = %s\n' % (res.url, res)
            print res.content
            return None;

        return res.content

    def list(self,communityUuid=None):

        if (communityUuid is None) :
            return None

        headers = { 'Content-Type': 'application/atom+xml;charset=UTF-8'}
        url = self.hostname + '/communities/service/atom/community/bookmarks?communityUuid=' + communityUuid

        res = requests.get(url=url,headers=headers,auth=self.auth,verify=False)
        if (res.status_code != 200):
            print 'CommunityBookmarks.list -> %s = %s\n' % (res.url, res)
            print res.content
            return None;

        feed =  self.parseCommunityBookmarks(res.content)
        return feed

    def parseCommunityBookmarks(self,content):
        bookmarks = []

        root = ET.fromstring(content)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        for entry in entries:
            referenceId = entry.find('{http://www.w3.org/2005/Atom}id').text
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            child = entry.find('{http://www.w3.org/2005/Atom}link')
            important = 'N'
            try:
                href = child.attrib['href']
            except:
                href = ''
                print entry
                pass

            bookmark = {
            'uuid': referenceId,
            'title': title.encode("utf-8"),
            'href': href,
            'important': important
            }
            bookmarks.append(bookmark)

        return bookmarks


class SametimeMeetings:

    def __init__(self,hostname=None,loginname=None,password=None):
        self.hostname = hostname
        self.loginname = loginname
        self.password = password
        self.username = None
        self.csrfToken = None
        self.session = None

    def doAuth(self):

        # If already has token return session
        if (self.csrfToken is not None):
            return self.session

        url = self.hostname + '/stmeetings/j_security_check'

        session = requests.session()
        payload = {'j_username': self.loginname, 'j_password': self.password}
        res = session.post(url, data=payload, verify=False)

        if (res.status_code != 200):
            print 'doAuth: requests.get -> %s = %s\n' % (res.url, res)
            return None

        if (res.headers['Content-Type'] != 'text/html;charset=UTF-8'):
            print 'doAuth: Not expected -> "Content-Type": "' + res.headers['Content-Type'] + '"'
            return None

        if (u"var userName = \"" not in res.text):
            print 'doAuth: Login Error no userName'
            return None

        html = str(res.text.encode('utf-8'))
        #var userName = "wsadmin@COMPANY.com";
        start = html.find('var userName = \"') + 16
        end = html.find('";', start)
        self.username = html[start:end]

        #var csrfToken = "53cb34906d36e6d5d0682c526b8a5bd0";
        start = html.find('var csrfToken = \"') + 17
        end = html.find('";', start)
        self.csrfToken = html[start:end]
        self.session = session
        return session


    def createRoom(self,data):

        if (self.doAuth() is None):
            return None

        params = { 'dojo.preventCache': str(time.time())  }
        url = self.hostname + '/stmeetings/restapi'
        headers = { 'Accept': 'text/json', 'X-ST-CSRF-Token': self.csrfToken }
        #print '--------------------------------------'
        #print data
        #print '--------------------------------------'
        res = self.session.post(url=url,headers=headers,data=data)

        if (res.status_code != 200):
            print 'createRoom -> %s = %s\n' % (res.url, res)
            print res.content
            return None;
        #print '-------------------------------------- res.content'
        #print res.content
        if (res.headers['Content-Type'] != 'text/json'):
            print 'createRoom: No Json returned'
            return None

        return res.json()

    def getRoom(self,uuid=None):

        if (uuid is None):
            return None

        if (self.doAuth() is None):
            return None

        #data = { 'id': uuid }
        params = { 'dojo.preventCache': str(time.time())  }
        url = self.hostname + '/stmeetings/restapi?id=' + uuid
        headers = { 'Accept': 'text/json', 'X-ST-CSRF-Token': self.csrfToken }
        res = self.session.get(url=url,headers=headers)#,data=data)

        #print res.content
        if (res.status_code != 200):
            print 'getRoom -> %s = %s\n' % (res.url, res)
            print res.content
            return None;
        #print '-------------------------------------- res.content'
        print res.content
        if (res.headers['Content-Type'] != 'text/json'):
            print 'getRoom: No Json returned'
            return None

        return res.json()

    def updateRoom(self,data):

        if (self.doAuth() is None):
            return None

        params = { 'dojo.preventCache': str(time.time())  }
        url = self.hostname + '/stmeetings/restapi'#?'+ urllib.urlencode(params);
        headers = { 'Accept': 'text/json', 'X-ST-CSRF-Token': self.csrfToken }
        res = self.session.post(url=url,headers=headers,data=data)

        if (res.status_code != 200):
            print 'updateRoom -> %s = %s\n' % (res.url, res)
            print res.content
            return None;
        #print '-------------------------------------- res.content'
        print res.content
        if (res.headers['Content-Type'] != 'text/json'):
            print 'updateRoom: No Json returned'
            return None

        return res.json()

    def listRoomsByOrigin(self,originType=None,originId=None):

        if ((originId is None) or (originType is None)):
            return None

        if (self.doAuth() is None):
            return None

        url = self.hostname + '/stmeetings/restapi?originType=' + originType + '&originId=' + originId + '&dojo.preventCache=' + str(time.time())
        headers = { 'Content-Type': 'text/json'}
        res = self.session.get(url,headers=headers)
        if (res.status_code != 200):
            print 'listRoomsByOrigin -> %s = %s\n' % (res.url, res)
            return None
        if (res.headers['Content-Type'] != 'text/json'):
            print 'listRoomsByOrigin: No Json returned'
            return None

        return res.json()

def WriteToFile(communities):
    f = open('communities.txt', 'w')
    f.write('List Communities and Owners and Rooms\n')
    i = 1
    for c in communities:
        f.write( '%s) %s\n' % (i,c['title']) )
        i = i + 1
        f.write( ' |--> uuid: %s\n' % c['uuid'] )
        try:
            f.write( ' |--> joinPath: %s\n' % c['joinPath'].encode("utf-8") )
        except:
            pass
        for o in c['owners']:
            f.write( ' |----> owner: %s\n' % o)
        for l in c['links']:
            f.write( ' |----> link: %s\n' % l['href'])
        f.write( '\n')
    f.close()

def CreateMeetingRoom(stmeetings, community):
    draftRoom = {
    'name': community['title'], # Required
    'description': 'communityUuid=' + community['uuid'],
    'originType': 'Connections',
    'originId': community['uuid'],
    'owner': 'wsadmin@ibm.com',
    'addManager': community['owners'],
    "allowsVideo": 'True'
    }
    return stmeetings.createRoom(draftRoom)

def SyncManagers(stmeetings,community,room):
    communityOwners = community['owners']
    roomOwners = room['managersList']
    addManager = list(set(communityOwners) - set(roomOwners))
    removeManager = list(set(roomOwners) - set(communityOwners) - set(['wsadmin@ibm.com'] ))

    if ((len(addManager) == 0) and (len(removeManager) == 0)):
        print ' |--> SyncManagers: syncronized'
        return None

    print ' |--> SyncManagers: addManager => %s' % addManager
    print ' |--> SyncManagers: removeManager => %s' % removeManager

    draftRoom = {
    'id': room['id'],
    'addManager': addManager,
    'removeManager': removeManager
    }
    #print 'Update Room \n'
    room = stmeetings.updateRoom(draftRoom)


def CreateMeetingBookmark(commbook, community, room):
    meetingUrl = MEETINGS_HOST + '/stmeetings/' + community['joinPath'].encode("utf-8")

    xml_data = '<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app" xmlns:snx="http://www.ibm.com/xmlns/prod/sn">'
    xml_data += '<category term="bookmark" scheme="http://www.ibm.com/xmlns/prod/sn/type"></category>'
    xml_data += '<category term="important" scheme="http://www.ibm.com/xmlns/prod/sn/flags"></category>'
    xml_data += '<content type="html">Meeting Room on Sametime Meetings. You can do presentation, share screen and audio/video.</content>'
    xml_data += '<title type="text">ST Meeting Room</title>'
    xml_data += '<link href="' + meetingUrl +  '">'
    xml_data += '</link>'
    xml_data += '</entry>'

    res = commbook.create(xml_data,community['uuid'])
    #print 'res.status_code --> %s' % res.status_code
    if (res.status_code == 201):
        print ' |--> CreateMeetingBookmark: success'
    elif (res.status_code == 409):
        print ' |--> CreateMeetingBookmark: exist'
    else:
        print ' |--> CreateMeetingBookmark: Unknow error %s\n' % res.status_code


def SyncBookmarks(commbook, community, room):

    joinPath = room['joinPath'].encode("utf-8")
    meetingUrl = MEETINGS_HOST + '/stmeetings/'
    count = 0
    if (community['links'] is not None):
        for link in community['links']:
            if (meetingUrl in link['href']):
                if (link['href'] == (meetingUrl + joinPath)):
    				count = count + 1
                else:
                    print ' |--> SyncBookmarks: delete'
                    #print '---------------------------'
                    #print "joinPath --> " + joinPath
                    #print "link['href'] --> " + link['href']
                    #print "link['uuid'] --> " + link['uuid']
                    start = link['uuid'].find('referenceId=') + 12
                    referenceId = link['uuid'][start:]
                    commbook.delete(referenceId=referenceId,communityUuid=community['uuid'])

    if (count == 0):
        CreateMeetingBookmark(commbook,community,room)
        print ' |--> SyncBookmarks: created'
    else:
        print ' |--> SyncBookmarks: syncronized'

#################### Main Module ###################

cc =  ConnectionsCommunities(CONNECTIONS_HOST,CONNECTIONS_USERNAME,base64.b64decode(CONNECTIONS_ENCODED_PASSWORD))
commbook =  CommunityBookmarks(CONNECTIONS_HOST,CONNECTIONS_USERNAME,base64.b64decode(CONNECTIONS_ENCODED_PASSWORD))
stmeetings = SametimeMeetings(MEETINGS_HOST,MEETINGS_USERNAME,base64.b64decode(MEETINGS_ENCODED_PASSWORD))

print 'Load All Communities...\n'
#communities = []
#community = {
#'uuid': '486e93ab-7349-4d9e-930b-20ec78fc91ce',
#'title': 'Web Colaboração - Comunidade de Testes'
#}
#communities.append(community)
communities = cc.listAll()
if (communities is None):
    print 'Cannot get Connections Communities.'
    sys.exit(1)

print 'For Each Community, Load Members...\n'
for community in communities:
    owners = cc.getCommunityOwners(community['uuid'])
    if (owners is not None):
        community['owners'] = owners

print 'For Each Community, Load Bookmarks...\n'
for community in communities:
    links = commbook.list(community['uuid'])
    if (links is not None):
        community['links'] = links

sys.exit(1)
for community in communities:
    print 'communityUuid => %s' % community['uuid']
    rooms = stmeetings.listRoomsByOrigin('Connections',community['uuid'])
    if ((rooms is None) or (rooms['count'] == 0)):    # Create new Room
        print ' |--> MeetingRoom: new'
        newroom = CreateMeetingRoom(stmeetings,community)
        if (newroom is not None):
            community['joinPath'] = newroom['joinPath']
            CreateMeetingBookmark(commbook,community,newroom)
    elif  (rooms['count'] == 1):
        print ' |--> MeetingRoom: exist'
        community['joinPath'] = rooms['results'][0]['joinPath']
        SyncManagers(stmeetings,community,rooms['results'][0])
        SyncBookmarks(commbook,community,rooms['results'][0])

WriteToFile(communities)
