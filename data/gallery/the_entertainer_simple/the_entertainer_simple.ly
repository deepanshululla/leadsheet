\version "2.24.0"

\include "lead-sheet.ily"

#(set-global-staff-size 24)

\header {
  title = "The Entertainer (simple theme)"
  composer = "Scott Joplin"
  poet = "Key of C major — simplified single-line melody"
  tagline = ##f
}

% A single-line reduction of the famous A-strain (right-hand top voice only),
% with a letter-note row. Rhythm and octaves follow the public-domain Mutopia
% two-hand edition (the_entertainer.ly, bars 5-12), so the ragtime syncopation
% and the characteristic octave leaps (low E vs accented high C, chromatic run
% up in the upper octave) are preserved. Written in absolute octaves for clarity.
melody = \absolute {
  \key c \major
  \time 2/4
  \tempo "Not fast"
  \partial 8
  d'16 dis'                          |  % D  D#            (pick-up)
  e'16 c''8 e'16 c''8 e'16 c''8 ~    |  % E  C  E  C  E  C  (syncopated leap figure)
  c''4 ~ c''16 c''' d''' dis'''      |  % C ~  C  D  D#     (cadence + chromatic run)
  e''' c''' d''' e''' ~ e''' b'' d'''8 |  % E  C  D  E ~ E  B  D
  c'''4 ~ c'''8 d'16 dis'            |  % C ~  C  D  D#     (re-take pick-up)
  e'16 c''8 e'16 c''8 e'16 c''8 ~    |  % E  C  E  C  E  C  (syncopated leap figure)
  c''4 ~ c''8 a''16 g''              |  % C ~  C  A  G
  fis'' a'' c''' e''' ~ e''' d''' c''' a'' |  % F# A  C  E ~ E  D  C  A
  d'''4 ~ d'''8 r8                   |  % D ~  D            (rest)
  c''2                               \bar "|."  % C  (final)
}

harmonies = \chordmode {
  s8   |          % under the pick-up
  c2   |
  c2   |
  c2   |
  g2:7 |
  c2   |
  c2   |
  d2:7 |
  g2:7 |
  c2   |
}

\score {
  <<
    \new ChordNames \harmonies
    \new Staff \new Voice = "mel" { \ezHeads \melody }
  >>
  \layout { }
  \midi { \tempo 4 = 100 }
}
