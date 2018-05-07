from __future__ import print_function

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from operator import add

#import pyspark

from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
from pyspark.sql.types import IntegerType
from pyspark.sql import Row # for DF creation
from pyspark.sql import SQLContext # for DF
from pyspark.ml.feature import StopWordsRemover ##for stop words removal


stop_words=["mr.","said","said","how","said,","because","do","there",
"make","now","its","two","one","said.","chief","up","if","out","some",
"what","just","year","like","told","since","only","may","into","any","one",
"over","after","three","before","him","them","back","four","did","get","-",
"mr","most","no","other","also","much","so","many","could","last","all",
"new","percent","than","can","her","about","would","said","more","has",
"or","i","are","will","but","it","its","be","been","at","said","his",
"have","by","had","from","not","at","as","the","with","of","a", "an", 
"the", "this", "that","those", "on", "in", "for","he", "she","their", 
"they", "we","been", "i", "you", "who", "which", "where", "when", "why", 
"was", "were","while","under","my","me", "is", "hi" , "hey", "hello","to",
"and","got","former","against","mrs.","mrs","between","ms.","ms","first",
"second","third","fourth","people","even","still","each","off","going","no.","york","new",
"through","during","united","states","made"]



def top_words(sc, path):
    icount=0;
    
    feature_list=[]
    textRDD=sc.textFile(path)
    words = textRDD.flatMap(lambda x: x.split(' ')).map(lambda x: (x, 1))
    wordcount = words.reduceByKey(add).map(lambda (x,y): (y,x)).sortByKey(ascending=False).collect()
    
    
    #mvv_list = DF.select('words').show()
    
    for (count, word) in wordcount:
        
        try:
            mynewstring = word.encode('ascii')
        except:
            #print("there are non-ascii characters in there")
            continue    
        
        if word.lower() in stop_words:
            continue
        else:
            #print("%s: %i" % (word, count))
            if(icount!=20):
                feature_list.append(word.lower())
                icount=icount+1
            else:
                break      

    #CONVERSION TO DF
#    R = Row('count', 'words')
#    sqlContext = SQLContext(sc)
#    DF = sqlContext.createDataFrame([R(i, x) for i, x in (wordcount)])
#    DF.show()
#                    
    
    return feature_list
    
def sparse_matrix(sc, path, feature_list):
    category_list=["Business/","Sports/","Politics/","Health/"]
        
    count_list=[]
    sm_file=open('/home/hadoop/Desktop/sm_file.txt','w+')
    
      
    for category in category_list:
        i=0
        for i in range(50):
            
            count_list=[]
            
            dir_path=path+str(category)+str(i)+".txt"
            
            textRDD=sc.textFile(dir_path)
            words = textRDD.flatMap(lambda x: x.split(' ')).map(lambda x: (x, 1))
            wordcount = words.reduceByKey(add).map(lambda (x,y): (y,x)).sortByKey(ascending=False).collect()        
            count_list.append(category)
            for feature in feature_list:
                flag=0
                
                for (count,word) in wordcount:
                    if word == feature:
                        count_list.append(count)
                        flag=1
                        break
                if flag!=1:
                    count_list.append(0)
            
            k=0
            for count in count_list:
                if(k==0):
                    sm_file.write(str(count))
                    k=1
                else:
                    sm_file.write(","+str(count))
                
            sm_file.write("\n")

    
    
    #for wc in wordcount:
    #    print(wc)

    #for count in count_list:
     #   print(count)
        
    #print(len(feature_list))
    #print(len(count_list))
#   
   

if __name__ == "__main__":
    
    categories_list=["Business","Sports","Politics","Health"]
    feature_list=[]
    
    conf = SparkConf().setAppName("Lab3")
    conf=conf.setMaster("local[*]")
    sc=SparkContext(conf=conf)
    path="../../data/"
    
    for word in categories_list:
        dir_path=path+word+"/*.txt"                
        temp_list= top_words(sc,dir_path)
        for w in temp_list:
            if(w in feature_list):
                pass
            else:
                feature_list.append(w)
    
    
#    for word in feature_list:
#        print("%s: " % (word))
        
     
    sparse_matrix(sc,path, feature_list)
    
        
    
    


	