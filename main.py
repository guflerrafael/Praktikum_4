import Lab3Functions as l3f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.integrate
import os

# Funktionen zum Plotten der Arbeitsschritte
def plot_steps_emg(time, emg, label):
    directory = os.path.join(os.getcwd(), "images")
    directory = os.path.join(directory, "emg")
    path = os.path.join(directory, label + ".png")

    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    plt.savefig(path)

# Funktion zum Verarbeiten der EMG-Daten
def process_emg(emg, time, fs, label):
    low_band, high_band, low_pass = 20, 450, 20

    plot_steps_emg(time, emg, "vor_average" + label)

    # Average berechnen und abziehen
    average = np.average(emg)
    emg = emg - average
    plot_steps_emg(time, emg, "nach_average" + label)

    # Signal mit Bandpass filtern
    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    emg = scipy.signal.filtfilt(b, a, emg)
    plot_steps_emg(time, emg, "nach_filter" + label)

    # Gleichrichten
    emg = abs(emg)
    plot_steps_emg(time, emg, "nach_rectify" + label)

    # Einhüllende bilden
    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    emg = scipy.signal.filtfilt(b, a, emg)
    plot_steps_emg(time, emg, "nach_envelope" + label)

    return emg


# Algorithmus zur Bearbeitung der Daten

data_hamstring, emg_processed = [], []
column_names = ["angle", "a_x", "a_y", "a_z", "emg", "time"]

directory = os.path.join(os.getcwd(), "images")
directory = os.path.join(directory, "angle")

for i in range(5):
    path = "Daten_Richi/phi_max_" + str(i + 1) + ".txt"

    # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
    data_hamstring.append(pd.read_csv(path, sep="\t", names=column_names, skiprows= 50))
    data_hamstring[i]["angle"] = data_hamstring[i]["angle"] * (-1)

    # EMG-Daten verarbeiten
    emg_processed.append(process_emg(data_hamstring[i]["emg"], data_hamstring[i]["time"], 1000, "_emg" + str(i + 1)))

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
            
