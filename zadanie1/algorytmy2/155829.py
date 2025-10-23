import sys
import copy
import threading
import time
import os


liczba = int(sys.argv[3])
    
daneWejsciowe = sys.argv[1]
plikWyjsciowy = sys.argv[2]

global wynik
wynik = []
lock = threading.Lock()

def main():
    if len(sys.argv) != 4:
        print("Użycie: program.exe dane_wejsciowe plik_wyjsciowy liczba")
        sys.exit(1)

    

    tablicaTowarow = []
    s = 0
    numerLinii = 0
    with open(daneWejsciowe) as plik:
        
        for line in plik:
            if numerLinii == 0:
                liczby = line.split()
                s = int(liczby[1])
                numerLinii += 1
            else:
                liczby = line.split()
                liczby[0] = int(liczby[0])
                liczby[1] = int(liczby[1])
                tablicaTowarow.append(liczby)

    tablicaUzycia = []
    tablicaKonca = []
    for i in tablicaTowarow:
        tablicaUzycia.append(0)
        tablicaKonca.append(1)
        global wynik
        wynik.append([i])


    #algorytm
    #poczatkowe wlozenie do kazdego po jednym

    posortowane = sorted(enumerate(tablicaTowarow, start=1), key=lambda x: x[1][1])
    with lock:
        wynik = [[i] for i, _ in posortowane]

    #patrzenie czy mozna polepszyc
    #najpierw prubujemy wlozyc do poprzednich
    koniec = False
    indexzmiany = 0
    while not koniec:
        koniec = True
        for i in range(indexzmiany+1,len(wynik)):
            
            opoznienie = liczOpoznienie(tablicaTowarow,wynik,s)

            wynik2 = copy.deepcopy(wynik)

            wynik2[indexzmiany].append(wynik2[i][0])
            wynik2.pop(i)
            opoznienie2 = liczOpoznienie(tablicaTowarow,wynik2,s)

            if(opoznienie2 < opoznienie):
                with lock:
                    wynik = wynik2
                koniec = False
                break
        if koniec == True and indexzmiany < len(wynik):
            indexzmiany += 1
            koniec = False


    
    
    with open(plikWyjsciowy,'w') as plik:

        opoznienie = liczOpoznienie(tablicaTowarow,wynik,s)
        plik.write(str(opoznienie))
        plik.write('\n')

        
        plik.write(str(len(wynik)))
        plik.write('\n')
        for el in wynik:
            linia = ""
            for eli in el:
                linia += str(eli)
                linia += ' '
            plik.write(linia)
            plik.write('\n')
    os._exit(0)

def liczOpoznienie(tablicaTowarow,tablicaWynikowa,s):
    opoznienie = 0
    liczbaCzasu = 0
    for el in tablicaWynikowa:
        for eli in el:
            liczbaCzasu += tablicaTowarow[eli-1][0]

        for eli in el:
            if liczbaCzasu > tablicaTowarow[eli-1][1]:
                opoznienie = opoznienie+ liczbaCzasu - tablicaTowarow[eli-1][1]
        liczbaCzasu += s

    return opoznienie

def zapisz_wynik():
    with lock:
        tablicaTowarow = []
        s = 0
        numerLinii = 0
        with open(daneWejsciowe) as plik:
            
            for line in plik:
                if numerLinii == 0:
                    liczby = line.split()
                    s = int(liczby[1])
                    numerLinii += 1
                else:
                    liczby = line.split()
                    liczby[0] = int(liczby[0])
                    liczby[1] = int(liczby[1])
                    tablicaTowarow.append(liczby)

        with open(plikWyjsciowy,'w') as plik:

            opoznienie = liczOpoznienie(tablicaTowarow,wynik,s)
            plik.write(str(opoznienie))
            plik.write('\n')

            
            plik.write(str(len(wynik)))
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

    timer = threading.Timer(liczba-1,zapisz_wynik)
    timer.start()
    main()
