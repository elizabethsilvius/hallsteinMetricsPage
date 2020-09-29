import pandas as pd
from datetime import datetime, timedelta, date
from dateutil import relativedelta
import requests
import json
import calendar
import statistics
import numpy

# This function finds the number of new subscribers in a time period
def new_subscribers(start_date, end_date, df):
    mask = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids = df[mask]
    ids = ids[ids['type'] == 'new-subscription']
    return(ids['account_id'].nunique())
	
	
# This function finds the Average number of units ordered per subscriber in a time period
def avg_order_subscribers(start_date, end_date, df):
    mask = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids = df[mask]
    ids = ids[ids['type'] != 'one-time']
    return(ids['sub_bottles'].mean())
	
# this function returns the start and end date of the previous period
def return_previous_dates(start_date, end_date):
    #find the length of the time period
    stop_plus = pd.to_datetime(end_date) + timedelta(days = 1)
    difference = relativedelta.relativedelta(stop_plus, pd.to_datetime(start_date))
    timediff = datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days = 1)
    # if the time period is exactly a number of months
    if(difference.days == 0):
	    start_date_previous = datetime.strptime(start_date, "%Y-%m-%d") - relativedelta.relativedelta(months = difference.months)
	    end_date_previous = datetime.strptime(end_date, "%Y-%m-%d")  - relativedelta.relativedelta(months = difference.months)
    # if the time period is not exactly a number of months
    else:
        start_date_previous = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days = timediff.days)
        end_date_previous = datetime.strptime(end_date, "%Y-%m-%d")  - timedelta(days = timediff.days)
    return([format(start_date_previous, "%Y-%m-%d"), format(end_date_previous, "%Y-%m-%d")])

# This function finds the Change (Number) in Active subscribers vs last period in a time period
def num_change_subscribers(start_date, end_date, df):
    # find the startand end date of the previous time period
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    # find the ids in the time period
    mask_current = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids_current = df[mask_current]
    # remove any one-timers
    ids_current = ids_current[ids_current['type'] != 'one-time']
    subscribers_current = ids_current['account_id'].nunique()
    # find the ids in the previous time period
    mask_previous = (df['created_at_date'] >= start_date_previous) & (df['created_at_date'] <= end_date_previous)
    ids_previous = df[mask_previous]
    # remove any one timers
    ids_previous = ids_previous[ids_previous['type'] != 'one-time']
    subscribers_previous = ids_previous['account_id'].nunique()
    # find and return the difference between the previous ids and the current ids and the %
    change = subscribers_current-subscribers_previous
    perc_change = (change/subscribers_previous * 100)
    return([subscribers_current, subscribers_previous, change, '{:f}%'.format(perc_change)])

# this function gets today's exchange rate (EUR to USD)
def get_exchange_rate():
    url = "https://api.exchangeratesapi.io/latest?symbols=USD,GBP"
    response = requests.get(url)
    data = response.text
    parsed = json.loads(data)
    date = parsed["date"]
    usd_rate = parsed["rates"]["USD"]
    return(usd_rate)
	
# This function finds the Change (Dollars) in Active subscribers vs last period in a time period
def dollars_change_subscribers(start_date, end_date, df):
    # find the previous period start and end dates
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    # find the current subscriber ids
    mask_current = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids_current = df[mask_current]
    ids_current = ids_current[ids_current['type'] != 'one-time']
    # separate the trasnsactions that are in euros
    euros_current = ids_current[ids_current['currency'] == 'EUR']
    euros_current = euros_current['total']
    new_euros_current = []
    # for each euro transaction, replace the commas with periods
    for euro in euros_current:
        new_euro = euro.replace(",", ".")
        new_euros_current.append(new_euro)
    # change the euros to floats, sum the values, and apply the exhcnage rate
    new_euros_current = [float(i) for i in new_euros_current]
    new_euros_current = sum(new_euros_current) * get_exchange_rate()
    # separate the dollars transaction
    dollars_current = ids_current[ids_current['currency'] == 'USD']
    dollars_current = dollars_current['total']
    new_dollars_current = []
    # for each dollar trasnsaction, replace the commas with periods
    for dollar in dollars_current:
        new_dollar = dollar.replace(",", ".")
        new_dollars_current.append(new_dollar)
    # change the dollars to floats, sum the total, and add the total from the euros
    new_dollars_current = [float(i) for i in new_dollars_current]
    new_dollars_current = sum(new_dollars_current) + new_euros_current
    # find the ids for the previous time period
    mask_previous = (df['created_at_date'] >= start_date_previous) & (df['created_at_date'] <= end_date_previous)
    ids_previous = df[mask_previous]
    ids_previous = ids_previous[ids_previous['type'] != 'one-time']
    # seprate the euro transactions
    euros_previous = ids_previous[ids_previous['currency'] == 'EUR']
    euros_previous = euros_previous['total']
    new_euros_previous = []
    # for each euro transaction, replace the commas with periods
    for euro in euros_previous:
        new_euro = euro.replace(",", ".")
        new_euros_previous.append(new_euro)
    # change the euro trasactions to floats, sum them, and apply the exchange rate
    new_euros_previous = [float(i) for i in new_euros_previous]
    new_euros_previous = sum(new_euros_previous) * get_exchange_rate()
    # separate the dollar transactions
    dollars_previous = ids_previous[ids_previous['currency'] == 'USD']
    dollars_previous = dollars_previous['total']
    new_dollars_previous = []
    # for each dollar trasnsaction, replace the commas with periods
    for dollar in dollars_previous:
        new_dollar = dollar.replace(",", ".")
        new_dollars_previous.append(new_dollar)
    # change the dollars to floats, sum the total, and add the total from the euros
    new_dollars_previous = [float(i) for i in new_dollars_previous]
    new_dollars_previous = sum(new_dollars_previous) + new_euros_previous
    return([new_dollars_current, new_dollars_previous, round(new_dollars_current - new_dollars_previous, 2), len(ids_current)])

# This function finds the Change (Number) in Active subscribers vs last period in a time period
def num_change_onetimers(start_date, end_date, df):
    # find the start and end date for the previous time period
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    # find the ids from the current time period and look at only the one-timers
    mask_current = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids_current = df[mask_current]
    ids_current = ids_current[ids_current['type'] == 'one-time']
    # count numebr of unique ids
    onetimers_current = ids_current['account_id'].nunique()
    # find the ids from the previous time period and look at only the one-timers
    mask_previous = (df['created_at_date'] >= start_date_previous) & (df['created_at_date'] <= end_date_previous)
    ids_previous = df[mask_previous]
    ids_previous = ids_previous[ids_previous['type'] == 'one-time']
    onetimers_previous = ids_previous['account_id'].nunique()
    # find and return the difference between the previous ids and the current ids and the %
    change = onetimers_current-onetimers_previous
    perc_change = (change/onetimers_previous * 100)
    return([onetimers_current, onetimers_previous, change, '{:f}%'.format(perc_change)])
	
# This function finds the Change (Dollars) in Active subscribers vs last period in a time period
def dollars_change_onetimers(start_date, end_date, df):
    # find the previous period start and end dates
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    # find the currentonetimer ids
    mask_current = (df['created_at_date'] >= start_date) & (df['created_at_date'] <= end_date)
    ids_current = df[mask_current]
    ids_current = ids_current[ids_current['type'] == 'one-time']
    # separate the trasnsactions that are in euros
    euros_current = ids_current[ids_current['currency'] == 'EUR']
    euros_current = euros_current['total']
    new_euros_current = []
    # for each euro transaction, replace the commas with periods
    for euro in euros_current:
        new_euro = euro.replace(",", ".")
        new_euros_current.append(new_euro)
    # change the euros to floats, sum the values, and apply the exhcnage rate
    new_euros_current = [float(i) for i in new_euros_current]
    new_euros_current = sum(new_euros_current) * get_exchange_rate()
    # separate the dollars transactions
    dollars_current = ids_current[ids_current['currency'] == 'USD']
    dollars_current = dollars_current['total']
    new_dollars_current = []
    # for each dollar transaction, replace the commas with periods
    for dollar in dollars_current:
        new_dollar = dollar.replace(",", ".")
        new_dollars_current.append(new_dollar)
    # change the dollars to floats, sum the total, and add the total from the euros
    new_dollars_current = [float(i) for i in new_dollars_current]
    new_dollars_current = sum(new_dollars_current) + new_euros_current
    # find the previous onetimer ids
    mask_previous = (df['created_at_date'] >= start_date_previous) & (df['created_at_date'] <= end_date_previous)
    ids_previous = df[mask_previous]
    ids_previous = ids_previous[ids_previous['type'] == 'one-time']
    # seprate the euro transactions
    euros_previous = ids_previous[ids_previous['currency'] == 'EUR']
    euros_previous = euros_previous['total']
    new_euros_previous = []
    # for each euro transaction, replace the commas with periods
    for euro in euros_previous:
        new_euro = euro.replace(",", ".")
        new_euros_previous.append(new_euro)
    # change the euros to floats, sum the values, and apply the exhcnage rate
    new_euros_previous = [float(i) for i in new_euros_previous]
    new_euros_previous = sum(new_euros_previous) * get_exchange_rate()
    # separate the dollars transactions
    dollars_previous = ids_previous[ids_previous['currency'] == 'USD']
    dollars_previous = dollars_previous['total']
    new_dollars_previous = []
    # for each dollar transaction, replace the commas with periods
    for dollar in dollars_previous:
        new_dollar = dollar.replace(",", ".")
        new_dollars_previous.append(new_dollar)
    # change the dollars to floats, sum the total, and add the total from the euros
    new_dollars_previous = [float(i) for i in new_dollars_previous]
    new_dollars_previous = sum(new_dollars_previous) + new_euros_previous
    # return the difference between the two umbers rounded to the tenth
    change =  round(new_dollars_current - new_dollars_previous, 2)
    perc_change = (round(change/new_dollars_previous * 100),2)
    return([new_dollars_current, new_dollars_previous, change, perc_change])

def months_between(start_date, end_date):
    """
    Given two instances of ``datetime.date``, generate a list of dates on
    the 1st of every month between the two dates (inclusive).

    e.g. "5 Jan 2020" to "17 May 2020" would generate:

        1 Jan 2020, 1 Feb 2020, 1 Mar 2020, 1 Apr 2020, 1 May 2020

    """
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} is not before end date {end_date}")

    year = start_date.year
    month = start_date.month

    while (year, month) <= (end_date.year, end_date.month):
        yield date(year, month, 1)

        # Move to the next month.  If we're at the end of the year, wrap around
        # to the start of the next.
        #
        # Example: Nov 2017
        #       -> Dec 2017 (month += 1)
        #       -> Jan 2018 (end of year, month = 1, year += 1)
        #
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

# function to get unique values 
def unique(list1): 
  
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x) 
    return(unique_list) 

def diff(li1, li2): 
    li_dif = [i for i in li1 + li2 if i not in li2] 
    return li_dif
  
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3
	
def get_churn_table(df, mos_bet):
    idsSoFar = []
    lastMonth = []
    numChurn = []
    for mos in mos_bet:
        mask_current = (pd.DatetimeIndex(df['created_at_date']).month ==  mos.month) & (pd.DatetimeIndex(df['created_at_date']).year == mos.year)
        ids_current = df[mask_current]
        mosIds = unique(ids_current['account_id'])
        idsSoFar = unique(idsSoFar + mosIds)
        if(len(lastMonth) > 0):
            numChurn.append(len(diff(lastMonth, mosIds))/len(lastMonth))
        else:
            numChurn.append("NaN")
        lastMonth = mosIds
    return(numChurn)
	
def churn_rate(start_date, end_date, df):
    df = df[df['type'] != 'one-time']
    oldest = min(df['created_at_date'])
    newest = max(df['created_at_date'])
    mos_bet = []
    for month in months_between(oldest, newest):
        mos_bet.append(month)
    # generate the churn table
    churn_table = get_churn_table(df, mos_bet)
    #find the length of the time period
    stop_plus = pd.to_datetime(end_date) + timedelta(days = 1)
    difference = relativedelta.relativedelta(stop_plus, pd.to_datetime(start_date))
    # find the month and year and compare to current date
    # start_date = datetime.strptime(start_date, "%Y-%m-%d") 
    # end_date = datetime.strptime(end_date, "%Y-%m-%d") 
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    current_date = date.today()
    if(start_date.month == current_date.month and start_date.year == current_date.year):
        return(churn_table[len(churn_table)-2])
    else:
        mos_bet_start_end = []
        for month in months_between(start_date, end_date):
            mos_bet_start_end.append(month)
        churn_ind = [i for i in range(len(mos_bet)) if mos_bet[i] in mos_bet_start_end]
        return(statistics.mean([churn_table[i] for i in churn_ind]) * 100)
	
def churn_rate_change(start_date, end_date, df):
    # find the previous period start and end dates
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    churn_current = churn_rate(start_date, end_date, df)
    churn_previous = churn_rate(start_date_previous, end_date_previous, df)
    return(churn_current - churn_previous)

def mrr(start_date, end_date, df):
    #find the length of the time period
    stop_plus = pd.to_datetime(end_date) + timedelta(days = 1)
    difference = relativedelta.relativedelta(stop_plus, pd.to_datetime(start_date))
    # find the month and year and compare to current date
    # start_date = datetime.strptime(start_date, "%Y-%m-%d") 
    # end_date = datetime.strptime(end_date, "%Y-%m-%d") 
    # start_date = pd.to_datetime(start_date)
    # end_date = pd.to_datetime(end_date)
    current_date = date.today()
    if(pd.to_datetime(start_date).month == current_date.month and pd.to_datetime(start_date).year == current_date.year):
        lastMonthEnd = current_date.replace(day=1) - timedelta(days=1)
        lastMonthStart = lastMonthEnd.replace(day=1)
        return(dollars_change_subscribers(format(lastMonthStart, '%Y-%m-%d'), format(lastMonthEnd, '%Y-%m-%d'), df)[0])
    else:
        mrr_all = []
        for month in months_between(pd.to_datetime(start_date), pd.to_datetime(end_date)):
            start_month = pd.to_datetime(month)
            end_month = pd.to_datetime(month).replace(day = calendar.monthrange(pd.to_datetime(month).year, pd.to_datetime(month).month)[1])
            start_month = format(start_month, '%Y-%m-%d')
            end_month = format(end_month, '%Y-%m-%d')
            mrr_all.append(float(dollars_change_subscribers(start_month, end_month, df)[0]))
        return(statistics.mean(mrr_all))

def mrr_change(start_date, end_date, df):
    # find the previous period start and end dates
    start_date_previous = return_previous_dates(start_date, end_date)[0]
    end_date_previous = return_previous_dates(start_date, end_date)[1]
    mrr_current = mrr(start_date, end_date, df)
    mrr_previous = mrr(start_date_previous, end_date_previous, df)
    return(mrr_current - mrr_previous)
	
def ltv(start_date, end_date, df):
    total_dollars = dollars_change_subscribers(start_date, end_date, df)[0]
    average_dollars = total_dollars/dollars_change_subscribers(start_date, end_date, df)[3]
    churn = churn_rate(start_date, end_date, df)
    return(average_dollars/(churn / 100))
	
def facility_costs(start_date, end_date, df_costs, df_sales, grid):
    grid = grid[(grid.Category == 'Bottling-Facility') | (grid.Category == 'Bottling-Process')]	
    mask_costs = (df_costs['Date'] >= start_date) & (df_costs['Date'] <= end_date)
    ids_current = df_costs[mask_costs]
    partners = grid.Partnername
    ids_current = ids_current[ids_current['Partnername'].isin(partners)] 
    fac_costs_eu = numpy.nansum(ids_current['Ausgehender Betrag'])
    fac_costs_dollars = abs(fac_costs_eu) * get_exchange_rate()
    mask_sales = (df_sales['created_at_date'] >= start_date) & (df_sales['created_at_date'] <= end_date)
    total_bottles = df_sales[mask_sales]
    total_bottles = sum(total_bottles.sub_bottles) + sum(total_bottles.ot_bottles)
    return(round(fac_costs_dollars/total_bottles, 2))

def cac(start_date, end_date, df_costsEU, df_costsUS, df_sales, grid):
    mask_sales = (df_sales['created_at_date'] >= start_date) & (df_sales['created_at_date'] <= end_date)
    total_new_customers = df_sales[mask_sales]
    total_new_customers = total_new_customers[total_new_customers['type'] == 'new-subscription']
    total_new_customers = len(total_new_customers)
    grid = grid[(grid.Category == 'Marketing') | (grid.Category == 'Marketing-Materials') | (grid.Category == 'Meals and Entertainment') | (grid.Category == 'Payroll') | (grid.Category == 'Web Development')]	
    partners = grid.Partnername
    mask_costs_eu = (df_costsEU['Date'] >= start_date) & (df_costsEU['Date'] <= end_date)
    all_costs_eu = df_costsEU[mask_costs_eu]
    all_costs_eu = all_costs_eu[all_costs_eu['Partnername'].isin(partners)] 
    marketing_costs_eu = sum(all_costs_eu['Ausgehender Betrag'])
    marketing_costs_eu_dollars = abs(marketing_costs_eu) * get_exchange_rate()
    mask_costs_us = (df_costsUS['Date'] >= start_date) & (df_costsUS['Date'] <= end_date)
    all_costs_us = df_costsUS[mask_costs_us]
    usSplits = ['Advertising', 'Alexander Muhr CC 2', 'Default Credit Card', 'Office Expenses', 'Elisabeth Muhr CC', 'Meals and Entertainment', 'Reimbursements', 'Sales Discounts', 'Travel', 'Alexander Muhr CC', 'Alexander Muhr CC x8188', 'Dues & Subscriptions', 'Materials', 'Office/General Administrative Expenses', 'Promotional', 'Sales', 'Stationary & Printing', 'Travel Meals', 'Payroll']
    marketing_costs_us = all_costs_us[all_costs_us['Split'].isin(usSplits)] 
    marketing_costs = sum(marketing_costs_us.Amount) + marketing_costs_eu_dollars
    return(round(marketing_costs/total_new_customers, 2))
	
def main():
    sales_file = input("Enter the path to your sales file:")
    sales = pd.read_excel(sales_file, skiprows = 2)
    sales['created at'] = pd.to_datetime(sales['created at'])
    sales['created_at_date'] = sales['created at'].dt.date
    sales['created_at_date'] = pd.to_datetime(sales['created_at_date'])
	
    costs_file = input("Enter the path to your costs file:")
    costsUS = pd.read_excel(costs_file, sheet_name = "Quickbooks Data")
    costsUS['Date'] = pd.to_datetime(costsUS['Date'])
	
    costsEU = pd.read_excel(costs_file, sheet_name = "Sparkasse Data", skiprows = 4)
    costsEU['Date'] = pd.to_datetime(costsEU['Valutadatum'])

    map_file = input("Enter the path to your Sparkasse-grid mapping file:")	
    map = pd.read_excel(map_file)
		
    start = input("Enter your start date: ")
    stop = input("Enter your end date: ")

    print("Number of new subscribers in time period:", new_subscribers(start, stop, sales))
    print("Average number of units ordered per subscriber in time period:", avg_order_subscribers(start,stop, sales))
    print("Start date of previous time period:", return_previous_dates(start, stop)[0])
    print("End date of previous time period:", return_previous_dates(start, stop)[1])
    print("Change (Number) in Active subscribers vs last period:",  num_change_subscribers(start, stop, sales)[2])
    print("Change (Percent) in Active subscribers vs last period:",  num_change_subscribers(start, stop, sales)[3])
    print("Change (Dollars) in Active subscribers vs last period:", "${:,.2f}".format(dollars_change_subscribers(start, stop, sales)[2]))
    print("Number of One-time order in this period:",  num_change_onetimers(start, stop, sales)[0])
    print("Dollars of One-time order in this period:",  "${:,.2f}".format(dollars_change_onetimers(start, stop, sales)[0]))
    print("Change (Number) in One-time orders vs last period:",  num_change_onetimers(start, stop, sales)[2])
    print("Change (Percent) in One-time orders vs last period:",  num_change_onetimers(start, stop, sales)[3])
    print("Change (Dollars) in One-time orders vs last period:", "${:,.2f}".format(dollars_change_onetimers(start, stop, sales)[2]))
    print("Churn Rate:", churn_rate(start, stop, sales))
    print("Churn Rate Change:", churn_rate_change(start, stop, sales))
    print("MRR:", "${:,.2f}".format(mrr(start, stop, sales)))
    print("MRR Change:", "${:,.2f}".format(mrr_change(start, stop, sales)))
    print("LTV:", "${:,.2f}".format(ltv(start, stop, sales)))
    print("Facility Costs per Bottle Sold (in Dollars):", "${:,.2f}".format(facility_costs(start, stop, costsEU, sales, map)))
    print("Cost of Acquiring a Customer (in Dollars):", "${:,.2f}".format(cac(start, stop, costsEU, costsUS, sales, map)))
    print("LVT Previous:",  "${:,.2f}".format(ltv(return_previous_dates(start, stop)[0], return_previous_dates(start, stop)[1], sales)))



if __name__ == "__main__":
    main()