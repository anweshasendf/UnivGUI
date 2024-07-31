import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_prominences, savgol_filter
import pandas as pd
import os
from nptdms import TdmsFile
import mplcursors
from scipy.interpolate import interp1d
import pandas as pd
from sklearn.linear_model import LinearRegression
import math
import re
from scipy.interpolate import griddata
from scipy.interpolate import RegularGridInterpolator
import sys 

def read_tdms(filepath):
    tdms_file = TdmsFile.read(filepath)
    df = tdms_file.as_dataframe()

    # Remove columns that only contain NaN values
    df = df.dropna(axis=1, how='all')

    # Clean up column names
    df.columns = df.columns.str.replace("/", "")
    df.columns = df.columns.str.replace("'", "")
    df.columns = df.columns.str.replace("Data", "")
    df.columns = df.columns.str.strip()
    return df


def extract_UDSP(filepath):
    """
    Extract Unit, Degree, RPM, and Pressure from a given filepath.

    Parameters:
    filepath (str): The file path to extract information from.

    Returns:
    dict: A dictionary containing extracted information.
    """
    # Normalize the file path to work with both Windows and Unix-style paths
    filepath = filepath.replace('\\', '/')

    # Regular expressions to capture the required information
    unit_pattern = re.compile(r'Unit\s*\d+', re.IGNORECASE)
    degree_pattern = re.compile(r'-?\d+(?:\.\d+)?deg', re.IGNORECASE)
    rpm_pattern = re.compile(r'(\d+)\s*rpm', re.IGNORECASE)
    pressure_pattern = re.compile(r'(\d+)\s*bar', re.IGNORECASE)

    # Extract information based on patterns
    unit = re.search(unit_pattern, filepath)
    degree = re.search(degree_pattern, filepath)
    rpm = re.search(rpm_pattern, filepath)
    pressure = re.search(pressure_pattern, filepath)

    # Dictionary to hold the results
    extracted_info = {
        "Unit": unit.group(0) if unit else None,
        "Degree": degree.group(0) if degree else None,
        "RPM": rpm.group(1) if rpm else None,
        "Pressure": pressure.group(1) if pressure else None
    }

    return extracted_info


def hst_efficiency_calculate(input_dir):
    all_df = pd.DataFrame()
    # Walk through the directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if not file.endswith(".tdms"):
                continue

            file_path = os.path.join(root, file)

            # Extract metadata using the extract_UDSP function
            info = extract_UDSP(file_path)
            if None in info.values():
                print(f"Skipping {file_path}: Missing key info.")
                continue

            try:
                # Read the .tdms file using nptdms
                with TdmsFile.open(file_path) as tdms_file:
                    print(f"Processing {file_path}")
                    df = tdms_file.as_dataframe()
                    df = df.dropna(axis=1, how='all')
                    df.columns = df.columns.str.replace("/", "")
                    df.columns = df.columns.str.replace("'", "")
                    df.columns = df.columns.str.replace("Data", "")
                    df.columns = df.columns.str.strip()
                    df['Speed Ratio'] = df['Input speed'] / df['Output RPM']
                    swash_angle_mean = df['Swashplate angle'].mean()
                    if swash_angle_mean > 0:
                        df['Efficiency'] = (
                                (df['Output RPM'] * df['Output motor shaft torque_Nm']) /
                                (df['Input speed'] * df['Input shaft torque_Nm'])
                        )
                    else:
                        df['Efficiency'] = (
                                (df['Input speed'] * df['Input shaft torque_Nm']) /
                                (df['Output RPM'] * df['Output motor shaft torque_Nm'])
                        )

                    new_row = {
                        'File': file_path,
                        'Speed': info['RPM'],
                        'Pressure': info['Pressure'],
                        'Unit': info['Unit'],
                        'Angle': info['Degree'],
                        'Mean_Temp': df['Inlet_C'].mean(),
                        'Mean_input_shaft_speed': df['Input speed'].mean(),
                        'Mean_output_shaft_tq': abs(df['Output motor shaft torque_Nm'].mean()),
                        'Mean_delta_P': abs(df['Delta_P_Bar'].mean()),
                        'Overall Efficiency': abs(df['Efficiency'].mean()),
                        'Speed Ratio': abs(df['Speed Ratio'].mean())
                    }

                    # Convert the dictionary to a DataFrame
                    new_row_df = pd.DataFrame([new_row])

                    # Append the new DataFrame row to all_df
                    all_df = all_df._append(new_row_df, ignore_index=True)
                    

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    results_path = os.path.join(input_dir, "results", "results.csv")
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    all_df.to_csv(results_path, index=False)
    return all_df, results_path



def plot_contours(temp_df, output_dir):
    plot_paths = []
    grouped = temp_df.groupby(['Unit', 'Angle'])

    for (unit, angle), df_filtered in grouped:
        if df_filtered.empty:
            continue

        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Contour Plots for Unit: {unit} and Angle: {angle}', fontsize=16)

        # Define the number of contour levels
        num_contours = 20

        # Create a grid for interpolation
        xi = np.linspace(df_filtered['Mean_output_shaft_tq'].min(), df_filtered['Mean_output_shaft_tq'].max(), 100)
        yi = np.linspace(df_filtered['Mean_input_shaft_speed'].min(), df_filtered['Mean_input_shaft_speed'].max(), 100)
        X, Y = np.meshgrid(xi, yi)

        # Input shaft speed vs Output torque (Overall Efficiency)
        Z1 = griddata((df_filtered['Mean_output_shaft_tq'], df_filtered['Mean_input_shaft_speed']), df_filtered['Overall Efficiency'], (X, Y), method='linear')
        cs1 = axs[0, 0].contour(X, Y, Z1, levels=num_contours, cmap='viridis')
        fig.colorbar(cs1, ax=axs[0, 0])
        axs[0, 0].set_title('Output Torque vs Input Shaft Speed (Overall Efficiency)')
        axs[0, 0].set_xlabel('Mean Output Shaft Torque')
        axs[0, 0].set_ylabel('Mean Input Shaft Speed')
        axs[0, 0].clabel(cs1, inline=True, fontsize=8)

        # Input shaft speed vs Output torque (Speed Ratio)
        Z2 = griddata((df_filtered['Mean_output_shaft_tq'], df_filtered['Mean_input_shaft_speed']), df_filtered['Speed Ratio'], (X, Y), method='linear')
        cs2 = axs[0, 1].contour(X, Y, Z2, levels=num_contours, cmap='viridis')
        fig.colorbar(cs2, ax=axs[0, 1])
        axs[0, 1].set_title('Output Torque vs Input Shaft Speed (Speed Ratio)')
        axs[0, 1].set_xlabel('Mean Output Shaft Torque')
        axs[0, 1].set_ylabel('Mean Input Shaft Speed')
        axs[0, 1].clabel(cs2, inline=True, fontsize=8)

        # Create a grid for interpolation for Delta P
        xi = np.linspace(df_filtered['Mean_delta_P'].min(), df_filtered['Mean_delta_P'].max(), 100)
        X, Y = np.meshgrid(xi, yi)

        # Input shaft speed vs Delta P (Overall Efficiency)
        Z3 = griddata((df_filtered['Mean_delta_P'], df_filtered['Mean_input_shaft_speed']), df_filtered['Overall Efficiency'], (X, Y), method='linear')
        cs3 = axs[1, 0].contour(X, Y, Z3, levels=num_contours, cmap='viridis')
        fig.colorbar(cs3, ax=axs[1, 0])
        axs[1, 0].set_title('Delta P vs Input Shaft Speed (Overall Efficiency)')
        axs[1, 0].set_xlabel('Mean Delta P')
        axs[1, 0].set_ylabel('Mean Input Shaft Speed')
        axs[1, 0].clabel(cs3, inline=True, fontsize=8)

        # Input shaft speed vs Delta P (Speed Ratio)
        Z4 = griddata((df_filtered['Mean_delta_P'], df_filtered['Mean_input_shaft_speed']), df_filtered['Speed Ratio'], (X, Y), method='linear')
        cs4 = axs[1, 1].contour(X, Y, Z4, levels=num_contours, cmap='viridis')
        fig.colorbar(cs4, ax=axs[1, 1])
        axs[1, 1].set_title('Delta P vs Input Shaft Speed (Speed Ratio)')
        axs[1, 1].set_xlabel('Mean Delta P')
        axs[1, 1].set_ylabel('Mean Input Shaft Speed')
        axs[1, 1].clabel(cs4, inline=True, fontsize=8)
    
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plot_path = os.path.join(output_dir, f"plot_{unit}_{angle}.png")
        plt.savefig(plot_path)
        plot_paths.append(plot_path)
        plt.close(fig)
        
    return plot_paths

def main(input_directory):
    all_df, results_path = hst_efficiency_calculate(input_directory)
    output_dir = os.path.join(input_directory, "results")
    os.makedirs(output_dir, exist_ok=True)
    results_dir = os.path.join(input_directory, "results")
    os.makedirs(results_dir, exist_ok=True)

    plot_paths = plot_contours(all_df, output_dir)
    #return results_path, plot_paths
    return {"results_path": results_path, "all_df": all_df}, plot_paths

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hst_eff_new.py <input_directory>")
        sys.exit(1)
    input_directory = sys.argv[1]
    results_path, plot_paths = main(input_directory)
    print(f"Results saved to: {results_path}")
    print(f"Plots saved to: {', '.join(plot_paths)}")