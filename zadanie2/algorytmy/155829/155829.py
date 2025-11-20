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

    for el in posortowane:
        for i,eli in enumerate(tablicaAktualnychCzasow):
            if eli <= el[1][1]:
                tablicaAktualnychCzasow[i] = tablicaAktualnychCzasow[i] + el[1][0]
                tablicaWyniku[i].append(el[0]+1)
                ktoreuzyte[el[0]] = 1
                break
    
    for i,el in enumerate(ktoreuzyte):
        if el == 0:
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
