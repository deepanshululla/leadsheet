\version "2.24.0"

\header {
  title = "Love Me Tender"
  composer = "Words and Music by Elvis Presley and Vera Matson"
  subtitle = "EZ-Play style — letter names inside the noteheads"
  tagline = ##f
}

#(set-global-staff-size 26)

global = { \key c \major \time 4/4 \tempo 4 = 76 }

% Transcribed bar-by-bar from the EZ Play page (p.156). C major, 4/4.
melody = {
  \global
  \clef treble
  \easyHeadsOn
  % uppercase letters inside the heads (matches the project's note-name style)
  \override NoteHead.note-names = #(vector "C" "D" "E" "F" "G" "A" "B")

  g4 c' b c'    | d'4 a4 d'2   | c'4 b4 a4 b4  |   % Love me ten-der / love me sweet / Nev-er let me
  c'1           | g4 c' b c'   | d'4 a4 d'2    | c'4 b4 a4 b4 |  % go. / You have made my / life com-plete / And I love you
  c'1           | e'4 e' e' e' | e'4 e' e'2    | e'4 d' c' d' |  % so. / Love me ten-der / love me true / All my dreams ful-
  e'1           | e'4 e' f' e' | d'4 a4 d'2    | c'4 b4 a4 b4 \bar "|."  % fill. / For my dar-lin' / I love you / And I al-ways
}

words = \lyricmode {
  Love me ten -- der, love me sweet; Nev -- er let me
  go. You have made my life com -- plete, And I love you
  so. Love me ten -- der, love me true, All my dreams ful --
  fill. For, my dar -- lin', I love you, And I al -- ways
}

harmonies = \chordmode {
  c1 | d1:7 | d2:m g2:7 |
  c1 | c1 | d1:7 | d2:m g2:7 |
  c1 | e2:7 a2:m | c1:7 | f2 f2:m |
  c1 | a1:7 | d1:7 | d2:m g2:7 |
}

% boxed chord symbols, like the EZ-Play chord squares
boxedChords = \new ChordNames \with {
  \override ChordName.stencil =
    #(lambda (grob)
       (box-stencil (ly:text-interface::print grob) 0.12 0.45))
} \harmonies

\score {
  <<
    \boxedChords
    \new Staff { \new Voice = "mel" \melody }
    \new Lyrics \lyricsto "mel" \words
  >>
  \layout { }
}

\score {
  << \melody \harmonies >>
  \midi { \tempo 4 = 76 }
}
