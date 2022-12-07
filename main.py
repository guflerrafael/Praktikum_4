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
    #plt.savefig("vor_average.svg")
    plt.savefig('vor_average' + label + '.svg')

    # Average berechnen und abziehen
    average = np.average(emg)
    emg = emg - average

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_average.svg")
    plt.savefig('nach_average' + label + '.svg')
    
    return emg

def filter_signal(emg, time, low_band, high_band, fs, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_bandpass.svg")
    plt.savefig('vor_bandpass' + label + '.svg')

    b, a = scipy.signal.butter(4, [low_band, high_band], btype="bandpass", analog=False, fs=fs)
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_bandpass.svg")
    plt.savefig('nach_bandpass' + label + '.svg')

    return emg

def rectify_signal(emg, time, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_rectify.svg")
    plt.savefig('vor_rectify' + label + '.svg')

    emg = abs(emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_rectify.svg")
    plt.savefig('nach_rectify' + label + '.svg')

    return emg  

def envelope_signal(emg, time, low_pass, fs, label):
    # Plot vorher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("vor_envelope.svg")
    plt.savefig('vor_envelope' + label + '.svg')

    low_pass = low_pass / (fs / 2)
    b, a = scipy.signal.butter(4, low_pass, btype='lowpass')
    emg = scipy.signal.filtfilt(b, a, emg)

    # Plot nachher
    plt.figure()
    plt.plot(time, emg)
    plt.xlabel("Zeit / Sekunden")
    plt.ylabel("EMG / mV")
    #plt.savefig("nach_envelope.svg")
    plt.savefig('nach_envelope' + label + '.svg')

    return emg  


# Aufgabe 1 Vorverarbeiten der EMG Daten
# Datensätze importieren
weights, mvc, fatigue = l3f.import_data("\t")

# Daten in Arrays speichern
# index 0 = weights; index 1 = mvc; index 2 = fatigue
emg_data = [weights.emg, mvc.emg, fatigue.emg]
time_data = [(weights.t)/1000, (mvc.t)/1000, (fatigue.t)/1000]
label_data = ["_weights", "_mvc", "_fat"]
emg_offset = []
emg_filtered = []
emg_rectified = []
emg_envelope = []


for i in range(3) :

    # Offset eliminieren
    emg_offset.append(eliminate_offset(emg_data[i], time_data[i], label_data[i]))
    
    # Filtern 
    # Funktionseingabe: (emg, time, low_band, high_band, fs)
    emg_filtered.append(filter_signal(emg_offset[i], time_data[i], 20, 450, 1000, label_data[i]))

    # Gleichrichten 
    emg_rectified.append(rectify_signal(emg_filtered[i], time_data[i], label_data[i]))

    # Einhüllende
    # Funktionseingabe: (emg, time, low_pass, fs)
    emg_envelope.append(envelope_signal(emg_rectified[i], time_data[i], 15, 1000, label_data[i]))
    

# Subplots erstellen für Frage 5
figure_a5, subplot_a5 = plt.subplots(5, sharex=True)
figure_a5.set_figheight(12)
figure_a5.set_figwidth(8)

subplot_a5[0].plot(time_data[1], emg_data[1])
subplot_a5[0].set_title("Rohdaten")
subplot_a5[1].plot(time_data[1], emg_offset[1])
subplot_a5[1].set_title("Nach Mittelwert entfernen")
subplot_a5[2].plot(time_data[1], emg_filtered[1])
subplot_a5[2].set_title("Nach Filtern")
subplot_a5[3].plot(time_data[1], emg_rectified[1])
subplot_a5[3].set_title("Nach Gleichrichten")
subplot_a5[4].plot(time_data[1], emg_envelope[1])
subplot_a5[4].set_title("Nach Hüllkurve erzeugen")

figure_a5.supxlabel("Zeit / Sekunden")
figure_a5.supylabel("EMG / mV")
figure_a5.tight_layout()
figure_a5.savefig("Verarbeitung_EMG.png")


# Aufgabe 2 MVC und relative Muskelaktivität
#mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e = l3f.get_bursts(emg_filtered[1],emg_filtered[0],emg_filtered[2])

#print(mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e)

# Zeitpunkte direkt in Variablen speicher
# Für Testzwecke
mvc_s = [249,3631,6886] 
mvc_e = [2477,5938,8719]

weights_s = [395,7487,13944] 
weights_e = [5614,11970,18326]

fatigue_s = [1290,8263,16453] 
fatigue_e = [6844,14912,22291]

# Mittelwerte der EMG Daten ermitteln
mvc_mean = []
weight_mean = []
fatigue_mean = []

for i in range(3):
    # Es werden nur die Bereiche der Muskelanspannung verwendet
    weight_mean.append(np.mean(emg_envelope[0][weights_s[i]:weights_e[i]]))
    mvc_mean.append(np.mean(emg_envelope[1][mvc_s[i]:mvc_e[i]]))
    fatigue_mean.append(np.mean(emg_envelope[2][fatigue_s[i]:fatigue_e[i]]))

# Referenz wird berechnet, gemittelter MVC Wert aller drei Versuche entspricht maximaler Muskelanspannung
mvc_mean_total = np.round(np.mean(mvc_mean),2)

# Muskelaktivität berechnen in Relation zu mvc_mean_total
# Ergebnis in Prozent
weight_relation = np.round((weight_mean/mvc_mean_total)*100,2)
fatigue_relation = np.round((fatigue_mean/mvc_mean_total)*100,2)

print(mvc_mean)
print(mvc_mean_total)
print(weight_mean)
print(fatigue_mean)
print(weight_relation)
print(fatigue_relation)

#Aufgabe 3: Berechnung der Spektralen Leistungsdichte.
Power_density = emg_filtered[2][fatigue_s[0]:fatigue_e[0]]

#x-Werte von Plot "Leistungsdichte" manuell abgelesen für Aufgane 3a 
Start_power_density = [126,2313,4900]

#Leere Arrays 
pw_d=[]
pw_d_power=[]
pw_d_frequencies=[]
#Aufgabe 3c: Vorberechnung für Butterworth Filter (40Hz cut-off Frequenz) 
low_pass =40/(1000/2)
b, a = scipy.signal.butter(4, low_pass, btype="lowpass")

md=[]
spectral_power_bw=[]

#Aufgabe 3: Isolieren am Anfang, Mitte und Ende des Bursts(3 Durchläufe) 
for j in range(3):
    #Aufgabe 3a: Definieren des Zeitraumes (0,5 Sekunden) 
    pw_d.append(Power_density[Start_power_density [j]:(Start_power_density [j]+500)])
    
    #Aufgabe 3b:
    power, frequencies=(l3f.get_power(pw_d[j],1000))
    #Aufgabe 3c: Filtern der Spektralen Leistungsdichte (Butterworthfilter) 
    power_bw = scipy.signal.filtfilt(b,a,power)

    #
    pw_d_power.append(power)
    pw_d_frequencies.append(frequencies)
    spectral_power_bw.append(power_bw)

    #Aufgabe 3c: Plotten von den gefilterten Spektrum 
    plt.figure()
    plt.plot(frequencies,power)
    plt.plot(frequencies,power_bw)
    plt.xlabel("Frequnz (Hz)")
    plt.ylabel("Leistung a.U.")
    plt.savefig('SpectralLD_'+str(j)+'.svg')

    #Aufgabe 4: Code von Aufgabenstellung (Berechnung der Fläche unter der Kuve)
    area_freq=scipy.integrate.cumtrapz(power , frequencies ,initial=0)
    total_power=area_freq[-1]
    median_freq=frequencies[np.where(area_freq >= total_power/2)[0][0]]


    md.append(median_freq)

  
# Aufgabe 4: Schleife zum Plotten der Medianfrequenz bei Ermüdung
plt.figure()
colors = ['blue','orange','green']
labels = ['Start','Middle','End']
for i in range(3):
    plt.plot(pw_d_frequencies[i],spectral_power_bw[i], label = labels[i])
    plt.axvline(md[i],color = colors[i])
    plt.xlabel("Frequenz (Hz)")
    plt.ylabel("Leistung a.U.")
    plt.legend(loc='upper right')



plt.savefig('pw_d_Medianfrequency.svg')

# Aufgabe 4.letzter plot
plt.figure()
# Startzeiten Start_power_density  [126,2313,4900]
len_LD = len(Power_density)
time_measurement = [Start_power_density [0]/len_LD,Start_power_density [1]/len_LD,Start_power_density [2]/len_LD]
time_measurement = np.round(time_measurement,2)
print(len(Power_density))
print(time_measurement)

plt.figure()
plt.plot(time_measurement,md)
plt.plot(time_measurement,md,'ob',color='red')
plt.xlabel("Time of Measurement (%)")
plt.ylabel("Median Frequency (Hz)")
plt.savefig('Medianfrequency_Fat.svg')

print(md)