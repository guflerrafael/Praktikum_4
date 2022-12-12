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

directory_img = os.path.join(os.getcwd(), "images")
directory_data = os.path.join(os.getcwd(), "Daten_Raf")
directory = os.path.join(directory_img, "angle")

for i in range(3):
    
    path = os.path.join(directory_data, "phi_max_" + str(i + 1) + ".txt")

    # Daten einlesen (Winkel, Beschleunigung, EMG, Zeit)
    data_hamstring.append(pd.read_csv(path, sep="\t", names=column_names, skiprows= 50))
    data_hamstring[i]["angle"] = data_hamstring[i]["angle"] * (-1)

    

    # ----------- Neuen Funktionen, noch nicht fertig ------------
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

    # Differenz zwischen zwei Indexen unter 60, wenn größer 500 -> letzer unter 60
    for a in range(len(index_under_60)):
        if index_under_60[a] - index_under_60[a - 1] > 500:
            break

        start_index = index_under_60[a]

    # Daten vor Trigger abschneiden (x Indexe nach Trigger -> Anfang der neuen Daten)
    to_drop = np.arange(0, start_index + 200)
    data_hamstring[i] = data_hamstring[i].drop(to_drop)
    data_hamstring[i].reset_index(drop=True, inplace=True) # Indize auf Null zurücksetzen

    # Winkel plotten nach abschneiden
    path = os.path.join(directory, "angle_after_cut" + str(i + 1) + ".png")

    plt.figure()
    plt.plot(data_hamstring[i]["time"], data_hamstring[i]["angle"])
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig(path)

    # Winkelfunktion filtern (Tiefpass)
    low_pass = 10
    low_pass = low_pass / (1000 / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    data_hamstring[i]["angle"] = scipy.signal.filtfilt(b, a, data_hamstring[i]["angle"])
    
    # Winkel plotten nach filtern
    path = os.path.join(directory, "angle_after_filter" + str(i + 1) + ".png")

    plt.figure()
    plt.plot(data_hamstring[i]["time"], data_hamstring[i]["angle"])
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig(path)

    # Ableitung vom Winkelverlauf bilden mit variabler Schrittweite

    diff_angle = []
    help_vek = data_hamstring[i]["angle"].values
    angle_len = len(help_vek)
    resolution = 20
    step_size = int(angle_len/resolution)

    y = 0
    while y < (angle_len-step_size):
        diff_angle.append(abs(help_vek[y]-help_vek[y+step_size]))
        y = y + step_size

    # Maximalwert suchen
    max_value = max(diff_angle)
    index_max= (np.where(diff_angle==max_value))[0][0]
    x_value = (index_max*step_size) - 35

    plt.figure()
    plt.plot(data_hamstring[i]["angle"])
    plt.axvline(x_value, color='red')
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("Winkel / Grad")
    plt.savefig("angle_endindex" + str(i + 1) + ".png")
    

    # EMG-Daten verarbeiten
    emg_processed.append(process_emg(data_hamstring[i]["emg"], data_hamstring[i]["time"], 1000, "_emg" + str(i + 1)))

    # Idee zum berechnen des Indexes, wo Person abfällt: Um Mittelwert einen "Schlauch", wenn Werte drüber
    # oder drunter -> Person fällt ab, Versuch ist also fertig 
    