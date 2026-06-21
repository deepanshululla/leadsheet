\version "2.24.0"

\header {
  title = "The Entertainer"
  composer = "Scott Joplin"
  subtitle = "Transcribed from a MuseScore easy-piano arrangement"
  tagline = ##f
}

#(set-global-staff-size 21)

global = {
  \key c \major
  \time 4/4
  \tempo 4 = 100
  % EZ-Play style: letter names printed inside the noteheads (uppercase C D E ...)
  \easyHeadsOn
  \override NoteHead.note-names = #(vector "C" "D" "E" "F" "G" "A" "B")
}

%% Force at most 4 measures per line (skip-voice carries the breaks so the
%% note staves keep a single voice / natural stem directions).
lineBreaks = { \repeat unfold 9 { s1*4 \break } }

%% ===========================================================================
%% TOP STAFF (treble / right hand)
%% Transcribed bar-by-bar from the three source images.
%% Octave: c' = middle C (C4); the melody sits mostly in the c'' (C5) octave.
%% ===========================================================================
top = \relative c'' {
  \global
  \clef treble

  % ---- m1 (intro, f): descending run then tied C's, triplet, A ----
  \mark \markup { \bold "1" }
  e8\f d8 c8 c8 c8( c8) \tuplet 3/2 { c8 e8 } a8 |
  % ---- m2 : descending eighths (under watermark - reconstructed) ----
  g8 g8 e8 d8 e8 c8 d8 b8 |
  % ---- m3 : ascending eighth run ----
  c8 d8 e8 g8 a8 b8 c8 d8 |
  % ---- m4 : half rest, marcato chord, E-F# eighths ----
  r2 <d g>4-^ e8 fis8 |

  % ===== SEGNO : A-strain begins (m5, p) =====
  \mark \markup { \musicglyph "scripts.segno" }
  % ---- m5 (p): C-E rocking ----
  c8\p e8 c8 e8 c8 e8 c4 |
  % ---- m6 : tied half then run up to F# (cresc) ----
  c2~\< c8 e8 c8 fis8 |
  % ---- m7 (f): run, descending eighths ----
  c8\f e8 c8 e8 c8 e8 d8 c8 |
  % ---- m8 : dotted-half D, E-F# eighths (accent) ----
  d2.( e8) fis8-> |

  % ---- m9 (p): D#, with grace figure ----
  dis8\p d8 c8 e8 d2 |
  % ---- m10 (cresc): triplet-ish run up to high C, F# ----
  \tuplet 3/2 { c8 e8 g8 } \tuplet 3/2 { c8 d8 e8 } fis4 g8 r8 |
  % ---- m11 (dim): dotted-half C, eighths ----
  c2.( e8) fis8-> |
  % ---- m12 : descending phrase ----
  e8 d8 c8 e8 d8 c8 b8 g8 |
  % ---- m13 : closing of strain ----
  c2. e8 c8 |

  % ---- m14 (p): B-strain / second theme begins ----
  c8\p d8 ees8 d8 c8 e8 g8 e8 |
  % ---- m15 : (cresc) ----
  c2.\< d8 b8 |
  % ---- m16 (f): run up to F# ----
  c8\f e8 g8 c8 b8 a8 g8 fis8 |
  % ---- m17 : (natural) dotted-half, eighths ----
  d2. e8 fis8 |

  % ===== m18 ("To Coda") =====
  \mark \markup { \italic "To Coda" }
  c8 e8 c8 e8 d8 c8 d8 e8 |
  % ---- m19 ----
  c8 e8 c8 e8 c8 d8 e8 c8 |
  % ---- m20 : half C, rest, eighths up to F# ----
  c2 r8 e8 dis8 e8 |
  % ---- m21 (f): C run ----
  c8\f e8 c8 e8 d8 e8 c8 d8 |

  % ---- m22 : eighths up, descending ----
  c8 d8 e8 c8 g'8 e8 d8 c8 |
  % ---- m23 ----
  c8 d8 e8 g8 c8 d8 e8 c8 |
  % ---- m24 : half then rest then F# eighths ----
  d2 r8 c8 b8 c8 |
  % ---- m25 ----
  e8 c8 d8 c8( c8) e8 dis8 e8 |
  % ---- m26 ----
  c8 d8 e8 c8 g'8 e8 dis8 e8 |

  % ===== m27 (page 2 system 3) =====
  c8 d8 e8 fis8 g8 a8 g8 e8 |
  % ---- m28 : (cresc / >) ----
  c2~\> c8 e8 dis8 e8 |
  % ---- m29 (p): ----
  c8\p e8 d8 c8 d8 e8 dis8 e8 |
  % ---- m30 : ----
  c8 e8 c8( c8) d8 e8 c'8 g8 |
  % ---- m31 (cresc): ----
  e8\< d8 c8 e8 c8 d8 e8 g8 |

  % ===== m32 (page 2 system 4) =====
  c2( c8) e8 dis8 e8 |
  % ---- m33 (p): ----
  c8\p d8 e8 c8 g'8 e8 d8 c8 |
  % ---- m34 : ----
  c2~ c8 e8 d8 c8 |
  % ---- m35 : ----
  fis8 g8 a8 g8 fis8 e8 d8 c8 |

  % ===== m36 (page 3) =====
  <b d>2.( e8) fis8-> |
  % ===== m37 ("D.S. al Coda") =====
  \mark \markup { \italic "D.S. al Coda" }
  c1 |
  % ===== m38 (Coda - final tonic) =====
  \mark \markup { \musicglyph "scripts.coda" }
  <c e>4 r4 r2 |
}

%% ===========================================================================
%% BOTTOM STAFF (bass / left hand)
%% ===========================================================================
bottom = \relative c {
  \global
  \clef bass

  % ---- m1 : rest ----
  R1 |
  % ---- m2 : rest ----
  R1 |
  % ---- m3 : descending eighth walk C-B-Bb ----
  c8 d8 c8 b8( b8) c8 b8 bes8 |
  % ---- m4 : oom-pah ----
  c4 r4 c4 r4 |

  % ===== SEGNO m5 : stride bass C / chord =====
  c4 <e g>4 g,4 <bes' c>4 |
  % ---- m6 ----
  c,4 <e g>4 cis4 <e g>4 |
  % ---- m7 ----
  c4 <bes' c>4 c,4 <e g>4 |
  % ---- m8 ----
  g4 <d' g>4 g,4 <d' g>4 |

  % ---- m9 ----
  c4 <e g>4 cis4 <bes' c>4 |
  % ---- m10 ----
  c,4 <e g>4 g4 <c e>4 |
  % ---- m11 ----
  c,4 <e g>4 c4 <e g>4 |
  % ---- m12 ----
  c4 cis4 d4 g,4 |
  % ---- m13 ----
  c4 <e g>4 c4 r4 |

  % ---- m14 ----
  c4 <e g>4 ees4 <a c>4 |
  % ---- m15 ----
  c,4 <e g>4 g,4 <bes' c>4 |
  % ---- m16 ----
  c,4 <e g>4 cis4 <e g>4 |
  % ---- m17 ----
  g4 <d' g>4 g,4 <d' g>4 |

  % ===== m18 ("To Coda") =====
  c4 <e g>4 ees4 <e g>4 |
  % ---- m19 ----
  c4 <e g>4 c4 <e g>4 |
  % ---- m20 ----
  <c e>4 g4 c,4 r4 |
  % ---- m21 ----
  c4 <e g>4 c4 <e g>4 |

  % ---- m22 ----
  <c e>4 g'4 c,4 <bes' c>4 |
  % ---- m23 ----
  c,4 <e g>4 g,4 <e' g>4 |
  % ---- m24 ----
  c,4 <e g>4 g,2 |
  % ---- m25 ----
  <c e>4 g'4 c,4 g'4 |
  % ---- m26 ----
  <c, e>4 g'4 c,4 g'4 |

  % ===== m27 =====
  c,4 <e g>4 cis4 <e g>4 |
  % ---- m28 ----
  <c e>4 b4 c4 cis4 |
  % ---- m29 ----
  c4 <e g>4 c4 <e g>4 |
  % ---- m30 ----
  c4 d4 e4 g,4 |
  % ---- m31 ----
  c4 <e g>4 c4 <bes' c>4 |

  % ===== m32 =====
  c,4 cis4 d4 g,4 |
  % ---- m33 ----
  <c e>4 g'4 cis,4 <e g>4 |
  % ---- m34 ----
  c4 <e g>4 g,4 <e' g>4 |
  % ---- m35 ----
  c,4 cis4 d4 <fis a>4 |

  % ===== m36 =====
  d'4 c4 a4 r4 |
  % ===== m37 ("D.S. al Coda") =====
  <c, e>4 g'4 c,4 r4 |
  % ===== m38 (Coda) =====
  c,4 r4 r2 |
}

\score {
  \new PianoStaff <<
    \new Staff = "up" \top
    \new Dynamics \lineBreaks
    \new Staff = "down" \bottom
  >>
  \layout { }
}

\score {
  \unfoldRepeats
  \new PianoStaff <<
    \new Staff = "up" \top
    \new Staff = "down" \bottom
  >>
  \midi { \tempo 4 = 100 }
}
