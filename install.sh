#!/bin/bash

# Script to install launchd script to automatically log in to Telstra Air.
#
# Arguments
# - username
# - password
#

help() {
  echo
  echo "Usage: $0 username password"
  echo
  exit 1
}

if [ $# -eq 0 ]; then
  echo
  echo "You need to provide Telstra Air username and password"
  help
fi

username="$1"
password="$2"
label_name="telstraair.autologin"

cat << EOF > "$HOME/Library/LaunchAgents/${label_name}.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" \
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label_name}</string>

  <key>LowPriorityIO</key>
  <true/>

  <key>ProgramArguments</key>
  <array>
    <string>$PWD/autologin.py</string>
    <string>$username</string>
    <string>$password</string>
  </array>

  <key>WatchPaths</key>
  <array>
    <string>/etc/resolv.conf</string>
    <string>/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist</string>
    <string>/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

</dict>
</plist>
EOF

chmod +x autologin.py
launchctl load "$HOME/Library/LaunchAgents/${label_name}.plist"
