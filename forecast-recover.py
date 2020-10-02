import pandas as pd
from math import inf
from sqlitedict import SqliteDict
from statsmodels.tsa.ar_model import AutoReg

cache = SqliteDict('recover.db', autocommit=True)
# A US manufacturer buys raw materials in multiple currencies
purchases = pd.read_excel('Purchases.xlsx')

# For each of those currencies, find the best model to forecast prices
best_model = {}
for currency in purchases.currency:
    print('Currency', currency)
    if currency not in cache:
        data = pd.read_excel(f'{currency}.xlsx')
        data = data[data[currency] > 0]
        best_aic, best_fit = inf, None
        for lags in (3, 5, 7, 10, 14, 28, 60, 90, 120, 183, 365, 730, 1095):
            print('    Lag', lags)
            model = AutoReg(data[currency], lags=lags)
            fit = model.fit()
            if fit.aic < best_aic:
                best_aic, best_fit = fit.aic, fit
        cache[currency] = best_fit
    best_model[currency] = cache[currency]

# Estimate next month's price increase assuming the same volume as today
forecasted_value = 0
for index, row in purchases.iterrows():
    fit = best_model[row.currency]
    prices = fit.predict(fit.model.nobs, fit.model.nobs + 30)
    change = prices.iloc[-1] / prices.iloc[0]
    forecasted_value += row.value * change

print('Sales value will move from {:,.0f} to {:,.0f}'.format(
    purchases.value.sum(), forecasted_value))
