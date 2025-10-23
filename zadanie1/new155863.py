import os
import sys
import time

def algorytm(input_path, output_path, czas):
    start = time.time()
    
    # Wczytywanie danych
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                print(f"Błąd: Plik wejściowy '{input_path}' jest pusty.")
                return

            n, s = map(int, lines[0].split())
            
            zadania = []
            for i in range(n):
                czas_zamowienia, deadline = map(int, lines[i + 1].split())
                zadania.append({
                    'id': i + 1, 
                    'czas_zamowienia': czas_zamowienia, 
                    'deadline': deadline,
                    'slack': deadline - czas_zamowienia  # Zapas czasu
                })

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego '{input_path}'.")
        return
    except (ValueError, IndexError):
        print(f"Błąd: Nieprawidłowy format danych w pliku '{input_path}'.")
        return

    # Przetwarzanie po wczytaniu
    if not zadania:
        wszystkie_batche = []
        opoznienie_calkowite = 0
    else:
        zadania.sort(key=lambda x: (x['deadline'], x['slack'], x['czas_zamowienia']))
        
        wszystkie_batche = []
        obecny_batch = []
        czas_w_batchu = 0
        obecny_czas = 0
        
        for idx, zadanie in enumerate(zadania):
            czas_zadania = zadanie['czas_zamowienia']
            
            if not obecny_batch:
                obecny_batch.append(zadanie)
                czas_w_batchu = czas_zadania
            else:
                
                czas_ukonczenia_w_batchu = obecny_czas + czas_w_batchu + czas_zadania
                opoznienie_w_batchu = max(0, czas_ukonczenia_w_batchu - zadanie['deadline'])
                
                koszt_przedluzenia = 0
                for z in obecny_batch:
                    stare_ukonczenie = obecny_czas + czas_w_batchu
                    nowe_ukonczenie = obecny_czas + czas_w_batchu + czas_zadania
                    stare_opoznienie = max(0, stare_ukonczenie - z['deadline'])
                    nowe_opoznienie = max(0, nowe_ukonczenie - z['deadline'])
                    koszt_przedluzenia += (nowe_opoznienie - stare_opoznienie)
                
                lookahead_bonus = 0
                if idx + 1 < len(zadania):
                    nastepne = zadania[idx + 1]
                    if abs(nastepne['deadline'] - zadanie['deadline']) < s:
                        lookahead_bonus = -s * 0.3
                
                koszt_scenariusz1 = opoznienie_w_batchu + koszt_przedluzenia + lookahead_bonus
                
                czas_ukonczenia_nowy_batch = obecny_czas + czas_w_batchu + s + czas_zadania
                opoznienie_nowy_batch = max(0, czas_ukonczenia_nowy_batch - zadanie['deadline'])
                
                kara_dlugosc = 0
                if len(obecny_batch) > 5:
                    kara_dlugosc = len(obecny_batch) * 0.1
                
                koszt_scenariusz2 = opoznienie_nowy_batch + kara_dlugosc
                
                if koszt_scenariusz1 <= koszt_scenariusz2:
                    obecny_batch.append(zadanie)
                    czas_w_batchu += czas_zadania
                else:
                    wszystkie_batche.append(obecny_batch)
                    obecny_czas += czas_w_batchu + s
                    obecny_batch = [zadanie]
                    czas_w_batchu = czas_zadania
        
        if obecny_batch:
            wszystkie_batche.append(obecny_batch)
        
        for batch in wszystkie_batche:
            batch.sort(key=lambda x: (x['deadline'], x['czas_zamowienia']))
        
        def oblicz_opoznienie_total(batche):
            opoznienie = 0
            czas = 0
            for i, batch in enumerate(batche):
                batch_czas = sum(z['czas_zamowienia'] for z in batch)
                czas += batch_czas
                for z in batch:
                    opoznienie += max(0, czas - z['deadline'])
                if i < len(batche) - 1:
                    czas += s
            return opoznienie
        
        def oblicz_opoznienie_batch(batch, czas_start):
            """Oblicza opóźnienie dla pojedynczego batch'a"""
            opoznienie = 0
            czas = czas_start + sum(z['czas_zamowienia'] for z in batch)
            for z in batch:
                opoznienie += max(0, czas - z['deadline'])
            return opoznienie
        
        #przesuwanie zadann miedzy batrchami
        if time.time() - start > czas * 0.7:
            pass  # jesl i nie ma czasu to skip, chwile poczekacie
        else:
            # 
            max_iteracji = 5
            for iteracja in range(max_iteracji):
                if time.time() - start > czas * 0.7:
                    break
                
                zmieniono = False
                
                for i in range(len(wszystkie_batche) - 1):
                    if not wszystkie_batche[i] or not wszystkie_batche[i+1]:
                        continue
                    
                    # ostatnie zadanie z batch do batch +1
                    if len(wszystkie_batche[i]) > 1:
                        opoznienie_przed = oblicz_opoznienie_total(wszystkie_batche)
                        
                        zadanie = wszystkie_batche[i].pop()
                        wszystkie_batche[i+1].insert(0, zadanie)
                        wszystkie_batche[i+1].sort(key=lambda x: (x['deadline'], x['czas_zamowienia']))
                        
                        opoznienie_po = oblicz_opoznienie_total(wszystkie_batche)
                        
                        if opoznienie_po < opoznienie_przed:
                            zmieniono = True
                        else:
                            wszystkie_batche[i+1].remove(zadanie)
                            wszystkie_batche[i].append(zadanie)
                    
                    # wstecz
                    if len(wszystkie_batche[i+1]) > 1:
                        opoznienie_przed = oblicz_opoznienie_total(wszystkie_batche)
                        
                        zadanie = wszystkie_batche[i+1].pop(0)
                        wszystkie_batche[i].append(zadanie)
                        wszystkie_batche[i].sort(key=lambda x: (x['deadline'], x['czas_zamowienia']))
                        
                        opoznienie_po = oblicz_opoznienie_total(wszystkie_batche)
                        
                        if opoznienie_po < opoznienie_przed:
                            zmieniono = True
                        else:
                            wszystkie_batche[i].remove(zadanie)
                            wszystkie_batche[i+1].insert(0, zadanie)
                
                if not zmieniono:
                    break
            
            # laczneie batchy w wieksze
            if time.time() - start < czas * 0.75:
                i = 0
                while i < len(wszystkie_batche) - 1:
                    if time.time() - start > czas * 0.75:
                        break
                    
                    if len(wszystkie_batche[i]) <= 3 and len(wszystkie_batche[i+1]) <= 3:
                        opoznienie_przed = oblicz_opoznienie_total(wszystkie_batche)
                        
                        polaczony = wszystkie_batche[i] + wszystkie_batche[i+1]
                        polaczony.sort(key=lambda x: (x['deadline'], x['czas_zamowienia']))
                        
                        wszystkie_batche[i] = polaczony
                        wszystkie_batche.pop(i+1)
                        
                        opoznienie_po = oblicz_opoznienie_total(wszystkie_batche)
                        
                        if opoznienie_po < opoznienie_przed:
                            continue
                        else:
                            # jesli jest gorzej to cofnij
                            wszystkie_batche.insert(i+1, polaczony[len(wszystkie_batche[i]):])
                            wszystkie_batche[i] = polaczony[:len(wszystkie_batche[i])]
                    
                    i += 1
            
            # zamina roznych bachy w celu prownania
            if time.time() - start < czas * 0.85:
                for _ in range(2):
                    if time.time() - start > czas * 0.85:
                        break
                    
                    zmieniono = False
                    for i in range(len(wszystkie_batche)):
                        for j in range(i + 2, len(wszystkie_batche)):
                            if time.time() - start > czas * 0.85:
                                break
                            
                            # zamiana batch i z j i prowonainae
                            opoznienie_przed = oblicz_opoznienie_total(wszystkie_batche)
                            
                            wszystkie_batche[i], wszystkie_batche[j] = wszystkie_batche[j], wszystkie_batche[i]
                            
                            opoznienie_po = oblicz_opoznienie_total(wszystkie_batche)
                            
                            if opoznienie_po < opoznienie_przed:
                                zmieniono = True
                            else:
                                # Cofnij
                                wszystkie_batche[i], wszystkie_batche[j] = wszystkie_batche[j], wszystkie_batche[i]
                    
                    if not zmieniono:
                        break
        
        #oblcizanie opoznienia
        opoznienie_calkowite = 0
        czas_ukonczenia = 0
        
        for i, batch in enumerate(wszystkie_batche):
            batch_p_sum = sum(zadanie['czas_zamowienia'] for zadanie in batch)
            czas_ukonczenia += batch_p_sum
            
            for zadanie in batch:
                tardiness = max(0, czas_ukonczenia - zadanie['deadline'])
                opoznienie_calkowite += tardiness
            
            if i < len(wszystkie_batche) - 1:
                czas_ukonczenia += s

    end = time.time()
    if end - start > czas:
        print("za duzo czasu")
        return 
    
    # zapis plik do
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w') as f_out:
            f_out.write(f"{opoznienie_calkowite}\n")
            f_out.write(f"{len(wszystkie_batche)}\n")
            for batch in wszystkie_batche:
                line = ' '.join(str(zadanie['id']) for zadanie in batch)
                f_out.write(f"{line}\n")
        
        print(f"opoznienie: {opoznienie_calkowite}, czas: {end-start:.2f}s")

    except IOError as e:
        print(f"Błąd podczas zapisu do pliku '{output_path}': {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia: python 155863.py <plik_wejsciowy> <index> <plik_wyjsciowy> <limit_czasu>")
        sys.exit(1)

    plik_wejsciowy = sys.argv[1]
    wyniki = sys.argv[2]
    czas = float(sys.argv[3])
    
        
    algorytm(plik_wejsciowy, wyniki, czas)