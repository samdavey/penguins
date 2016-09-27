# Data preparation

There are a number data sets to prepare:
1. Master data
  1. Nest Box master data
  2. Topographic information
2. Observational data
  1. Temperature and Humidity observations
  2. Breeding and usage obserations
  3. Nest Characteristics

## Temperature and humidity data
The data is in separate `.csv` files in the folder `.\data\TempHumidData_22_7_2016`.
Within the `TempHumidData_22_7_2016` folder are subfolders named `BOX <id number>` and within these are `.csv` files in the following format:
```
Date/Time,Value,Nest Id,Visit Id
8/01/2014 12:54,57.961,117,4
8/01/2014 13:24,61.458,117,4
8/01/2014 13:54,64.33,117,4
```

Will be turned into the following format for both the temp and the humidity data:
```
Date/Time,
Value,
Nest Id (comes from the folder name),
filename of the data csv
md5 hash of the record (for identification of duplicates)
```
Each of these `.csv` files are to be merged into a single data set of all observations for all nests in files named `a_Temp_merged.csv` and `a_Humidity_merged.csv`. (**in progress**)
* Files where the filename contains 'ibutton' are excluded.
* Files commencing with sensor metadata will have the metadata stripped during the append.

At the completion of the appending, duplicate records will be extracted out of the merged file and recorded in files called `b2_Temp_duplicates.csv` and `b2_Humidity_duplicates.csv`. Non-duplicates will be recorded in `b1_Temp_nondupes.csv` and `b1_Humidity_nondupes.csv`.