import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, '')

def value_to_int(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return int(float(x.replace('K', '')) * 1000)
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return int(float(x.replace('M', '')) * 1000000)
        return 1000000.0
    if 'B' in x:
        return int(float(x.replace('B', '')) * 1000000000)
    return locale.atoi(x)

if __name__ == "__main__":
    data = pd.read_csv("webtoons.csv")
    data["view"] = data["view"].apply(value_to_int)
    data["subscribe"] = data["subscribe"].apply(value_to_int)
    data["likes"] = data["likes"].apply(value_to_int)
    data.to_csv("webtoons2.csv", index=False)