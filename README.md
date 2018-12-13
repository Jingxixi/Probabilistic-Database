# Probabilistic-Database

## Members 
[Jingxi Yu](mailto:yjx941125@gmail.com)

[Sijie Xiong](mailto:sjxiong3ny@ucla.edu)

[Linzuo Li](mailto:linzuo@ucla.edu)

## Instructions

Our project is only compatible with python3.6+. It will not work with the default python version (3.4.3) on linux machines and many queries will not be liftable on python 3.4. So the next section will install a python 3.6 first and then use that version of python

### Prerequisites

Python 3.6+
Pandas (installed using pip)
Numpy (installed using pip)

To start, run
    
    ./install.sh

This will download python3.6.3 and build into your ~/project directory and then install pandas and numpy using pip3

### Commandline Arguments

Our main class is inside [lifted.py](https://github.com/Jingxixi/Probabilistic-Database/blob/master/lifted.py)

We have four arguments in our program in order to run lifted.py

Two of them are required:

    --query path_to_query_files
    --table path_to_table files

Note that *--table* can be repeated mutiple times to add addtional input files

    --table table1.txt --table table2.txt

Another two are optional arugments

    -d

    -p

-d will run the program using a sqlite3 datbase

-p will run the program in parallel 

### Example 

In this repository, you can run the program with:

    ~/project/bin/python3 lifted.py --query files/query.txt \
    --table files/table_file_1.txt \
    --table files/table_file_2.txt \
    --table files/table_file_3.txt 

