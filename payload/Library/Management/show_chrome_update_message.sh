#!/bin/bash

/usr/local/bin/yo_scheduler --title "Google Chrome Update" --info "Google Chrome needs to be restarted so it can be updated. Tabs will be restored." -B "osascript -e 'tell application \"Google Chrome\" to open location \"chrome://restart\"'" --action-btn "Restart"
