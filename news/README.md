# Internal Reporting Tool

The Internal Reporting tool will use the information from a user-facing newspaper site frontend itself, and the database behind it to discover what kind of articles the site's readers like. This reporting tool is a Python program using the `psycopg2` module to connect to the database.

## The Database
- Newspaper articles
- The web server log for the site

The log has a database row for each time a reader loaded a web page with fields representing information that a web server would record, such as HTTP status codes and URL paths.



## Installation

To start on this project, you'll need database software (provided by a Linux virtual machine) and the data to analyze.

### The virtual machine
This project makes use of Linux-based virtual machine (VM).

You will need to install two pieces of software:
- VirtualBox, which you can get from [this download page](https://www.virtualbox.org/wiki/Downloads).
- Vagrant, which you can get from [this download page](https://www.vagrantup.com/downloads.html).

You will also need a Unix-style terminal program. On Mac or Linux systems, you can use the built-in Terminal. On Windows, we recommend Git Bash, which is installed with the Git version control software.

Once you have VirtualBox and Vagrant installed, open a terminal and run the following commands:
```
mkdir news
cd news
vagrant init ubuntu/trusty64

vagrant up
```

This will give you the PostgreSQL database and support software needed for this project.
If you need to bring the virtual machine back online (with `vagrant up`), do so now. Then log into it with `vagrant ssh`.


## Download the data

[Download the data here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip). You will need to unzip this file after downloading it. The file inside is called `newsdata.sql`. Put this file into the `vagrant/news` directory, which is shared with your virtual machine.

To build the reporting tool, you'll need to load the site's data into your local database.
To load the data, `cd` into the `vagrant/news` directory and use the command `psql -d news -f newsdata.sql`.

Here's what this command does:
- `psql` — the PostgreSQL command line program
-	`-d news` — connect to the database named news which has been set up for you
-	`-f newsdata.sql` — run the SQL statements in the file newsdata.sql

Running this command will connect to your installed database server and execute the SQL commands in the downloaded file, creating tables and populating them with data.

## Explore the data

The database includes three tables:
-	The `authors` table includes information about the authors of articles.
-	The `articles` table includes the articles themselves.
-	The `log` table includes one entry for each time a user has accessed the site.


# The newsdb.py code

The newsdb.py code is a reporting tool to build informative summaries from logs by using a PostgreSQL database.
It prints out reports (in plain text) based on the data in the database. This reporting tool is a Python program using the psycopg2 module to connect to the database.

`db = psycopg2.connect("dbname=news")`

## The assignments
Here are the questions and how the reporting tool answers them.
1. **What are the most popular three articles of all time?** Which articles have been accessed the most? Present this information as a sorted list with the most popular article at the top.
```
c.execute("""
    SELECT title, count(*) AS num
      FROM articles JOIN log
             ON split_part(log.path, '/', 3)=articles.slug
     GROUP BY articles.title
     ORDER BY num desc limit 3;""")
```
During data exploration we found that the _path_ in `log` table and _slug_ in the `articles` table can be used for `JOIN` by removing its first part by `split_part` command.\
First we used `count()` to aggregat on the _title_, then joined the `log` and `articles` tables `ON` _log.path_ and _articles.slug_. `GROUP BY articles.title` and then `ORDER BY num desc` when the result is limited to 3 will give us **the most popular three articles of all time**. \
Finally following command will print out the result in plaint text:\
```
top3title = c.fetchall()
print("Finding the most popular three articles of all time:\n")
for title in top3title:
    print("\"%s\" -- %s views" % (title[0], title[1]))
```


2. **Who are the most popular article authors of all time?** That is, when you sum up all of the articles each author has written, which authors get the most page views? Present this as a sorted list with the most popular author at the top.\
First we used `count()` to aggregat on the _authors.name_, then used `split_part(log.path, '/', 3)=articles.slug` for the `WHERE` clause restriction. `GROUP BY authors.name` and then `ORDER BY num DESC` when the result is limited to 3 will give us **the most popular article authors of all time**. \
```
c.execute("""
    SELECT authors.name,count(*) AS num
      FROM articles, log, authors
     WHERE split_part(log.path, '/', 3)=articles.slug
       AND articles.author=authors.id
     GROUP BY authors.name
     ORDER BY num DESC;""")
```
Finally following command will print out the result in plaint text:\
```
top_author = c.fetchall()
print("\n\nThe most popular article authors of all time:\n")
for author in top_author:
    print('%s -- %s views' % (author[0], author[1]))
```

3. **On which days did more than 1% of requests lead to errors?** The log table includes a column status that indicates the HTTP status code that the news site sent to the user's browser. \
For this task I created a `statviw` VIEW with a extracted date from time column and status column in log table. The aggregated table on date and status completes our `statviw` VIEW table. Then I created two local variables `statOk` and `statNok` for HTTP messages `200 OK`, `404 NOT FOUND` respectively. Finally calculating the percentage of `404 NOT FOUND` messages by using `statOk.num` and `statNok.num` values per day and select the ones over 1%, gives us the final answer.
```
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
```
Finally following command will print out the result in plaint text:\
```
error_days = c.fetchall()
print("\n\nDays with more than 1% of requests lead to errors:\n")
for item in error_days:
    print("%s -- %s%% errors" % (item[0], item[3]))
```


## Authors

* **Manouchehr Bagheri** - *Initial work* - [Manonuro](https://github.com/Manonuro)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
