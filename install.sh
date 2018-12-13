mkdir ~/project
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
tar xJf Python-3.6.3.tar.xz
cd Python-3.6.3
./configure prefix=~/project/
make
make install
~/project/bin/pip3 install pandas --user
~/project/bin/python3 lifted.py --query files/query.txt \
--table files/table_file_1.txt \
--table files/table_file_2.txt \
--table files/table_file_3.txt 