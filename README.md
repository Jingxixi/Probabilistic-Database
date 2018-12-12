# Probabilistic-Database

## Members 
[Jingxi Yu](mailto:yjx941125@gmail.com)

[Sijie Xiong](mailto:sjxiong3ny@ucla.edu)

[Linzuo Li](mailto:linzuo@ucla.edu)

## Instructions

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

    python3 lifted.py --query files/query.txt \
    --table files/table_file_1.txt \
    --table files/table_file_2.txt \
    --table files/table_file_3.txt 

