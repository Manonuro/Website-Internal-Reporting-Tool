#!/usr/bin/env python2.7


"""This module builds an internal reporting tool that will use information
from "News" database to discover what kind of articles the site's readers like.
The database contains newspaper articles, as well as the web server log
for the site. The log has a database row for each time a reader loaded
a web page. Using that information, this code will answer questions about the
site's user activity.
"""


import psycopg2

DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()


"""Finding the most popular three articles of all time"""
c.execute("""
    SELECT title, count(*) AS num
      FROM articles JOIN log
             ON split_part(log.path, '/', 3)=articles.slug
     GROUP BY articles.title
     ORDER BY num DESC LIMIT 3;""")

top3title = c.fetchall()
print("Finding the most popular three articles of all time:\n")
for title in top3title:
    print("\"%s\" -- %s views" % (title[0], title[1]))


"""The most popular article authors of all time"""
c.execute("""
    SELECT authors.name,count(*) AS num
      FROM articles, log, authors
     WHERE split_part(log.path, '/', 3)=articles.slug
       AND articles.author=authors.id
     GROUP BY authors.name
     ORDER BY num DESC;""")

top_author = c.fetchall()
print("\n\nThe most popular article authors of all time:\n")
for author in top_author:
    print('%s -- %s views' % (author[0], author[1]))


"""Extracting days with more than 1% of requests lead to errors"""
stat = ("200 OK", "404 NOT FOUND")
c.execute("""
    CREATE VIEW statviw AS
         SELECT split_part(time::TEXT, ' ', 1) date, status, count(*) AS num
           FROM log
          GROUP BY date, status;
      WITH statOk AS (SELECT DATE, status, num
                        FROM statviw
                       WHERE status=%s),
           statNok AS (SELECT date, status, num
                         FROM statviw
                        WHERE status=%s)
      SELECT statOk.date,statOk.num AS OK_count,
             statNok.num AS NoK_count,
             round((100.*statNok.num/(statNok.num+statOk.num)),2) AS percentg
        FROM statOk,statNok
       WHERE statOk.date=statNok.date
         AND (100.*statNok.num/(statNok.num+statOk.num))>=1;""", stat)

error_days = c.fetchall()
print("\n\nDays with more than 1% of requests lead to errors:\n")
for item in error_days:
    print("%s -- %s%% errors" % (item[0], item[3]))

db.close()
