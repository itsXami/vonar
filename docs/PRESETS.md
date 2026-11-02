# VOLT – presety fabryczne

121 presetów: **Init** + 60 inspirowanych Kanye Westem + 60 inspirowanych Daft Punk. *Nazwy* presetów nie zawierają
nazwisk artystów, nazw albumów ani tytułów utworów – inspiracja jest zapisana wyłącznie w tagach i w tym dokumencie.
Presety oddają charakter brzmień danej ery (barwa, obróbka, ruch); żaden nie odtwarza melodii.

Wszystkie presety generuje `tools/presets/generate_presets.py` (ten plik też). Poziomy skorygowano rendererem offline
do ok. −15 LUFS (szczegóły w `docs/DECISIONS.md`). Każdy preset ma podpięte wszystkie cztery makra – ich etykiety
są w tabelach. Opisy presetów są po angielsku, bo tak wyświetla je interfejs pluginu.

Kategorie: Bass, Lead, Pad, Keys, Arp, Brass, FX. Podglądy audio każdego presetu generuje CI
(artefakt `VOLT-preset-previews`).

## Init

| # | Preset | Kategoria | Makra | Opis |
|---|---|---|---|---|
| 000 | Init | Lead | Bright / Morph / Grit / Space | Neutral starting point with one saw oscillator and the four macros pre-wired to tone, morph, grit and space. |

## Kanye West – Yeezus (24)

Industrialna agresja: przesterowane i zgniecione bitcrusherem basy, buzz i acid, krzykliwe leady, syreny i szorstkie, przesterowane 808. Najważniejsza i najmocniej brzmiąca grupa.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 001 | Concrete Saw | Bass | Kanye West, Yeezus, Industrial, Distorted, Aggressive | Grit / Snarl / Sync / Crush | Buzzing mono bass driven through hard clipping and a snarling ladder filter. |
| 002 | Furnace Sub | Bass | Kanye West, Yeezus, Industrial, 808, Distorted | Heat / Body / Growl / Click | Saturated sub bass with a fast pitch drop and tube heat on top. |
| 003 | Rivet Gun | Bass | Kanye West, Yeezus, Industrial, Lo-Fi, Aggressive | Bits / Bite / Metal / Mix | Bit-crushed square bass with a metallic attack that rattles like machinery. |
| 004 | Acid Bath | Bass | Kanye West, Yeezus, Industrial, Acid, Aggressive | Squelch / Open / Dirt / Wobble | Screaming acid line with a self-resonant ladder and a hard-driven filter stage. |
| 005 | Static Throat | Lead | Kanye West, Yeezus, Industrial, Vocal, Distorted | Vowel / Fold / Scream / Space | Fuzzy formant lead that growls through vowel shapes and folded distortion. |
| 006 | Air Raid | FX | Kanye West, Yeezus, Industrial, Siren | Sweep / Grit / Hall / Echo | Wailing siren that swings an octave up and down with tube grit and a long hall. |
| 007 | Alarm Pulse | FX | Kanye West, Yeezus, Industrial, Siren | Tone / Grit / Width / Echo | Two-tone square alarm that flips pitch on every quarter note. |
| 008 | Chain Link Scream | Lead | Kanye West, Yeezus, Industrial, Distorted, Aggressive | Sync / Clip / Tone / Slap | Hard-synced lead that tears upward as the sync sweep opens. |
| 009 | Steel Mill Drone | Pad | Kanye West, Yeezus, Industrial, Dark, Texture | Grind / Metal / Noise / Space | Metallic drone of ring-modulated tones and noise that slowly grinds and phases. |
| 010 | Overload 808 | Bass | Kanye West, Yeezus, Industrial, 808, Distorted | Drive / Tone / Rasp / Sub | Long 808 that breaks up into a raspy, clipped tail. |
| 011 | Gutter Growl | Bass | Kanye West, Yeezus, Industrial, Wobble | Growl / Speed / Heat / Sub | FM bass that growls in eighth-note pulses under heavy saturation. |
| 012 | Shock Collar | Bass | Kanye West, Yeezus, Industrial, Lo-Fi, Aggressive | Fold / Crush / Bite / Width | Wavefolded bass with a bit-crushed bite that jumps out of the mix. |
| 013 | Black Iron Lead | Lead | Kanye West, Yeezus, Industrial, Distorted, Wide | Width / Clip / Tone / Hall | Wide stacked saw lead pushed into hard clipping for a brutal topline. |
| 014 | Riot Horn | Brass | Kanye West, Yeezus, Industrial, Stab | Blare / Bite / Open / Room | Blaring distorted brass stab with a nasal tube bite. |
| 015 | Feedback Choir | Pad | Kanye West, Yeezus, Industrial, Dark, Choir | Vowel / Fold / Flange / Hall | Dark choir that folds and flanges into a menacing wall of feedback. |
| 016 | Sawblade Arp | Arp | Kanye West, Yeezus, Industrial, Arp, Distorted | Edge / Grind / Tone / Echo | Buzzing two-octave arpeggio that cuts like a grinder. |
| 017 | Scrapyard Hit | FX | Kanye West, Yeezus, Industrial, Impact | Pitch / Metal / Crush / Room | Clanging noise impact that drops in pitch and smashes into a dark room. |
| 018 | Klaxon Drop | FX | Kanye West, Yeezus, Industrial, Siren | Dive / Grit / Tone / Echo | Distorted horn that dives two octaves like a warning call. |
| 019 | Rust Bass | Bass | Kanye West, Yeezus, Industrial, Distorted | PWM / Rust / Pluck / Sub | Pulse-width bass with a rusty tube edge and a quick filter pluck. |
| 020 | Kick Sub Smash | Bass | Kanye West, Yeezus, Industrial, 808, Punch | Punch / Clip / Tone / Tail | Punchy kick-like 808 with a steep pitch dive and clipped transient. |
| 021 | Panic Lead | Lead | Kanye West, Yeezus, Industrial, Lo-Fi | Panic / Crush / Tone / Echo | Crushed square lead with a nervous fast vibrato. |
| 022 | Pressure Drone | Pad | Kanye West, Yeezus, Industrial, Dark, Texture | Fold / Rasp / Breath / Hall | Folded, raspy drone whose filter breathes in slow waves. |
| 023 | Breaker Keys | Keys | Kanye West, Yeezus, Industrial, Stab, Digital | Index / Crush / Tone / Room | Harsh digital FM stab with a bit-crushed decay. |
| 024 | Smoke Signal | FX | Kanye West, Yeezus, Industrial, Texture, Vocal | Chatter / Grit / Echo / Space | Random formant chatter bouncing between ping-pong echoes. |

## Kanye West – Graduation (10)

Stadionowe supersawy, błyszczące plucki i jasne leady.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 025 | Arena Saw Stack | Lead | Kanye West, Graduation, Stadium, Supersaw, Bright | Width / Shine / Octave / Hall | Huge detuned supersaw lead with octave layer, chorus and a stadium hall. |
| 026 | Varsity Stabs | Keys | Kanye West, Graduation, Stadium, Supersaw, Stab | Pluck / Width / Echo / Hall | Bright supersaw chord stab with a short pluck and stereo delay. |
| 027 | Neon Anthem | Lead | Kanye West, Graduation, Stadium, Bright | Bright / Pulse / Vibrato / Echo | Bright analog saw and pulse lead with glide and mod-wheel vibrato. |
| 028 | Gloss Pluck | Keys | Kanye West, Graduation, Stadium, Pluck, Bright | Gloss / Body / Echo / Hall | Glassy FM pluck layered with a soft triangle for shiny chords. |
| 029 | Skyline Arp | Arp | Kanye West, Graduation, Stadium, Supersaw, Arp | Shine / Width / Echo / Hall | Shimmering supersaw arpeggio rising over two octaves. |
| 030 | Victory Brass | Brass | Kanye West, Graduation, Stadium, Brass, Bright | Swell / Brass / Width / Hall | Bold synth brass section with a swelling filter and warm unison. |
| 031 | Shine Lead | Lead | Kanye West, Graduation, Stadium, Bright | Sync / Sweep / Width / Echo | Synced square lead with a moving sweep that sparkles on top of a mix. |
| 032 | Campus Pad | Pad | Kanye West, Graduation, Stadium, Supersaw, Warm | Air / Strings / Width / Hall | Warm string and supersaw blend that swells in slowly. |
| 033 | Big Room Saw Bass | Bass | Kanye West, Graduation, Stadium, Supersaw | Bright / Stack / Sub / Drive | Stacked saw bass with a solid sub that fills a stadium. |
| 034 | Synth Choir Lift | Pad | Kanye West, Graduation, Stadium, Choir, Bright | Vowel / Saw / Air / Hall | Airy synthetic choir layered with saws for uplifting chords. |

## Kanye West – 808s & Heartbreak (10)

Zimne, oszczędne pady, syntetyczne pseudowokale i długie 808 z glide.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 035 | Glass Heart Pad | Pad | Kanye West, 808s & Heartbreak, Cold, Pad, Minimal | Frost / Breath / Width / Hall | Cold, hollow pad with a slow bloom and a very wide hall. |
| 036 | Frozen Voice Box | Lead | Kanye West, 808s & Heartbreak, Cold, Vocal, Glide | Vowel / Mouth / Echo / Hall | Synthetic vocal lead that glides between vowels like a pitch-corrected singer. |
| 037 | Long Glide 808 | Bass | Kanye West, 808s & Heartbreak, Cold, 808, Glide | Drive / Tone / Knock / Sub | Deep sustained 808 with a long tail and portamento between notes. |
| 038 | Winter Choir | Pad | Kanye West, 808s & Heartbreak, Cold, Choir, Vocal | Vowel / Air / Width / Hall | Breathy synthetic choir drifting through vowels in the cold. |
| 039 | Cold Bell Keys | Keys | Kanye West, 808s & Heartbreak, Cold, Bell, Minimal | Ring / Tone / Echo / Hall | Clear FM bell keys with a frosty decay and long reverb. |
| 040 | Lonely Sine Lead | Lead | Kanye West, 808s & Heartbreak, Cold, Minimal, Soft | Shape / Vibrato / Echo / Hall | Soft sine lead with delayed vibrato and ping-pong echoes. |
| 041 | Tom Drop 808 | Bass | Kanye West, 808s & Heartbreak, Cold, 808 | Drop / Drive / Tone / Room | Tom-like 808 with a pronounced pitch drop and a short, round tail. |
| 042 | Synthetic Sigh | Lead | Kanye West, 808s & Heartbreak, Cold, Vocal | Vowel / Bend / Echo / Hall | Vowel-shaped lead that sighs and bends like a vocoder. |
| 043 | Grey Sky Strings | Pad | Kanye West, 808s & Heartbreak, Cold, Strings, Minimal | Air / Ensemble / Bow / Hall | Muted synthetic strings with a slow attack and melancholic shimmer. |
| 044 | Tin Croon | Lead | Kanye West, 808s & Heartbreak, Cold, Vocal | Vowel / Steps / Echo / Hall | Nasal, robotic-sounding sung tone with stepped vowel changes. |

## Kanye West – My Beautiful Dark Twisted Fantasy (10)

Dramatyczne brassy, ciemne syntetyczne smyczki i epickie basy.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 045 | Throne Brass | Brass | Kanye West, MBDTF, Epic, Brass, Dramatic | Swell / Blare / Heat / Hall | Majestic synth brass that swells with tube warmth and a long hall. |
| 046 | Velvet Doom Strings | Pad | Kanye West, MBDTF, Epic, Strings, Dark | Bow / Dark / Ensemble / Hall | Dark synthetic strings in low register with slow motion and drama. |
| 047 | Cathedral Low End | Bass | Kanye West, MBDTF, Epic, Epic | Open / Drive / Sub / Hall | Enormous saw and sub bass with a slow-opening filter for epic drops. |
| 048 | Gilded Horns | Brass | Kanye West, MBDTF, Epic, Brass, Stab | Gold / Bite / Width / Hall | Punchy FM horn stab with a bright, golden edge. |
| 049 | Opera Synth Lead | Lead | Kanye West, MBDTF, Epic, Vocal, Dramatic | Vowel / Vibrato / Echo / Hall | Theatrical vowel lead with wide vibrato that sings over strings. |
| 050 | Dark Orchestra Hit | FX | Kanye West, MBDTF, Epic, Impact, Dramatic | Brass / Tone / Air / Hall | Orchestral brass and string hit with noise air and a huge tail. |
| 051 | Grand Synth Keys | Keys | Kanye West, MBDTF, Epic, Keys, Warm | Attack / Body / Tone / Hall | Piano-like synth keys mixing a soft bell attack and a warm square body. |
| 052 | Velvet Rope Bass | Bass | Kanye West, MBDTF, Epic, Glide | Weight / Tone / Drive / Sub | Smooth FM bass that slides between notes with a rich low mid. |
| 053 | Midnight Cellos | Pad | Kanye West, MBDTF, Epic, Strings, Dark | Bow / Tone / Ensemble / Hall | Low synthetic cello section with a slow bow and dark tone. |
| 054 | Fanfare Swell | Brass | Kanye West, MBDTF, Epic, Brass, Epic | Swell / Octave / Width / Hall | Massive octave-stacked brass swell for cinematic climaxes. |

## Kanye West – Gospel / Donda (6)

Organy, chóralne pady i potężne akordy.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 055 | Sunday Drawbars | Keys | Kanye West, Donda, Gospel, Organ | Drawbars / Rotor / Drive / Hall | Classic drawbar organ with a gentle rotary-style chorus. |
| 056 | Revival Organ | Keys | Kanye West, Donda, Gospel, Organ, Distorted | Drawbars / Swirl / Grit / Hall | Overdriven church organ with a swirling phaser and lots of soul. |
| 057 | Stadium Choir | Pad | Kanye West, Donda, Gospel, Choir, Epic | Vowel / Choir / Air / Hall | Massive choir pad that rises slowly into a huge hall. |
| 058 | Pulpit Chords | Pad | Kanye West, Donda, Gospel, Organ, Epic | Organ / Bright / Width / Hall | Huge organ-and-saw chord bed that feels like a full congregation. |
| 059 | Holy Drone | Pad | Kanye West, Donda, Gospel, Organ, Drone | Pipes / Tone / Air / Hall | Sustained pipe organ drone with a cathedral-sized reverb. |
| 060 | Praise Bass | Bass | Kanye West, Donda, Gospel, Organ | Drawbars / Tone / Sub / Grit | Round organ bass with a clean sub for gospel bass lines. |

## Daft Punk – Homework (14)

Surowy acid squelch, filtrowane basy i szorstkie leady.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 061 | Squelch Box | Bass | Daft Punk, Homework, Acid, Acid | Squelch / Open / Dirt / Echo | Classic acid squelch with a resonant ladder, accent-like envelope and slide. |
| 062 | Rubber Acid | Bass | Daft Punk, Homework, Acid, Acid | Squelch / Open / Drive / Echo | Square-wave acid bass with a rubbery resonant bounce. |
| 063 | Warehouse Filter Bass | Bass | Daft Punk, Homework, Acid, Filter House | Sweep / Grit / Res / Sub | Raw saw bass whose filter sweeps every two beats under a pump. |
| 064 | Raw Filter Lead | Lead | Daft Punk, Homework, Acid, Filter | Filter / Res / Grit / Echo | Gritty square lead with a slowly moving resonant ladder. |
| 065 | Distorted Riff Saw | Lead | Daft Punk, Homework, Acid, Distorted | Crunch / Tone / Width / Echo | Overdriven saw riff tone with tube crunch and a tight filter. |
| 066 | Acid Line Arp | Arp | Daft Punk, Homework, Acid, Acid, Arp | Squelch / Open / Dirt / Echo | Random acid arpeggio with squelching accents and slapback echo. |
| 067 | Chicago Organ Stab | Keys | Daft Punk, Homework, Acid, House, Organ | Drawbars / Tone / Grit / Room | Short house organ stab with a punchy decay. |
| 068 | Phaser Sweep Bass | Bass | Daft Punk, Homework, Acid, Filter House | Phase / Tone / Grit / Sub | Raw saw bass smeared by a slow, deep phaser. |
| 069 | Grinding Sweep | FX | Daft Punk, Homework, Acid, Noise, Sweep | Sweep / Grind / Res / Echo | Distorted noise sweep that rises and falls through a resonant band-pass. |
| 070 | Funky Filter Keys | Keys | Daft Punk, Homework, Acid, Funk | Wah / Pulse / Phase / Room | Clavinet-like pulse keys with a resonant envelope wah. |
| 071 | Garage Squelch Lead | Lead | Daft Punk, Homework, Acid, Acid | Squelch / Open / Dirt / Echo | Acid table lead with a nasal squelch that sits above the groove. |
| 072 | Siren Sweep | FX | Daft Punk, Homework, Acid, Siren | Rate / Tone / Grit / Echo | Analog-style siren that rises and falls with a resonant filter. |
| 073 | Fuzz Bassline | Bass | Daft Punk, Homework, Acid, Distorted | Fuzz / Tone / Buzz / Sub | Buzzy fuzz bass with a short filter snap. |
| 074 | Mono Wah Lead | Lead | Daft Punk, Homework, Acid, Filter | Wah / Res / Grit / Echo | Band-pass lead that opens like a wah pedal on every note. |

## Daft Punk – Discovery (18)

Filter house z Pumpem, leady w stylu talkboxa (filtr Formant), disco strings, leady lat 80., słodkie pady.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 075 | Pumping Filter Chords | Keys | Daft Punk, Discovery, French House, Pump, Filter House | Filter / Phase / Grit / Hall | Saw chord stack that pumps on every beat while the filter sweeps open. |
| 076 | Talkbox Lead | Lead | Daft Punk, Discovery, French House, Talkbox, Vocal | Vowel / Mouth / Echo / Grit | Talkbox-style lead that speaks through moving vowel formants. |
| 077 | Talk Synth Chords | Keys | Daft Punk, Discovery, French House, Talkbox, Vocal | Vowel / Grit / Width / Hall | Chords that say a vowel on every hit, like a talkbox section. |
| 078 | Disco Strings | Pad | Daft Punk, Discovery, French House, Strings, Disco | Bow / Air / Ensemble / Hall | Lush disco string section with ensemble chorus and gentle pumping. |
| 079 | Eighties Solo Lead | Lead | Daft Punk, Discovery, French House, 80s, Solo | Sync / Vibrato / Echo / Hall | Bright synced lead with portamento and delayed vibrato for solos. |
| 080 | Sweet Analog Pad | Pad | Daft Punk, Discovery, French House, Warm, Sweet | Warmth / Hollow / Width / Hall | Soft warm pad with gently detuned saws and a glossy chorus. |
| 081 | Filter House Bass | Bass | Daft Punk, Discovery, French House, Pump, Filter House | Filter / Grit / Res / Sub | Round octave saw bass that pumps behind the kick. |
| 082 | Sidechain Organ | Keys | Daft Punk, Discovery, French House, Pump, Organ | Drawbars / Tone / Phase / Hall | House organ chords breathing with a strong quarter-note pump. |
| 083 | Vocoded Chords | Pad | Daft Punk, Discovery, French House, Vocal, Talkbox | Vowel / Voice / Width / Hall | Vocoder-like chord pad built from vowel tables and formants. |
| 084 | Glitter Arp | Arp | Daft Punk, Discovery, French House, Arp, Bright | Sparkle / Tone / Echo / Hall | Sparkling FM bell arpeggio bouncing between ping-pong delays. |
| 085 | Funk Riff Synth | Lead | Daft Punk, Discovery, French House, Funk | Snap / Phase / Grit / Echo | Snappy phased synth riff that plays like a muted funk guitar. |
| 086 | Laser Harp | Lead | Daft Punk, Discovery, French House, 80s, Pluck | Zap / Pulse / Echo / Hall | Pulse pluck with a zapping pitch envelope, built for melodic hooks. |
| 087 | Sunset Pad | Pad | Daft Punk, Discovery, French House, Warm, Sweet | Warmth / Shimmer / Width / Hall | Golden warm pad with a soft swell and slow chorus. |
| 088 | French Disco Bass | Bass | Daft Punk, Discovery, French House, Disco, Pump | Tone / Octave / Grit / Sub | Octave-bouncing disco bass that pumps with the groove. |
| 089 | Crystal Keys | Keys | Daft Punk, Discovery, French House, Bright, Keys | Crystal / Tone / Width / Hall | Bright FM keys with a crisp attack and silky tail. |
| 090 | Shuffle Pump Pad | Pad | Daft Punk, Discovery, French House, Pump, Filter House | Air / Grit / Width / Hall | Airy pad chopped into a shuffling eighth-note pump. |
| 091 | Vowel Sweep FX | FX | Daft Punk, Discovery, French House, Talkbox, Sweep | Vowel / Sweep / Echo / Hall | Formant sweep that says a long slow word across the stereo field. |
| 092 | Metal Mouth Lead | Lead | Daft Punk, Discovery, French House, Talkbox, Vocal | Vowel / Metal / Echo / Grit | Ring-modulated talkbox lead with a metallic, synthetic voice. |

## Daft Punk – Human After All (8)

Szorstkie, „gitarowe”, mechaniczne riffy i fuzz.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 093 | Gritty Riff Saw | Lead | Daft Punk, Human After All, Mechanical, Rock, Distorted | Gain / Tone / Chug / Room | Overdriven saw riff that chugs like a distorted guitar. |
| 094 | Fuzz Chord Stab | Keys | Daft Punk, Human After All, Mechanical, Rock, Distorted | Fuzz / Tone / Fifth / Room | Saw and fifth stacked into a fuzzed-out chord stab. |
| 095 | Machine Riff | Lead | Daft Punk, Human After All, Mechanical, Mechanical, Lo-Fi | Bits / Tone / Pulse / Echo | Bit-crushed square riff with a cold, mechanical edge. |
| 096 | Talking Fuzz | Lead | Daft Punk, Human After All, Mechanical, Talkbox, Distorted | Vowel / Fuzz / Mouth / Room | Formant lead slammed into hard distortion for a talking fuzz pedal sound. |
| 097 | Steel String Synth | Keys | Daft Punk, Human After All, Mechanical, Rock, Pluck | Pick / Fuzz / Pulse / Room | Plucky pulse tone with fuzz that mimics a picked electric guitar. |
| 098 | Mechanic Bass | Bass | Daft Punk, Human After All, Mechanical, Mechanical | Crunch / Tone / Buzz / Sub | Clanky buzz bass with a crunchy bite for repetitive riffs. |
| 099 | Clockwork Arp | Arp | Daft Punk, Human After All, Mechanical, Mechanical, Arp | Tick / Crunch / Pulse / Echo | Distorted square arpeggio ticking in tight eighth notes. |
| 100 | Distortion Wah | FX | Daft Punk, Human After All, Mechanical, Rock, Sweep | Wah / Fuzz / Res / Echo | Fuzzed saw swept by an auto-wah band-pass for gritty transitions. |

## Daft Punk – Tron: Legacy (12)

Monumentalne brassy, pulsujące basy i arpeggia.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 101 | Grid Pulse Bass | Bass | Daft Punk, Tron: Legacy, Cinematic, Pulse, Synthwave | Pulse / Drive / Sub / Hall | Relentless sixteenth-note bass pulse with a cutting filter envelope. |
| 102 | Monolith Brass | Brass | Daft Punk, Tron: Legacy, Cinematic, Brass, Cinematic | Swell / Blare / Weight / Hall | Towering low brass with slow swell, octave weight and a giant hall. |
| 103 | Light Cycle Arp | Arp | Daft Punk, Tron: Legacy, Cinematic, Arp, Synthwave | Glow / Width / Echo / Hall | Glowing supersaw arpeggio racing upward with dotted echoes. |
| 104 | Neon Grid Pad | Pad | Daft Punk, Tron: Legacy, Cinematic, Synthwave, Dark | Glow / Pulse / Width / Hall | Dark pulsing pad whose filter moves on a slow tempo-synced triangle. |
| 105 | Frontier Sync Lead | Lead | Daft Punk, Tron: Legacy, Cinematic, Cinematic | Sync / Tone / Echo / Hall | Cinematic synced lead with long echoes for soaring themes. |
| 106 | Pulse Engine Bass | Bass | Daft Punk, Tron: Legacy, Cinematic, Pulse, Synthwave | Gate / Drive / Sub / Grit | Bass gated by a square LFO into a driving sixteenth-note engine. |
| 107 | Cinematic Low Brass | Brass | Daft Punk, Tron: Legacy, Cinematic, Brass, Cinematic | Blare / Tone / Grit / Hall | Short, heavy low-brass stab for trailer hits. |
| 108 | Data Stream Arp | Arp | Daft Punk, Tron: Legacy, Cinematic, Arp, Digital | Index / Tone / Echo / Hall | Random digital FM arpeggio flickering like scrolling code. |
| 109 | Shutdown Hit | FX | Daft Punk, Tron: Legacy, Cinematic, Impact, Cinematic | Collapse / Noise / Crush / Hall | System-crash impact that collapses in pitch into noise and reverb. |
| 110 | Sky Bridge Pad | Pad | Daft Punk, Tron: Legacy, Cinematic, Cinematic, Wide | Light / Morph / Width / Hall | Wide luminous pad with slow movement and a long reflective tail. |
| 111 | Pulsing String Ostinato | Arp | Daft Punk, Tron: Legacy, Cinematic, Strings, Cinematic | Bow / Tone / Ensemble / Hall | Synthetic strings repeating a tight ostinato for tension. |
| 112 | Circuit Bass Drone | Bass | Daft Punk, Tron: Legacy, Cinematic, Dark, Drone | Open / Res / Drive / Sub | Dark sustained bass drone with slowly opening resonance. |

## Daft Punk – Random Access Memories (8)

Ciepłe analogowe polisynthy, funkowe klawisze i modularne basy.

| # | Preset | Kategoria | Tagi | Makra | Opis |
|---|---|---|---|---|---|
| 113 | Warm Poly Brass | Brass | Daft Punk, Random Access Memories, Analog, Brass, Vintage | Swell / Warmth / Width / Room | Vintage polysynth brass with a soft envelope swell. |
| 114 | Studio Poly Pad | Pad | Daft Punk, Random Access Memories, Analog, Warm, Vintage | Warmth / Pulse / Width / Room | Rich warm studio pad with slow filter movement and ensemble. |
| 115 | Funk Clav Keys | Keys | Daft Punk, Random Access Memories, Analog, Funk, Keys | Bite / Pulse / Phase / Room | Tight funky clav tone with a percussive filter bite. |
| 116 | Modular Pluck Bass | Bass | Daft Punk, Random Access Memories, Analog, Modular, Funk | Snap / Res / Drive / Sub | Woody modular bass pluck with a snappy ladder envelope. |
| 117 | Electric Tine Keys | Keys | Daft Punk, Random Access Memories, Analog, Keys, Vintage | Bark / Tone / Trem / Room | Soft electric-piano-like tines with a velocity-driven bark. |
| 118 | Seventies Solo Lead | Lead | Daft Punk, Random Access Memories, Analog, Solo, Vintage | Tone / Vibrato / Echo / Room | Warm square lead with portamento and expressive vibrato. |
| 119 | Boogie Bass | Bass | Daft Punk, Random Access Memories, Analog, Funk, Disco | Tone / Bounce / Drive / Sub | Round, bouncy square bass for funky disco lines. |
| 120 | Vintage String Ensemble | Pad | Daft Punk, Random Access Memories, Analog, Strings, Vintage | Bow / Tone / Ensemble / Room | Classic string machine with thick ensemble chorus. |

## Liczba presetów w kategoriach

| Kategoria | Presety |
|---|---|
| Bass | 28 |
| Lead | 27 |
| Pad | 22 |
| Keys | 17 |
| Arp | 8 |
| Brass | 8 |
| FX | 11 |
