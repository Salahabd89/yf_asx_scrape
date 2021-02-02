import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import math
import time
import warnings
warnings.filterwarnings('ignore')

# paramter setup

# define the location of the ASX input list
location_of_listed_companies = ''
name_of_listed_companies_file = 'asx.csv'

# define the location of the ASX output list
location_of_output_file = ''
name_of_output_file = 'ASX_CASH_TEST.csv'

# read the input file
data = pd.read_csv(location_of_listed_companies + name_of_listed_companies_file, sep=',')


# define the data frame
asx_dataset = pd.DataFrame(columns=[  'asx_code',
                                      'company_name',
                                      'listing_date',
                                      'industry',
                                      'total_cash',
                                      'period'])


print('started!') 

prev_letter =  ''
curr_letter =  ''


# loop through each ASX code
for code in data['ASX code']:

    curr_letter = code[0]
    if prev_letter == '':
        prev_letter = curr_letter

    #if curr_letter != prev_letter:
        #time.sleep(15)
    
    # initialise the two variable that will be scraped
    total_cash = 0
    reporting_period = 0
    
    try:
        # from the ASX csv grab the industry, company name and listing date
        industry = data[data['ASX code'] == code]['GICs industry group'].values[0]
        company_name = data[data['ASX code'] == code]['Company name'].values[0]
        listing_date = data[data['ASX code'] == code]['Listing date'].values[0]

        # url to check
        URL = 'https://au.finance.yahoo.com/quote/'+code+'.ax/balance-sheet?p='+code+'.AX'

        # got to link
        page = requests.get(URL, verify=False, timeout = 20)
        print(page)

        # parse the returned HTML
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # find the name of the tag related to cash
        cash_tag_name = soup.find(text="Cash and cash equivalents")

        # move to the next span to get the value
        if (len(cash_tag_name)> 0):

            next_span_tag = cash_tag_name.findNext('span')

            # get cash value
            total_cash = next_span_tag.text.replace(',', '')
            total_cash  =  math.trunc(float(total_cash))
            total_cash =  total_cash / 1000 #

            # find the name of the period value
            period_tag_name = soup.find(text="Breakdown")

            # move to the next span to get the value
            next_span_tag = period_tag_name.findNext('span')

            # get period value
            period = next_span_tag.text
            
            # convert the date to 'YYYYMM' FORMAT
            period_date_converted = datetime.strptime(period,'%d/%m/%Y')
            period_date_adjusted = period_date_converted.strftime("%Y%m")
            reporting_period =period_date_adjusted

        
    except Exception as e:
        time.sleep(15)
        print(e)
    
    prev_letter = curr_letter

    print(code)
    print(total_cash)
    print(reporting_period)

    
    # add each one to a pandas dataframe
    asx_dataset = asx_dataset.append({
                                      'asx_code':code,
                                      'company_name':company_name, 
                                      'listing_date':listing_date,
                                      'industry':industry,
                                      'total_cash':total_cash,
                                      'period':reporting_period}, ignore_index=True)

# create a csv with the completed 
asx_dataset.to_csv(location_of_output_file + name_of_output_file, index=False, header=True)
print('completed!')    
