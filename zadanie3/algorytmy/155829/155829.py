import sys
import copy
import threading
import time
import os

if len(sys.argv) != 4:
        print("Użycie: program.exe dane_wejsciowe plik_wyjsciowy liczba")
        sys.exit(1)

czas = int(sys.argv[3])
    
daneWejsciowe = sys.argv[1]
plikWyjsciowy = sys.argv[2]

def main():

    tablicaZadan = []
    tablicaS = []
    nDoLiczenia = 0


    with open(daneWejsciowe) as plik:
        PierwszaLinia = True
        for line in plik:
            if PierwszaLinia:
                liczba = line.split()
                n = int(liczba[0])
                PierwszaLinia = False
            elif nDoLiczenia < n :
                liczby = line.split()
                tablicaTmp = []
                for el in liczby:
                    tablicaTmp.append(int(el))
                tablicaZadan.append(tablicaTmp)
                nDoLiczenia += 1
            else:
                liczby = line.split()
                tablicaTmp = []
                for el in liczby:
                    tablicaTmp.append(int(el))
                tablicaS.append(tablicaTmp)
    
    wynik = []

    czasPierwszy = 0
    tablicaUzytych = []
    for i in range(n):
        tablicaUzytych.append(0)

    najmniejszeR = 99999
    zapamietaneI = 0
    #ulozeniePierwszego
    for i in range(n):
        if tablicaZadan[i][4] == 0:
            tablicaUzytych[i] = 1
            czasPierwszy += tablicaUzytych[0]
            wynik.append(i+1)
            break
        elif tablicaZadan[i][4] < najmniejszeR:
            najmniejszeR = tablicaZadan[i][4]
            zapamietaneI = i
    if 1 not in tablicaUzytych:
        czasPierwszy = najmniejszeR + tablicaZadan[zapamietaneI][0]
        tablicaUzytych[zapamietaneI] = 1
        wynik.append(zapamietaneI+1)

    for _ in range(n-1):
        tablicaAktualnych = []
        for j,el in enumerate(tablicaZadan):
            if el[4] < czasPierwszy and tablicaUzytych[j] == 0:
                tablicaAktualnych.append(j)
        najmniejszeS = 9999
        zapamietaneJ = 0
        przetwarzanyNumer = wynik[-1]
        indexNumeru = przetwarzanyNumer-1
        if tablicaAktualnych != []:
            for el in tablicaAktualnych:
                if tablicaS[indexNumeru][el] < najmniejszeS:
                    najmniejszeS = tablicaS[indexNumeru][el]
                    zapamietaneJ = el
                
            wynik.append(zapamietaneJ+1)
            czasPierwszy += najmniejszeS + tablicaZadan[zapamietaneJ][0]
            tablicaUzytych[zapamietaneJ] = 1
        else:
            for i,el in enumerate(tablicaUzytych):
                if el == 0:
                    wynik.append(i+1)
                    czasPierwszy += tablicaS[wynik[-2]-1][wynik[-1]-1] + tablicaZadan[i][0]
                    tablicaUzytych[i] = 1
                    break

    #obliczanie Kryterium

    obliczoneKryterium = 0
    czasyMaszyn = [tablicaZadan[wynik[0]-1][0]+tablicaZadan[wynik[0]-1][4],0,0,0]
    #pierwsze wykonanie
    for i in range(3):
        czasyMaszyn[i+1] = czasyMaszyn[i] + tablicaZadan[wynik[0]-1][i+1]

    for i in range(n-1):
        rozwazaneZadanie = wynik[i+1]
        poprzednieZadanie = wynik[i]
        indeksRozwazanegoZadania = rozwazaneZadanie-1
        indeksPoprzedniegoZadania = poprzednieZadanie-1
        
        czasyMaszyn[0] += tablicaS[indeksPoprzedniegoZadania][indeksRozwazanegoZadania]
        if czasyMaszyn[0] <= tablicaZadan[indeksRozwazanegoZadania][4]:
            czasyMaszyn[0] = tablicaZadan[indeksRozwazanegoZadania][4]+tablicaZadan[indeksRozwazanegoZadania][0]
        else:
            czasyMaszyn[0] += tablicaZadan[indeksRozwazanegoZadania][0]
        for j in range(3):
            #najpierw dodanie przestawienia maszyny
            czasyMaszyn[j+1] += tablicaS[indeksPoprzedniegoZadania][indeksRozwazanegoZadania]
            if czasyMaszyn[j+1] < czasyMaszyn[j]:
                czasyMaszyn[j+1] = czasyMaszyn[j] + tablicaZadan[indeksRozwazanegoZadania][j+1]
            else:
                czasyMaszyn[j+1] += tablicaZadan[indeksRozwazanegoZadania][j+1]
    obliczoneKryterium = czasyMaszyn[3]

    #zapisanie Wyniku
    with open(plikWyjsciowy,'w') as plik:
        plik.write(str(obliczoneKryterium))
        plik.write('\n')
        linia = ""
        for el in wynik:
            linia += str(el) + ' '
        plik.write(linia)

        

if __name__ == "__main__":
    main()