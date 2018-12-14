mkdir $HOME/py36
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
tar xJf Python-3.6.3.tar.xz
rm Python-3.6.3.tar.xz
cd Python-3.6.3
./configure prefix=$HOME/py36
make
make install
cd ..
$HOME/py36/bin/pip3 install pandas --user
$HOME/py36/bin/python3 lifted.py --query files/query.txt \
--table files/table_file_1.txt \
--table files/table_file_2.txt \
--table files/table_file_3.txt 