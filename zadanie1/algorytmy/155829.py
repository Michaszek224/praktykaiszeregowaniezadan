import sys

def main():
    if len(sys.argv) != 4:
        print("Użycie: program.exe dane_wejsciowe plik_wyjsciowy liczba")
        sys.exit(1)

    daneWejsciowe = sys.argv[1]
    plikWyjsciowy = sys.argv[2]
    liczba = sys.argv[3]

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

    wynik = []
    tablicaUzycia = []
    tablicaKonca = []
    for _ in tablicaTowarow:
        tablicaUzycia.append(0)
        tablicaKonca.append(1)


    #algorytm
    koniec = False
    aktualnyCzas = 0
    while not koniec:
        
        index,granica = znajdzNajmniejszyNieuzyty(tablicaTowarow,tablicaUzycia)

        #TODO ogarnij to lepiej
        if granica == 999999:
            tablicaWynikowa = []
            for i,el in enumerate(tablicaTowarow):
                if tablicaUzycia == 0:
                    tablicaWynikowa.append(i)
                    aktualnyCzas += el[0]
        
        tablicaWynikowa = [index+1]

        tablicaUzycia[index] = 1
        aktualnyCzas += tablicaTowarow[index][0]

        while aktualnyCzas < granica:
            index,_ = znajdzNajmniejszyNieuzyty(tablicaTowarow,tablicaUzycia)
            tablicaUzycia[index] = 1
            aktualnyCzas += tablicaTowarow[index][0]
            tablicaWynikowa.append(index+1)
        
        wynik.append(tablicaWynikowa)
        aktualnyCzas += s
        
        if(tablicaKonca == tablicaUzycia):
            koniec = True
    
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

def szukajGranicy(tablicaTowarow,tablicaUzycia,aktualnyCzas):
    najmniejszaWartosc = 999999
    najmniejszyIndex = 0
    for i,el in enumerate(tablicaTowarow):
        if tablicaUzycia[i] == 0:
            if el[1] < najmniejszaWartosc and el[1] > aktualnyCzas:
                najmniejszaWartosc = el[1]
                najmniejszyIndex = i
        
def znajdzNajmniejszyNieuzyty(tablicaTowarow, tablicaUzycia):
    najmniejszaWartosc = 999999
    najmniejszyIndex = 0
    for i,el in enumerate(tablicaTowarow):
        if tablicaUzycia[i] == 0:
            if el[1] < najmniejszaWartosc:
                najmniejszaWartosc = el[1]
                najmniejszyIndex = i
    
    return najmniejszyIndex, najmniejszaWartosc


if __name__ == "__main__":
    main()
