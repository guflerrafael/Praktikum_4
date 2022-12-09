import Lab3Functions as l3f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.integrate
import os

# Funktionen zum Plotten der Arbeitsschritte
def plot_steps(time, emg, label):
    directory = os.path.join(os.getcwd(), "images")
    path = os.path.join(directory, label + ".png")

    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    plt.savefig(path)

# Funktionen zum Verarbeiten der EMG-Daten

def eliminate_offset(emg, time, label):
    # Plot vorher
    plot_steps(time, emg, "vor_average" + label)

    # Average berechnen und abziehen
    average = np.average(emg)
    emg = emg - average

    # Plot nachher
    plot_steps(time, emg, "nach_average" + label)
    
    return emg

def filter_signal(emg, time, low_band, high_band, fs, label):
    # Plot vorher
    plot_steps(time, emg, "vor_bandpass" + label)

    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plot_steps(time, emg, "nach_bandpass" + label)

    return emg

def rectify_signal(emg, time, label):
    # Plot vorher
    plot_steps(time, emg, "vor_rectify" + label)

    emg = abs(emg)

    # Plot nachher
    plot_steps(time, emg, "nach_rectify" + label)

    return emg  

def envelope_signal(emg, time, low_pass, fs, label):
    # Plot vorher
    plot_steps(time, emg, "vor_envelope" + label)

    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plot_steps(time, emg, "nach_envelope" + label)

    return emg 


# Datensätze importieren

data_hamstring, emg_offset, emg_filtered, emg_rectified, emg_envelope = [], [], [], [], []
column_names = ["angle", "a_x", "a_y", "a_z", "emg", "time"]

directory = os.path.join(os.getcwd(), "images")
directory = os.path.join(directory, "angle")

for i in range(5):
    path = "Daten_Richi/phi_max_" + str(i + 1) + ".txt"

    # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
    data_hamstring.append(pd.read_csv(path, sep="\t", names=column_names, skiprows= 50))
    data_hamstring[i]["angle"] = data_hamstring[i]["angle"] * (-1)

    # EMG-Daten verarbeiten
    emg_offset.append(eliminate_offset(data_hamstring[i]["emg"], data_hamstring[i]["time"], "_emg" + str(i + 1)))
    emg_filtered.append(filter_signal(emg_offset[i], data_hamstring[i]["time"], 20, 450, 1000, "_emg" + str(i + 1)))
    emg_rectified.append(rectify_signal(emg_filtered[i], data_hamstring[i]["time"], "_emg" + str(i + 1)))
    emg_envelope.append(envelope_signal(emg_rectified[i], data_hamstring[i]["time"], 15, 1000, "_emg" + str(i + 1)))

    # Winkel plotten
    path = os.path.join(directory, "angle" + str(i + 1) + ".png")

    plt.figure()
    plt.plot(data_hamstring[i]["time"], data_hamstring[i]["angle"])
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig(path)

    # Letzen Wert über 60 finden, um vorderen Teil abzuschneiden
    index_under_60 = np.where(data_hamstring[i]["angle"] < 60)[0]
    start_index = 0

    for index in index_under_60:
        if index > 500:
            break

        start_index = index

    print(start_index)
        
    # Daten vor Trigger abschneiden (100 ms nach Trigger -> Anfang der neuen Daten)
    to_drop = np.arange(0, start_index + 100)
    data_hamstring[i] = data_hamstring[i].drop(to_drop)

    # Winkel plotten nach abschneiden
    path = os.path.join(directory, "angle_after" + str(i + 1) + ".png")

    plt.figure()
    plt.plot(data_hamstring[i]["time"], data_hamstring[i]["angle"])
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig(path)
            
