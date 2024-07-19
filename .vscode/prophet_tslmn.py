# -*- coding: utf-8 -*-
"""Prophet TSLMN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1P3dKc7iVwWpHLt6fdsmlS8jIriQO3ObS
"""

import pandas as pd
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets


# Load the data
data_path = 'Data\LymanDataForPred.csv'
data = pd.read_csv(data_path)
data['Date'] = pd.to_datetime(data['Date'])

# Fill missing ' ItemSold' and sort the data
data['ItemSold'] = data.groupby('Category Size')['ItemSold'].transform(lambda x: x.fillna(x.mean()))
data_sorted = data.sort_values(by=['Category Size', 'Date'])

# Resample to monthly data and interpolate missing values
data_monthly = data_sorted.groupby('Category Size').resample('M', on='Date')['ItemSold'].median().reset_index()
data_monthly['ItemSold'] = data_monthly.groupby('Category Size')['ItemSold'].transform(lambda x: x.interpolate())

# Forecast using Prophet for each Category Size and calculate accuracy
forecasts = pd.DataFrame()

# Forecast using Prophet for each Category Size
for CategorySize, group in data_monthly.groupby('Category Size'):
    if group['ItemSold'].notnull().sum() < 2:
        print(f"Skipping {CategorySize} due to insufficient data.")
        continue  # Skip to the next iteration

    # Prepare the data for Prophet
    df_prophet = pd.DataFrame({
        'ds': group['Date'],
        'y': group['ItemSold']
    })

    # Create and fit the Prophet model
    model = Prophet(yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False)
    model.fit(df_prophet)

    # Make a future dataframe for April to September 2024
    future = pd.date_range(start='2024-06-01', end='2024-08-01', freq='M')
    future = pd.DataFrame({'ds': future})

    # Forecast
    forecast = model.predict(future)

    # Add Category Size column to forecast dataframe
    forecast['Category Size'] = CategorySize

    # Append the results
    forecasts = pd.concat([forecasts, forecast], axis=0)


# Print forecasts
print(forecasts[['Category Size', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']])



# Print forecasts
OutForecast=(forecasts[['Category Size', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']])
OutForecast.to_csv('Data\ProphetForecastLymanCI.csv', index=False)
print(OutForecast)

# Create an empty list to store the forecast data
forecast_output = []

# Iterate through each group of forecasts
for CategorySize, group in forecasts.groupby('Category Size'):
    # Iterate through each row in the group
    for index, row in group.iterrows():
        # Calculate the accuracy
        accuracy = row['yhat_upper'] - row['yhat_lower']
        #Calculate Accuraacy Score
        # Calculate the accuracy score as a percentage
        accuracy_score = (accuracy / row['yhat']) * 100
        # Format accuracy score as percentage string
        accuracy_score_str = "{:.2f}%".format(accuracy_score)
        # Append the forecast data to the list
        forecast_output.append({
            'Category Size': CategorySize,
            'Date': row['ds'].strftime('%Y-%m-%d'),
            'Forecast': row['yhat'],
            'Lower': row['yhat_upper'],
            'Upper': row['yhat_lower'],
            'Confidence Interval': accuracy,
            'Accuracy Score': accuracy_score_str
        })

# Convert the list of dictionaries to a DataFrame
forecast_df = pd.DataFrame(forecast_output)

print(forecast_df)
Data=forecast_df
# Save the DataFrame to a CSV file
forecast_df.to_csv('Data\ProphetForecastLymanCI.csv', index=False)




# Create a DataFrame
df = pd.DataFrame(Data)

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Function to plot forecast for a selected category size
def plot_forecast(category_size):
    # Filter the DataFrame for the selected category size
    filtered_df = df[df['Category Size'] == category_size]

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_df['Date'], filtered_df['Forecast'], marker='o', linestyle='-')
    plt.title(f'Forecast for {category_size}')
    plt.xlabel('Date')
    plt.ylabel('Forecast')
    plt.grid(True)
    plt.show()

# Example usage
#plot_forecast('A-MN_.3125X96X288')

# Create a dropdown widget
category_dropdown = widgets.Dropdown(
    options=df['Category Size'].unique(),
    description='Category Size:'
)

# Use interact to create the interactive plot
interact(plot_forecast, category_size=category_dropdown)