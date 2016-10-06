import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import yaml
import glob
import os
import sys


class csv_upload(object):
	"""
	Class used to interact with the Amazon Web Services PostgreSQL database; takes 1 argument: data_path
	Available functions:
		append_upload(): Uploads all CSV files in the target folder to the DB, appending them all to a single table named after the target folder
		multi_upload(]): Uploads all CSV files in the target folder to the DB, creating a new table for each with the CSV name
    Attributes:
    	config_path = Path to the location of this script when executed
		host = AWS endpoint target
		port = Post used by the target DB
		dbname = Database name
		user = Database username
		password = Database password
		data = Path to the folder containing the target CSVs for upload
		allFiles = Glob file of all csvs in the target folder, used for iterating through each
		engine = sql_alchemy connection to the database, used to create tables and schema with the pandas dataframe structure from each CSV
		conn = Psycopg2 connection to the database, used for data transfer
		cursor = Active psycopg2 cursor for executiing PostgreSQL commands on the database
	"""
	
	script_path = None
	host = None
	port = None
	dbname = None
	user = None
	password = None
	data = None
	allFiles = None
	engine = None
	conn = None
	cursor = None

	def __init__(self,data_path):
		"""
		Creates the blob file of all csvs for upload, then uses the config.ini file to esablish both the sql_alchemy and psycopg2 connections to the database
		Note: the dual connections are for maximum efficiency in bulk uploads. Psycopg2 has a significantly faster transfer rate and is used for transferring the files,
		however the sql_alchemy engine connection and pandas to_sql() function are used initially generate the table for insertion as:
			a) psycopg2 copy_from() does not have functionality to create tables, it can only insert rows
			b) dynamically generating table schema in PostgreSQL is extremely complex, while pandas.to_sql() handles it elegantly
		"""
		try:
			#initialise the config.yml file
			script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
			with open(script_path+"/config.yml", 'r') as ymlfile:
				config = yaml.load(ymlfile)
			#set the database connection parameters based on the config.ini file
			host = config['PostgreSQL']['host']
			port = config['PostgreSQL']['port']
			dbname = config['PostgreSQL']['dbname']
			user  = config['PostgreSQL']['user']
			password = config['PostgreSQL']['password']
		except:
			print("Unable to read config.ini")

		try:
			#create a combined glob file of all the files in the target folder
			self.data = data_path
			self.allFiles = glob.glob(os.path.join(self.data,"*.csv"))

			#establish connections to the postgres database and an active cursor for queries
			self.engine = create_engine(r"postgresql://"+user+":"+password+"@"+host+"/"+dbname)
			self.conn = psycopg2.connect(host=host,port=port,dbname=dbname,user=user,password=password)
			self.cursor = self.conn.cursor()
			return
		except:
			print("Unable to reach PostgreSQL database")


	def append_upload(self):
		"""
		Uploads all CSV files in the target folder to the DB, appending them all to a single table named after the target folder
		"""
		try:
			#use pandas to_sql() to create a database table (and temp table) with the schema of the first csv
			df = pd.read_csv(self.allFiles[0], nrows=0)
			df.to_sql(con=self.engine, name='temp', if_exists='replace',index=False)
			df.to_sql(con=self.engine, name=self.data.rsplit('/', 1)[-1], if_exists='replace',index=False)

			#copy data from the csv into temp, remove the header row, then insert into the final table
			tablename = str(self.data.rsplit('/', 1)[-1])
			for file in self.allFiles:
				csv_stream = open(file, 'r')
				self.cursor.execute("DELETE FROM temp;")
				self.cursor.copy_from(file=csv_stream,table='temp',sep=',') #psycopg2 function copy_from() is used here as it has far greater upload times
				self.cursor.execute("DELETE FROM temp WHERE ctid = '(0,1)'; INSERT INTO "+tablename+" SELECT * FROM temp;")
				csv_stream.close()
			
			#remove the temp table, commit all changes to the database and close the connection
			self.cursor.execute("DROP TABLE temp;")
			self.conn.commit()
			self.conn.close()
			return "Files successfully transferred"

		except:
			return "Unable to upload files"

	def multi_upload(self):
		"""
		Uploads all CSV files in the target folder to the DB, creating a new table for each with the CSV name
		"""
		try:
			for file in self.allFiles:
				filename = file.rsplit('/',1)[-1]
				tablename = "csv_"+filename.rsplit('.',1)[0]
				#use pandas to_sql() to create a database table (and temp table) with the schema of the first csv
				df = pd.read_csv(file, nrows=0)
				df.to_sql(con=self.engine, name=tablename, if_exists='replace',index=False)
				#open each CSV and stream the rows to the target DB table
				csv_stream = open(file, 'r')
				self.cursor.copy_from(file=csv_stream,table=tablename,sep=',')
				#this command deletes the first row of the table, as copy_from() imports the headers as a row
				self.cursor.execute("DELETE FROM "+tablename+" WHERE ctid = '(0,1)';")
				csv_stream.close()
			#commit all changes to the database and close the connection
			self.conn.commit()
			self.conn.close()
			return "Files successfully transferred"
		except:
			return "Unable to upload files"