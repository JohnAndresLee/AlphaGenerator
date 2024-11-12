import os
import pandas as pd
import numpy as np
import argparse
import shutil
import seaborn as sns
import matplotlib.pyplot as plt

def load_alphas(alpha_folder):
    alpha_files = [f for f in os.listdir(alpha_folder) if f.endswith('.csv')]
    alphas = {}
    for file in alpha_files:
        alpha_name = os.path.splitext(file)[0]
        df = pd.read_csv(os.path.join(alpha_folder, file))
        alphas[alpha_name] = df[alpha_name]
    return pd.DataFrame(alphas)

def rank_alphas(alphas_df, label_folder='./target_data/'):
    ic_dict = {}
    target_df = pd.read_csv(label_folder+'target.csv')
    for factor in alphas_df.columns:
        r = alphas_df[factor].corr(target_df['target'])
        if pd.notna(r) and abs(r)>0.01:
            ic_dict[factor] = r
    ic_dict = dict(sorted(ic_dict.items(), key=lambda item: abs(item[1]), reverse=True))
    alphas_df = alphas_df[ic_dict.keys()]
    return alphas_df, ic_dict

def cal_corr(alphas_df, correlation_threshold=0.9):
    # Calculate the correlation matrix
    corr_matrix = alphas_df.corr()
    # Plot the correlation matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Alpha Correlation Matrix')
    plt.savefig('alpha_correlation_matrix.png')
    plt.close()
    
    # Identify highly correlated pairs
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = []
    for column in upper_tri.columns:
        if any(upper_tri[column].abs() > correlation_threshold):
            to_drop.append(column)
    
    # Filter out redundant alphas
    unique_alphas_df = alphas_df.drop(columns=to_drop)
    return unique_alphas_df, to_drop

def save_unique_alphas(unique_alphas_df, original_alpha_folder, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)
    for alpha_name in unique_alphas_df.columns:
        alpha_file = f"{alpha_name}.csv"
        source_file = os.path.join(original_alpha_folder, alpha_file)
        destination_file = os.path.join(output_folder, alpha_file)
        shutil.copyfile(source_file, destination_file)
        
def main():
    alpha_folder = './factors/'
    output_folder = './output_alpha/'
    correlation_threshold = 0.9
    
    # Load alphas
    print("Loading alphas...")
    alphas_df = load_alphas(alpha_folder)
    print(f"Loaded {len(alphas_df.columns)} alphas.")
    
    # Rank and filter alphas
    print("Ranking alphas and filtering highly correlated ones...")
    alphas_df, ic_dict = rank_alphas(alphas_df)
    print(list(ic_dict)[:20])
    unique_alphas_df, dropped_alphas = cal_corr(alphas_df, correlation_threshold)
    print(f"Retained {len(unique_alphas_df.columns)} unique alphas.")
    print(f"Dropped alphas due to high correlation: {dropped_alphas}")
    
    # Save unique alphas
    print(f"Saving unique alphas to {output_folder}...")
    save_unique_alphas(unique_alphas_df, alpha_folder, output_folder)
    print("Unique alphas saved.")

if __name__ == "__main__":
    main()