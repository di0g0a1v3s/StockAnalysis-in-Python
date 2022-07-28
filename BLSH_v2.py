#BUY LOW SELL HIGH

from os import times
from time import time
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

initial_investment = 100
cost_per_tx = 0.5/100

INTERVAL = '60m'
TICKERS = ['SPY-USD']
PERIODS = ['1d','2d','10d']

for TICKER in TICKERS:
    for PERIOD in PERIODS:

        stock = yf.Ticker(TICKER)
        stock_hist = stock.history(period=PERIOD, interval=INTERVAL)



        def bot(initial_investment, stock_hist, factor):
            sales = []
            buys = []
            money = initial_investment
            num_stocks = 0
            maximum_since_last_buy = -1
            minimum_since_last_sale = -1
            num_buys = 0
            num_sales = 0
            i = 0
            for date in stock_hist.index:
                if minimum_since_last_sale == -1:
                    current_price = stock_hist.get("Close")[date]
                    initial_stock_value = current_price
                    maximum_since_last_buy = current_price
                    minimum_since_last_sale = current_price
                    #buy
                    num_stocks = (money*(1-cost_per_tx))/current_price
                    money = 0

                    num_buys = num_buys + 1
                    last_buy_price = current_price
                    last_sell_price = current_price
                    buys.append(i)
                    i=i+1
                    continue
                last_stock_value = stock_hist.get("Close")[date]
                current_price = stock_hist.get("Close")[date]
                if maximum_since_last_buy < current_price:
                    maximum_since_last_buy = current_price
                if minimum_since_last_sale > current_price:
                    minimum_since_last_sale = current_price

                if current_price < maximum_since_last_buy * (1-factor) and num_stocks != 0 and current_price > last_buy_price:  #sell 
                    money = current_price*num_stocks*(1-cost_per_tx)
                    num_stocks = 0
                    num_sales = num_sales + 1
                    sales.append(i)
                    minimum_since_last_sale = current_price
                    
                    
                    
                elif current_price > minimum_since_last_sale * (1+factor) and money != 0: #and current_price < last_sell_price: #buy    
                    num_stocks = (money*(1-cost_per_tx))/current_price
                    money = 0
                    num_buys = num_buys + 1
                    buys.append(i)
                    maximum_since_last_buy = current_price
                    
                    #print("BUY", date, current_price, "last_minimum=",last_minimum)

                i = i+1

            if max(current_price*num_stocks, money) > initial_investment/initial_stock_value * last_stock_value:
                print("\n Factor=",factor)
                print("Final net worth: Money - ", money,", Stock - ", current_price*num_stocks, "; Buys -", num_buys,"times; Sales - ", num_sales,"times")
                print("\n\n")

            return last_stock_value, initial_stock_value, num_stocks, money, buys, sales



        factor_highest_return = 0
        highest_return = 0

        stock_price = [0] * len(stock_hist.index)
        i = 0
        for date in stock_hist.index:
            stock_price[i] = stock_hist.get("Close")[date]
            i=i+1


        for factor_aux in range(0, 50):
            factor = factor_aux/100
            last_stock_value, initial_stock_value, num_stocks, money, buys, sales = bot(initial_investment, stock_hist, factor)
            
            if max(last_stock_value*num_stocks, money) > highest_return:
                factor_highest_return = factor
                highest_return = max(last_stock_value*num_stocks, money)

        print("Net worth buy and hold - ", initial_investment/initial_stock_value * last_stock_value, "(Initial value:", initial_stock_value, ", Final value:", last_stock_value,")")
        #factor_highest_return = 0.11
        print("HIGHEST RETURN: ", highest_return, "FACTOR: ", factor_highest_return)

        last_stock_value, initial_stock_value, num_stocks, money, buys, sales = bot(initial_investment, stock_hist, factor_highest_return)
        highest_return = max(last_stock_value*num_stocks, money)
        return_bh = (initial_investment/initial_stock_value * last_stock_value - initial_investment)/initial_investment*100
        return_blsh = (highest_return - initial_investment)/initial_investment*100
        plt.figure()
        plt.title(TICKER + ", " + PERIOD + ", FACTOR = " + str(factor_highest_return) + ", B&H = " + str(round(return_bh,2))+"%"+", BLSH = " + str(round(return_blsh,2))+"%")
        plt.plot(range(len(stock_price)), stock_price, 'c', label= "Stock price")
        plt.scatter(buys, [stock_price[x] for x in buys], color='green')
        plt.scatter(sales, [stock_price[x] for x in sales], color='red')
        plt.savefig(TICKER + ", " + PERIOD + "-v2-"+" FACTOR = " + str(factor_highest_return) + ", B&H = " + str(round(return_bh,2))+"%"+", BLSH = " + str(round(return_blsh,2))+"%" + '.png')
        #plt.show()

