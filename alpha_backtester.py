# alpha_backtester.py

"""
This script backtests each unique alpha factor and evaluates their performance.
It plots a heatmap of the performance metrics for each alpha.
"""

import os
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

def backtest_alpha(alpha_series, price_series):
    """
    Simple backtest of an alpha factor.
    Assumes that the alpha signals are used to take positions in the next period.
    """
    # Generate signals (-1, 0, 1)
    signals = np.sign(alpha_series)
    # Calculate returns
    returns = price_series.pct_change().shift(-1)  # Shift returns to align with signals
    # Calculate strategy returns
    strategy_returns = signals * returns
    # Calculate cumulative returns
    cumulative_returns = (1 + strategy_returns).cumprod()
    # Performance metrics
    total_return = cumulative_returns.iloc[-1] - 1
    sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
    max_drawdown = (cumulative_returns.cummax() - cumulative_returns).max()
    return {
        'Total Return': total_return,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown,
        'Cumulative Returns': cumulative_returns
    }

def load_price_data(price_file):
    price_df = pd.read_csv(price_file, index_col=0, parse_dates=True)
    return price_df['Close']

def main():
    parser = argparse.ArgumentParser(description='Backtest unique alpha factors.')
    parser.add_argument('--alpha_folder', type=str, default='output_alpha', help='Folder containing unique alpha CSV files.')
    parser.add_argument('--price_file', type=str, default='price_data.csv', help='CSV file containing historical price data.')
    args = parser.parse_args()
    
    alpha_folder = args.alpha_folder
    price_file = args.price_file
    
    # Load price data
    print("Loading price data...")
    price_series = load_price_data(price_file)
    print("Price data loaded.")
    
    # Load unique alphas
    alpha_files = [f for f in os.listdir(alpha_folder) if f.endswith('.csv')]
    performance_metrics = {}
    
    print("Backtesting alphas...")
    for alpha_file in alpha_files:
        alpha_name = os.path.splitext(alpha_file)[0]
        alpha_df = pd.read_csv(os.path.join(alpha_folder, alpha_file), index_col=0, parse_dates=True)
        alpha_series = alpha_df['alpha']
        # Align alpha and price data
        common_index = alpha_series.index.intersection(price_series.index)
        alpha_series = alpha_series.loc[common_index]
        price_series_aligned = price_series.loc[common_index]
        # Backtest alpha
        metrics = backtest_alpha(alpha_series, price_series_aligned)
        performance_metrics[alpha_name] = metrics
        # Plot cumulative returns
        plt.figure()
        metrics['Cumulative Returns'].plot()
        plt.title(f'Cumulative Returns - {alpha_name}')
        plt.savefig(f'cumulative_returns_{alpha_name}.png')
        plt.close()
    
    # Create a DataFrame of performance metrics
    metrics_df = pd.DataFrame(performance_metrics).T
    # Save metrics to CSV
    metrics_df.to_csv('alpha_performance_metrics.csv')
    
    # Plot heatmap of performance metrics
    plt.figure(figsize=(10, 8))
    sns.heatmap(metrics_df[['Total Return', 'Sharpe Ratio', 'Max Drawdown']], annot=True, cmap='viridis')
    plt.title('Alpha Performance Metrics')
    plt.savefig('alpha_performance_heatmap.png')
    plt.close()
    
    print("Backtesting completed. Performance metrics saved and heatmap generated.")

if __name__ == "__main__":
    main()