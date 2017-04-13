# Description

This routine syncronizes IBM Connections Communities and IBM Sametime Meetings Rooms, i. e., for each community created in IBM Connections,
a meeting room is created in Sametime Meetings.

After creating the Meeting Room, a important bookmark is on Community in Connections. So a link will be show on Overview page of Community.

If user is an Owner is a Community, he will a proprietary on the Meeting Rooms.
 
However, I was not able to automatically enable Audio / Video, as Sametime Meetings, i still working on this. User must setup A/V manually.

# How to deploy


To use this script you must:

1) Install Python 2.7
2) Install library requests
```
 pip install requests
```
3) Download files ***encodedPassword.py*** and ***SyncCommunitiesAndMeetings.py***

4) Encode the password of wsadmin from Connections, through command
```
python encodedPassord.py
```
save this result

5) Encode the password of wsadmin from Sametime, through command
```
python encodedPassord.py
```
save this result

6) Change file SyncCommunitiesAndMeetings.py

replacing IBM Connections url, admin and password.

```
CONNECTIONS_HOST = 'https://connections.COMPANY.com'
CONNECTIONS_USERNAME = 'wsadmin'
CONNECTIONS_ENCODED_PASSWORD = 'REPLACE_HERE'
```
replacing IBM Sametime Meetings url, admin and password.

```
MEETINGS_HOST = 'https://stmeetings.COMPANY.com'
MEETINGS_USERNAME = 'wsadmin'
MEETINGS_ENCODED_PASSWORD = 'REPLACE_HERE'
```
Save and close.

# Running

7) Run using command 

```
python SyncCommunitiesAndMeetings.py
```
