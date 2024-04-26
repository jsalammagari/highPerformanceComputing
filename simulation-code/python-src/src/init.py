import pandas as pd

def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    # Step 1: Clean `DAILY_AQI_VALUE`
    # Convert DAILY_AQI_VALUE to numeric, setting errors='coerce' to turn non-convertible values into NaNs
    data['DAILY_AQI_VALUE'] = pd.to_numeric(data['DAILY_AQI_VALUE'], errors='coerce')

    # Step 2: Handle Missing Data for Key Pollutants
    # For simplicity in this ETL phase, fill missing values with the median of each column
    # This is a simplistic approach, more sophisticated methods might be needed for accurate simulations
    pollutant_columns = [
        'Daily Mean PM10 Concentration',
        'Daily Mean PM2.5 Concentration',
        'Daily Max 8-hour Ozone Concentration',
        'Daily Max 1-hour NO2 Concentration',
        'Daily Max 8-hour CO Concentration',
        'Daily Mean Pb Concentration',
        'Daily Max 1-hour SO2 Concentration'
        ]

    for col in pollutant_columns:
        data[col].fillna(data[col].median(), inplace=True)
    
    data.drop(columns=['Site Name', 'CBSA_CODE', 'CBSA_NAME'], inplace=True)   
    
    data.head()
    data.info()
        
    return data

def main():
    input_path = 'data/raw/combined_file_final.csv'
    processed_data = load_and_preprocess_data(input_path)
    
    # Save the preprocessed data to a file that will be read by the C++ simulation
    output_path = 'data/processed/preprocessed_for_cpp.csv'
    processed_data.to_csv(output_path, index=False)
    
    print("Data preprocessing complete. Ready for C++ simulation.")

if __name__ == "__main__":
    main()
