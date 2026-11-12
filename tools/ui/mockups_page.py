"""Comparison page for the three UI mock-ups (HTML fragment published as an artifact for the user's choice)."""

VARIANTS = [
    ("Łuk", "Jeden akcent, modulacja zawsze na wierzchu",
     ["Grafitowe tło i jeden kolor akcentu (elektryczny błękit). Wszystko inne jest w odcieniach szarości.",
      "Trzy obwiednie i oba LFO widać stale jako wykresy pod oscylatorami i filtrem.",
      "Duże podglądy wavetable z klatkami „w głąb” i krzywa filtra w górnym rzędzie."],
     ["Sekcje rozróżnia położenie i tytuł, nie kolor.",
      "String Decay i Tone pojawiają się w panelu oscylatora dopiero po wybraniu typu String. Pitch Env dzieli "
      "panel z ENV 3. Arpeggiator dostaje własną zakładkę.",
      "Najwięcej pracy: nowy układ całego ekranu."]),
    ("Spektrum", "Kolor na sekcję, wersja dojrzała",
     ["Zostaje obecna zasada: turkus to oscylatory, pomarańcz filtr, zieleń obwiednie, fiolet modulacja, niebieski "
      "wyjście, żółty makra. Kolor jest tylko na wykresach, łukach pokręteł i znaczniku przy tytule.",
      "Wszystko z dzisiejszej zakładki SYNTH zostaje na jednym ekranie, nic nie zmienia miejsca na inną zakładkę.",
      "Obwiednie mają jeden duży wykres z przełącznikiem AMP / FILTER / MOD / PITCH, a LFO mały podgląd kształtu."],
     ["Sześć kolorów zamiast jednego: mniej jednolity znak rozpoznawczy, najbliżej obecnego wyglądu.",
      "Naraz widać wykres tylko jednej obwiedni.",
      "Najmniej ryzyka i najmniej pracy."]),
    ("Żarnik", "Duży ekran kontekstowy i pulpit pokręteł",
     ["Na górze jeden szeroki ekran. Pokazuje to, czego dotykasz: wavetable, filtr, obwiednie, LFO albo oscyloskop, "
      "razem z odczytem wartości.",
      "Pod ekranem pulpit pokręteł bez ramek. Ciepła czerń i pomarańczowy akcent, wygląd bliższy sprzętowi.",
      "Obwiednie mają miniatury z pokrętłami A D S R obok."],
     ["Naraz widać jedną dużą grafikę. Krzywa filtra i oscyloskop są w zakładkach ekranu.",
      "Miernik poziomu wyjścia to nowa rzecz do zrobienia w silniku.",
      "Najodważniejszy kierunek, najdalej od obecnego wyglądu."]),
]

CSS = """
/* Layout: one reading column of numbered options, each a full-width window mock-up followed by gains and costs. */
:root {
  --bg: #F4F5F7; --surface: #FFFFFF; --fg: #14171C; --muted: #5B6470; --line: #D9DDE3; --accent: #0B7FB5;
  --frame: #06070A; --pick: #E6F4FB;
  --display: 'Space Grotesk', 'Segoe UI', system-ui, sans-serif;
  --body: Inter, 'Segoe UI', system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --bg: #0F1114; --surface: #171A1F; --fg: #E9ECF0; --muted: #98A2AE;
    --line: #2A2F37; --accent: #55C6F5; --frame: #000000; --pick: #12303D; color-scheme: dark }
}
:root[data-theme="dark"] { --bg: #0F1114; --surface: #171A1F; --fg: #E9ECF0; --muted: #98A2AE;
  --line: #2A2F37; --accent: #55C6F5; --frame: #000000; --pick: #12303D; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 16px; line-height: 1.55; }
.wrap { max-width: 1240px; margin: 0 auto; padding-block: 40px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column; gap: 56px; }
header { display: flex; flex-direction: column; gap: 12px; max-width: 68ch; }
h1 { font-family: var(--display); font-size: clamp(28px, 4vw, 40px); line-height: 1.1; margin: 0; text-wrap: balance;
  letter-spacing: -0.01em; }
header p { margin: 0; color: var(--muted); }
.option { display: flex; flex-direction: column; gap: 18px; }
.option-head { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.num { font-family: var(--display); font-size: 15px; font-weight: 700; color: var(--accent);
  border: 1.5px solid var(--accent); border-radius: 999px; width: 30px; height: 30px; display: inline-flex;
  align-items: center; justify-content: center; flex: none; align-self: center; }
h2 { font-family: var(--display); font-size: 24px; margin: 0; line-height: 1.2; }
.idea { color: var(--muted); margin: 0; }
.shot { background: var(--frame); border-radius: 10px; overflow-x: auto; border: 1px solid var(--line); }
.shot svg { display: block; width: 100%; min-width: 880px; height: auto; }
.notes { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px 40px; }
.notes > div { min-width: 0; }
h3 { font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px;
  font-weight: 600; }
ul { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 6px; max-width: 62ch; }
.rec { background: var(--pick); border-radius: 10px; padding: 20px 22px; max-width: 72ch; display: flex;
  flex-direction: column; gap: 8px; }
.rec p { margin: 0; }
.common { color: var(--muted); max-width: 72ch; margin: 0; }
"""


def render(svgs):
    out = ['<title>Makiety interfejsu VOLT</title>', '<meta name="claude:viewport-fit-sides" content="cover">',
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&'
           'family=Space+Grotesk:wght@500;700&display=swap">', f"<style>{CSS}</style>", '<div class="wrap">',
           '<header><h1>Makiety interfejsu VOLT</h1>',
           '<p>Trzy kierunki wyglądu na etap B. Każda makieta pokazuje okno 1200×740 z zakładką SYNTH i tym samym '
           'presetem. To rysunki, nie zrzuty działającego pluginu: pokazują układ, kolory i rodzaj grafik.</p>',
           '<p>Wybierz numer albo powiedz, co połączyć, na przykład układ z 1 i kolory z 2.</p></header>']
    for i, ((name, idea, gains, costs), svg) in enumerate(zip(VARIANTS, svgs), start=1):
        out.append(f'<section class="option"><div class="option-head"><span class="num">{i}</span><h2>{name}</h2>'
                   f'<p class="idea">{idea}</p></div><div class="shot">{svg}</div><div class="notes">'
                   '<div><h3>Co zyskujesz</h3><ul>' + "".join(f"<li>{g}</li>" for g in gains) + '</ul></div>'
                   '<div><h3>Cena</h3><ul>' + "".join(f"<li>{c}</li>" for c in costs) + '</ul></div></div></section>')
    out.append('<div class="rec"><h3>Rekomendacja</h3><p><strong>Makieta 1.</strong> Najlepiej pasuje do ustalonego '
               'kierunku: ciemno, czysto, dużo wizualizacji i jeden wyrazisty akcent. Obwiednie i LFO na głównym '
               'ekranie to też największa praktyczna zmiana przy robieniu brzmień.</p><p>Jeśli ważniejsze jest, żeby '
               'od razu było widać, co do czego należy, bezpieczniejsza jest makieta 2.</p></div>')
    out.append('<p class="common">Wspólne dla wszystkich trzech: czcionka Inter, okno 1200×740 ze skalowaniem 75–200%, '
               'przeglądarka presetów w górnym pasku, zakładki MODULATION i EFFECTS w tym samym stylu oraz okno '
               '„O programie” z licencją. Logo na makietach jest tymczasowe, bo nazwa jest jeszcze otwarta.</p>')
    out.append("</div>")
    return "\n".join(out)
