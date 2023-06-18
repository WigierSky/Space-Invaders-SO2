# Space-Invaders
Celem projektu było utworzenie aplikacji wykorzystującej wielowątkowość oraz sekcje krytyczne: muteksy lub semafory. 
W rezultacie powstała gra Space-Invaders. Jest to gra zręcznościowa, która przenosi gracza w kosmiczne starcie z najeźdźcami.

Gracz wciela się w rolę pilota statku kosmicznego, który jest jedyną nadzieją Ziemi na powstrzymanie inwazji obcych. 
Na początku gry gracz posiada dwa życia, a jego zadaniem jest unikanie strzałów obcych statków oraz kontratakowanie, eliminując wroga przy pomocy laserowych pocisków. 
Statek gracza porusza się we wszystkich kierunkach, umożliwiając skuteczne manewrowanie wśród wrogich statków i ich ataków.

Wraz z postępami w grze, poziom trudności wzrasta. Statki obcych zaczynają nadlatywać w coraz większych ilościach i ciężej jest je pokonać. 
Gracz musi zachować zręczność i skupienie, aby unikać trafień i jednocześnie zadawać ostateczne ciosy przeciwnikom.

Dodatkowo, statki obcych mogą próbować ominąć nasz statek, co grozi utratą jednego życia. Jeśli gracz nie da rady uniknąć pocisków wroga odejmowane są mu pynkty życia. 

Celem gry jest utrzymanie się przy życiu jak najdłużej. 

# Wizualizacja gry 
![image](https://github.com/WigierSky/Space-Invaders-SO2/assets/92050973/b5edcec8-c530-4b77-b958-0a20da22aae7)

# Wątki 

1. Wątek draw_thr:

- Reprezentuje rysowanie aktualnego stanu gry na ekranie.
- Aktualizuje grafikę w oknie gry, w tym rysuje statki obcych, statek gracza i lasery, a także wyświetla informacje o poziomie i ilości pozostałych żyć.
- Odpowiada za wyświetlanie zmian na ekranie.

2. Wątek lost_thr:

- Reprezentuje sprawdzanie, czy gracz stracił wszystkie życia lub statek gracza został zniszczony.
- Sprawdza, czy liczba żyć wynosi 0 lub zdrowie gracza jest mniejsze lub równe 0, co oznacza koniec gry.
- Ustawia flagę run na False, aby zakończyć pętlę gry.

3. Wątek enemy_thr:

- Reprezentuje sprawdzanie, czy wszyscy wrogowie zostali zniszczeni i tworzenie nowej fali wrogów.
- Sprawdza, czy lista wrogów jest pusta.
- Jeśli tak, inkrementuje poziom gry, tworzy nową falę wrogów i dodaje je do listy wrogów.

4. Wątek enemy_mov_thread:

- Reprezentuje ruch wrogów i strzały wrogich statków.
- Aktualizuje pozycję wrogów, sprawdza kolizje z graczem, usuwa trafionych wrogów, sprawdza, czy wrogowie dotarli do dolnej krawędzi ekranu i aktualizuje ich ruch.
- Dodatkowo, w niektórych przypadkach wrogowie oddają strzały w kierunku gracza.

# Sekcja krytyczna 
W kodzie zastowoswana została jedna sekcja krytyczna.
Linia kodu **semaphore_enemies = threading.Semaphore(1)** tworzy semafor o wartości początkowej 1.
Semafor ten jest używany do synchronizacji dostępu do operacji związanych z tworzeniem i poruszaniem się wrogów. 
