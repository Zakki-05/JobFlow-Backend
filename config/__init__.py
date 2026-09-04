# Config package initialization
import sys

# Try to initialize pymysql for MySQL compatibility if installed
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
