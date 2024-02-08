import pandas as pd

# Function to prompt the user for file paths
def get_file_path(prompt):
    path = input(prompt)
    return path

# Prompting the user for the file paths
nav_file_path = get_file_path('Enter the path to the NAV file: ')
sealog_file_path = get_file_path('Enter the path to the SeaLog file: ')
output_file_path = 'combined_data.csv'

# Read the NAV file
nav_columns = ['timestamp', 'latitude', 'longitude', 'depth']
nav_data = pd.read_csv(nav_file_path, sep='\t', names=nav_columns, parse_dates=['timestamp'])

# Read the SeaLog file
sealog_data = pd.read_csv(sealog_file_path, parse_dates=['ts'])

# Function to find the closest SeaLog entry for each NAV entry
def find_closest_sealog_entry(nav_timestamp):
    # Compute absolute difference between NAV timestamp and all SeaLog timestamps
    time_diff = sealog_data['ts'] - nav_timestamp
    # Ignore negative deltas (future SeaLog entries)
    time_diff[time_diff < pd.Timedelta(0)] = pd.Timedelta.max
    # Find the index of the minimum time difference
    min_index = time_diff.idxmin()
    if time_diff[min_index] == pd.Timedelta.max:
        # No valid SeaLog entry found, return None
        return pd.Series([None] * len(sealog_data.columns), index=sealog_data.columns)
    # Return the closest SeaLog entry
    return sealog_data.iloc[min_index]

# Apply the function to each NAV entry
closest_sealog_entries = nav_data['timestamp'].apply(find_closest_sealog_entry)

# Combine NAV data with the closest SeaLog entries
combined_data = pd.concat([nav_data, closest_sealog_entries.reset_index(drop=True)], axis=1)

# Save the combined data to a new file
combined_data.to_csv(output_file_path, index=False)

print(f"Combined data saved to {output_file_path}")
