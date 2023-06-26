# black-hole
Collect and log payloads on open ports asynchronously.

## Requirements
- Python3 (tested on 3.11)

## Install
Note: `sudo` is required to open ports <1024
```
python3 -m venv venv
source venv/bin/activate
make install
sudo make run
```
Test that everything works:
```
sudo nmap -v --top-ports 20 -A localhost
```
