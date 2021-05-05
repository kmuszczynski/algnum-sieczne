from tkinter import *
from tkinter import messagebox
from tk_html_widgets import HTMLLabel
from itertools import combinations
from functools import total_ordering
import os.path
import math
import numpy as np

#------------------------------------------------Program--------------------------------------------------#

#Klasa trzymająca wyniki
class Wynik:
    def __init__(self, typ, x=None, dok=None, ttk=None):
        self.typ = typ
        self.x = x
        self.dok = dok
        self.ttk = ttk

#Deklaracja Wyjątków
class ZaDuzaDokladnosc(Exception): pass
class BrakPrzedzialu(Exception): pass

#Funkcje pomocnicze
def który_mniejszy(x, y):
    if x < y: return x, y
    else: return y, x
    
def różne_znaki(x, y):
    if x * y < 0: return True
    else: return False

#Funkcja czytająca dane z pliku
def czytaj_plik(file_name):
    try:
        f = open(file_name, "r")

        line=next(f).split()
        e=float(line.pop(0))

        line=next(f).split()
        x1=float(line.pop(0))
        x2=float(line.pop(0))

        x1, x2=który_mniejszy(x1, x2)

        if x1==x2: raise BrakPrzedzialu()
        if e>abs(x2-x1): raise ZaDuzaDokladnosc()

    except ValueError:
        messagebox.showerror("Error", "Błąd 1: Niepoprawne wartości w pliku!")
    except FileNotFoundError:
        messagebox.showerror("Error", "Błąd 2: Nie znaleziono pliku!")
    except BrakPrzedzialu:
        messagebox.showerror("Error", "Błąd 3: Nie ma przedziału!")
        return
    except ZaDuzaDokladnosc:
        messagebox.showerror("Error", "Błąd 4: Dokładność jest większa od przedziału!")
        return
    except:
        messagebox.showerror("Error", "Błąd 4: Niewykryty błąd, sprawdź poprawność pliku!")

    f.close()
    return e, x1, x2

#Funkcja dla określonego zadania
def funkcja(x):
    return math.log(x**2) - math.sin(x) - 2

#Metoda Siecznych        
def sieczne_krok(f, x, y):
    return x - (f(x) * (x - y)) / (f(x) - f(y))

def sieczne(f, x, y, eps):
    ttk = 64
    while ttk > 0 and abs(x-y) > eps:
        temp = sieczne_krok(f, x, y)
        x = y
        y = temp
        ttk = ttk - 1
        dok=abs(x-y)
    if ttk==0: return Wynik("sieczne 64")
    else: return Wynik("sieczne", temp, dok, ttk)

#Metoda Siecznych+ - sieczne + reguły bisekcji
def sieczne_plus(f, x, y, eps):
    if not różne_znaki(f(x), f(y)): 
        return Wynik("sieczne+ - znak")
    ttk = 64
    while ttk > 0 and abs(x-y) > eps:
        kolejny = sieczne_krok(f, x, y)
        if różne_znaki(f(y), f(kolejny)):
            x = kolejny
        else:
            y = kolejny
        ttk = ttk - 1
        dok=abs(x-y)
    if ttk==0: return Wynik("sieczne+ 64")
    else: return Wynik("sieczne+", kolejny, dok, ttk)

#Metoda Bisekcji        
def bisekcja(f, x, y, eps):
    if not różne_znaki(f(x), f(y)):
        return Wynik("bisekcja - znak")
    ttk = 64
    while ttk > 0 and abs(x - y) > eps:
        srodek = (x + y) / 2
        if różne_znaki(f(y), f(srodek)): 
            x = srodek
        else: 
            y = srodek
        ttk = ttk - 1
    dok=abs(x - y)
    if ttk==0: return Wynik("bisekcja 64")
    else: return Wynik("bisekcja", srodek, dok, ttk)

#Tabela wyników:
def tab_wyn(x1, x2, f, e):
    wyniki=[]
    r=[x for x in np.arange(x1, x2, 0.01)]
    for i in r:
        for j in r:
            if i<j and i*j>0:
                wyniki.append(bisekcja(f,i,j,e))
                wyniki.append(sieczne(f,i,j,e))
                wyniki.append(sieczne_plus(f,i,j,e))
    return wyniki

#Zliczanie wyników
def licz(wyniki):
    sz = 0; sr = 0; sttk = 0
    bz = 0; bzn = 0; bttk = 0
    spz = 0; spzn = 0; spttk = 0

    for j in wyniki:
        i = j.typ
        if i == "sieczne":
            sz += 1
            sttk=sttk+64-j.ttk
        if i == "sieczne 64":
            sr += 1
        if i == "bisekcja":
            bz += 1
            bttk=bttk+64-j.ttk
        if i == "bisekcja - znak" or i=="bisekcja 64":
            bzn += 1
        if i == "sieczne+":
            spz += 1
            spttk=spttk+64-j.ttk
        if i == "sieczne+ - znak" or i=="sieczne+ 64":
            spzn += 1
    
    if sz!=0: sśttk = sttk / sz
    else: sśttk=0
    if bz!=0: bśttk = bttk / bz
    else: bśttk=0
    if spz!=0: spśttk = spttk / spz
    else: spśttk=0

    return(bz, bzn, bśttk, sz, sr, sśttk, spz, spzn, spśttk)

#--------------------------------------------------GUI-----------------------------------------------------#

# Funkcja tworząca okno
def to(nazwa, rozmiar, warunek):
    nowe = Tk()
    nowe.title(nazwa)
    nowe.geometry(rozmiar)
    if warunek == 1: nowe.resizable(False, False)
    return nowe

# Funkcja zapisuje zawartość textbox do pliku dane.txt
def zapisz():
    try:
        f = open('dane.txt', 'w')
        f.write(text.get(1.0, END))
        f.close()
        messagebox.showinfo("Informacja!", "Plik został poprawnie zapisany!")
    except:
        messagebox.showerror("Error", "Błąd 4: Niewykryty błąd, sprawdź poprawność pliku!")

# Funkcja odpowiadająca za umożliwienie edycji pliku
def ep():
    #Deklarowanie Ramki
    ep = to("Edycja pliku", "300x150", 1)

    # tworzenie ramki, scroll'a i textbox'a
    frame = Frame(ep)
    frame.pack()
    scroll = Scrollbar(frame, orient=HORIZONTAL)
    scroll.pack(side=BOTTOM, fill=X)

    global text
    text = Text(frame,
                width=25,
                height=3,
                font=("Helvetica", 16),
                selectbackground="yellow",
                selectforeground="black",
                undo=True,
                xscrollcommand=scroll.set,
                wrap="none")
    text.pack()

    # konfiguracja scrolla
    scroll.config(command=text.xview)

    if os.path.exists('dane.txt'):
        # Otwieranie pliku dane.txt
        f = open('dane.txt', 'r')
        stuff = f.read()
        text.insert(END, stuff)  # wstawianie tekstu z dane.txt do textbox'a
    else:
        f = open('dane.txt', 'w')  # tworzenie pliku jeżeli nie istnieje
        f.close()

    Button(ep, text="Edytuj plik dane.txt", padx=40, pady=10, command=zapisz).pack()

    ep.mainloop()
    f.close()

# Funkcja wyświetla wyniki tylko dla podanego przedziału
def odp():
    try:
        odp = to("Obliczanie dla podanego", "1500x300", 0)
        e, x1, x2=czytaj_plik("dane.txt")

        Label(odp, text="Przedział: [{}, {}]\nDokładność: {}\n".format(x1, x2, e), font="Arial 12", justify=LEFT).grid(row=0,
                                                                                                                  sticky=W + S)

        #Deklaracja Bisekcji
        Label(odp, text="Bisekcja Wyniki:", font="Arial 12", justify=LEFT).grid(row=1, sticky=W+S)
        BW=bisekcja(funkcja,x1,x2,e)

        if BW.typ=="bisekcja - znak":
            Label(odp, text="W tym przedziale nie ma miejsca zerowego, metoda nie zadziała!\n", font="Arial 12").grid(row=2, sticky=W+S)
        else:
            if BW.typ=="bisekcja 64":
                Label(odp, text="Metoda dla podanego przykładu nie zmieściła się w 64 krokach").grid(row=2, sticky=W+S)
            else:
                Label(odp, text="Miejsce zerowe występuje w pobliżu x={} z dokladnością: {}, metoda wykonała {} kroków\n".format(BW.x, BW.dok, 64-BW.ttk), font="Arial 12").grid(row=2, sticky=W+S)
    
        #Deklaracja Siecznych
        Label(odp, text="Sieczne Wyniki:", font="Arial 12", justify=LEFT).grid(row=3, sticky=W+S)
        SW=sieczne(funkcja, x1, x2, e)
        
        if SW.typ=="sieczne 64":
            Label(odp, text="Metoda siecznych nie znalazła przedziału o podanej dokładności w 64 krokach\n", font="Arial 12").grid(row=4, sticky=W+S)
        else:
            Label(odp, text="Miejsce zerowe występuje w pobliżu x={} z dokladnością: {}, metoda wykonała {} kroków\n".format(SW.x, SW.dok, 64-SW.ttk), font="Arial 12").grid(row=4, sticky=W+S)

        #Deklaracja Siecznych++
        Label(odp, text="Sieczne++ Wyniki:", font="Arial 12", justify=LEFT).grid(row=5, sticky=W+S)
        SPW=sieczne_plus(funkcja, x1, x2, e)

        if SPW.typ=="sieczne+ - znak":
            Label(odp, text="Podane wartości są tego samego znaku, metoda nie zadziałała!\n", font="Arial 12").grid(row=6, sticky=W+S)
        else:
            if SPW.typ=="sieczne+ 64":
                Label(odp, text="Metoda siecznych++ nie znalazła przedziału o podanej dokładności w 64 krokach!\n", font="Arial 12").grid(row=6, sticky=W+S)
            else:
                Label(odp, text="Miejsce zerowe występuje w pobliżu x={} z dokladnością: {}, metoda wykonała {} kroków\n".format(SPW.x, SPW.dok, 64-SPW.ttk), font="Arial 12").grid(row=6, sticky=W+S)
        
        odp.mainloop()
    except:
        messagebox.showerror("Error", "Program nie zadziałał, sprawdź czy dane są poprawne!")
        odp.destroy()

# Funkcja wyświetla wyniki dla kilku podprzedziałów podanego przedziału
def gd():
    try:
        gd = to("Generuj dla przedziału", "1000x500", 0)
        e, x1, x2=czytaj_plik("dane.txt")

        wyn_tab=tab_wyn(x1, x2, funkcja, e)
        wyniki=licz(wyn_tab)

        Label(gd, text="Przedział: [{}, {}]\nDokładność: {}\nLiczba wygenerowanych przedziałów: {}\n".format(x1, x2, e, int(len(wyn_tab)/3)), font="Arial 12", justify=LEFT).grid(row=0,
                                                                                                                    sticky=W + S)

        Label(gd, text="1.Bisekcja\n Znalezione: {}\n Nieznalezione: {}\n Średnia liczba kroków dla znalezionych: {}".format(wyniki[0], wyniki[1], wyniki[2]), font="Arial 12", justify=LEFT).grid(row=1, sticky=W+S)
        Label(gd, text="2.Sieczne\n Znalezione: {}\n Nieznalezione: {}\n Średnia liczba kroków dla znalezionych: {}".format(wyniki[3], wyniki[4], wyniki[5]), font="Arial 12", justify=LEFT).grid(row=2, sticky=W+S)
        Label(gd, text="3.Sieczne++\n Znalezione: {}\n Nieznalezione: {}\n Średnia liczba kroków dla znalezionych: {}".format(wyniki[6], wyniki[7], wyniki[8]), font="Arial 12", justify=LEFT).grid(row=3, sticky=W+S)

        gd.mainloop()
    except:
        messagebox.showerror("Error", "Program nie zadziałał, sprawdź czy dane są poprawne!")
        gd.destroy()

# Funkcja ta uruchamia się po naćisnięciu guzika dodatkowe informacje, i informuje użytkownika jak użyć programu
def di():
    di = to("Dodatkowe informacje", "500x150", 1)
    Label(di, text="Autorzy Programu:\n- Cyprian Lazarowski\n- Kacper Karwot\n- Kacper Muszczyński", justify=LEFT,
          font="Arial 12").grid(row=0, sticky=W + S)
    Label(di, text="Plik pdf z dokumentacją programu oraz instrukcjami dla użytkownika:", justify=LEFT,
          font="Arial 12").grid(row=1, sticky=W + S)
    HTMLLabel(di,
              html='<a href="https://drive.google.com/file/d/1veMlgxby2U9pdjgfJptqZTg6EG-FkLUF/view?usp=sharing"> Dokumentacja Programu </a>').grid(
        row=2, sticky=W + S) #zmienić linka bo ten jest do starej dokumentacji
    
    di.mainloop()

# Funkcja wyświetlająca gui startowe
def start_gui():
    root = to("Porównanie", "300x300", 1)

    napis = Label(root, text="Porównanie metody\nPołowienia a Siecznych", height=5, font="Arial 12");
    napis.pack()
    Button(root, text="Edytuj plik", padx=40, pady=10, command=ep).pack()
    Button(root, text="Oblicz dla podanego", padx=13, pady=10, command=odp).pack()
    Button(root, text="Wygeneruj dla podanego", padx=1, pady=10, command=gd).pack()
    Button(root, text="Dodatkowe informacje", padx=8, pady=10, command=di).pack()

    root.mainloop()

start_gui()