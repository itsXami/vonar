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


FINISHES = [
    ("2A", "Techniczne", "Płaskie panele stykające się ze sobą, cienkie łuki, odczyty czcionką o stałej szerokości.",
     ["Najczystsze i najbardziej czytelne, wartości łatwo porównać wzrokiem.",
      "Lekkie w rysowaniu, najprostsze do wiernego przeniesienia do pluginu."],
     ["Mniej „fizyczne”: pokrętła to płaskie krążki ze wskaźnikiem."]),
    ("2B", "Sprzętowe", "Pokrętła z cieniowaną główką, wgłębione ekrany, świecące linie i diody przy tytułach.",
     ["Więcej głębi i charakteru, wykresy wyglądają jak świecący ekran.",
      "Wskaźnik pokrętła i łuk mają kolor sekcji, więc kolor widać mocniej."],
     ["Więcej szczegółów do dopracowania w kodzie; poświatę trzeba narysować oszczędnie, żeby nie obciążała procesora."]),
]

EXTRA_CSS = """
.round { display: flex; flex-direction: column; gap: 48px; }
.changes { max-width: 72ch; }
details { border-top: 1px solid var(--line); padding-top: 20px; }
summary { cursor: pointer; font-family: var(--display); font-size: 18px; font-weight: 700; }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }
details .round { margin-top: 32px; }
.tag { font-family: var(--display); font-size: 13px; font-weight: 700; color: var(--accent);
  border: 1.5px solid var(--accent); border-radius: 999px; padding: 3px 10px; flex: none; align-self: center; }
"""


def option(tag, name, idea, svg, gains, costs, cls="num"):
    return (f'<section class="option"><div class="option-head"><span class="{cls}">{tag}</span><h2>{name}</h2>'
            f'<p class="idea">{idea}</p></div><div class="shot">{svg}</div><div class="notes">'
            '<div><h3>Co zyskujesz</h3><ul>' + "".join(f"<li>{g}</li>" for g in gains) + '</ul></div>'
            '<div><h3>Cena</h3><ul>' + "".join(f"<li>{c}</li>" for c in costs) + '</ul></div></div></section>')


TYPEFACES = [
    ("3A", "Barlow Semi Condensed", "Wąski, spokojny krój w duchu oznaczeń na sprzęcie pomiarowym.",
     ["Najwięcej miejsca na etykiety, więc tekst może być większy.", "Neutralny: nie odwraca uwagi od wykresów."],
     ["Mniej „syntezatorowy” charakter niż 3B."]),
    ("3B", "Oxanium", "Szerszy i bardziej kanciasty krój, kojarzy się z napisami na syntezatorach.",
     ["Wyraźniejszy charakter, od razu widać, że to instrument.", "Cyfry są bardzo czytelne."],
     ["Etykiety zajmują więcej miejsca, przy długich nazwach robi się ciasno."]),
]

FINDINGS = [
    ("Czcionka bez decyzji.", "Inter to krój, po który generatory sięgają domyślnie, a liczby były dodatkowo osobnym "
     "krojem „programistycznym”.", "Jeden krój z charakterem dla nazw, wartości i tytułów. Cyfry mają stałą szerokość, "
     "ale pochodzą z tego samego kroju."),
    ("Wszystko jednakowe.", "Te same ramki, nagłówki, rozmiary pokręteł i odstępy na całym ekranie.",
     "Hierarchia: Cutoff i Position są wyraźnie większe. Pasek pomocniczy (unison, LFO, voice, arp) jest ciemniejszy "
     "i drobniejszy. Makra to osobny, jaśniejszy pas z dużymi pokrętłami."),
    ("Wygląd okna ustawień.", "Obramowane sekcje wszędzie.",
     "Mniej pudełek: oba oscylatory leżą na jednej powierzchni, pasek pomocniczy nie ma ramek, a grupy rozdziela odstęp "
     "i cienka kreska. Tytuł sekcji ma kolor sekcji zamiast paska z kwadracikiem."),
    ("Za dużo kolorów.", "Sześć równie mocnych barw.",
     "Cztery kolory sekcji (oscylatory, filtr, obwiednie, modulacja) i bursztyn tylko dla makr. Wyjście i oscyloskop "
     "są bez koloru."),
    ("Każdy wykres taki sam.", "Linia z gradientem pod spodem, wszędzie.",
     "Wavetable to powierzchnia, filtr ma wypełnienie, obwiednia płaskie tło i kwadratowe punkty, a LFO i oscyloskop "
     "samą linię."),
    ("Pokrętła rozstawione równo na całą szerokość.", "Brak grup, dużo pustego miejsca.",
     "Pokrętła są zbite w grupy. Makra pokazują, czym sterują, na przykład Bark steruje pozycją wavetable A."),
    ("Logo z ikonką i zwykłym tekstem.", "Nic, co by wyróżniało ten instrument.",
     "Znak narysowany od zera: proste kreski, a litera O jest pokrętłem."),
]

FINAL_CSS = """
.findings { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px 36px; }
.findings > div { min-width: 0; border-top: 1px solid var(--line); padding-top: 12px; }
.findings h4 { margin: 0 0 4px; font-size: 16px; font-family: var(--display); }
.findings p { margin: 0; }
.findings .was { color: var(--muted); margin-bottom: 6px; }
.block { display: flex; flex-direction: column; gap: 16px; }
.block > h3 { margin: 0; }
"""


def render(svgs, detail=None, final=None):
    if final is None:
        return render_rounds(svgs, detail)
    out = ['<title>Makiety interfejsu VOLT</title>', '<meta name="claude:viewport-fit-sides" content="cover">',
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&'
           'family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&'
           'family=Barlow+Semi+Condensed:wght@400;500;600;700&family=Oxanium:wght@400;500;600;700&display=swap">',
           f"<style>{CSS}{EXTRA_CSS}{FINAL_CSS}</style>", '<div class="wrap">',
           '<header><h1>Makiety interfejsu VOLT</h1>',
           '<p>Runda 3. Wybrane wykończenie to 2A, ale nadal wyglądało na wygenerowane. Poniżej 2A po poprawkach, '
           'w dwóch krojach pisma. Układ i funkcje są te same w obu, różni je tylko czcionka.</p>',
           '<p>Wybierz 3A albo 3B. Jeśli coś nadal razi, wskaż miejsce na makiecie.</p></header>', '<div class="round">']
    for (tag, name, idea, gains, costs), svg in zip(TYPEFACES, final):
        out.append(option(tag, name, idea, svg, gains, costs, "tag"))
    out.append("</div>")
    out.append('<div class="block"><h3>Co wyglądało na wygenerowane i co zmieniłem</h3><div class="findings">'
               + "".join(f'<div><h4>{t}</h4><p class="was">{was}</p><p>{now}</p></div>' for t, was, now in FINDINGS)
               + '</div></div>')
    out.append('<p class="common">Oba kroje są na otwartej licencji (SIL OFL), więc można je wbudować w plugin tak jak '
               'dotychczasową czcionkę. Miernik poziomu przy wyjściu i podpisy pod makrami to nowe funkcje, których '
               'dziś w pluginie nie ma.</p>')
    inner = render_rounds(svgs, detail, body_only=True)
    out.append('<details><summary>Wcześniejsze rundy: wykończenia 2A i 2B oraz trzy kierunki</summary>' + inner
               + '</details>')
    out.append("</div>")
    return "\n".join(out)


def render_rounds(svgs, detail=None, body_only=False):
    out = ['<title>Makiety interfejsu VOLT</title>', '<meta name="claude:viewport-fit-sides" content="cover">',
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&'
           'family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">',
           f"<style>{CSS}{EXTRA_CSS}</style>", '<div class="wrap">']
    if body_only:
        out = []
    round1 = ['<div class="round">']
    for i, ((name, idea, gains, costs), svg) in enumerate(zip(VARIANTS, svgs), start=1):
        round1.append(option(i, name, idea, svg, gains, costs))
    round1.append("</div>")
    if detail is None:
        out += ['<header><h1>Makiety interfejsu VOLT</h1>',
                '<p>Trzy kierunki wyglądu na etap B. Każda makieta pokazuje okno 1200×740 z zakładką SYNTH.</p>'
                '</header>'] + round1 + ["</div>"]
        return "\n".join(out)
    if body_only:
        out.append('<div class="round">')
        for (tag, name, idea, gains, costs), svg in zip(FINISHES, detail):
            out.append(option(tag, name, idea, svg, gains, costs, "tag"))
        out += round1[1:-1] + ["</div>"]
        return "\n".join(out)
    out += ['<header><h1>Makiety interfejsu VOLT</h1>',
            '<p>Runda 2. Wybrany układ to makieta 2 (kolor na sekcję). Poniżej ten sam układ dopracowany w dwóch '
            'wykończeniach. To nadal rysunki, ale już w docelowej szczegółowości: tak mają wyglądać pokrętła, panele '
            'i wykresy w pluginie.</p>',
            '<p>Wybierz 2A albo 2B i napisz, co nadal wygląda sztucznie. Im konkretniej, tym lepiej: pokrętła, '
            'kolory, czcionka, odstępy, logo.</p></header>',
            '<div class="changes"><h3>Co się zmieniło względem szkicu</h3><ul>'
            '<li>Panele stykają się ze sobą zamiast pływać jako zaokrąglone karty. Ekran jest gęstszy, wykresy większe.</li>'
            '<li>Kolory sekcji są głębsze i mniej pastelowe. Kolor jest na wykresach, łukach i znaczniku przy tytule.</li>'
            '<li>Wavetable jest rysowane jako pełna powierzchnia z zaznaczoną bieżącą klatką, a nie plątanina linii.</li>'
            '<li>Wykresy mają siatkę i podziałkę: czas na obwiedni, częstotliwość i 0 dB na filtrze.</li>'
            '<li>Przełączniki są prostokątne i wbudowane w nagłówki paneli zamiast owalnych „pigułek”.</li>'
            '<li>Znak VOLT ma pokrętło w miejscu litery O. Miernik poziomu przy wyjściu to nowa funkcja.</li>'
            '</ul></div>', '<div class="round">']
    for (tag, name, idea, gains, costs), svg in zip(FINISHES, detail):
        out.append(option(tag, name, idea, svg, gains, costs, "tag"))
    out.append("</div>")
    out.append('<div class="rec"><h3>Rekomendacja</h3><p><strong>2B</strong>, jeśli zależy Ci na wrażeniu „prawdziwego '
               'instrumentu” w stylu, o którym rozmawialiśmy. <strong>2A</strong>, jeśli wolisz czystość i czytelność.'
               '</p><p>Można też mieszać: na przykład płaskie panele z 2A i pokrętła z 2B.</p></div>')
    out.append('<details><summary>Runda 1: trzy kierunki (wybrana makieta 2)</summary>' + "\n".join(round1) + '</details>')
    out.append("</div>")
    return "\n".join(out)
