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
    low_band, high_band, low_pass = 20, 450, 8

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

# EMG im Bezug auf Winkel mitteln, wobei hierbei weiter diskretisiert wird
def average_angle_emg(emg_avg, angle_avg):
    angle_len, emg_avg_all, angle_avg_all = [], [], []
    index_longest, length_longest, angle_increment = 0, 0, 1
    windows, window_length = [], [] # Anzahl der Fenster für jeden Datensatz; Anzahl der Indize pro Fenster
    angle_end = [] # Winkel, bei welchen von 3 auf 2 bzw. 1 Array gewechselt wird
    first_1, first_2 = 0, 0

    # Längstes Array und Länge jedes einzelnen
    for dataset in range(3):
        length = len(angle_avg[dataset])
        angle_len.append(length)

        if length >= length_longest:
            length_longest = length
            index_longest = dataset

    # Anzahl der Iterationsschritt (1 Grad) ermitteln
    for dataset in range(3):
        windows.append(int((90 - angle_avg[dataset][angle_len[dataset] - 1]) / angle_increment))
        window_length.append(int(angle_len[dataset] / windows[dataset]))

    # EMG Daten mitteln, mit Abfrage welche noch verfügbar sind (noch nicht fertig)
    for window_counter in range(windows[index_longest]):
        index = []

        for dataset in range(3):
            index.append(window_counter * window_length[dataset])

        # Alle 3 mitteln
        if index[0] < angle_len[0] and index[1] < angle_len[1] and index[2] < angle_len[2]: 
            emg_avg_all.append((emg_avg[0][index[0]] + emg_avg[1][index[1]] + emg_avg[2][index[2]]) / 3)
            
        # Nur mehr 2 mitteln
        elif index[0] < angle_len[0] and index[1] < angle_len[1]: 
            emg_avg_all.append((emg_avg[0][index[0]] + emg_avg[1][index[1]]) / 2)
            
            if first_1 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_1 = 1
            
        elif index[1] < angle_len[1] and index[2] < angle_len[2]: 
            emg_avg_all.append((emg_avg[1][index[1]] + emg_avg[2][index[2]]) / 2)

            if first_1 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_1 = 1

        elif index[0] < angle_len[0] and index[2] < angle_len[2]: 
            emg_avg_all.append((emg_avg[0][index[0]] + emg_avg[2][index[2]]) / 2)

            if first_1 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_1 = 1

        # Nur mehr 1 Array verfügbar
        elif index[0] < angle_len[0]: 
            emg_avg_all.append(emg_avg[0][index[0]])

            if first_2 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_2 = 1
            
        elif index[1] < angle_len[1]: 
            emg_avg_all.append(emg_avg[1][index[1]])

            if first_2 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_2 = 1
            
        elif index[2] < angle_len[2]: 
            emg_avg_all.append(emg_avg[2][index[2]])
            
            if first_2 == 0:
                angle_end.append(90 - window_counter * angle_increment)
                first_2 = 1
            
        angle_avg_all.append(90 - window_counter * angle_increment)
        
    return emg_avg_all, angle_avg_all, angle_end  

# ---------------------------------------------------
# ---------------------------------------------------

data_hamstring = []
emg_avg, angle_avg, angle_end, index_end = [], [], [], []
emg_avg_all, angle_avg_all, angle_end_all = [], [], []
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

        # Angle_Emg_Avg mitteln
        if dataset == 2:
            # Listen mit EMG bzw. Winkel aller 3 Datensätze
            emg_all = [data_hamstring[person][0]["emg"], data_hamstring[person][1]["emg"], data_hamstring[person][2]["emg"]]
            angle_all = [data_hamstring[person][0]["angle"], data_hamstring[person][1]["angle"], data_hamstring[person][2]["angle"]]

            emg_avg_p, angle_avg_p, angle_end = average_angle_emg(emg_all, angle_all)
            emg_avg.append(emg_avg_p)
            angle_avg.append(angle_avg_p)

            # Plot
            directory = os.path.join(os.getcwd(), "images")
            directory = os.path.join(directory, "result")
            path = os.path.join(directory, "result_angle_emg_avg_" + str(person + 1) + "_" + str(dataset + 1) + ".png")

            plt.figure()
            plt.plot(angle_avg[person], emg_avg[person])
            plt.gca().invert_xaxis() # x-Achse mit abnehmenden Werten
            plt.axvline(angle_end[0], color = "orange", linestyle = "dashed", label = "2 Datensätze")   
            plt.axvline(angle_end[1], color = "red", linestyle = "dotted", label = "1 Datensatz")  
            plt.legend(loc='upper left')
            plt.title("Mittelwert Proband " + str(person + 1))
            plt.xlabel("Winkel / Grad")
            plt.ylabel("EMG / mV")
            plt.savefig(path)
            plt.close()
    
    # Angle_Emg_Avg aller Personen mitteln
    if person == 2:
        emg_avg_all, angle_avg_all, angle_end_all = average_angle_emg(emg_avg, angle_avg)

        # Plot
        directory = os.path.join(os.getcwd(), "images")
        directory = os.path.join(directory, "result")
        path = os.path.join(directory, "result_angle_emg_avg_all.png")

        plt.figure()
        plt.plot(angle_avg_all, emg_avg_all)
        plt.gca().invert_xaxis() # x-Achse mit abnehmenden Werten
        plt.axvline(angle_end_all[0], color = "orange", linestyle = "dashed", label = "2 Datensätze")   
        plt.axvline(angle_end_all[1], color = "red", linestyle = "dotted", label = "1 Datensatz")   
        plt.legend(loc='upper left')
        plt.title("Mittelwert aller 3 Probanden")
        plt.xlabel("Winkel / Grad")
        plt.ylabel("EMG / mV")
        plt.savefig(path)
        plt.close()