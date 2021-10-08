curl --location --request PUT 'http://127.0.0.1:8087/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/live/pushpublish/mapentries/613840e5efbdbe201f49133du342-yt' \
--header 'Authorization: Basic dXNlcjAxOnVzZXIwMUBBQkM=' \
--header 'Content-Type: application/json' \
--data '{
   "serverName": "_defaultServer_",
   "sourceStreamName": "613840e5efbdbe201f49133du342",
   "entryName": "613840e5efbdbe201f49133du342-yt",
   "enabled": true,
   "profile": "rtmp",
   "host": "a.rtmp.youtube.com",
   "application": "live2",
   "streamName": "s5re-z4qc-693q-ygdm-4t21",
   "port": 1935
}'