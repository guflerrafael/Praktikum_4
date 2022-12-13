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
    plt.close()

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
    plt.close()

# Funktion zum Verarbeiten der EMG-Daten
def process_emg(data, fs, label):
    low_band, high_band, low_pass = 20, 450, 5

    plot_steps_emg(data["time"], data["emg"], "vor_average_" + label)

    # Average berechnen und abziehen
    average = np.average(data["emg"])
    data["emg"] = data["emg"] - average
    plot_steps_emg(data["time"], data["emg"], "nach_average_" + label)

    # Signal mit Bandpass filtern
    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    data["emg"] = scipy.signal.filtfilt(b, a, data["emg"])
    plot_steps_emg(data["time"], data["emg"], "nach_filter_" + label)

    # Gleichrichten
    data["emg"] = abs(data["emg"])
    plot_steps_emg(data["time"], data["emg"], "nach_rectify_" + label)

    # Einhüllende bilden
    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    data["emg"] = scipy.signal.filtfilt(b, a, data["emg"])
    plot_steps_emg(data["time"], data["emg"], "nach_envelope_" + label)

    return data

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

    # Maximum suchen (davor nochmals abschneiden)
    index_max_front = (np.where(data["angle"] == max(data["angle"])))[0][0]
    to_drop = np.arange(0, index_max_front)
    data = data.drop(to_drop)
    data.reset_index(drop=True, inplace=True) # Indize auf Null zurücksetzen

    # Maximalen Winkel auf 90 Grad setzen, damit alle gleichen Startpunkt haben
    max_value = data["angle"][0]
    data["angle"] = data["angle"] + (90 - max_value)

    plot_steps_angle(data["time"], data["angle"], False, 0, "angle_end_cut_" + label)

    return data

# ---------------------------------------------------
# ---------------------------------------------------

data_hamstring = []
column_names = ["angle", "a_x", "a_y", "a_z", "emg", "time"]
dataset_path, dataset_name = 0, 0

directory_img = os.path.join(os.getcwd(), "images")
directory_data = os.path.join(os.getcwd(), "data")

for person in range(3):
    for dataset in range(3):
        dataset_name = "phi_emg_" + str(person + 1) + "_" + str(dataset + 1) + ".txt"
        dataset_path = os.path.join(directory_data, dataset_name)

        # Person zu Liste hinzufügen (als leere Liste)
        data_hamstring.append([])

        # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
        data_hamstring[person].append(pd.read_csv(dataset_path, sep="\t", names=column_names, skiprows= 50))
        data_hamstring[person][dataset]["angle"] = data_hamstring[person][dataset]["angle"] * (-1)

        # Winkel-Daten verarbeiten
        data_hamstring[person][dataset] = process_angle(data_hamstring[person][dataset], 1000, str(person + 1) + "_" + str(dataset + 1))

        # EMG-Daten verarbeiten
        data_hamstring[person][dataset] = process_emg(data_hamstring[person][dataset], 1000, str(person + 1) + "_" + str(dataset + 1))

        # Plot
        directory = os.path.join(os.getcwd(), "images")
        directory = os.path.join(directory, "result")
        path = os.path.join(directory, "result_angle_emg_" + str(person + 1) + "_" + str(dataset + 1) + ".png")

        print(data_hamstring[person][dataset])

        plt.figure()
        plt.plot(data_hamstring[person][dataset]["angle"], data_hamstring[person][dataset]["emg"])
        plt.xlabel("Winkel / Grad")
        plt.ylabel("EMG / mV")
        plt.savefig(path)
        plt.close()