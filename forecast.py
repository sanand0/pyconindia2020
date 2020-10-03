import pandas as pd
from math import inf
from statsmodels.tsa.ar_model import AutoReg


# A US manufacturer buys raw materials in multiple currencies
purchases = pd.read_excel('Purchases.xlsx')

# For each of those currencies, find the best model to forecast prices
best_model = {}

LAG_IN_DAYS = (3, 5, 7, 10, 14, 28, 60, 90, 120, 183, 365, 730, 1095)

for currency in purchases.currency:
    data = pd.read_excel(f'{currency}.xlsx')
    data = data[data[currency] > 0]
    best_aic, best_fit = inf, None
    for lags in LAG_IN_DAYS:
        model = AutoReg(data[currency], lags=lags, old_names=False)
        fit = model.fit()
        if fit.aic < best_aic:
            best_aic, best_fit = fit.aic, fit
    best_model[currency] = best_fit

# Estimate next month's price increase assuming the same volume as today
forecasted_value = 0
for index, row in purchases.iterrows():
    fit = best_model[row.currency]
    prices = fit.predict(fit.model.nobs, fit.model.nobs + 30)
    change = prices.iloc[-1] / prices.iloc[0]
    forecasted_value += row.value * change

print('Sales value will move from {:,.0f} to {:,.0f}'.format(
    purchases.value.sum(), forecasted_value))
