Download and prepare your card – https://www.raspberrypi.org/downloads/

Setup your Pi

Usually try to boost security a little – https://www.raspberrypi.org/documentation/configuration/security.md

sudo apt update
sudo apt install -y gnupg2 curl wget

wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt install -y influxdb
sudo apt-get install -y grafana

pip3 install pymodbus
pip3 install isolate
pip3 install solcast
pip3 install pytz
pip3 install influx db
 
sudo service grafana-server start
sudo service grafana-server status

sudo service influxdb start


sudo ufw allow from {Subnet/IPaddress} to any port 8083 proto tcp
sudo ufw allow from {Subnet/IPaddress} to any port 3000


If you need to fix your db, i had to use these commands on my computer, since the pi didn't had enough memory (adjust your paths)

rm -r /Volumes/root/var/lib/influxdb/data/*/*/*/index

sudo -u influxdb bash -c 'influx_inspect buildtsi -datadir /Volumes/root/var/lib/influxdb/data -waldir /Volumes/root/var/lib/influxdb/wal'

influxd -config /usr/local/etc/influxdb.conf

check the number of files with
su influxdb --shell /bin/bash --command "ulimit -a"

