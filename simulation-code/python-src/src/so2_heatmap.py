from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd  # For easier date handling

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def read_data_slice(filepath, start_line, end_line, date_column, so2_column):
    dates = []
    so2_values = []
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            if i + 1 < start_line or i + 1 >= end_line:
                continue
            if i == 0:  # Skip header
                continue
            values = line.strip().split(',')
            try:
                dates.append(values[date_column])  # Read date
                so2_values.append(float(values[so2_column]))  # Read so2 value
            except ValueError:
                continue
    return dates, so2_values

def get_line_counts(filepath):
    with open(filepath, 'r') as file:
        return sum(1 for _ in file)
        
date_column = 0
so2_column = 22

# Adjust the file path as necessary
filepath = 'data/processed/preprocessed_for_cpp.csv'  # Update based on your setup
total_lines = get_line_counts(filepath) - 1

lines_per_process = total_lines // size
remainder = total_lines % size

start_line = rank * lines_per_process + min(rank, remainder) + 1
if rank < remainder:
    lines_per_process += 1
end_line = start_line + lines_per_process

# Read data slice for both dates and so2
dates, so2_values = read_data_slice(filepath, start_line, end_line, date_column, so2_column)

# Gather data at root
gathered_dates = comm.gather(dates, root=0)
gathered_so2 = comm.gather(so2_values, root=0)

if rank == 0:
    all_dates = [date for sublist in gathered_dates for date in sublist]
    all_so2 = [so2 for sublist in gathered_so2 for so2 in sublist]

    # Create a DataFrame and convert dates to datetime for sorting
    df = pd.DataFrame({'Date': pd.to_datetime(all_dates), 'so2': all_so2})
    df.sort_values('Date', inplace=True)

    # Pivot the DataFrame for the heatmap (assuming daily data)
    heatmap_data = df.pivot_table(index='Date', values='so2', aggfunc=np.mean)

    # Plot the heatmap
    plt.figure(figsize=(20, 8))
    plt.imshow(heatmap_data.T, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='SO2 Concentration')
    plt.title('Heatmap of Daily SO2 Concentrations')
    plt.xlabel('Day')
    plt.ylabel('so2')
    plt.xticks(ticks=range(len(heatmap_data)), labels=heatmap_data.index.strftime('%Y-%m-%d'), rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("data/output/SO2_heatmap_figure.png")
    plt.show()
