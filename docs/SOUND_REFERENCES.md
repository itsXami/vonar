# VOLT – wzorce brzmień

Wzorce wskazane przez użytkownika jako punkt odniesienia dla kolejnych partii presetów (etap D). **To wyłącznie
opis charakteru dźwięku.** Niczego nie kopiujemy: ani parametrów, ani wavetable, ani nazw. Każdy preset VOLT jest
projektowany od zera na silniku VOLT, a nazwy wzorców nie trafiają do nazw, tagów ani opisów presetów
(zasady w `.claude/skills/preset-design/SKILL.md`).

Jak korzystać: przed planem partii przeczytaj wzorce dla danej kategorii i zapisz w planie, które presety mają
iść w stronę którego charakteru. Wzorzec wyznacza kierunek dla kilku presetów w partii, nie dla wszystkich –
partia nadal musi być różnorodna i przejść pomiar podobieństwa.

## Keys

| Wzorzec (źródło) | Charakter | Co to znaczy dla presetu VOLT |
|---|---|---|
| Vital – „Chorusy Keys” | Miękkie elektryczne pianino z falującym chorusem. | Łagodny atak bez kliku, dzwoneczkowo-okrągła barwa pianina elektrycznego, średni zanik; chorus wyraźnie słyszalny jako powolne falowanie i szerokość stereo, a nie subtelny dodatek; velocity dodaje jasności („bark”), nie tylko głośności. |
| Vital – „Smoker Lounge” | Ciemne, ciepłe, lekko lo-fi barowe klawisze bez ostrego ataku. | Stłumiona góra (filtr nisko, mało wysokich harmonicznych), ciepły dół i środek, zaokrąglony atak; lekkie „zużycie”: delikatne nasycenie, drobne pływanie stroju lub szum, krótki, ciemny pokój zamiast błyszczącego pogłosu; nastrój spokojny, nocny. |

## Wzorce z Roland Zenology (nagranie użytkownika, 2026-11-12)

Użytkownik nagrał 9 presetów jednym ciągiem (ok. 2 min, MP3). Nagranie nie jest w repo – to dźwięk cudzego
instrumentu, służy tylko do opisu charakteru. Poniżej pomiary z nagrania (środek widma, udział pasm, ruch barwy,
atak, szerokość stereo) i odczyt ze spektrogramu. Interpretacje „co to znaczy dla VOLT” są Claude’a, nie
użytkownika; pomiary zależą też od tego, jak i w jakim rejestrze grał.

**Wspólny mianownik wszystkich 9:** ciepło i ciemno. Środek widma 250–830 Hz, prawie cała energia poniżej 1 kHz,
góra powyżej 3 kHz śladowa (najwyżej 3–4 % energii, poza przesterowaną gitarą). Do tego dwa wcześniejsze wzorce
Keys z Vitala też są ciepłe i miękkie. Wniosek dla etapu D: domyślnie projektować od strony ciepłej (niższy cutoff,
miękki atak, mało „powietrza”), a jasne brzmienia traktować jako wyjątki w partii, nie normę.

| Wzorzec | Kategoria VOLT | Co pokazuje nagranie | Co to znaczy dla presetu VOLT (propozycja) |
|---|---|---|---|
| Phaser Syn Maj7 | Keys / Pad | Akordy, energia 300–600 Hz, widoczne powolne przemiatanie wycięć phasera po całym paśmie (~4 s na cykl), atak ok. 150 ms, szerokie stereo. | Ciepły akord z wolnym, głębokim phaserem jako głównym ruchem; miękki atak, bez ostrej góry. |
| Oohs Chords | Vocal & Choir | Gładki chórek „uu”, wąskie pasmo 120–700 Hz, bardzo szeroki (stereo), delikatna modulacja ~1 Hz, wybrzmienie trzymane. | Formant „U”/„O” (filtr Formant lub tablica Choir), szeroki unison, wolne LFO na formancie; ciemny. |
| Dark Sub | Bass | Prawie czysty sub, mono, natychmiastowy atak, bez ruchu, 99 % energii poniżej 300 Hz, najgłośniejszy fragment nagrania. | Prosty, mocny sub (sinus + odrobina nasycenia), mono, bez efektów – „podłoga” pod resztą. |
| X-Mod Lead | Lead | Wiele szybkich nut, partie falują (modulacja krzyżowa), amplituda pulsuje ~5 Hz (vibrato), powolne narastanie ok. 0,7 s. | Lead z warpem FM/RM między oscylatorami, vibrato ~5 Hz, łagodne wejście zamiast twardego ataku. |
| Searing Gtr 2 | Guitar | Gęsty szereg harmonicznych aż do ~7 kHz (przester), trzymany dźwięk bez zaniku, mono, na początku podciągnięcie wysokości. | Przesterowana gitara prowadząca: String/saw przez Hard/Tube, długi sustain, glide lub pitch bend do podciągnięć. |
| Lilting Vo and Syn | Vocal & Choir / Pad | Warstwa głos + syntezator, energia 300–700 Hz, bardzo szeroka, wolne narastanie ~0,5 s, szybkie drżenie amplitudy (vibrato/tremolo). | Pad wokalno-syntezatorowy: Formant + miękki saw, wolny atak, delikatne vibrato, szerokie stereo. |
| Breathy Bubbles | FX / Texture | „Bąble” – plamy energii skaczące po wysokości 300 Hz–2 kHz, pod spodem niski dół, wolny atak, szybki zanik po puszczeniu. | Tekstura z Random/S&H na formancie lub filtrze BP z rezonansem, dodatek szumu (oddech), sub pod spodem. |
| SysCtrl Deep Echo 2 | Pluck / Arp | Krótkie nuty (atak ~40 ms, szybki zanik) i wyraźne powtórzenia echa; ciemny, wąski stereo. | Ciemny, krótki pluck, w którym delay jest częścią frazy (sync, feedback ok. 0,4–0,5), mało pogłosu. |
| 1 Note Phaser EP1 | Keys | Pianino elektryczne, energia 100–1000 Hz, tremolo ~4 Hz i phaser, prawie mono. | E-piano (FM/Hammer) z tremolem ~4 Hz i phaserem; ciepłe, bez szklanej góry; blisko wzorca „Chorusy Keys”. |

## Kolejne kategorie

Wzorców jest teraz 11 (2 z Vitala, 9 z Zenology). Kolejne użytkownik może dopisać w ten sam sposób
(nagranie albo jedno zdanie o charakterze).
