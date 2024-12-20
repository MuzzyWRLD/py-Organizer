import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

def organisiere_mit_konfiguration(verzeichnis, konfigurationsdatei="config.json"):
    log_ausgabe.insert(tk.END, f"Starte Organisation mit Verzeichnis: {verzeichnis} und Konfigurationsdatei: {konfigurationsdatei}\n")
    try:
        with open(konfigurationsdatei, "r") as f:
            konfiguration = json.load(f)
        log_ausgabe.insert(tk.END, "Konfigurationsdatei erfolgreich geladen.\n")
    except FileNotFoundError:
        log_ausgabe.insert(tk.END, "Fehler: Konfigurationsdatei nicht gefunden!\n")
        messagebox.showerror("Fehler", "Konfigurationsdatei nicht gefunden!")
        return
    except json.JSONDecodeError:
        log_ausgabe.insert(tk.END, "Fehler: Ungültiges JSON in der Konfigurationsdatei!\n")
        messagebox.showerror("Fehler", "Fehler beim Lesen der Konfigurationsdatei (ungültiges JSON)!")
        return

    try:
        if not os.path.exists(verzeichnis) or not os.access(verzeichnis, os.R_OK):
            log_ausgabe.insert(tk.END, "Fehler: Verzeichnis existiert nicht oder ist nicht zugänglich!\n")
            messagebox.showerror("Fehler", "Das gewählte Verzeichnis existiert nicht oder ist nicht zugänglich!")
            return

        for datei in os.listdir(verzeichnis):
            log_ausgabe.insert(tk.END, f"Verarbeite Datei: {datei}\n")
            if os.path.isfile(os.path.join(verzeichnis, datei)):
                dateiname, dateiendung = os.path.splitext(datei)
                log_ausgabe.insert(tk.END, f"Dateiname: {dateiname}, Dateiendung: {dateiendung}\n")
                if dateiendung:
                    for regel in konfiguration["regeln"]:
                        log_ausgabe.insert(tk.END, f"Prüfe Regel: {regel}\n")
                        if dateiendung.lower() in regel["dateiendungen"]:
                            ordnername = regel["ordnername"]
                            ordnerpfad = os.path.join(verzeichnis, ordnername)
                            log_ausgabe.insert(tk.END, f"Ordner für {dateiendung} ist {ordnerpfad}\n")
                            if not os.path.exists(ordnerpfad):
                                os.makedirs(ordnerpfad)
                                log_ausgabe.insert(tk.END, f"Ordner erstellt: {ordnerpfad}\n")
                            try:
                                shutil.move(os.path.join(verzeichnis, datei), ordnerpfad)
                                log_ausgabe.insert(tk.END, f"Datei {datei} verschoben nach {ordnerpfad}\n")
                            except (shutil.Error, PermissionError) as move_error:
                                log_ausgabe.insert(tk.END, f"Fehler beim Verschieben der Datei {datei}: {move_error}\n")
                                messagebox.showerror("Fehler", f"Die Datei {datei} konnte nicht verschoben werden: {move_error}")
                            break
        log_ausgabe.insert(tk.END, "Organisation abgeschlossen.\n")
        messagebox.showinfo("Erfolg", "Dateien wurden erfolgreich organisiert!")
    except Exception as e:
        log_ausgabe.insert(tk.END, f"Ein Fehler ist aufgetreten: {e}\n")
        log_ausgabe.insert(tk.END, traceback.format_exc())
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")


def waehle_verzeichnis():
    verzeichnis = filedialog.askdirectory()
    log_ausgabe.insert(tk.END, f"Ausgewähltes Verzeichnis: {verzeichnis}\n")
    if verzeichnis:
        verzeichnis_eingabe.delete(0, tk.END)
        verzeichnis_eingabe.insert(0, verzeichnis)

def starte_organisation():
    verzeichnis = verzeichnis_eingabe.get()
    log_ausgabe.insert(tk.END, f"Eingegebenes Verzeichnis: {verzeichnis}\n")
    if not verzeichnis or not os.path.isdir(verzeichnis):
        log_ausgabe.insert(tk.END, "Warnung: Ungültiges oder kein Verzeichnis ausgewählt.\n")
        messagebox.showwarning("Warnung", "Bitte wähle ein gültiges Verzeichnis aus!")
        return
    organisiere_mit_konfiguration(verzeichnis)


# Hauptfenster erstellen
fenster = tk.Tk()
fenster.title("Datei-Organizer")

# Verzeichnis auswählen
verzeichnis_label = tk.Label(fenster, text="Verzeichnis:")
verzeichnis_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

verzeichnis_eingabe = tk.Entry(fenster, width=50)
verzeichnis_eingabe.grid(row=0, column=1, padx=5, pady=5)

waehle_verzeichnis_button = tk.Button(fenster, text="Auswählen", command=waehle_verzeichnis)
waehle_verzeichnis_button.grid(row=0, column=2, padx=5, pady=5)

# Start-Button
start_button = tk.Button(fenster, text="Organisieren", command=starte_organisation)
start_button.grid(row=1, column=1, pady=10)

# Log-Ausgabe
log_ausgabe = tk.Text(fenster, height=20, width=80)
log_ausgabe.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

# Konfigurationsdatei erstellen (falls nicht vorhanden)
if not os.path.exists( "venv/config.json" ):
    log_ausgabe.insert(tk.END, "Erstelle Standard-Konfigurationsdatei.\n")
    with open( "venv/config.json", "w" ) as f:
        standard_konfiguration = {"regeln": []}
        json.dump(standard_konfiguration, f, indent=4)
        log_ausgabe.insert(tk.END, "Standard-Konfigurationsdatei erstellt.\n")

    # Validierung der Struktur
    try:
        with open( "venv/config.json", "r" ) as f:
            config_inhalt = json.load(f)
            if not isinstance(config_inhalt, dict) or "regeln" not in config_inhalt:
                raise ValueError("Ungültige Struktur der Konfigurationsdatei.")
            log_ausgabe.insert(tk.END, "Struktur der Konfigurationsdatei erfolgreich validiert.\n")
    except Exception as e:
        log_ausgabe.insert(tk.END, f"Fehler bei der Validierung der Konfigurationsdatei: {e}\n")

fenster.mainloop()
