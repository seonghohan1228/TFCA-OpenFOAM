import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import argparse
import time

# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Process centerline data.')
    parser.add_argument('case', nargs='?', default='centerline', help='Case directory name')
    return parser.parse_args()

# Function to construct directory paths
def construct_paths(case):
    if case == 'centerline':
        directory = './centerline'
        save_directory = './results'
    else:
        directory = f'./{case}/results/centerline'
        save_directory = f'./{case}/results'
    os.makedirs(save_directory, exist_ok=True)
    return directory, save_directory

# Function to load and filter data
def load_data(directory):
    files = sorted(glob.glob(os.path.join(directory, 'data0.*.csv')), key=lambda x: int(os.path.basename(x).split('.')[1]))
    data_frames = []
    for file in files:
        df = pd.read_csv(file)
        df = df[(df['Points:0'] == 0) & (df['Points:2'] == 0)]
        data_frames.append(df)
    return data_frames

# Function to track droplet sizes
def measure_breakup_length_and_droplet_size(df_sorted, max_droplet_diameter, quasi_steady):
    breakup_length = 0
    found_breakup_length = False

    droplet_sizes = []
    measuring_droplet = False
    current_droplet_start = None
    current_droplet_end = None
    current_droplet_size = 0
    water_at_outlet = True
    
    for _, row in df_sorted.iterrows():
        if not found_breakup_length:
            if 0.5 <= row['alpha.water'] <= 1:
                breakup_length = abs(row['Points:1'])
            if row['alpha.water'] < 0.5:
                found_breakup_length = True
        elif quasi_steady:
            if not measuring_droplet and row['alpha.water'] >= 0.5:
                measuring_droplet = True
                current_droplet_start = row['Points:1']
            
            if measuring_droplet and row['alpha.water'] < 0.5:
                current_droplet_end = row['Points:1']
                droplet_diameter = abs(current_droplet_end - current_droplet_start)
                if droplet_diameter <= max_droplet_diameter:
                    current_droplet_size = droplet_diameter
                measuring_droplet = False
            
            if row['Points:1'] == -0.1 and row['alpha.water'] < 0.001:
                water_at_outlet = False
                if current_droplet_size > 0 and current_droplet_size <= max_droplet_diameter:
                    droplet_sizes.append(current_droplet_size)
                    current_droplet_size = 0

    return breakup_length, droplet_sizes, water_at_outlet

# Function to plot heatmap
def plot_heatmap(heatmap_data, case, save_directory):
    plt.figure(figsize=(12, 8))
    plt.imshow(heatmap_data, aspect='auto', cmap='coolwarm', origin='lower', extent=[0, 0.5, heatmap_data.index.min(), heatmap_data.index.max()])
    plt.colorbar(label='alpha.water')
    plt.xlabel('Time (s)')
    plt.ylabel('Y Position (m)')
    plt.title(f'Heatmap of alpha.water over Time and Y Position - {case}')
    plt.savefig(os.path.join(save_directory, f'heatmap-{case}.png'))

# Function to plot breakup length over time
def plot_breakup_length(breakup_lengths, case, save_directory):
    print(f'Breakup Lengths (m): {breakup_lengths}')
    plt.figure(figsize=(10, 6))
    plt.plot(np.arange(0, 0.501, 0.001), breakup_lengths)
    plt.xlabel('Time (s)')
    plt.ylabel('Breakup Length (Y Position) (m)')
    plt.title(f'Breakup Length over Time - {case}')
    plt.grid(True)
    plt.savefig(os.path.join(save_directory, f'breakup_length-{case}.png'))

# Function to plot droplet size distribution
def plot_droplet_size_distribution(droplet_sizes, case, save_directory):
    print(f'Droplet Sizes (m): {droplet_sizes}')
    plt.figure(figsize=(10, 6))
    plt.hist(droplet_sizes, bins=np.arange(0, 0.005, 0.0001))
    plt.xlabel('Droplet Diameter (m)')
    plt.ylabel('Frequency')
    plt.title(f'Droplet Size Distribution - {case}')
    plt.grid(True)
    axes = plt.gca()
    axes.set_ylim([0,35])
    plt.savefig(os.path.join(save_directory, f'droplet_size_distribution-{case}.png'))

# Main function
def main():
    args = parse_arguments()
    directory, save_directory = construct_paths(args.case)
    data_frames = load_data(directory)

    breakup_lengths = []
    all_droplet_sizes = []
    searching_droplet = True
    quasi_steady = False

    max_droplet_diameter = 0.005  # d where d = 5 mm

    for idx, df in enumerate(data_frames):
        print(f'Reading file #{idx:4d}')
        df['time'] = idx * 0.001  # Add time column
        df = df[['Points:1', 'alpha.water', 'time']]  # Keep only Points:1 (y-axis), alpha.water, and time
        df_sorted = df.sort_values(by='Points:1', ascending=False)

        if idx > 200:
            quasi_steady = True
        
        breakup_length, droplet_sizes, water_at_outlet = measure_breakup_length_and_droplet_size(df_sorted, max_droplet_diameter, quasi_steady)
        breakup_lengths.append(breakup_length)
        if droplet_sizes != [] and searching_droplet:
            all_droplet_sizes.extend(droplet_sizes)
            searching_droplet = False
        
        if water_at_outlet:
            searching_droplet = True

    combined_df = pd.concat(data_frames, ignore_index=True)

    combined_df = combined_df.groupby(['Points:1', 'time'], as_index=False).mean()

    heatmap_data = combined_df.pivot(index='Points:1', columns='time', values='alpha.water')

    heatmap_data = heatmap_data.fillna(0)  # Fill NaNs with 0 or use another method

    print()
    print("Plotting...")

    plot_heatmap(heatmap_data, args.case, save_directory)
    plot_breakup_length(breakup_lengths, args.case, save_directory)
    plot_droplet_size_distribution(all_droplet_sizes, args.case, save_directory)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print()
    print(f'Took {(time.time() - start_time):.2f} s')
