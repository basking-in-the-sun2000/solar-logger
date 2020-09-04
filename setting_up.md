Download and prepare your card – https://www.raspberrypi.org/downloads/

Setup your Pi

Usually try to boost security a little – https://www.raspberrypi.org/documentation/configuration/security.md

```
sudo apt update
sudo apt upgrade
sudo apt install -y gnupg2 curl wget

wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt-get install -y influxdb
sudo apt-get install -y grafana

pip3 install pymodbus
pip3 install isolate
pip3 install solcast
pip3 install pytz
pip3 install influxdb

sudo service grafana-server enable
sudo service grafana-server start

sudo service influxdb enable
sudo service influxdb start 
```


if you installed ufw:
```
sudo ufw allow from {Subnet/IPaddress} to any port 8083 proto tcp
sudo ufw allow from {Subnet/IPaddress} to any port 3000

```

cd to where you want the solar folder to reside
`git clone https://github.com/basking-in-the-sun2000/solar-logger.git`

edit `solar.service` to reflect the location and default user
```
sudo cp solar.service /lib/systemd/system/solar.service

sudo mkdir /var/log/solar
sudo chown ***me***:***me*** /var/log/solar  (use your user's name rather than ***me***)
```

You might want to setup the `config.py` file with the parameter for your site


cd to the directory where the code is, and try python3 main.py. If you have problems enable the debug flag in config.py, if you need more data (or i do)

To start the logger as a service,

1. cd to the directory with the code
2. cp solar.service /lib/systemd/system/solar.service
3. change the text within the *** to what you need 
4. sudo systemctl enable solar.service
5. sudo systemctl start solar.service
6. check it 
  a. sudo systemctl status solar.service


If you need to fix your db, i had to use these commands on my computer, since the pi didn't had enough memory (adjust your paths)

```
rm -r /Volumes/root/var/lib/influxdb/data/*/*/*/index

sudo -u influxdb bash -c 'influx_inspect buildtsi -datadir /var/lib/influxdb/data/ -waldir /var/lib/influxdb/wal/'

influxd -config /usr/local/etc/influxdb.conf
```

check the number of files with
`sudo -u influxdb bash -c 'ulimit -a'`
