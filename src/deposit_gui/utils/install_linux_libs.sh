#!/bin/bash

if [ $# -lt 2 ]; then
	echo "Usage: $0 <title> <libraries>"
	exit 1
fi

title="$1"
libraries="$2"

# Function to display the notification repeatedly
# This is a hack to keep the notification displayed while the updating takes place
display_notification() {
	while true; do
		notify-send "$title is installing required libraries..." -t 5000
		sleep 5
	done
}

display_notification &
notification_pid=$!

libraries=$(echo "$libraries" | tr ',' ' ')

pkexec sh -c "apt update && apt install -y $libraries"

kill $notification_pid
