import json
import pandas as pd
from math import inf
from statsmodels.tsa.ar_model import AutoReg


def forecast(handler, message):
    # A US manufacturer buys raw materials in multiple currencies
    purchases = pd.read_excel('Purchases.xlsx')
    purchases.sort_values('value', ascending=False, inplace=True)
    purchases['forecast'] = purchases['value']

    # For each of those currencies, find the best model to forecast prices
    best_model = {}
    for i, (index, row) in enumerate(purchases.iterrows()):
        data = pd.read_excel(f'{row.currency}.xlsx')
        data = data[data[row.currency] > 0]
        best_aic, best_fit = inf, None
        # for lags in (3, 5, 7, 10, 14, 28, 60, 90, 120, 183, 365, 730, 1095):
        for lags in (3, 5, 7, 10, 14):
            model = AutoReg(data[row.currency], lags=lags)
            fit = model.fit()
            if fit.aic < best_aic:
                best_aic, best_fit = fit.aic, fit
        prices = best_fit.predict(best_fit.model.nobs, best_fit.model.nobs + 30)
        change = prices.iloc[-1] / prices.iloc[0]
        row.loc['forecast'] = purchases.loc[index, 'forecast'] = row.value * change
        data = row.to_dict()
        data.update(
          progress=(i + 1) / len(purchases),
          total_value=float(purchases.value.sum()),
          total_forecast=float(purchases.forecast.sum()),
        )
        handler.write_message(data)
