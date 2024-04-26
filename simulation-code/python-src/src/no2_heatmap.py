from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd  # For easier date handling

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def read_data_slice(filepath, start_line, end_line, date_column, no2_column):
    dates = []
    no2_values = []
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            if i + 1 < start_line or i + 1 >= end_line:
                continue
            if i == 0:  # Skip header
                continue
            values = line.strip().split(',')
            try:
                dates.append(values[date_column])  # Read date
                no2_values.append(float(values[no2_column]))  # Read no2 value
            except ValueError:
                continue
    return dates, no2_values

def get_line_counts(filepath):
    with open(filepath, 'r') as file:
        return sum(1 for _ in file)
        
date_column = 0
no2_column = 19

# Adjust the file path as necessary
filepath = 'data/processed/preprocessed_for_cpp.csv'  # Update based on your setup
total_lines = get_line_counts(filepath) - 1

lines_per_process = total_lines // size
remainder = total_lines % size

start_line = rank * lines_per_process + min(rank, remainder) + 1
if rank < remainder:
    lines_per_process += 1
end_line = start_line + lines_per_process

# Read data slice for both dates and no2
dates, no2_values = read_data_slice(filepath, start_line, end_line, date_column, no2_column)

# Gather data at root
gathered_dates = comm.gather(dates, root=0)
gathered_no2 = comm.gather(no2_values, root=0)

if rank == 0:
    all_dates = [date for sublist in gathered_dates for date in sublist]
    all_no2 = [no2 for sublist in gathered_no2 for no2 in sublist]

    # Create a DataFrame and convert dates to datetime for sorting
    df = pd.DataFrame({'Date': pd.to_datetime(all_dates), 'no2': all_no2})
    df.sort_values('Date', inplace=True)

    # Pivot the DataFrame for the heatmap (assuming daily data)
    heatmap_data = df.pivot_table(index='Date', values='no2', aggfunc=np.mean)

    # Plot the heatmap
    plt.figure(figsize=(20, 8))
    plt.imshow(heatmap_data.T, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='no2 Concentration')
    plt.title('Heatmap of Daily no2 Concentrations')
    plt.xlabel('Day')
    plt.ylabel('no2')
    plt.xticks(ticks=range(len(heatmap_data)), labels=heatmap_data.index.strftime('%Y-%m-%d'), rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("data/output/no2_heatmap_figure.png")
    plt.show()

'''if rank == 0:
    all_dates = [date for sublist in gathered_dates for date in sublist]
    all_no2 = [no2 for sublist in gathered_no2 for no2 in sublist]

    # Create a DataFrame and convert dates to datetime for sorting
    df = pd.DataFrame({'Date': pd.to_datetime(all_dates), 'NO2': all_no2})
    df.sort_values('Date', inplace=True)

    # Resample and aggregate data on a monthly basis
    monthly_data = df.set_index('Date').resample('M').mean()

    # Plot the heatmap
    plt.figure(figsize=(20, 8))
    # Transpose is necessary if we have multiple columns for NO2, e.g., from different locations
    # Here, assuming a single NO2 value per date, thus, no need to transpose
    plt.imshow(monthly_data.T, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='NO2 Concentration')

    # Generate x-ticks and labels
    x_ticks = np.arange(len(monthly_data.index))
    x_labels = [date.strftime('%Y-%m') for date in monthly_data.index]

    plt.xticks(ticks=x_ticks, labels=x_labels, rotation=45, ha="right")
    plt.title('Monthly Average NO2 Concentrations')
    plt.xlabel('Month')
    plt.ylabel('NO2')
    plt.tight_layout()
    plt.savefig("data/output/no2_monthly_heatmap.png")
    plt.show()'''

'''if rank == 0:
    all_dates = [date for sublist in gathered_dates for date in sublist]
    all_no2 = [no2 for sublist in gathered_no2 for no2 in sublist]

    # Create a DataFrame and convert dates to datetime for sorting
    df = pd.DataFrame({'Date': pd.to_datetime(all_dates), 'NO2': all_no2})
    df.sort_values('Date', inplace=True)

    # Resample and aggregate data on a yearly basis
    yearly_data = df.set_index('Date').resample('Y').mean()

    # Plot the heatmap
    plt.figure(figsize=(20, 8))
    # Transpose is necessary if we have multiple columns for NO2, e.g., from different locations
    # Here, assuming a single NO2 value per date, thus, no need to transpose
    plt.imshow(yearly_data.T, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='NO2 Concentration')

    # Generate x-ticks and labels
    x_ticks = np.arange(len(yearly_data.index))
    x_labels = [date.strftime('%Y') for date in yearly_data.index]

    plt.xticks(ticks=x_ticks, labels=x_labels, rotation=45, ha="right")
    plt.title('Yearly Average NO2 Concentrations')
    plt.xlabel('Year')
    plt.ylabel('NO2')
    plt.tight_layout()
    plt.savefig("data/output/no2_yearly_heatmap.png")
    plt.show()'''



