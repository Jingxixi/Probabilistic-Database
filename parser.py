import pandas as pd
import numpy as np

class pdbTable:
    def __init__( self , file_addr):
        self.df = pd.read_csv(file_addr,sep=",",skiprows=[0],header=None)
        f = open(file_addr,'r')
        self.table_name = f.read(1)
        self.vals = self.df.values
        w,h = self.vals.shape
        self.variable_length = h-1
        
    def getProb(self,var_list):
        if (self.variable_length != len(var_list)):
            print("dimension error")
            return 0
        index_array= np.empty((0))
        for i in range(len(var_list)):
            a = np.argwhere(self.vals[:,i]==var_list[i]).flatten()
            if len(index_array)==0:
                index_array = a
            else:
                index_array = np.intersect1d(a,index_array).flatten()
        if (len(index_array) == 0):
            return 0
        else:
            return self.vals[index_array[0]][-1]

def parse_query_to_string(query_addr):
    df_val = pd.read_csv(query_addr,header=None,sep='\n').values
    q=[]
    for i in range(len(df_val)):
        s = str(df_val[i])
        s = s.replace('|','')
        s = s.replace('[','')
        s = s.replace(']','')
        s = s.replace('\'','')
        s = s.replace(' ','')
        q.append(s)
    return q

def parse_cq(q_str):
    i = 0
    #Format: List
    #[ [Table name1,[List of variables],bool], 
    #  [Table name2,[List of variables],bool] ]
    #
    L = []
    table_list=[]
    variables=[]
    var=''	
    negation = False
    while(i<len(q_str)):
        if (q_str[i] == '~'):
            negation = True
        elif (q_str[i].isupper()):
            if (i!= 0 and i!=1):
                table_list.append(variables)
                table_list.append(negation)
                L.append(table_list)
                variables=[]
                table_list=[]
                negation = False
            table_list.append(q_str[i])
        else:
            if((q_str[i] == ',' or q_str[i] == ')') and var):
                variables.append(var)
                var=''
                if(i == len(q_str)-1):
                    table_list.append(variables)
                    table_list.append(negation)
                    L.append(table_list)
            elif (q_str[i] not in "(),"):
                var+=q_str[i]
        i = i+1
    return L

def parse_query(query_addr):
    query_strings = parse_query_to_string(query_addr)
    query = []
    for q in query_strings:
        query.append(parse_cq(q))
    return query
