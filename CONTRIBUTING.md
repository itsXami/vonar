# Wkład w Vonar

Dziękujemy za zainteresowanie! Na tym etapie projekt przyjmuje od innych **wyłącznie presety**. Zmiany w kodzie
(pull requesty z kodem, przeróbki silnika lub interfejsu) nie są na razie przyjmowane – błędy i pomysły zgłaszaj
jako *issue*.

## Jak zgłosić preset

1. Zrób brzmienie w Vonar i zapisz je przyciskiem **SAVE** (nazwa, kategoria, tagi, opis). Plik JSON znajdziesz
   w `%APPDATA%\Vonar\Presets`.
2. Otwórz *issue* z tytułem „Preset: nazwa” i dołącz plik JSON (albo kilka plików).
3. Preset przechodzi ten sam proces co fabryczne: render offline, kontrola poziomu, pomiar podobieństwa do
   istniejących brzmień i odsłuch. Do biblioteki trafiają presety, które wnoszą coś nowego.

## Wymagania dla presetu

- Zrobiony od zera w Vonar. Nie odtwarzaj presetów, wavetable ani nazw z innych syntezatorów.
- **Żadnych nazw artystów, albumów, utworów ani marek** w nazwie, tagach i opisie. Tagi opisują dźwięk
  (np. `Warm`, `Plucky`, `Dark`, `Wide`, `Lo-Fi`).
- Nazwa: 1–3 słowa, unikalna w bibliotece. Opis: jedno zdanie po angielsku, kończące się kropką.
- Wszystkie cztery makra są podpięte i mają etykiety mówiące, co robią.
- Preset reaguje na siłę uderzenia (velocity), a Mod Wheel robi coś słyszalnego.
- Głośność podobna do presetów fabrycznych (ok. −15 LUFS); limiter wyjściowy nie powinien stale pracować.

## Licencja wkładu

Zgłaszając preset, potwierdzasz, że jesteś jego autorem i zgadzasz się na jego włączenie do Vonar oraz
rozpowszechnianie na licencji projektu (AGPLv3, plik `LICENSE`). Autor presetu może zostać wymieniony
w dokumentacji, jeśli sobie tego życzy.
