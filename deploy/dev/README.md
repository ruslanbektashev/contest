## Инструкция для развертывания локального dev-сервера

Подарзумевается что git и python3.8+ уже установлены.  
Инструкция проверена на Ubuntu 22.04.
```
git clone https://github.com/ruslanbektashev/contest.git
cd contest
git checkout stable
sudo apt install mysql-server -y
sudo apt install build-essential pkg-config default-libmysqlclient-dev -y
sudo apt install python3-pip python3-venv -y
sudo service mysql start
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
sudo mysql -u root < utils/contest.sql
cp utils/settings.py contest
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py createsuperaccount
python3 manage.py runserver
```
