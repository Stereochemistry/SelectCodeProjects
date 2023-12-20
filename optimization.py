""""""
"""MC1-P2: Optimize a portfolio.                                                                                

Copyright 2018, Georgia Institute of Technology (Georgia Tech)                                                                                  
Atlanta, Georgia 30332                                                                                  
All Rights Reserved                                                                                  

Template code for CS 4646/7646                                                                                  

Georgia Tech asserts copyright ownership of this template and all derivative                                                                                
works, including solutions to the projects assigned in this course. Students                                                                                
and other users of this template code are advised not to share it with others                                                                                
or to make it available on publicly viewable websites including repositories                                                                                
such as github and gitlab.  This copyright statement should not be removed                                                                                  
or edited.                                                                                  

We do grant permission to share solutions privately with non-students such                                                                                  
as potential employers. However, sharing with other current or future                                                                                
students of CS 7646 is prohibited and subject to being investigated as a                                                                                
GT honor code violation.                                                                                

-----do not edit anything above this line---                                                                                

Student Name: Tucker Balch (replace with your name)                                                                                  
GT User ID: amckay33 (replace with your User ID)                                                                                
GT ID: 903853993 (replace with your GT ID)                                                                                  
"""

import datetime as dt

import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
from util import get_data, plot_data
from scipy.optimize import minimize

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(
        sd='2008-01-01',
        ed='2009-01-01',
        syms=["GOOG", "AAPL", "GLD", "XOM"],
        gen_plot=False,
):
    """
    This function should find the optimal allocations for a given set of stocks. You should optimize for maximum Sharpe
    Ratio. The function should accept as input a list of symbols as well as start and end dates and return a list of
    floats (as a one-dimensional numpy array) that represents the allocations to each of the equities. You can take
    advantage of routines developed in the optional assess portfolio project to compute daily portfolio value and
    statistics.

    :param sd: A datetime object that represents the start date, defaults to 1/1/2008
    :type sd: datetime
    :param ed: A datetime object that represents the end date, defaults to 1/1/2009
    :type ed: datetime
    :param syms: A list of symbols that make up the portfolio (note that your code should support any
        symbol in the data directory)
    :type syms: list
    :param gen_plot: If True, optionally create a plot named plot.png. The autograder will always call your
        code with gen_plot = False.
    :type gen_plot: bool
    :return: A tuple containing the portfolio allocations, cumulative return, average daily returns,
        standard deviation of daily returns, and Sharpe ratio
    :rtype: tuple
    """
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all["SPY"]  # only SPY, for comparison later

    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
    allocs = np.random.random(len(syms))
    allocs /= np.sum(allocs)
    # add code here to find the allocations

    num_stocks = len(syms)

    # prices.fillna(method='ffill', inplace=True)
    # prices.fillna(method='bfill', inplace=True)

    normal = prices/prices.iloc[0]
    rets = np.log(normal / normal.shift(1))
    normal.plot(figsize=(8, 5))
    plt.savefig('OriginalPortfolio.png')

    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bnds = tuple((0, 1) for x in range(num_stocks))

    sharpe_ratio(allocs, rets)
    minimized = minimize(sharpe_ratio, allocs, args=(rets, ), method='SLSQP', constraints=cons, bounds=bnds)

    allocations = minimized.x
    print(allocations)

    cr, adr, sddr, sr = [
        0.25,
        0.001,
        0.0005,
        2.1,
    ]  # add code here to compute stats

    # Sharpe Ratio
    sr = sharpe_ratio(allocs, rets)

    # Average Daily Return
    adr = np.sum(rets.mean() * allocs)

    # Average Volatility
    sddr = np.sqrt(np.dot(allocs.T, np.dot(rets.cov() * 252, allocs)))

    # Get daily portfolio value
    port_val = prices_SPY  # add code here to compute daily portfolio values
    df = pd.DataFrame(index=dates)
    df.join(port_val)
    normSPY = df/df.iloc[0]
    retsSPY = np.log(df/ df.shift(1))

    # Cumulative Return
    cumulative = rets

    for sym in syms:
        cumulative[sym] = rets[sym].cumsum()

    cumulative = cumulative.mul(allocations, axis=1)
    cum_ret = cumulative.sum(axis=1)

    cr = cum_ret[-1]

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df_temp = pd.concat(
            [cum_ret, retsSPY], keys=["Portfolio", "SPY"], axis=1
        )
        ax = df_temp.plot()
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        plt.savefig('OptimizedPortfolio.png')

        pass

    return allocs, cr, adr, sddr, sr

def sharpe_ratio(allocs, rets):
    # Expected return
    pret = np.sum(rets.mean() * allocs) * 252
    # Expected Variance
    pvol = np.sqrt(np.dot(allocs.T, np.dot(rets.cov() * 252, allocs)))
    # Sharpe Ratio
    sharpe = pret / pvol

    return -sharpe

def test_code():
    """
    This function WILL NOT be called by the auto grader.
    """

    start_date = dt.datetime(2009, 1, 1)
    end_date = dt.datetime(2010, 1, 1)
    symbols = ["GOOG", "AAPL", "GLD", "XOM", "IBM"]

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(
        sd=start_date, ed=end_date, syms=symbols, gen_plot=False
    )

    # Print statistics
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Symbols: {symbols}")
    print(f"Allocations:{allocations}")
    print(f"Sharpe Ratio: {sr}")
    print(f"Volatility (stdev of daily returns): {sddr}")
    print(f"Average Daily Return: {adr}")
    print(f"Cumulative Return: {cr}")


if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()