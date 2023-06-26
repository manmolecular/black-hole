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
Check that everything works as expected:
```
sudo nmap --top-ports 20 localhost
```
Expected output:
```
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00016s latency).
Other addresses for localhost (not scanned): ::1

PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
23/tcp   open  telnet
25/tcp   open  smtp
53/tcp   open  domain
80/tcp   open  http
110/tcp  open  pop3
111/tcp  open  rpcbind
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
143/tcp  open  imap
443/tcp  open  https
445/tcp  open  microsoft-ds
993/tcp  open  imaps
995/tcp  open  pop3s
1723/tcp open  pptp
3306/tcp open  mysql
3389/tcp open  ms-wbt-server
5900/tcp open  vnc
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.05 seconds
```
Check that data is collected - `data.csv` file with payloads will appear in the root directory:
```
sudo nmap -v --top-ports 20 -A localhost
```
Expected data representation:
```csv
client_id,client_ip,client_port,listen_host,listen_port,data_hex,data_decode,timestamp
127.0.0.1:54250,127.0.0.1,54250,0.0.0.0,80,474554202f20485454502f312e300d0a0d0a,'GET / HTTP/1.0\r\n\r\n',1687770151
```
