from os import times
from time import time
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

monthly_investment = 100

def getMonthYear(timestamp):
    return str(timestamp.year) + "-" + str(timestamp.month)

stock = yf.Ticker('SPY')
stock_hist = stock.history(period='2y')
current_price = stock.info['regularMarketPrice']


dict = {}
for date in stock_hist.index:
    month_year = getMonthYear(date)
    if month_year not in dict:
        dict[month_year] = {"worst_day": 0, "best_day": 0, "worst_price": 0, "best_price": 1000000000}
        for n in range(1,32):
            dict[month_year]["price_day_"+str(n)] = 0

    dict[month_year]["price_day_"+str(date.day)] = stock_hist.get("Low")[date]

    if stock_hist.get("High")[date] > dict[month_year]["worst_price"]:
        dict[month_year]["worst_price"] = stock_hist.get("High")[date]
        dict[month_year]["worst_day"] = date.day

    if stock_hist.get("Low")[date] < dict[month_year]["best_price"]:
        dict[month_year]["best_price"] = stock_hist.get("Low")[date]
        dict[month_year]["best_day"] = date.day

#print(dict)

worst_case_shares = 0
best_case_shares = 0
day_x_shares = [0] * 31
total_invested = 0
worst_day_hist = {}
best_day_hist = {}


for n in range(1,32):
    worst_day_hist[n] = 0
    best_day_hist[n] = 0

total_invested_graph = [0] * len(dict.keys())
net_worth_graph_worst = [0] * len(dict.keys())
net_worth_graph_best = [0] * len(dict.keys())
net_worth_graph_day_x = [0] * len(dict.keys())
net_worth_graph_day_1 = [0] * len(dict.keys())
i = 0
for date in dict:
    if i == 0:
        total_invested_graph[0] = monthly_investment
    else:
        total_invested_graph[i] = total_invested_graph[i-1] + monthly_investment

    for n in range(1,32):
        if dict[date]["price_day_"+str(n)] != 0:
            day_x_shares[n-1] = day_x_shares[n-1] + monthly_investment/dict[date]["price_day_"+str(n)]
        else:
            day_x_shares[n-1] = day_x_shares[n-1] + monthly_investment/dict[date]["worst_price"]

    worst_case_shares = worst_case_shares + monthly_investment/dict[date]["worst_price"]
    best_case_shares = best_case_shares + monthly_investment/dict[date]["best_price"]
    total_invested = total_invested + monthly_investment
    
    
    net_worth_graph_worst[i] = worst_case_shares * dict[date]["worst_price"]
    net_worth_graph_best[i] = best_case_shares * dict[date]["worst_price"]
    net_worth_graph_day_1[i] = day_x_shares[0] * dict[date]["worst_price"]
    
    worst_day_hist[dict[date]["worst_day"]] = worst_day_hist[dict[date]["worst_day"]] + 1
    best_day_hist[dict[date]["best_day"]] = best_day_hist[dict[date]["best_day"]] + 1 
    i = i + 1

max_shares = 0
max_shares_day = 0
for day in range(1,32):
    num_shares = day_x_shares[day-1]
    if num_shares > max_shares:
        max_shares = num_shares
        max_shares_day = day

i = 0
day_max_shares = 0
for date in dict:
    if dict[date]["price_day_"+str(max_shares_day)] != 0:
        day_max_shares = day_max_shares + monthly_investment/dict[date]["price_day_"+str(max_shares_day)]
    else:
        day_max_shares = day_max_shares + monthly_investment/dict[date]["worst_price"]
    
    net_worth_graph_day_x[i] = day_max_shares * dict[date]["worst_price"]
    i = i+1


print("Total Invested: ", total_invested)
print("Worst case net worth: ", worst_case_shares*current_price)
print("Day 1 case net worth: ", day_x_shares[0]*current_price)
print("Day", max_shares_day, "case net worth (best): ", day_x_shares[max_shares_day-1]*current_price)
print("Best case net worth: ", best_case_shares*current_price)

#print("Worst days: ", worst_day_hist.__str__())
#print("Best days: ", best_day_hist.__str__())

fig, (ax1, ax2) = plt.subplots(2)

ax1.bar(worst_day_hist.keys(), worst_day_hist.values(), 1, color='r')

ax2.bar(best_day_hist.keys(), best_day_hist.values(), 1, color='g')

plt.figure()

plt.plot(range(len(total_invested_graph)), total_invested_graph, 'b', label= "total invested")
plt.plot(range(len(net_worth_graph_worst)), net_worth_graph_worst, 'r', label= "worst")
plt.plot(range(len(net_worth_graph_best)), net_worth_graph_best, 'g', label= "best")
plt.plot(range(len(net_worth_graph_day_x)), net_worth_graph_day_x, 'm', label= "Day "+str(max_shares_day)+" (best)")
plt.plot(range(len(net_worth_graph_day_1)), net_worth_graph_day_1, 'k', label= "Day 1")
plt.legend(loc="upper left")




#SKIP HIGH MONTH?
skip_threshold = 0.05
total_invested_graph_skip = [0] * len(dict.keys())
net_worth_graph_skip_high_month = [0] * len(dict.keys())
shares_skip_high_month = 0
monthly_investment_acc = monthly_investment
stock_price = [0] * len(dict.keys())
i = 0
for date in dict:
    stock_price[i] = dict[date]["worst_price"]*100
    if i == 0:
        total_invested_graph_skip[i] = total_invested_graph_skip[i-1] + monthly_investment
        shares_skip_high_month = shares_skip_high_month + monthly_investment/dict[date]["worst_price"]
        date_prev = date
    else:
        if dict[date]["worst_price"] > (1+skip_threshold)*dict[date_prev]["worst_price"]:
            total_invested_graph_skip[i] = total_invested_graph_skip[i-1]
            monthly_investment_acc = monthly_investment_acc + monthly_investment
        else:
            
            total_invested_graph_skip[i] = total_invested_graph_skip[i-1] + monthly_investment_acc
            shares_skip_high_month = shares_skip_high_month + monthly_investment_acc/dict[date]["worst_price"]
            monthly_investment_acc = monthly_investment
    date_prev = date
    net_worth_graph_skip_high_month[i] = shares_skip_high_month * dict[date]["worst_price"]
    i = i + 1

plt.figure()

plt.plot(range(len(total_invested_graph)), total_invested_graph, 'b', label= "total invested")
plt.plot(range(len(net_worth_graph_worst)), net_worth_graph_worst, 'r', label= "worst")
plt.plot(range(len(total_invested_graph_skip)), total_invested_graph_skip, 'm', label= "Total invested skip " + str(skip_threshold*100)+"%")
plt.plot(range(len(net_worth_graph_skip_high_month)), net_worth_graph_skip_high_month, 'k', label= "Skip high months")
plt.plot(range(len(stock_price)), stock_price, 'c', label= "Stock price")
plt.legend(loc="upper left")


#Exponential investment
total_invested_graph_exp = [0] * len(dict.keys())
net_worth_graph_exp = [0] * len(dict.keys())
shares_exp = 0
i = 0
for date in dict:
    
    investment_this_month = monthly_investment*len(dict)/(2**((i+1)))
   
    if i == 0:
        total_invested_graph_exp[i] = investment_this_month
    else:
        total_invested_graph_exp[i] = total_invested_graph_exp[i-1] + investment_this_month

    shares_exp = shares_exp + investment_this_month/dict[date]["worst_price"]
    
    net_worth_graph_exp[i] = shares_exp * dict[date]["worst_price"]
    i = i + 1

plt.figure()

plt.plot(range(len(total_invested_graph)), total_invested_graph, 'b', label= "total invested normal")
plt.plot(range(len(net_worth_graph_worst)), net_worth_graph_worst, 'r', label= "worst")
plt.plot(range(len(total_invested_graph_exp)), total_invested_graph_exp, 'm', label= "Total invested exponential ")
plt.plot(range(len(net_worth_graph_exp)), net_worth_graph_exp, 'k', label= "net worth exp")
#plt.plot(range(len(stock_price)), stock_price, 'c', label= "Stock price")
plt.legend(loc="upper left")


plt.show()