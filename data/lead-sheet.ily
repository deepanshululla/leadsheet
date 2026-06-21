%% lead-sheet.ily — shared helpers for the leadsheet collection.
%%
%% Provides `uppercase-note-name`, a noteNameFunction for the \NoteNames context
%% that prints letter notes in uppercase with readable accidentals: C, F#, Bb.
%% Use as:  \new NoteNames \with { noteNameFunction = #uppercase-note-name } { \melody }

\version "2.24.0"

#(define uppercase-note-name
   ;; Signature matches the default note-name->markup: (pitch context) -> markup.
   (lambda (pitch context)
     (let* ((idx     (ly:pitch-notename pitch))
            (alter   (ly:pitch-alteration pitch))
            (letters (vector "C" "D" "E" "F" "G" "A" "B"))
            (letter  (vector-ref letters idx))
            (acc     (cond ((= alter -1)   "bb")
                           ((= alter -1/2) "b")
                           ((= alter 1/2)  "#")
                           ((= alter 1)    "##")
                           (else           ""))))
       (markup (string-append letter acc)))))

%% ezHeads — EZ-Play / big-note style: print the letter name INSIDE each
%% notehead (uppercase), instead of a separate row below the staff.
%% Apply to a melody voice:  \new Voice = "mel" { \ezHeads \melody }
%% Pair with  #(set-global-staff-size 24)  so the letters are legible.
ezHeads = {
  \easyHeadsOn
  \override NoteHead.note-names = #(vector "C" "D" "E" "F" "G" "A" "B")
}
