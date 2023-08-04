#!/bin/bash

BOT_COMMAND="python3 main.py"
LOG_FILE="path_to_directory/bash_logs.log"

pgrep -p "$BOT_COMMAND" > /dev/null

if [ $? -eq 0]; then
	echo "Bot is running" >> "$LOG_FILE"
	sleep 60
else
	echo "Starting the bot..." >> "$LOG_FILE"
	nohup $BOT_COMMAND
	echo "Bot started" >> "$LOG_FILE"
fi
