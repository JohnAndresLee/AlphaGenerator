import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load factor data and target returns
def load_data(factor_file, returns_file):
    factor_df = pd.read_csv(factor_file)
    returns_df = pd.read_csv(returns_file)
    factor_df.columns = ['datetime','instrument','factor']
    factor_df['datetime'] = pd.to_datetime(factor_df['datetime'])
    factor_df['target'] = returns_df['target']
    return factor_df

# Calculate daily IC
def calc_daily_ic(df):
    grouped = df.groupby(df['datetime'].dt.date)
    # Calculate correlation for each day
    daily_corr = grouped.apply(lambda x: x['factor'].corr(x['target']))
    return daily_corr

# Calculate cumulative IC over time
def calc_cumulative_ic(ic_series):
    return ic_series.cumsum()

def backtest_return(df):
    df['datetime'] = pd.to_datetime(df['datetime'])

    def calculate_quantile_returns(df):
        # Group by date
        grouped = df.groupby(df['datetime'].dt.date)

        def calc_quantile_returns(group):
            group['quantile'] = pd.qcut(group['factor'], 5, labels=False) + 1
            # Calculate the mean target return for each quantile
            return group.groupby('quantile')['target'].mean()

        quantile_returns = grouped.apply(calc_quantile_returns)
        return quantile_returns

    daily_quantile_returns = calculate_quantile_returns(df)

    return daily_quantile_returns

def plot_results(ic_daily, cumulative_ic):
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 2, 1)
    plt.plot(ic_daily, label='Daily IC')
    plt.title('Daily IC')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(cumulative_ic, label='Cumulative IC', color='orange')
    plt.title('Cumulative IC')
    plt.legend()

    plt.tight_layout()
    plt.show()
    
# Main function to execute the analysis
def main():
    factor_file = './output_alpha/Corr($open,$low,30).csv'
    # factor_file = './rl_factors/Mul(Greater(Constant(10.0),Mad(Min(Max($close,10),20),10)),$volume).csv'
    returns_file = './target_data/target.csv'

    df = load_data(factor_file, returns_file)

    # Calculate daily and cumulative IC
    ic_daily = calc_daily_ic(df)
    cumulative_ic = calc_cumulative_ic(ic_daily)

    # Plot results
    plot_results(ic_daily, cumulative_ic)
    
    backtest = backtest_return(df)
    plt.plot((backtest+1).cumprod(axis=0))
    plt.title('Cumulative Returns in Group')
    plt.show()
    print(backtest)
    
if __name__ == "__main__":
    main()