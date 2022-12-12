import Lab3Functions as l3f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.integrate
import os

# Funktionen zum Plotten der Arbeitsschritte (EMG)
def plot_steps_emg(time, emg, label):
    directory = os.path.join(os.getcwd(), "images")
    directory = os.path.join(directory, "emg")
    path = os.path.join(directory, label + ".png")

    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    plt.savefig(path)

# Funktionen zum Plotten der Arbeitsschritte (Winkel)
def plot_steps_angle(time, angle, line, index_max, label):
    directory = os.path.join(os.getcwd(), "images")
    directory = os.path.join(directory, "angle")
    path = os.path.join(directory, label + ".png")

    plt.figure()
    plt.plot(time, angle)

    if line == True:
        plt.axvline(time[index_max], color='red') # Zeit in ms bei maximalen Index

    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig(path)

# Funktion zum Verarbeiten der EMG-Daten
def process_emg(emg, time, fs, label):
    low_band, high_band, low_pass = 20, 450, 10

    plot_steps_emg(time, emg, "vor_average_" + label)

    # Average berechnen und abziehen
    average = np.average(emg)
    emg = emg - average
    plot_steps_emg(time, emg, "nach_average_" + label)

    # Signal mit Bandpass filtern
    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    emg = scipy.signal.filtfilt(b, a, emg)
    plot_steps_emg(time, emg, "nach_filter_" + label)

    # Gleichrichten
    emg = abs(emg)
    plot_steps_emg(time, emg, "nach_rectify_" + label)

    # Einhüllende bilden
    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    emg = scipy.signal.filtfilt(b, a, emg)
    plot_steps_emg(time, emg, "nach_envelope_" + label)

    return emg

# Funktion zum Verarbeiten der Winkeldaten
def process_angle(data, fs, label):
    low_pass = 10

    plot_steps_angle(data["time"], data["angle"], False, 0, "angle_" + label)

    # Letzen Wert über 60 finden, um vorderen Teil abzuschneiden
    index_under_60 = np.where(data["angle"] < 60)[0]
    start_index = 0

    # Differenz zwischen zwei Indexen unter 60, wenn größer 500 -> letzer unter 60
    for a in range(len(index_under_60)):
        if index_under_60[a] - index_under_60[a - 1] > 500:
            break

        start_index = index_under_60[a]

    # Daten vor Trigger abschneiden (x Indexe nach Trigger -> Anfang der neuen Daten)
    to_drop = np.arange(0, start_index + 200)
    data = data.drop(to_drop)
    data.reset_index(drop=True, inplace=True) # Indize auf Null zurücksetzen

    plot_steps_angle(data["time"], data["angle"], False, 0, "angle_front_cut_" + label)

    # Winkel filtern
    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    data["angle"] = scipy.signal.filtfilt(b, a, data["angle"])

    plot_steps_angle(data["time"], data["angle"], False, 0, "angle_filter_" + label)

    # Ableitung vom Winkelverlauf bilden mit variabler Schrittweite
    diff_angle, resolution, y = [], 20, 0
    angle_len = len(data["angle"])
    step_size = int(angle_len / resolution)

    while y < (angle_len - step_size):
        diff_angle.append(abs(data["angle"][y] - data["angle"][y + step_size]))
        y = y + step_size

    # Maximalwert suchen
    index_max = (np.where(diff_angle == max(diff_angle)))[0][0]
    index_max = (index_max * step_size) - 35

    plot_steps_angle(data["time"], data["angle"], True, index_max, "angle_max_index_" + label)

    # Daten nach maximalen Index abschneiden (Versuch beendet)
    to_drop = np.arange(index_max, len(data["angle"]))
    data = data.drop(to_drop)
    data.reset_index(drop=True, inplace=True) # Indize auf Null zurücksetzen

    plot_steps_angle(data["time"], data["angle"], False, 0, "angle_end_cut_" + label)

    return data

# ---------------------------------------------------
# ---------------------------------------------------

data_hamstring, emg_processed = [], []

column_names = ["angle", "a_x", "a_y", "a_z", "emg", "time"]

directory_img = os.path.join(os.getcwd(), "images")
directory_data = os.path.join(os.getcwd(), "Daten_Raf")
directory = os.path.join(directory_img, "angle")

for i in range(3):
    
    path = os.path.join(directory_data, "phi_max_" + str(i + 1) + ".txt")

    # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
    data_hamstring.append(pd.read_csv(path, sep="\t", names=column_names, skiprows= 50))
    data_hamstring[i]["angle"] = data_hamstring[i]["angle"] * (-1)

    # Winkel-Daten verarbeiten
    data_hamstring[i] = process_angle(data_hamstring[i], 1000, str(i + 1))

    # EMG-Daten verarbeiten
    emg_processed.append(process_emg(data_hamstring[i]["emg"], data_hamstring[i]["time"], 1000, "emg_" + str(i + 1)))
    