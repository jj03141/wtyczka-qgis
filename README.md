# Wtyczka QGIS
## Opis
Program umożliwia przeprowadzenie w programie QGIS operacji takich jak:
- dla 2 punktów:
  - obliczenie różnicy wysokości
  - obliczenie odległości
  - obliczenie azymutu oraz azymutu odwrotnego
- dla 3 lub więcej punktów:
  - obliczenie pola powierzchni
  - utworzenie nowej warstwy z poligonem
- a także:
  - zliczenie zaznaczonych punktów
  - wczytanie pliku ze współrzędnymi punktów w układzie PL-1992 lub PL-2000
  - czyszczenie otrzymanych wyników
  - odznaczenie wszystkich zaznaczonych punktów
 
 W przypadku wszystkich obliczeń program pozwala na zmianę jednostki przedstawionego wyniku:
 - rożnica wysokości: metry, centymetry, milimetry
 - odległość: metry, kilometry
 - azymut oraz azymut odwrotny: radiany, stopnie, grady
 - pole powierzchni: metry kwadratowe, ary, hektary

## Wymagania
- Python 3.9
- Biblioteki: math, PyQt5
- QGIS 3.28.4

## System operacyjny
Program został napisany dla systemu operacyjnego Windows.

## Instrukcja obsługi
Program umożliwia przeprowadzenie wyżej wymienionych operacji w określonej wersji programu QGIS.
Poniżej opis każdego przycisku, a także instrukcja wczytania pliku.

**Pole wyboru "Aktualna warstwa:"** \
Jest to pole, w którym wybieramy warstwę na której będziemy przeprowadzać operacje w naszej wtyczce.

**Licz elementy** \
Przycisk po wciśnięciu zwraca liczbę zaznaczonych elementów.

**Różnica odległości** \
Przycisk przeznaczony jest dla punktów mających atrybut wysokości oznaczony jako *"h"*.
Po wciśnięciu, z prawej strony przycisku, program wyświetla różnicę wysokości między zaznaczonymi punktami podaną w metrach.
Z prawej strony okna wyświetlają się również trzy przyciski do zmiany jednostki wyświetlanego wyniku. Po wyborze któregoś z nich program powinien 
wyświetlić wynik w odpowiedniej jednostce, gdzie:
- ***[m]***: metry
- ***[cm]***: centymetry
- ***[mm]***: milimetry

**Pole powierzchni** \
Po wciśnięciu, z prawej strony przycisku zostanie wyświetlone pole powierzchni obszaru między zaznaczonymi punktami, podane w metrach kwadratowych.
Pojawią się również, z prawej strony okna, przyciski odpowiedzialne za zmianę jednostki wyświetlanego wyniku. Po wyborze któregoś z nich program powinien 
wyświetlić wynik w odpowiedniej jednostce, gdzie:
- ***[m2]***: metry kwadratowe
- ***[ha]***: hektary
- ***[a]***: ary

**Odległość** \
Po wciśnięciu przycisku, z jego prawej strony zostanie wyświetlona odległość pomiędzy zaznaczonymi punktami, podana w metrach.
Z prawej strony okna pojawią sie przyciski odpowiedzialne za zmianę jednostki wyświetlanego wyniku. Po wyborze któregoś z nich program powinien 
wyświetlić wynik w odpowiedniej jednostce, gdzie:
- ***[m]***: metry
- ***[km]***: kilometry

**Azymut** \
Po wciśnięciu, z prawej strony przycisku zostanie wyświetlona wartość azymutu pomiędzy zaznaczonymi punktami, podana w radianach.
Z prawej strony okna pojawią się przyciski odpowiedzialne za zmianę jednostki wyświetlanego wyniku. Po wyborze któregoś z nich program powinien 
wyświetlić wynik w odpowiedniej jednostce, gdzie: 
- ***[g]***: grady
- ***[deg]***: stopnie
- ***[rad]***: radiany 

Pod wyświetlonym wynikiem pojawi się natomiast przycisk **Azymut odwrotny**. Po wciśnięciu wspomnianego przycisku, na jego miejscu wyświetli się wartość azymutu odwrotnego
a sam przycisk zniknie. Po wyborze, któregoś z przycisków radiowych, odpowiedzialnych za zmianę jednostki wyświetlanego wyniku, obie wartości tj.: azymutu i azymutu odwrotnego
zostaną przedstawione w odpowiedniej jednostce.

**Rysuj poligon** \
Przycisk odpowiedzialny jest za dodanie nowej warstwy z narysowanym poligonem łączącym zaznaczone punkty.

**Wyczyść wyniki** \
Po użyciu przycisku wszystkie wyświetlane wyniki zostają usunięte. Także wszystkie komunikaty o wynikach lub błędach, wyświetlone w górnej części interfejsu QGIS
zostają usunięte.

**Odznacz wszystko** \
Odznacza wszystkie zaznaczone punkty.

**Wczytaj plik** \
Przycisk odpowiedzialny za wczytanie pliku .txt lub .csv zawierającego współrzędne punktów. Powinny być one umieszczone w pliku w sposób taki, że wspołrzędne każdego kolejnego punktu
są zawarte w nowym wierszu, współrzędne są w kolejności X,Y, separatorem dziesiętnym jest kropka, a separatorem oddzielającym współrzędną X od Y przecinek. Poniżej przykład dla układu PL-1992: \
*521912.62,610971.36* \
*521918.62,610973.36* \
*521915.62,610977.36* \
*521920.62,610977.36* \
*521940.62,610981.36* \
Po naciśnięciu przycisku program wyświetli nam okno wyboru, w którym musimy wybrać układ w jakim chcemy wprowadzić nasze współrzędne. Jeśli wybierzemy układ program wyświetli
okno, w którym mamy możliwość wyboru pliku z dowolnego miejsca na naszym urządzeniu. W przypadku układu PL-1992 po wybraniu pliku program wczyta i wyświetli punkty na nowo utworzonej warstwie.
Jednak w przypadku układu PL-2000, po wyborze pliku program zapyta nas o strefę w jakiej są położone wprowadzane punkty. Po wybraniu odpowiedniej strefy z czterech możliwych (*strefa 5, strefa 6, strefa 7, strefa 8)*,
program wczyta i wyświetli punkty na nowo utworzonej warstwie.

## Znane błędy i nietypowe zachowania
- w przypadku gdy użytkownik wybierze opcję **Różnica wysokośći, Odległość** lub **Azymut** mając zaznaczoną inną ilość punktów niż 2 program wyświetli komunikat na dole okna:
*"Zaznacz dokładnie 2 punkty!"*
- jeśli punkty wybrane przez użytkownika do obliczenia różnicy wysokości nie posiadają atrybutu wysokości
program wyświetli ostrzeżenie w głównym interfejsie QGIS oraz komunikat na dole okna: *"Wybrane punkty nie mają atrybutu wysokości."*
- w przypadku gdy użytkownik wybierze dwa punkty o tych samych współrzędnych i skorzysta z opcji **Azymut**, program wyświetli komunikat na dole okna: *"Punkty są identyczne!*
- w przypadku korzystania z przycisku **Pole powierzchni**, jeśli użytkownik ma zaznaczone mniej niż 3 punkty program wyświetli komunikat na dole okna: *"Zaznacz więcej punktów"*
- podobnie w przypadku funkcji **Rysuj poligon**, jeśli liczba zaznaczonych punktów jest mniejsza niż 3, program wyświetli komunikat na dole okna: *"Za mało punktów"*
- jeśli po wciśnięciu przycisku **Rysuj poligon** program wyświetli któryś z błędów:
  - *"Nieprawidłowa geometria poligonu"*
  - *"Nie udało się utworzyć warstwy poligonowej"*
  - *"Nie udało się dodać funkcji do warstwy poligonowej"* 

  oznacza to że prawdopodobnie utworzenie poligonu dla wybranych punktów jest niemożliwe.
 - w przypadku użycia funkcji **Wczytaj plik** dla pliku mającego więcej niż dwie kolumny danych lub z błędnie oddzielonymi współrzędnymi program wyświetli ostrzeżenie w głównym interfejsie
 programu QGIS: *"Wybrany plik ma więcej niż 2 kolumny danych."*
 - jeśli podczas próby wczytania pliku z danymi za pomocą **Wczytaj plik**, w interfejsie głównym QGIS pojawi się komunikat błędu konwersji: *"Wystąpił błąd podczas konwersji współrzędnych."*
 należy ponowić próbę wczytania pliku lub sprawdzić czy jest ma on poprawną formę.

