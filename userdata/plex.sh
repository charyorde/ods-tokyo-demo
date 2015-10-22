#!/bin/bash

# First download and install the plexmedia server...
HTTPS_PROXY=http://squid.internal:3192 wget -O /tmp/plexmediaserver.deb https://downloads.plex.tv/plex-media-server/0.9.12.13.1464-4ccd2ca/plexmediaserver_0.9.12.13.1464-4ccd2ca_amd64.deb
sudo dpkg -i /tmp/plexmediaserver.deb

# Next, allow remote access without a plex account
# Need to wait for the plex server to initialize (check with the wget)
PREFERENCES="/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Preferences.xml"
while [ ! -f "$PREFERENCES" ]; do
    wget -O /dev/null http://localhost:32400/web
    sleep 1
done

# Some fuzz time to let plex do its thing
sleep 20

# Accept the EULA and allow any network remotely without having a plex account.
sudo service plexmediaserver stop
sed -i -e 's,/>, allowedNetworks="0.0.0.0/0.0.0.0" AcceptedEULA="1"/>,g' "$PREFERENCES"
sudo service plexmediaserver start

# Download some movies. The rest is client side configuration unfortunately.
mkdir -p /media/Movies
HTTPS_PROXY=http://squid.internal:3192 wget -O "/media/Movies/Elephants Dream (2006).mp4" https://archive.org/download/ElephantsDream/ed_1024_512kb.mp4

