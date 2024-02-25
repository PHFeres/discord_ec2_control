#!/bin/bash

# to execute it in crontab (ec2)
# remember to chmod +x run_control.sh
# @reboot /bin/bash -c "/home/ubuntu/discord_ec2_control/run_control.sh >> /home/ubuntu/discord_ec2_control/cron_log.txt 2>&1"

# Define the directory path variable
CRYPTO_REPORT_DIR="/home/ubuntu/discord_ec2_control"

# just to test
echo "hello world"
sleep 1

# Move to the crypto report directory
cd "$CRYPTO_REPORT_DIR"

# Activate the virtual environment
source "$CRYPTO_REPORT_DIR/.venv/bin/activate"

# Install dependencies
poetry install

# Run the Python script
python bot.py

echo "bot.py finished"

# Deactivate the virtual environment
deactivate

# to don't turn off too quick
sleep 500

# if something happens and the script stops, attempt to reboot so it starts again
sudo reboot now
