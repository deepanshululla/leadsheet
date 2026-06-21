\version "2.24.0"

\include "lead-sheet.ily"

#(set-global-staff-size 24)

\header {
  title = "Happy Birthday to You"
  composer = "Traditional"
  poet = "Key of C major"
  tagline = ##f
}

melody = {
  \key c \major
  \time 3/4
  \partial 4
  g'8. g'16              |  % Hap-py
  a'4 g'4 c''4           |  % Birth-day to
  b'2 g'8. g'16          |  % you ~ Hap-py
  a'4 g'4 d''4           |  % Birth-day to
  c''2 g'8. g'16         |  % you ~ Hap-py
  g''4 e''4 c''4         |  % Birth-day dear
  b'4( a'4) f''8. f''16  |  % [Name] ~ Hap-py
  e''4 c''4 d''4         |  % Birth-day to
  c''2.                  \bar "|."  % you
}

words = \lyricmode {
  Hap -- py Birth -- day to you
  Hap -- py Birth -- day to you
  Hap -- py Birth -- day dear "[Name]"
  Hap -- py Birth -- day to you
}

harmonies = \chordmode {
  s4         |
  c2.        |
  g2.:7      |
  c2.        |
  c2.        |
  c2.        |
  c2.:7      |
  f4 c4 g4:7 |
  c2.        |
}

\score {
  <<
    \new ChordNames \harmonies
    \new Staff \new Voice = "mel" { \ezHeads \melody }
    \new Lyrics \lyricsto "mel" \words
  >>
  \layout { }
  \midi { \tempo 4 = 112 }
}
