# VOLT – pomiar CPU presetów (2026-11-13)

`VOLT_Render --out DIR --bench --block 256`: każdy preset gra akord 8 nut przez 3 s ("gra"), potem po wybrzmieniu
3 s ciszy z włączonym pluginem ("bezczynny"). Wynik w % jednego rdzenia, procesor serwerowy Intel Xeon 2,1 GHz
(rdzeń podobny do słabszego laptopa; szybki laptop będzie liczył ok. 1,5–2× mniej). 48 kHz, bufor 256.

| | Mediana | 90 % presetów poniżej | Najcięższy |
|---|---|---|---|
| Gra (akord 8 nut) | 1.8 % | 2.8 % | 5.0 % |
| Bezczynny | 0.45 % | 0.93 % | 1.88 % |

## Ranking (od najcięższego)

| # | Preset | Kategoria | Gra % | Bezczynny % |
|---|---|---|---|---|
| 1 | Festival Sync Lead | Lead | 4.96 | 1.12 |
| 2 | Nineties House Piano | Keys | 3.77 | 1.32 |
| 3 | Rap Synth Stab | Keys | 3.59 | 0.86 |
| 4 | Ooh Vowel Keys | Keys | 3.55 | 0.45 |
| 5 | Garage Organ Stab | Keys | 3.49 | 1.78 |
| 6 | Festival Saw Stab | Lead | 3.46 | 1.08 |
| 7 | Saturated Keys Stab | Keys | 3.40 | 1.13 |
| 8 | Staccato Strings | Strings | 3.35 | 0.71 |
| 9 | Hoover Stab | Keys | 3.33 | 1.09 |
| 10 | Trap Brass Hit | Brass | 3.18 | 1.10 |
| 11 | Reed Growl Keys | Keys | 3.17 | 0.84 |
| 12 | Choir Hit | FX | 3.16 | 0.71 |
| 13 | Rubber Ladder Pluck | Pluck | 3.11 | 0.07 |
| 14 | Bright Poly Pad | Pad | 3.11 | 1.21 |
| 15 | Hard House Stab | Keys | 3.10 | 0.93 |
| 16 | Orchestral Brass Stab | Brass | 3.05 | 0.71 |
| 17 | Rubber Bridge Guitar | Guitar | 3.05 | 1.13 |
| 18 | Breaker Keys | Keys | 3.04 | 0.78 |
| 19 | Classic Saw Pluck | Pluck | 2.99 | 0.58 |
| 20 | Disco String Stab | Strings | 2.99 | 0.73 |
| 21 | Rave Piano Stab | Keys | 2.94 | 1.88 |
| 22 | Crescendo Swell Strings | Strings | 2.92 | 0.68 |
| 23 | Supersaw Lead | Lead | 2.90 | 0.73 |
| 24 | Distant Choir Pad | Pad | 2.88 | 0.64 |
| 25 | Varsity Stabs | Keys | 2.87 | 0.51 |
| 26 | Grieving Strings | Strings | 2.87 | 0.29 |
| 27 | Overdrive Rhythm Guitar | Guitar | 2.86 | 1.11 |
| 28 | Vocoded Chords | Pad | 2.85 | 0.41 |
| 29 | Boom Bap Snare | Drums | 2.84 | 1.09 |
| 30 | Deep Sub Pad | Pad | 2.84 | 0.70 |
| 31 | Clean Bridge Guitar | Guitar | 2.83 | 0.72 |
| 32 | Palm Mute Chug | Guitar | 2.83 | 0.83 |
| 33 | Distorted Fanfare | Brass | 2.82 | 0.87 |
| 34 | Overdrive Rock Organ | Keys | 2.81 | 1.18 |
| 35 | Choir Vowel Pad | Pad | 2.80 | 0.42 |
| 36 | Vocal Ahh Pad | Pad | 2.78 | 0.30 |
| 37 | Industrial Guitar Wall | Guitar | 2.78 | 0.77 |
| 38 | Dark Drone | FX | 2.78 | 0.28 |
| 39 | Boom Bap Kick | Drums | 2.77 | 0.86 |
| 40 | Pizzicato Section | Strings | 2.74 | 1.08 |
| 41 | Dark Orchestra Hit | FX | 2.74 | 0.66 |
| 42 | Riot Horn | Brass | 2.73 | 0.68 |
| 43 | Muted Felt Upright | Keys | 2.72 | 1.58 |
| 44 | Neon Grid Pad | Pad | 2.69 | 0.54 |
| 45 | Rainy Day EP | Keys | 2.67 | 0.72 |
| 46 | Ukulele Strum | Guitar | 2.66 | 0.70 |
| 47 | Crunch Rhythm Guitar | Guitar | 2.66 | 1.12 |
| 48 | Funk Clav Keys | Keys | 2.65 | 1.00 |
| 49 | Slow Phaser Chords | Keys | 2.64 | 0.60 |
| 50 | Temple Bell Strike | Bell | 2.64 | 0.29 |
| 51 | Eerie Music Box | Bell | 2.63 | 0.36 |
| 52 | String Ensemble | Strings | 2.63 | 0.34 |
| 53 | Winter Choir | Pad | 2.63 | 0.44 |
| 54 | Boom Bap Jazz EP | Keys | 2.63 | 0.88 |
| 55 | Reed Electric Piano | Keys | 2.58 | 0.70 |
| 56 | Wavetable Drift Pad | Pad | 2.57 | 0.60 |
| 57 | Synth Brass | Brass | 2.56 | 0.70 |
| 58 | Sul Ponticello | Strings | 2.56 | 0.57 |
| 59 | Filter Sweep Pad | Pad | 2.55 | 0.31 |
| 60 | Phaser Rhythm Guitar | Guitar | 2.55 | 0.78 |
| 61 | Musette Accordion | Woodwind | 2.52 | 0.32 |
| 62 | Double Course Pluck | Pluck | 2.52 | 1.08 |
| 63 | Dulcimer Keys | Keys | 2.51 | 1.09 |
| 64 | Lilting Voice Pad | Pad | 2.51 | 0.31 |
| 65 | Crystal Keys | Keys | 2.49 | 0.72 |
| 66 | Trap Bell Melody | Bell | 2.46 | 0.50 |
| 67 | Haunted Choir Pad | Pad | 2.46 | 0.27 |
| 68 | Chord Memory Stab | Keys | 2.45 | 0.54 |
| 69 | Fuzzbox Bass Guitar | Guitar | 2.45 | 0.42 |
| 70 | Nylon Pluck | Guitar | 2.45 | 0.44 |
| 71 | Dub Chord Stab | Keys | 2.44 | 0.78 |
| 72 | Wah Clav | Keys | 2.44 | 0.85 |
| 73 | Clave Click Pluck | Pluck | 2.43 | 0.73 |
| 74 | Empty Room Pad | Pad | 2.43 | 0.37 |
| 75 | House Piano Stab | Keys | 2.41 | 0.73 |
| 76 | Notch Phaser Pad | Pad | 2.38 | 0.40 |
| 77 | Sidechain Organ | Keys | 2.38 | 0.62 |
| 78 | Metal Smash Stab | Pluck | 2.37 | 0.60 |
| 79 | Cross Mod Keys | Keys | 2.35 | 0.30 |
| 80 | Broken Bell | Bell | 2.34 | 0.71 |
| 81 | Low String Section | Strings | 2.33 | 0.30 |
| 82 | Dark Pad | Pad | 2.33 | 0.29 |
| 83 | Low Octave Strings | Strings | 2.33 | 0.29 |
| 84 | Tech Kick | Drums | 2.31 | 0.85 |
| 85 | Balafon Buzz | Bell | 2.30 | 0.84 |
| 86 | Synth Strings | Strings | 2.27 | 0.44 |
| 87 | Trap Kick Punch | Drums | 2.26 | 1.17 |
| 88 | Warm Saw Pad | Pad | 2.25 | 0.30 |
| 89 | Trap Open Hat | Drums | 2.25 | 0.42 |
| 90 | Classic FM Bell | Bell | 2.24 | 0.37 |
| 91 | House Pump Pad | Pad | 2.24 | 0.33 |
| 92 | Funky Filter Keys | Keys | 2.24 | 0.78 |
| 93 | Talk Synth Chords | Keys | 2.23 | 0.45 |
| 94 | Comb Tube Pluck | Pluck | 2.23 | 0.38 |
| 95 | Church Bell Toll | Bell | 2.23 | 0.30 |
| 96 | Tech Perc Pluck | Pluck | 2.22 | 0.51 |
| 97 | Hard Clipped Kick | Drums | 2.21 | 0.78 |
| 98 | Trap Clap | Drums | 2.21 | 1.06 |
| 99 | Smoky Lounge Keys | Keys | 2.20 | 0.49 |
| 100 | Deep Echo Keys | Keys | 2.20 | 0.54 |
| 101 | Breath Bubble Pluck | Pluck | 2.20 | 1.18 |
| 102 | Funk Scratch Guitar | Guitar | 2.20 | 0.87 |
| 103 | Brass Section | Brass | 2.20 | 0.30 |
| 104 | Future House Pluck | Pluck | 2.19 | 0.54 |
| 105 | Marimba Keys | Keys | 2.17 | 0.78 |
| 106 | Sub Sine Pluck | Pluck | 2.17 | 0.45 |
| 107 | Distorted Impact | FX | 2.16 | 0.63 |
| 108 | Crotale Ring | Bell | 2.16 | 0.44 |
| 109 | Chorus Tine EP | Keys | 2.15 | 0.42 |
| 110 | Wide Disco Clap | Drums | 2.15 | 0.83 |
| 111 | Ring Clang Pluck | Pluck | 2.15 | 0.30 |
| 112 | Country Twang Guitar | Guitar | 2.15 | 0.93 |
| 113 | Steel Pan Melody | Bell | 2.14 | 0.42 |
| 114 | Gilded Horns | Brass | 2.14 | 0.30 |
| 115 | Gloss Pluck | Keys | 2.14 | 0.80 |
| 116 | Kalimba Thumb | Pluck | 2.13 | 0.72 |
| 117 | Dream Keys | Keys | 2.13 | 0.49 |
| 118 | Soft French Horn | Brass | 2.13 | 0.29 |
| 119 | Bellows Harmonium | Keys | 2.13 | 0.29 |
| 120 | Detroit Bounce Pluck | Pluck | 2.13 | 0.47 |
| 121 | Gamelan Gong | Bell | 2.11 | 0.31 |
| 122 | Phaser Wash Pad | Pad | 2.11 | 0.60 |
| 123 | Clean Delay Lead Guitar | Guitar | 2.11 | 0.78 |
| 124 | Tubular Bell | Bell | 2.10 | 0.31 |
| 125 | Rosewood Marimba | Bell | 2.10 | 0.71 |
| 126 | Sad Trap Piano | Keys | 2.10 | 0.48 |
| 127 | Grinding Sweep | FX | 2.10 | 0.46 |
| 128 | Classic EP | Keys | 2.10 | 0.20 |
| 129 | Impact Downlifter | FX | 2.10 | 0.64 |
| 130 | Simple Bell | Bell | 2.09 | 0.29 |
| 131 | Felt Tine EP | Keys | 2.09 | 0.42 |
| 132 | Polysynth Chords | Keys | 2.09 | 0.20 |
| 133 | String Clav | Keys | 2.07 | 0.85 |
| 134 | Square Pluck | Pluck | 2.07 | 0.10 |
| 135 | Grand Synth Keys | Keys | 2.07 | 0.29 |
| 136 | Choir Pad | Pad | 2.06 | 0.30 |
| 137 | Wooden Pluck | Pluck | 2.05 | 0.49 |
| 138 | Cinematic Low Brass | Brass | 2.04 | 0.27 |
| 139 | Ghost Vocal Pad | Pad | 2.04 | 0.37 |
| 140 | Dub Echo Pluck | Pluck | 2.04 | 0.20 |
| 141 | Cold Brass Swell | Brass | 2.04 | 0.28 |
| 142 | FM Glass Pluck | Pluck | 2.02 | 0.30 |
| 143 | Harmonics Chime Guitar | Guitar | 2.01 | 0.79 |
| 144 | Phaser Tremolo EP | Keys | 2.01 | 0.37 |
| 145 | Glass Pad | Pad | 2.00 | 0.28 |
| 146 | Snap Clap | Drums | 1.99 | 0.85 |
| 147 | Sunday Drawbars | Keys | 1.97 | 0.80 |
| 148 | Dark Trap Piano | Keys | 1.96 | 0.71 |
| 149 | Vocal Chop Stab | Lead | 1.96 | 0.14 |
| 150 | Emo Guitar Pluck | Guitar | 1.95 | 0.69 |
| 151 | Sitar Buzz | Guitar | 1.95 | 0.92 |
| 152 | 808 Boom Kick | Drums | 1.94 | 0.54 |
| 153 | Honky Tonk Bar | Keys | 1.94 | 0.30 |
| 154 | Dark Ballad Piano | Keys | 1.94 | 0.29 |
| 155 | Funeral Organ | Keys | 1.92 | 0.30 |
| 156 | Banjo Pluck | Guitar | 1.92 | 0.70 |
| 157 | Concert Harp | Pluck | 1.90 | 0.70 |
| 158 | Chorused Clean Guitar | Guitar | 1.90 | 0.76 |
| 159 | Koto Bend Pluck | Pluck | 1.89 | 0.72 |
| 160 | Steel String Synth | Keys | 1.88 | 0.45 |
| 161 | Chicago Organ Stab | Keys | 1.86 | 0.35 |
| 162 | Metal Hat | Drums | 1.85 | 0.07 |
| 163 | Bossa Nylon Guitar | Guitar | 1.85 | 0.66 |
| 164 | Hyper Pluck Lead | Lead | 1.84 | 0.14 |
| 165 | Dirty Crack Snare | Drums | 1.83 | 0.77 |
| 166 | Four Floor Kick | Drums | 1.83 | 0.74 |
| 167 | Trap Snare | Drums | 1.83 | 0.85 |
| 168 | PWM Pluck | Pluck | 1.81 | 0.26 |
| 169 | Groove Shaker | Drums | 1.81 | 0.11 |
| 170 | Haunted Clap | Drums | 1.81 | 0.67 |
| 171 | Electric Tine Keys | Keys | 1.79 | 0.42 |
| 172 | Trance Gate Lead | Lead | 1.77 | 0.14 |
| 173 | Weeping Guitar | Guitar | 1.77 | 0.52 |
| 174 | Detuned Lullaby | Bell | 1.77 | 0.28 |
| 175 | Glass Piano | Keys | 1.76 | 0.36 |
| 176 | House Clap | Drums | 1.75 | 0.71 |
| 177 | Pizz Hollow Pluck | Pluck | 1.73 | 0.63 |
| 178 | Laser Gun Zap | FX | 1.73 | 0.46 |
| 179 | Bossa Organ Pluck | Pluck | 1.72 | 0.43 |
| 180 | Round Pluck | Pluck | 1.70 | 0.30 |
| 181 | Sync Zap Pluck | Pluck | 1.70 | 0.14 |
| 182 | Vowel Pluck | Pluck | 1.70 | 0.14 |
| 183 | Glockenspiel | Bell | 1.68 | 0.29 |
| 184 | Buzzy Combo Organ | Keys | 1.67 | 0.17 |
| 185 | Soft Horns | Brass | 1.66 | 0.29 |
| 186 | Pain Pluck | Pluck | 1.66 | 0.33 |
| 187 | Laser Harp | Lead | 1.65 | 0.53 |
| 188 | Full Drawbar Organ | Keys | 1.64 | 0.20 |
| 189 | Warm Percussion Organ | Keys | 1.64 | 0.42 |
| 190 | Dark Room Snare | Drums | 1.63 | 0.29 |
| 191 | Bit Crushed Riff | Guitar | 1.63 | 0.11 |
| 192 | Plectrum Synth Pluck | Pluck | 1.61 | 0.51 |
| 193 | Digital Bell Pluck | Pluck | 1.60 | 0.14 |
| 194 | Trap 808 Punch | Bass | 1.59 | 0.78 |
| 195 | Bowed Cymbal | Bell | 1.59 | 0.32 |
| 196 | Open Hat Shimmer | Drums | 1.59 | 0.29 |
| 197 | Bowed Metal Pad | Pad | 1.55 | 0.29 |
| 198 | Tight Rim Snare | Drums | 1.53 | 0.45 |
| 199 | Water Drop Pluck | Pluck | 1.53 | 0.36 |
| 200 | Init | Lead | 1.51 | 0.07 |
| 201 | White Noise Riser | FX | 1.51 | 0.28 |
| 202 | Pulsing String Ostinato | Arp | 1.51 | 0.53 |
| 203 | Laser Zap | FX | 1.49 | 0.13 |
| 204 | Crunchy Shaker | Drums | 1.48 | 0.42 |
| 205 | Synth Piano | Keys | 1.48 | 0.29 |
| 206 | Chain Link Scream | Lead | 1.46 | 1.20 |
| 207 | Mirror Hollow Pluck | Pluck | 1.45 | 0.28 |
| 208 | Col Legno Taps | Strings | 1.44 | 0.68 |
| 209 | Deep Thud Kick | Drums | 1.40 | 0.06 |
| 210 | Mandolin Tremolo | Guitar | 1.40 | 1.09 |
| 211 | House Snare | Drums | 1.37 | 0.29 |
| 212 | Rave Siren Lead | Lead | 1.37 | 1.07 |
| 213 | Closed Hat Tick | Drums | 1.36 | 0.07 |
| 214 | Drill Bell | Bell | 1.35 | 1.47 |
| 215 | Finger Snap | Drums | 1.35 | 0.31 |
| 216 | Emo Saw Lead | Lead | 1.35 | 1.17 |
| 217 | Soft Egg Shaker | Drums | 1.34 | 0.29 |
| 218 | Glitch Stutter | FX | 1.34 | 0.24 |
| 219 | Dusty Closed Hat | Drums | 1.34 | 0.13 |
| 220 | Dark Trap Arp | Arp | 1.33 | 0.30 |
| 221 | Pedal Hat Chick | Drums | 1.33 | 0.07 |
| 222 | Concrete Saw | Bass | 1.32 | 0.78 |
| 223 | Bass House Snarl | Bass | 1.31 | 1.06 |
| 224 | Fingerpicked Pattern Guitar | Guitar | 1.30 | 0.72 |
| 225 | Hard Trance Gate | Arp | 1.29 | 0.89 |
| 226 | Racing Saw Arp | Arp | 1.29 | 0.37 |
| 227 | Gritty Riff Saw | Lead | 1.28 | 0.82 |
| 228 | Dusty Knock Kick | Drums | 1.28 | 0.13 |
| 229 | Shredder Reese | Bass | 1.27 | 0.89 |
| 230 | Wood Block Knock | Drums | 1.26 | 0.07 |
| 231 | Rage Synth Lead | Lead | 1.26 | 0.90 |
| 232 | High Gain Lead Guitar | Guitar | 1.24 | 1.00 |
| 233 | Rage 808 Distorted | Bass | 1.24 | 0.93 |
| 234 | FM Snarl Bass | Bass | 1.23 | 0.93 |
| 235 | Lap Steel Glide | Guitar | 1.20 | 0.67 |
| 236 | Dry Tambourine | Drums | 1.17 | 0.06 |
| 237 | Rage Guitar Lead | Guitar | 1.16 | 0.93 |
| 238 | Harmony Twin Lead | Guitar | 1.15 | 0.94 |
| 239 | Trap Hat Roll | Drums | 1.15 | 0.07 |
| 240 | Tom Drop 808 | Bass | 1.15 | 1.32 |
| 241 | Plucked Sequence | Arp | 1.12 | 0.62 |
| 242 | Night Drive Arp | Arp | 1.11 | 0.38 |
| 243 | Pedal Wah Lead | Guitar | 1.10 | 0.53 |
| 244 | Future House Bass | Bass | 1.10 | 0.86 |
| 245 | Sync Punch Bass | Bass | 1.10 | 0.88 |
| 246 | Gutter Growl | Bass | 1.08 | 0.87 |
| 247 | Drill Slide 808 | Bass | 1.07 | 0.81 |
| 248 | Clipped 808 | Bass | 1.05 | 0.78 |
| 249 | Sawblade Arp | Arp | 1.03 | 0.56 |
| 250 | Skyline Arp | Arp | 1.02 | 0.36 |
| 251 | Phaser Sweep Bass | Bass | 0.96 | 0.75 |
| 252 | Feedback Sustain Guitar | Guitar | 0.96 | 0.58 |
| 253 | Raw Filter Lead | Lead | 0.96 | 0.47 |
| 254 | Searing Sustain Lead | Guitar | 0.96 | 0.72 |
| 255 | Tenor Sax Growl | Woodwind | 0.95 | 0.73 |
| 256 | Hoover Lead | Lead | 0.95 | 0.61 |
| 257 | Acid Line Arp | Arp | 0.93 | 0.52 |
| 258 | Fuzz Octave Lead | Guitar | 0.92 | 0.64 |
| 259 | Zap Drop Lead | Lead | 0.92 | 0.58 |
| 260 | Blues Harmonica | Woodwind | 0.90 | 0.69 |
| 261 | Acid Scream Lead | Lead | 0.89 | 0.51 |
| 262 | Distorted Riff Saw | Lead | 0.88 | 0.63 |
| 263 | Acid Bath | Bass | 0.87 | 0.46 |
| 264 | Gospel Slide Guitar | Guitar | 0.87 | 0.65 |
| 265 | Slide Blues Guitar | Guitar | 0.87 | 0.77 |
| 266 | Grind Square Bass | Bass | 0.85 | 0.59 |
| 267 | Rivet Gun | Bass | 0.84 | 0.50 |
| 268 | Muted Disco Picking | Guitar | 0.83 | 0.42 |
| 269 | Squelch Box | Bass | 0.80 | 0.42 |
| 270 | Rust Bass | Bass | 0.80 | 0.42 |
| 271 | Long Glide 808 | Bass | 0.80 | 0.49 |
| 272 | Acid Rave Arp | Arp | 0.78 | 0.20 |
| 273 | Bit Riot Lead | Lead | 0.77 | 0.56 |
| 274 | Fold Glide 808 | Bass | 0.77 | 0.45 |
| 275 | Lonely Whistle Lead | Lead | 0.76 | 0.57 |
| 276 | Crushed Rage 808 | Bass | 0.74 | 0.51 |
| 277 | Eighties Solo Lead | Lead | 0.73 | 0.34 |
| 278 | Disco Octave Arp | Arp | 0.71 | 0.39 |
| 279 | Rolling Tech Bass | Bass | 0.71 | 0.65 |
| 280 | Soprano Sax Smooth | Woodwind | 0.70 | 0.41 |
| 281 | Neon Anthem | Lead | 0.69 | 0.36 |
| 282 | Audible 808 Glide | Bass | 0.69 | 0.47 |
| 283 | Filter Sweep Lead | Lead | 0.68 | 0.44 |
| 284 | Praise Bass | Bass | 0.68 | 0.45 |
| 285 | Fuzz Bassline | Bass | 0.68 | 0.44 |
| 286 | Distorted Reese | Bass | 0.68 | 0.46 |
| 287 | Deep House Organ Bass | Bass | 0.67 | 0.45 |
| 288 | Slow Tears 808 | Bass | 0.66 | 0.51 |
| 289 | Sliding 808 | Bass | 0.66 | 0.47 |
| 290 | Kick Sub Smash | Bass | 0.65 | 0.42 |
| 291 | Mechanic Bass | Bass | 0.65 | 0.42 |
| 292 | Choir Solo Lead | Lead | 0.64 | 0.44 |
| 293 | Rubber Square Line | Bass | 0.64 | 0.09 |
| 294 | House Groove Arp | Arp | 0.63 | 0.18 |
| 295 | Overload 808 | Bass | 0.62 | 0.43 |
| 296 | Phase Mod Lead | Lead | 0.62 | 0.44 |
| 297 | Tin Croon | Lead | 0.61 | 0.37 |
| 298 | Furnace Sub | Bass | 0.61 | 0.45 |
| 299 | Round Analog Bass | Bass | 0.58 | 0.09 |
| 300 | Pulse Lead | Lead | 0.58 | 0.20 |
| 301 | Machine Riff | Lead | 0.57 | 0.30 |
| 302 | Sinister Saw Lead | Lead | 0.56 | 0.32 |
| 303 | Oboe Solo | Woodwind | 0.56 | 0.35 |
| 304 | Portamento Whine Lead | Lead | 0.52 | 0.60 |
| 305 | Formant Whistle | Lead | 0.52 | 0.29 |
| 306 | Fiddle Folk | Strings | 0.51 | 0.52 |
| 307 | Dark Cello Line | Strings | 0.51 | 0.29 |
| 308 | Solo Violin | Strings | 0.51 | 0.31 |
| 309 | Sinister Choir Lead | Lead | 0.51 | 0.26 |
| 310 | Bassoon Low | Woodwind | 0.50 | 0.30 |
| 311 | Glide Sine Lead | Lead | 0.50 | 0.38 |
| 312 | Modular Pluck Bass | Bass | 0.50 | 0.07 |
| 313 | Simple Up Arp | Arp | 0.50 | 0.14 |
| 314 | Octave Bounce Lead | Lead | 0.50 | 0.26 |
| 315 | Solo Cello | Strings | 0.49 | 0.30 |
| 316 | G-Funk Rubber Bass | Bass | 0.49 | 0.07 |
| 317 | Concert Flute | Woodwind | 0.49 | 0.29 |
| 318 | Funk Slap Bass | Bass | 0.47 | 0.06 |
| 319 | Duduk Lament | Woodwind | 0.47 | 0.28 |
| 320 | Cathedral Low End | Bass | 0.34 | 0.07 |
| 321 | Shock Collar | Bass | 0.34 | 0.12 |
| 322 | Big Room Saw Bass | Bass | 0.32 | 0.06 |
| 323 | French Disco Bass | Bass | 0.31 | 0.09 |
| 324 | Filter House Bass | Bass | 0.31 | 0.09 |
| 325 | Bitcrush Sub | Bass | 0.31 | 0.12 |
| 326 | Pulse Engine Bass | Bass | 0.30 | 0.07 |
| 327 | Grid Pulse Bass | Bass | 0.29 | 0.07 |
| 328 | Simple Saw Bass | Bass | 0.28 | 0.07 |
| 329 | Plain Saw Lead | Lead | 0.28 | 0.07 |
| 330 | Warehouse Filter Bass | Bass | 0.28 | 0.09 |
| 331 | Grid FM Pulse | Bass | 0.27 | 0.07 |
| 332 | Boogie Bass | Bass | 0.26 | 0.06 |
| 333 | Square Lead | Lead | 0.26 | 0.12 |
| 334 | Pure Sub | Bass | 0.26 | 0.07 |
| 335 | Velvet Rope Bass | Bass | 0.25 | 0.06 |
| 336 | Clean 808 | Bass | 0.24 | 0.07 |
