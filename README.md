# Gamma modell


A CA3-as hippokampális régió gamma tartományú tevékenységére készült modell (Brunel network implemented in nest-1.0.13/examples/brunel.sli to use PyNN alapján)

Két esetet különbözetetek meg, a rekurrens kapcsolatokkal ellátott (ca3net8_gamma62_lif.py) és a rekurrens kapcsolatok nélküli  (ca3net8_gamma62_lif_norec.py) hálózatot. Az oszcilláció detektálása 15-50 Hz között történt.(detect_oscillations_15_50.py)


- 3600 piramis sejt (10 alpopulációra osztva)
- 200 kosár sejt
- 200 lassú inhibitoros sejt

A piramissejtek 10 alpopulációra vannak osztva, ez által is hitelesebben modellezve a kérgi tevékenységet, továbbá az alpopulációk jelenléte nélkül nehezebb lenne úgy összekötni a hálózatot, hogy az ne legyen hajlamos túlzottan szinkron működésre. Így még egy szint érvényesülhet az összeköttetések véletlenszerű mivoltában.

Amennyiben a modellt szeretnénk kiegészíteni úgy, hogy az SWR tevékenységet is reprodukáljon, ezt lassú gátló sejtek implementálásával valósíthatjuk meg, melyek a folyamat leállításáért lesznek felelősek.

A piramis és kosár sejtekre vonatkozó adatok egyaránt kísérleti eredményekből származnak, figyelembe véve a CCh jelenléte mellett megfigyelt működés paramétereit egyaránt. 

Annak érdekében, hogy a neuronális heterogenitás jobban érvényesüljön, a principális sejtek nyugalmi membránpotenciálját egy 5 Hz-es szórású, random egyenletes eloszlás alapján felülírjuk.


A piramissejtek külső meghajtásáért a Poisson folyamatok által generált, moha rost (MR) működését imitáló külső bemenet a felelős. Ennek a serkentésnek (MR serkentés) a mértékét fogjuk a szimuláció során egy adott skálán változtatni.
A valóságban piramis és a kosársejtek egyéb külső hajtóerőben is részesülnek, melyek a hippokampuszon kívüli területekről érkeznek, viszont mivel a szimuláció a hippokampális CA3 régió leképezésére szorítkozik, ezért ezeket a bemeneteket nullához közeli értékekkel helyettesítjük, egyedül a magas frekvenciájú moha rostos serkentésre koncentrálva.



# Események közötti időintervallumok (Interevent Interval)

Az Interevent Interval eloszlást a piramissejtek tüzelése alapján számítjuk ki. Egy interevent intervallum a két csúcs közötti eltelt időt ad meg, az előző és az aktuális csúcs közti időintervallumot. (plotiei.m fájlal lehet kirajzolni a Gulyás Attila által futtatott elemzéseket).

# Eredmények

A szimuláció során két különböző esetet hasonlítok össze: a piramissejtek közötti rekurrens kapcsolatok meglétével és annak hiányában végzek \textit{in silico} kísérleteket. A külső bemenetek tartománya a rekurrenssel ellátott esetben [5,100] Hz-es tartományban egyenletes eloszlással 20 adatpont felvételével volt adott, míg a rekurrens nélküli esetben ez a tartomány [10,100] Hz-re mozdult, mivel 10 Hz alatt ilyen feltételek mellett nem volt megfigyelhető jelentős gamma tevékenység. 
Mindegyik MR serkentés értékhez külön hálózati szimuláció tartozik, mely alatt megfigyelésre került a piramis és kosársejtek átlagos tüzelési rátája, illetve az energiaspektrum, a gamma frekvenciás csúcsokra koncentrálva. (gammapower/gammapower_norec.png)




