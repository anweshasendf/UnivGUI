import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nptdms import TdmsFile
from scipy import signal
from scipy.stats import mode
import pandas as pd
import matplotlib.pyplot as plt
from nptdms import TdmsFile
from scipy import signal
from scipy.stats import mode
from scipy.stats import mode
import sys
import json
import logging

def process_tdms_file(file_path):
    tdms_file = TdmsFile.read(file_path)
    data = {group.name: group.as_dataframe() for group in tdms_file.groups()}
    
    # Assuming the data is in the 'Data' group
    df = data['Data']
    
    # Rename columns to match the MATLAB script
    column_mapping = {
        'Time_ms': 'time',
        'RPM': 'speed',
        'Inlet_Temp_F': 'inletTemp',
        'Inlet_PSI': 'inletPressure',
        'Outlet_Pressure_Psi': 'outletPressure',
        'Load-sense_pressure_Psi': 'loadSensePressure',
        'Delta P': 'deltaP',
        'Pump_Torque_In.lbf': 'pumpTorque',
        'Pump_Case_Pressure_PSI': 'casePressure',
        'Main_Flow_GPM': 'mainFlow',
        'Pump_Case Flow_gpm': 'caseFlow',
        'Pump_Case_Temp_F': 'caseTemp',
        'Control_Pressure_PSI': 'controlPressure',
        'Swash Angle_Deg': 'swashAngle',
        '%VE': 'volumetricEfficiency',
        '%ME': 'mechanicalEfficiency',
        '%OVE': 'overallEfficiency'
    }
    df = df.rename(columns=column_mapping)
    
    # Convert time to seconds
    df['time'] = df['time'] / 1000
    
    return df

def analyze_speed_sweep(df, file_name, test_request, test_date):
    # Calculate basic statistics
    temperature = 120 if 100 <= df['inletTemp'].mean() <= 130 else 180
    
    # Filtering
    fs = 1 / (df['time'].iloc[1] - df['time'].iloc[0])  # Sampling frequency
    cutoff = 10  # Cutoff frequency
    order = 8  # Filter order
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    
    outlet_pressure_filtered = signal.filtfilt(b, a, df['outletPressure'])
    swash_angle_filtered = signal.filtfilt(b, a, df['swashAngle'])
    
    # Create plots
    plt.figure(figsize=(12, 8))
    plt.plot(df['time'], df['speed'])
    plt.title(f"Pump Speed Sweep:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}")
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (RPM)")
    plt.savefig(f"{file_name}_speed_sweep.png", dpi=300)
    plt.close()
    
    # Speed sweep plot with stability analysis
    plt.figure(figsize=(12, 8))
    
    # Plot speed vs time
    plt.plot(df['time'], df['speed'])
    
    # Find the peak speed and its index
    peak_speed_index = df['speed'].idxmax()
    peak_speed_time = df['time'][peak_speed_index]
    peak_speed = df['speed'][peak_speed_index]
    
    # Calculate the percentage of data points before the peak
    total_points = len(df)
    points_before_peak = peak_speed_index + 1  # +1 because index starts at 0
    percentage_before_peak = (points_before_peak / total_points) * 100
    
    # Check for instability
    instability_threshold = 10  # Percentage deviation from 50% to be considered unstable
    if abs(percentage_before_peak - 50) > instability_threshold:
        instability_message = f"Instability detected at {peak_speed_time:.2f}s"
        plt.text(0.05, 0.95, instability_message, transform=plt.gca().transAxes, 
                 color='red', fontweight='bold', verticalalignment='top')
    
    # Add stability info to the plot
    stability_info = f"Data distribution: {percentage_before_peak:.1f}% before peak, {100-percentage_before_peak:.1f}% after peak"
    plt.text(0.05, 0.90, stability_info, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top')
    
    # Highlight the peak point
    plt.plot(peak_speed_time, peak_speed, 'ro', markersize=10, label='Peak Speed')
    
    plt.title(f"Pump Speed Sweep:\nTemperature: 180°F, Test Request: {test_request}, Date: {test_date}")
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (RPM)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f"{file_name}_speed_sweep_with_stability.png", dpi=300)
    plt.close()

    # Pressure vs Speed plot
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df['outletPressure'], df['speed'], label='Outlet pressure')
    plt.xlabel("Outlet pressure (Psi)")
    plt.ylabel("Shaft speed (RPM)")
    plt.legend()
    plt.title(f"Pump Speed Sweep:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}")
    
    plt.subplot(2, 1, 2)
    plt.plot(df['controlPressure'], df['speed'], label='Control pressure')
    plt.xlabel("Control pressure (Psi)")
    plt.ylabel("Shaft speed (RPM)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{file_name}_pressure_vs_speed.png", dpi=300)
    plt.close()

    # Histograms
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.hist(df['controlPressure'], bins=30)
    plt.xlabel("Control pressure (Psi)")
    plt.title(f"Control pressure histogram:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}")
    
    plt.subplot(1, 2, 2)
    plt.hist(df['outletPressure'], bins=30)
    plt.xlabel("Outlet pressure (Psi)")
    plt.title(f"Outlet pressure histogram:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}")
    plt.tight_layout()
    plt.savefig(f"{file_name}_pressure_histograms.png", dpi=300)
    plt.close()

    # Time-based trace
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['swashAngle'], label='Swash angle (°)')
    plt.plot(df['time'], df['caseFlow'], label='Case flow (gpm)')
    plt.plot(df['time'], df['speed']/1000, label='Shaft speed (RPM)/1000')
    plt.plot(df['time'], df['outletPressure']/1000, label='Outlet Pressure (Psi)/1000')
    plt.xlabel("Time (s)")
    plt.ylabel("Pressure (psi), Speed (RPM), angle (°)")
    plt.legend()
    plt.title(f"Time based trace:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}")
    plt.savefig(f"{file_name}_time_trace.png", dpi=300)
    plt.close()

    # Power Spectral Density
    f, Pxx_den = signal.welch(df['outletPressure'], fs, nperseg=1024)
    plt.figure(figsize=(12, 6))
    plt.semilogy(f, Pxx_den)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.title(f'Outlet Pressure Power Spectral Density:\nTemperature: {temperature}°F, Test Request: {test_request}, Date: {test_date}')
    plt.savefig(f"{file_name}_outlet_pressure_psd.png", dpi=300)
    plt.close()
    
    
    peak_speed_index = df['speed'].idxmax()

    # Pressure vs Speed plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
    
    # Outlet Pressure vs Speed
    ax1.plot(df.loc[:peak_speed_index, 'outletPressure'], df.loc[:peak_speed_index, 'speed'], 
             color='blue', label='Speed increasing')
    ax1.plot(df.loc[peak_speed_index:, 'outletPressure'], df.loc[peak_speed_index:, 'speed'], 
             color='red', label='Speed decreasing')
    ax1.set_xlabel("Outlet pressure (Psi)")
    ax1.set_ylabel("Shaft speed (RPM)")
    ax1.legend()
    ax1.set_title(f"Pump Speed Sweep:\nTemperature: 180°F, Test Request: {test_request}, Date: {test_date}")
    
    # Control Pressure vs Speed
    ax2.plot(df.loc[:peak_speed_index, 'controlPressure'], df.loc[:peak_speed_index, 'speed'], 
             color='blue', label='Speed increasing')
    ax2.plot(df.loc[peak_speed_index:, 'controlPressure'], df.loc[peak_speed_index:, 'speed'], 
             color='red', label='Speed decreasing')
    ax2.set_xlabel("Control pressure (Psi)")
    ax2.set_ylabel("Shaft speed (RPM)")
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f"{file_name}_pressure_vs_speed_with_direction.png", dpi=300)
    plt.close()
    
    

    # Spectral analysis for Swash Angle and Outlet Pressure
    fig = plt.figure(figsize=(16, 20))

    # Swash Angle Spectral Analysis
    ax1 = fig.add_subplot(211, projection='3d')
    f_swash, t_swash, Sxx_swash = signal.spectrogram(df['swashAngle'], fs, nperseg=1024)
    T_swash, F_swash = np.meshgrid(t_swash, f_swash)
    surf1 = ax1.plot_surface(T_swash, F_swash, 10 * np.log10(Sxx_swash), cmap='viridis')
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Frequency [Hz]')
    ax1.set_zlabel('PSD [dB/Hz]')
    ax1.set_title(f'Swash Angle Power Spectral Density:\nTemperature: 180°F, Test Request: {test_request}, Date: {test_date}')
    fig.colorbar(surf1, ax=ax1, label='PSD [dB/Hz]', shrink=0.5, aspect=10)

    # Outlet Pressure Spectral Analysis
    ax2 = fig.add_subplot(212, projection='3d')
    f_pressure, t_pressure, Sxx_pressure = signal.spectrogram(df['outletPressure'], fs, nperseg=1024)
    T_pressure, F_pressure = np.meshgrid(t_pressure, f_pressure)
    surf2 = ax2.plot_surface(T_pressure, F_pressure, 10 * np.log10(Sxx_pressure), cmap='viridis')
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Frequency [Hz]')
    ax2.set_zlabel('PSD [dB/Hz]')
    ax2.set_title(f'Outlet Pressure Power Spectral Density:\nTemperature: 180°F, Test Request: {test_request}, Date: {test_date}')
    fig.colorbar(surf2, ax=ax2, label='PSD [dB/Hz]', shrink=0.5, aspect=10)

    plt.tight_layout()
    plt.savefig(f"{file_name}_3d_spectral_analysis.png", dpi=300)
    plt.close()

    # Calculate statistics
    stats = {
        'tdms_file': file_name,
        'Temperature (°F)': temperature,
        'Min Case Flow (gpm)': df['caseFlow'].min(),
        'Mean Case flow (gpm)': df['caseFlow'].mean(),
        'Max Case Flow (gpm)': df['caseFlow'].max(),
        'Minimum Outlet Pressure (psi)': df['outletPressure'].min(),
        'Maximum Outlet Pressure (psi)': df['outletPressure'].max(),
        'Minimum Control Pressure (psi)': df['controlPressure'].min(),
        'Maximum Control Pressure (psi)': df['controlPressure'].max(),
        'Outlet Pressure Range (psi)': df['outletPressure'].max() - df['outletPressure'].min(),
        'Mean Outlet Pressure (psi)': df['outletPressure'].mean(),
        'Control Pressure Range (psi)': df['controlPressure'].max() - df['controlPressure'].min(),
        'Mean Control Pressure (psi)': df['controlPressure'].mean(),
    }
    
    return stats

def process_folder(folder_path, test_request, test_date):
    all_stats = []
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tdms'):
            file_path = os.path.join(folder_path, file_name)
            df = process_tdms_file(file_path)
            stats = analyze_speed_sweep(df, file_name, test_request, test_date)
            all_stats.append(stats)
    
    # Save results to CSV
    results_df = pd.DataFrame(all_stats)
    output_file = os.path.join(folder_path, f"Result_Speed_sweep-{test_request}.csv")
    results_df.to_csv(output_file, index=False)

    print("Data processing complete. All figures and summaries are stored in the working folder.")
    print(f"Data has been saved in: {output_file}")
    
    all_data = pd.DataFrame()
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tdms'):
            file_path = os.path.join(folder_path, file_name)
            df = process_tdms_file(file_path)
            all_data = pd.concat([all_data, df], ignore_index=True)
    
    # Save the complete dataframe to a CSV file
    output_file = os.path.join(folder_path, 'processed_combined_data.csv')
    all_data.to_csv(output_file, index=False)
    
    # Continue with the existing analysis
    stats = analyze_speed_sweep(all_data, "combined_data", test_request, test_date)
    
    # Save results to CSV
    results_df = pd.DataFrame([stats])
    output_file = os.path.join(folder_path, f"Result_Speed_sweep-{test_request}.csv")
    results_df.to_csv(output_file, index=False)
    
    output_file = os.path.join(folder_path, 'results', 'processed_combined_data.csv')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    all_data.to_csv(output_file, index=False)

    print("Data processing complete. All figures and summaries are stored in the working folder.")
    print(f"Complete data has been saved in: {os.path.join(folder_path, 'processed_combined_data.csv')}")
    print(f"Analysis results have been saved in: {output_file}")
    
    return all_data

    
def main(tdms_folder_path, output_path):
    try:
        logging.info(f"TDMS folder path: {tdms_folder_path}")
        logging.info(f"Output path: {output_path}")
        
  
        test_request = "TEST123"
        test_date = "2023-04-15"

        all_data = process_folder(tdms_folder_path, test_request, test_date)
        output_file = os.path.join(tdms_folder_path, 'processed_combined_data.csv')
        all_data.to_csv(output_file, index=False)
        setattr(main, 'pc_ss_dataframe', all_data)


        print(json.dumps({"success": "Data processing completed successfully"}))
    except Exception as e:
        logging.exception("An error occurred during script execution")
        error_message = json.dumps({"error": str(e)})
        print(error_message, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pc_ss.py <tdms_folder_path> <output_path>")
        sys.exit(1)
    
    tdms_folder_path = sys.argv[1]
    output_path = sys.argv[2]
    main(tdms_folder_path, output_path)