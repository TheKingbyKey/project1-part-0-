# -*- coding: utf-8 -*-
"""
Created on Sat May  9 20:15:19 2020

@author: Bharti Arora
"""

import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
engine = create_engine("postgres://boaqtdatmuhusp:568946665bde49b4c20c29ab15259a2c9029462c4d92a29fe9aa37c44dcfe580@ec2-50-17-90-177.compute-1.amazonaws.com:5432/dd4t41ubcfugk1")
db = scoped_session(sessionmaker(bind=engine))

def main():
    #f = open("books.csv")
    #reader = csv.reader(f)
    #next(reader)
    #for isbn,title,author,year in reader:
        #db.execute("INSERT INTO books(isbn,title,author,year) VALUES(:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
        #db.commit()

    authors = db.execute("SELECT DISTINCT author FROM books").fetchall()
    for author in authors:
        db.execute("INSERT INTO author_score(name) VALUES(:author)",{"author":author[0]})
        db.commit()

if __name__ == "__main__":
    main()
