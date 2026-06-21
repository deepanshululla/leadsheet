\version "2.24.0"

\header {
  title = "Rush E"
  composer = "Sheet Music Boss (Andrew Wrangell), 2018"
  subtitle = "Main theme — recognizable reduction of the official MIDI"
  poet = "Transcribed from the published MIDI (archive.org/details/rush-e_202312). Not public domain."
  tagline = ##f
}

% Faithful reduction of the RECOGNIZABLE main theme, transcribed note-for-note
% from the official Rush E MIDI (parsed with music21), not from memory:
%   - intro: the single E4 that accelerates from sparse hits into a blur
%   - the drop: E4 sixteenth "spam" with the genuine E-F-E-D#-E turn, then the
%     A4 -> C5 -> D5 ... B4-F#-G# answer phrase
%   - left hand: the broken-Am walking bass (A2 . C3-E3 . E2 . C3-E3) with the
%     G#/E7 turnaround that is the harmonic engine of the groove
% The full piece is a 3200-note "impossible" texture across all 88 keys; this is
% the recognizable theme only, octaves and rhythm taken straight from the MIDI.

global = { \key a \minor \time 4/4 \tempo 4 = 120 }

right = {
  \global
  \clef treble
  e'4 e'4 e'8 e'8 e'8 e'8                                              | % intro: accelerating E
  e'16 e' e' e' e' e' e' e' e' e' e' e' e' e' e' e'                    | % RUSH E
  e'16 e' e' e' e' e' e' e' e' e' e' e' e' e' e' e'                    | % RUSH E
  e'16 e' e' e' e'16 f' e' ees' e'8 a'8 c''4                           | % E-F-E-D#-E, up to A C
  d''16 d'' d'' d'' d''16 c'' b' d'' c''16 c'' c'' c'' c''16 b' a' c'' | % D ... C ... answer
  b'16 b' b' b' fis'8 b'8 gis'2                                        | % B ... F# B, G#
  e'16 e' e' e' e' e' e' e' e' e' e' e' e' e' e' e'                    | % RUSH E
  <a' c'' e''>1                                                        \bar "|." % resolve to Am
}

left = {
  \global
  \clef bass
  r1                                                                  | % (intro: RH alone)
  r1                                                                  |
  a,8 <c e>8 e,8 <c e>8 a,8 <c e>8 e,8 <c e>8                          | % Am vamp
  a,8 <c e>8 e,8 <c e>8 a,8 <c e>8 e,8 <c e>8                          | % Am vamp
  gis,8 <d e>8 e,8 <d e>8 a,8 <c e>8 e,8 <c e>8                        | % E7 -> Am
  b,8 <dis a>8 fis,8 <dis a>8 e,8 <gis b>8 e,8 <gis b>8                | % turnaround (E7)
  a,8 <c e>8 e,8 <c e>8 a,8 <c e>8 e,8 <c e>8                          | % Am vamp
  <a, c e>1                                                           \bar "|." % Am
}

harmonies = \chordmode {
  s1 | s1 |
  a1:m | a1:m |
  e2:7 a2:m | e1:7 |
  a1:m | a1:m |
}

\score {
  <<
    \new ChordNames \harmonies
    \new PianoStaff <<
      \new Staff = "up"   \right
      \new Staff = "down" \left
    >>
  >>
  \layout { }
}

\score {
  \new PianoStaff <<
    \new Staff = "up"   { \unfoldRepeats \right }
    \new Staff = "down" { \unfoldRepeats \left }
  >>
  \midi { \tempo 4 = 120 }
}
