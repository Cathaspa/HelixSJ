# Copyright (c) 2017 Anne-Laure Ehresmann 
# Licenced under the MIT License (https://en.wikipedia.org/wiki/MIT_License)
# version 0.0.1

#### Guidelines ####

# The first line is ignored: it is understood that it will be used for titling.

# It is assumed that the sheet is in the following format: odd numbered cols are gene
# symbols, even numbered cols are log_FC values.

import sys
import math
import pandas as pd

def build_samples(data_file):
    headers = pd.read_csv(data_file, index_col=0,nrows=1) # reads only first row, just to get column quantity.
    samples = []
    i = 0
    while i < len(list(headers)):
        sample = pd.read_csv(data_file, skipinitialspace=True, usecols = [i, i + 1])
        sample = sample.dropna() # removing NaN rows
        finished = pd.DataFrame([["FinishedRow", 0]], columns = list(sample))
        sample = sample.append(finished, ignore_index = True) # adding this to delimit the end of the column. Note: obviously, don't name a gene 'FinishedRow'.
        samples.append(sample)
        i += 2
    return samples

def build_indexes(length):
    indexes = []
    for i in range(length):
        indexes.append(0)
    return indexes

def get_last(samples):
    max = "!" # The first visible character in the ASCII table is '!'. This is to guarantee the variable will be rewritten.
    for sample  in samples:
        sample_max = sample.iloc[-2,0] 
        if(sample_max > max):
            max = sample_max
    return max

def process_line(vals, output):
    newline = []
    current = "~" # Same logic as in get_last() but reversed. '~' is one of the last characters.
    for i  in range(len(samples)):
        vals[i] = samples[i].iloc[indexes[i],0]
        if (vals[i] < current) & (vals[i] != "FinishedRow"):
            current = vals[i]
    newline.append(current)
    for i in range(len(samples)):
        if current == vals[i]:
            newline.append( samples[i].iloc[indexes[i],1])
            if (indexes[i] < len(samples[i]) - 1) & (vals[i] != "FinishedRow"):
                indexes[i] += 1
        else:
            newline.append("NaN")
    output.loc[len(output)] = newline
    return current

if (len(sys.argv) != 2):
    print("You must give me (at-least / only) one source file. Exiting.")
    sys.exit()

samples = build_samples(sys.argv[1])
indexes = build_indexes(len(samples))
vals = build_indexes(len(samples))
last_gene = get_last(samples)
headers = []
headers.append(list(samples[0])[0]) # add first gene name
# add each log_FC columns' headers
for i in range(0, len(samples)):
    headers.append(list(samples[i])[1])

print(len(headers), headers)
# empty dataframe to append to, with column headers built above
output = pd.DataFrame(columns=headers)
more = process_line(vals,output)
count = 0
print("running....")
while more != last_gene:
    count +=1
    more = process_line(vals,output)
    if( count%1000  == 0):
        print("Computed %d rows..." % (count))
print("Done")  
output.to_csv("output.csv", index=False)