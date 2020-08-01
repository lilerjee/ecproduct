Configration of ECProduct
=========================

#. Set up Database

   #. Install mariaDB server::
     
        # apt install mariadb-server

   #. Create a user and database::

        # mysql -u root
        MariaDB [(none)]> CREATE DATABASE ecproduct CHARACTER SET utf8;
        MariaDB [(none)]> CREATE USER 'ecproduct'@'localhost' IDENTIFIED BY 'ecproduct@pwd';
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON ecproduct.* TO 'ecproduct'@'localhost';

   #. Import database data::

        $ mysql -u ecproduct -pecproduct@pwd ecproduct < database/platform.sql
        mysql -u ecproduct -pecproduct@pwd ecproduct < database/ecproduct.sql

   #. Modify settings.py::

        MYSQL_HOST = 'localhost'
        MYSQL_USERNAME = 'ecproduct'
        MYSQL_PASSWORD = 'ecproduct@pwd'
        MYSQL_DATABASE = 'ecproduct'
        # MYSQL_DATABASE = 'aims'
        MYSQL_CHARSET = 'utf8'

#. Create the spider for electronic commerce web site:

   * The directory of the spider: <project_home_dir>/ecproduct/spiders/
   * The file name of the spider: <electronic commerce web site's domain name>.py

#. Create input data for spider:

   * For test environment, the input data file: <project_home_dir>/input/<site's domain name>_url_test.txt
   * For product environment, the input data file: <project_home_dir>/input/<site's domain name>_url.txt

   In the file, write one url per line, and can comment it with hash '#'. 
   Input the corresponding page's url for the specific spider.

#. Run the spider:

   * For test environment::

     $ python main.py vvic product product -f test

   * For product environment::

     $ python main.py vvic product product -f product

   * For specific spider::

     $ scrapy crawl jd -a url=https://www.jd.com/allSort.aspx -a entrance_page=category -a data_type=category -o output/jd.jl


