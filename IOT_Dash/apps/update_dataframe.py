import os
import pandas as pd
from pandas.io import gbq
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "data/pi-iot-project.json"

# Instantiates a client
bigquery_client = bigquery.Client()

improved=pd.read_csv('../data/improved.csv')
#print(improved_old.tail())

last_input=improved['time'].max()
last_input=last_input[:10]+" 00:00:00"

device="catfeeder"
query = '''
SELECT time, val FROM `pi-iot-project-235918.home.sensors` 
where sensor = "Weight"
and device = '{}' 
and time >'{}'
order by time desc 
'''.format(device, last_input)

print(query)

df = gbq.read_gbq(query, dialect='standard' );


df['time'] = df['time'].astype(str)

# Weight val cleaning

df=df[df.val > 0]
df=df[df.val < 200]

df['Day']=df['time'].str[:10]
df['Hour']=df['time'].str[10:]

print(df.head())

# Converting function!!

# Data for the Days in the last query
Days = list(set(df['Day']))

print(Days)
# remove the last incomplete day...
improved = improved[~improved.Day.isin(Days)]

for day in Days:
    print(day)
    temp = df.copy(deep=True)

    temp = temp[temp.Day == day]
    temp = temp.sort_values(['time'])

    temp['delta'] = 0
    temp['eaten'] = 0
    temp['given'] = 0

    for i in range(1, len(temp)):
        value = temp['val'].iloc[i] - temp['val'].iloc[i - 1]
        temp['delta'].iloc[i] = value
        if value < 0:
            temp['eaten'].iloc[i] = value * (-1)
        if value > 0:
            temp['given'].iloc[i] = value

    temp['eaten_cum_Day'] = temp['eaten']
    temp['given_cum_Day'] = temp['given']

    for i in range(1, len(temp)):
        value = temp['eaten_cum_Day'].iloc[i - 1] + temp['eaten_cum_Day'].iloc[i]
        temp['eaten_cum_Day'].iloc[i] = value

        value = temp['given_cum_Day'].iloc[i - 1] + temp['given_cum_Day'].iloc[i]
        temp['given_cum_Day'].iloc[i] = value

    improved = improved.append(temp)


print(improved.head())

improved.to_csv('../data/improved.csv', index=False)