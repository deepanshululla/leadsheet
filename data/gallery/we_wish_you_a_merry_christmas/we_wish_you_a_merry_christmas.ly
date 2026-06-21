\version "2.24.0"

\include "lead-sheet.ily"

#(set-global-staff-size 24)

\header {
  title = "We Wish You a Merry Christmas"
  composer = "Traditional English Carol"
  poet = "Key of G major"
  tagline = ##f
}

% Popular (Arthur Warrell-style) arrangement: the high "Good tidings" chorus.
% Melody + lyrics are exact; chord symbols recovered from the engraved score.
melody = {
  \key g \major
  \time 3/4
  \partial 4
  %% ---------- Verse ----------
  d'4                        |  % We
  g'4 g'8 a'8 g'8 fis'8      |  % wish you a mer-ry   (G G A G F#)
  e'4 e'4 e'4                |  % Christ-mas, We      (E E E)
  a'4 a'8 b'8 a'8 g'8        |  % wish you a mer-ry   (A A B A G)
  fis'4 fis'4 fis'4          |  % Christ-mas, We      (F# F# F#)
  b'4 b'8 c''8 b'8 a'8       |  % wish you a mer-ry   (B B C B A)
  c''4 b'4 a'8 a'8           |  % Christ-mas and a    (C B A A)
  a'4 b'4 a'4                |  % hap-py New          (A B A)
  g'2 b'4                    |  % Year ~ Good         (G ~ B pickup)
  %% ---------- Chorus: "Good tidings" ----------
  c''4 c''4 c''4             |  % tid-ings we         (C C C)
  b'2 a'4                    |  % bring to            (B A)
  c''4 b'4 a'4               |  % you and your        (C B A)
  a'2 b'4                    |  % kin, Good           (A ~ B pickup)
  d''4 c''4 b'4              |  % tid-ings for        (D C B)
  e''4 c''4 b'8 a'8          |  % Christ-mas and a    (E C B A)
  a'4 b'4 a'4                |  % Hap-py New          (A B A)
  g'2.                       \bar "|."  % Year         (G)
}

words = \lyricmode {
  We
  wish you a mer -- ry
  Christ -- mas, We
  wish you a mer -- ry
  Christ -- mas, We
  wish you a mer -- ry
  Christ -- mas and a
  hap -- py New
  Year! Good
  tid -- ings we
  bring to
  you and your
  kin, Good
  tid -- ings for
  Christ -- mas and a
  Hap -- py New
  Year!
}

harmonies = \chordmode {
  s4    |          % We (pick-up)
  g2.   |          % G   - wish you a mer-ry
  c2.   |          % C   - Christ-mas we
  a2.   |          % A   - wish you a mer-ry
  d2.   |          % D   - Christ-mas we
  b2.:7 |          % B7  - wish you a mer-ry
  e2.:m |          % Em  - Christ-mas and a
  c2.   |          % C   - hap-py New
  d2.   |          % D   - Year ~ Good
  g2.   |          % G   - tid-ings we
  d2.   |          % D   - bring to
  a2.   |          % A   - you and your
  d2.:7 |          % D7  - kin ~ Good
  g2.   |          % G   - tid-ings for
  c4 d2 |          % C D - Christ-mas and a
  d2.   |          % D   - Hap-py New
  g2.   |          % G   - Year
}

\score {
  <<
    \new ChordNames \harmonies
    \new Staff \new Voice = "mel" { \ezHeads \melody }
    \new Lyrics \lyricsto "mel" \words
  >>
  \layout { }
  \midi { \tempo 4 = 120 }
}
