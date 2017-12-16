# update_noip

| **No longer maintained:** This project is no longer being maintained. |
| ----------------------------------------------------------------------|

Refreshes all your hostnames on [noip.com].

If run regularly, no-ip won't nag you to update your hostnames every 30 days.

This script is intended to be hooked up to cron or some other periodic task scheduler. 
It reports execution errors via [notifymail].

[noip.com]: https://www.noip.com/
[notifymail]: https://github.com/davidfstr/notifymail

## Installation

```
# (Install Python 3.x)

# Download source code
git clone https://github.com/davidfstr/update_noip.git
cd update_noip/

# Install dependencies
pip3 install -r requirements.txt

# Define no-ip settings
cp settings.example.py settings.py
nano settings.py  # or your favorite text editor

# Run
python3 update_noip.py
```
