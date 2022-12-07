import Lab3Functions as l3f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.integrate

def eliminate_offset(emg, time, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_average.png")
    plt.savefig('vor_average' + label + '.png')

    # Average berechnen und abziehen
    average = np.average(emg)
    emg = emg - average

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_average.png")
    plt.savefig('nach_average' + label + '.png')
    
    return emg

def filter_signal(emg, time, low_band, high_band, fs, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_bandpass.png")
    plt.savefig('vor_bandpass' + label + '.png')

    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_bandpass.png")
    plt.savefig('nach_bandpass' + label + '.png')

    return emg

def rectify_signal(emg, time, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_rectify.png")
    plt.savefig('vor_rectify' + label + '.png')

    emg = abs(emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_rectify.png")
    plt.savefig('nach_rectify' + label + '.png')

    return emg  

def envelope_signal(emg, time, low_pass, fs, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_envelope.png")
    plt.savefig('vor_envelope' + label + '.png')

    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_envelope.png")
    plt.savefig('nach_envelope' + label + '.png')

    return emg  


# Aufgabe 1 Vorverarbeiten der EMG Daten
# Datensätze importieren
# weights, mvc, fatigue = l3f.import_data("\t")

data_hamstring, emg_offset, emg_filtered, emg_rectified, emg_envelope = [], [], [], [], []
column_names = ["angle", "a_x", "a_y", "a_z", "emg", "time"]

for i in range(5):
    path = "Daten_Richi/phi_max_" + str(i + 1) + ".txt"

    # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
    data_hamstring.append(pd.read_csv(path, sep="\t", names=column_names, skiprows= 50))

    # EMG-Daten verarbeiten
    emg_offset.append(eliminate_offset(data_hamstring[i]["emg"], data_hamstring[i]["time"], "_emg" + str(i + 1)))
    emg_filtered.append(filter_signal(emg_offset[i], data_hamstring[i]["time"], 20, 450, 1000, "_emg" + str(i + 1)))
    emg_rectified.append(rectify_signal(emg_filtered[i], data_hamstring[i]["time"], "_emg" + str(i + 1)))
    emg_envelope.append(envelope_signal(emg_rectified[i], data_hamstring[i]["time"], 15, 1000, "_emg" + str(i + 1)))