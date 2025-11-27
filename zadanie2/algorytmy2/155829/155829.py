import sys
import copy
import threading
import time
import os


czas = int(sys.argv[3])
    
daneWejsciowe = sys.argv[1]
plikWyjsciowy = sys.argv[2]

global wynik
lock = threading.Lock()

def obliczanieWyniku(tablicaWyniku,tablicaAut):

    obliczoneKryterium = 0

    for el in tablicaWyniku:
        pierwszaLiczba = True
        aktualnyCzas = 0
        for liczba in el:
            if pierwszaLiczba:
                obliczoneKryterium += tablicaAut[liczba-1][0] * tablicaAut[liczba-1][2]
                aktualnyCzas = tablicaAut[liczba-1][1] + tablicaAut[liczba-1][0]
                pierwszaLiczba = False
            else:
                if tablicaAut[liczba-1][1] > aktualnyCzas:
                    obliczoneKryterium += tablicaAut[liczba-1][0] * tablicaAut[liczba-1][2]
                    aktualnyCzas = tablicaAut[liczba-1][1] + tablicaAut[liczba-1][0]
                else:
                    obliczoneKryterium += (aktualnyCzas - tablicaAut[liczba-1][1] + tablicaAut[liczba-1][0])*tablicaAut[liczba-1][2]
                    aktualnyCzas += tablicaAut[liczba-1][0]
    return obliczoneKryterium

def znajdzElement(tablicaWynikowa,element):
    for maszyna,el in enumerate(tablicaWynikowa):
        for index,eli in enumerate(el):
            if eli == element:
                return maszyna,index

def main():
    if len(sys.argv) != 4:
        print("Użycie: program.exe dane_wejsciowe plik_wyjsciowy liczba")
        sys.exit(1)

    global wynik
    tablicaAut = []
    n = 0
    LiniaPierwsza = True

    with open(daneWejsciowe) as plik:
        for line in plik:
            if LiniaPierwsza:
                liczba = line.split()
                n = int(liczba[0])
                LiniaPierwsza = False
            else:
                liczby = line.split()
                if len(liczby) > 0:
                    liczby[0] = int(liczby[0])
                    liczby[1] = int(liczby[1])
                    liczby[2] = int(liczby[2])
                    tablicaAut.append(liczby)
    

    tablicaAutZIndeksami = list(enumerate(tablicaAut))

    posortowane = sorted(tablicaAutZIndeksami, key=lambda x: x[1][1])


    tablicaAktualnychCzasow = [0,0,0,0]
    tablicaWyniku = [[],[],[],[]]

    ktoreuzyte = []
    for i in range (n):
        ktoreuzyte.append(0)

    #pierwotne ulozenie
    for el in posortowane:
        for i,eli in enumerate(tablicaAktualnychCzasow):
            if eli <= el[1][1]:
                tablicaAktualnychCzasow[i] = tablicaAktualnychCzasow[i] + el[1][0]
                tablicaWyniku[i].append(el[0]+1)
                ktoreuzyte[el[0]] = 1
                break
    
    for i,el in enumerate(ktoreuzyte):
        if el == 0:
            #algorytm dodawania do wyniku
            kopiaTablicyWyniku = copy.deepcopy(tablicaWyniku)
            kopiaTablicyWyniku[0].insert(0,i+1)
            kryteriumPoczatkowe = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
            wybranaMaszyna = 0
            kopiaTablicyWyniku[0].pop(0)
            for j in range(3):
                
                kopiaTablicyWyniku[j+1].insert(0,i+1)
                kryteriumTmp = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                if kryteriumTmp < kryteriumPoczatkowe:
                    kryteriumPoczatkowe =kryteriumTmp
                    wybranaMaszyna = j+1
                kopiaTablicyWyniku[j+1].pop(0)

            wybranyIndex = 0
            for j in range(len(tablicaWyniku[wybranaMaszyna])):
                kopiaTablicyWyniku[wybranaMaszyna].insert(j+1,i+1)
                kryteriumTmp = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                if kryteriumTmp > kryteriumPoczatkowe:
                    break
                else:
                    kryteriumPoczatkowe = kryteriumTmp
                    wybranyIndex = j+1
                    kopiaTablicyWyniku[wybranaMaszyna].pop(j+1)
            
            tablicaWyniku[wybranaMaszyna].insert(wybranyIndex,i+1)
    with lock: 
        wynik = tablicaWyniku

    
    
    for i in range(n):
            elementRozwazany = i+1
            indeksMaszyny,indeks = znajdzElement(tablicaWyniku,elementRozwazany)

            tablicaWyniku[indeksMaszyny].pop(indeks)
            kopiaTablicyWyniku = copy.deepcopy(tablicaWyniku)

            kopiaTablicyWyniku[0].insert(0,elementRozwazany)
            kryteriumPoczatkowe = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
            kopiaTablicyWyniku[0].pop(0)
            zapisanyIndeks = 0
            zapisanaMaszyna = 0
            #patrzymy po kazdej maszynie
            for maszyna,el in enumerate(kopiaTablicyWyniku):

                kopiaTablicyWyniku[maszyna].insert(0,elementRozwazany)
                kryteriumTmp = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                kopiaTablicyWyniku[maszyna].pop(0)
                zapisanyIndeksTmp = 0
                #i kazde miejsce w maszynie
                for indeks,eli in enumerate(el):
                    kopiaTablicyWyniku[maszyna].insert(indeks+1,elementRozwazany)
                    kryteriumTmp2 = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                    if kryteriumTmp2 > kryteriumTmp:
                        kopiaTablicyWyniku[maszyna].pop(indeks+1)
                        #break
                    else:
                        kryteriumTmp = kryteriumTmp2
                        zapisanyIndeksTmp = indeks+1
                        kopiaTablicyWyniku[maszyna].pop(indeks+1)
                if kryteriumTmp < kryteriumPoczatkowe:
                    kryteriumPoczatkowe = kryteriumTmp
                    zapisanyIndeks = zapisanyIndeksTmp
                    zapisanaMaszyna = maszyna
            tablicaWyniku[zapisanaMaszyna].insert(zapisanyIndeks,elementRozwazany)
            with lock:
                wynik = tablicaWyniku

    poczatkowy = obliczanieWyniku(tablicaWyniku,tablicaAut)
    for _ in range (1000):
        
        for i in range(n):
            elementRozwazany = i+1
            indeksMaszyny,indeks = znajdzElement(tablicaWyniku,elementRozwazany)

            tablicaWyniku[indeksMaszyny].pop(indeks)
            kopiaTablicyWyniku = copy.deepcopy(tablicaWyniku)

            kopiaTablicyWyniku[0].insert(0,elementRozwazany)
            kryteriumPoczatkowe = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
            kopiaTablicyWyniku[0].pop(0)
            zapisanyIndeks = 0
            zapisanaMaszyna = 0
            #patrzymy po kazdej maszynie
            for maszyna,el in enumerate(kopiaTablicyWyniku):

                kopiaTablicyWyniku[maszyna].insert(0,elementRozwazany)
                kryteriumTmp = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                kopiaTablicyWyniku[maszyna].pop(0)
                zapisanyIndeksTmp = 0
                #i kazde miejsce w maszynie
                for indeks,eli in enumerate(el):
                    kopiaTablicyWyniku[maszyna].insert(indeks+1,elementRozwazany)
                    kryteriumTmp2 = obliczanieWyniku(kopiaTablicyWyniku,tablicaAut)
                    if kryteriumTmp2 > kryteriumTmp:
                        kopiaTablicyWyniku[maszyna].pop(indeks+1)
                        #break
                    else:
                        kryteriumTmp = kryteriumTmp2
                        zapisanyIndeksTmp = indeks+1
                        kopiaTablicyWyniku[maszyna].pop(indeks+1)
                if kryteriumTmp < kryteriumPoczatkowe:
                    kryteriumPoczatkowe = kryteriumTmp
                    zapisanyIndeks = zapisanyIndeksTmp
                    zapisanaMaszyna = maszyna
            tablicaWyniku[zapisanaMaszyna].insert(zapisanyIndeks,elementRozwazany)
            with lock:
                
                wynik = tablicaWyniku

        koncowy = obliczanieWyniku(tablicaWyniku,tablicaAut)
        if poczatkowy == koncowy:
            break
        else:
            poczatkowy = koncowy

    # przestawanie
    poczatkowy = obliczanieWyniku(tablicaWyniku, tablicaAut)

    for _ in range(1000):

        ulepszenie = False

        for i in range(n):
            element1 = i + 1
            pos1 = znajdzElement(tablicaWyniku, element1)
            if pos1 is None:
                continue
            masz1, idx1 = pos1

            przedZamiana = obliczanieWyniku(tablicaWyniku, tablicaAut)

            najlepsza_zamiana = None
            najlepszy_wynik = przedZamiana

            for j in range(i+1, n):
                element2 = j + 1
                pos2 = znajdzElement(tablicaWyniku, element2)
                if pos2 is None:
                    continue
                masz2, idx2 = pos2

                # --- wykonujemy zamianę NA KOPII ---
                kopia = copy.deepcopy(tablicaWyniku)

                kopia[masz1][idx1], kopia[masz2][idx2] = kopia[masz2][idx2], kopia[masz1][idx1]

                wynik_po = obliczanieWyniku(kopia, tablicaAut)

                if wynik_po < najlepszy_wynik:
                    najlepszy_wynik = wynik_po
                    najlepsza_zamiana = (masz1, idx1, masz2, idx2)

            # wykonujemy najlepszą znalezioną zamianę
            if najlepsza_zamiana is not None:
                masz1, idx1, masz2, idx2 = najlepsza_zamiana
                tablicaWyniku[masz1][idx1], tablicaWyniku[masz2][idx2] = tablicaWyniku[masz2][idx2], tablicaWyniku[masz1][idx1]
                ulepszenie = True

        if not ulepszenie:
            break







    with open(plikWyjsciowy,'w') as plik:

        opoznienie = obliczanieWyniku(tablicaWyniku,tablicaAut)
        plik.write(str(opoznienie))
        plik.write('\n')

        for el in tablicaWyniku:
            linia = ""
            for eli in el:
                linia += str(eli)
                linia += ' '
            plik.write(linia)
            plik.write('\n')
    
    os._exit(0)
        


def zapisz_wynik():
    #zapisywanie wyniku
    with lock:
        tablicaAut = []
        n = 0
        LiniaPierwsza = True

        with open(daneWejsciowe) as plik:
                for line in plik:
                    if LiniaPierwsza:
                        liczba = line.split()
                        n = int(liczba[0])
                        LiniaPierwsza = False
                    else:
                        liczby = line.split()
                        if len(liczby) > 0:
                            liczby[0] = int(liczby[0])
                            liczby[1] = int(liczby[1])
                            liczby[2] = int(liczby[2])
                            tablicaAut.append(liczby)

        global wynik

        with open(plikWyjsciowy,'w') as plik:

            opoznienie = obliczanieWyniku(wynik,tablicaAut)
            plik.write(str(opoznienie))
            plik.write('\n')

            for el in wynik:
                linia = ""
                for eli in el:
                    linia += str(eli)
                    linia += ' '
                plik.write(linia)
                plik.write('\n')
        os._exit(0)

if __name__ == "__main__":

    timer = threading.Timer(czas-1,zapisz_wynik)
    timer.start()
    main()
