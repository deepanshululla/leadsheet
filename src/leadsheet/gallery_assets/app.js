/* leadsheet gallery — Synthesia-style falling-notes piano, synced to the <audio>.
 * Reads window.SONG = { notes: [[midi,start,dur],...], audio, duration }.
 * No dependencies. Notes scroll down a lane and light the keys as they land. */
(function () {
  "use strict";
  var SONG = window.SONG || { notes: [], duration: 0 };
  var notes = SONG.notes || [];
  var measures = SONG.measures || [];
  var hl = document.getElementById("hl");
  var hlIndex = -2;
  var canvas = document.getElementById("piano");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  var audio = document.getElementById("audio");
  var playBtn = document.getElementById("play");
  var clock = document.getElementById("clock");
  var readout = document.getElementById("now");
  var FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif';
  var lastReadout = "";

  var LOOKAHEAD = 3.0; // seconds of falling-note runway above the keyboard
  var KEY_H = 78;      // keyboard height in CSS px

  // ---- pitch range -> key layout -------------------------------------
  var WHITE = { 0: 1, 2: 1, 4: 1, 5: 1, 7: 1, 9: 1, 11: 1 }; // C D E F G A B
  var lo = 60, hi = 72;
  if (notes.length) {
    lo = Math.min.apply(null, notes.map(function (n) { return n[0]; }));
    hi = Math.max.apply(null, notes.map(function (n) { return n[0]; }));
  }
  while (!WHITE[((lo % 12) + 12) % 12]) lo--;       // start on a white key
  while (!WHITE[((hi % 12) + 12) % 12]) hi++;        // end on a white key
  lo -= 2; hi += 2;                                  // a little padding

  var whites = [];
  for (var m = lo; m <= hi; m++) if (WHITE[((m % 12) + 12) % 12]) whites.push(m);
  var whiteIndex = {};
  whites.forEach(function (m, i) { whiteIndex[m] = i; });

  function hue(midi) { return (((midi % 12) + 12) % 12) * 30; }
  function noteColor(midi, a) { return "hsla(" + hue(midi) + ",85%,62%," + (a == null ? 1 : a) + ")"; }

  var NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
  function midiName(midi) { return NAMES[((midi % 12) + 12) % 12] + (Math.floor(midi / 12) - 1); }

  // geometry recomputed on resize
  var W = 0, H = 0, ww = 0, laneH = 0, dpr = 1;
  function layout() {
    dpr = window.devicePixelRatio || 1;
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ww = W / whites.length;
    laneH = H - KEY_H;
  }

  function midiX(midi) {
    var pc = ((midi % 12) + 12) % 12;
    if (WHITE[pc]) return { x: whiteIndex[midi] * ww, w: ww, black: false };
    // black key sits between its lower white neighbour and the next
    var below = whiteIndex[midi - 1];
    if (below == null) below = whiteIndex[midi + 1] - 1;
    var bw = ww * 0.62;
    return { x: (below + 1) * ww - bw / 2, w: bw, black: true };
  }

  function rr(x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function active(now) {
    var on = {};
    for (var i = 0; i < notes.length; i++) {
      var s = notes[i][1], d = notes[i][2];
      if (now >= s && now < s + d) on[notes[i][0]] = 1;
    }
    return on;
  }

  function draw() {
    var now = audio && !isNaN(audio.currentTime) ? audio.currentTime : 0;
    var kbTop = H - KEY_H;
    ctx.clearRect(0, 0, W, H);

    // lane backdrop + faint white-key gridlines
    ctx.fillStyle = "#0b0814";
    ctx.fillRect(0, 0, W, kbTop);
    ctx.strokeStyle = "#ffffff08"; ctx.lineWidth = 1;
    for (var i = 0; i <= whites.length; i++) {
      ctx.beginPath(); ctx.moveTo(i * ww, 0); ctx.lineTo(i * ww, kbTop); ctx.stroke();
    }

    // falling notes within the lookahead window
    for (var n = 0; n < notes.length; n++) {
      var midi = notes[n][0], s = notes[n][1], d = notes[n][2];
      var dt = s - now;                       // time until this note lands
      if (dt > LOOKAHEAD || s + d < now) continue;
      var geo = midiX(midi);
      var hgt = Math.max(6, (d / LOOKAHEAD) * laneH);
      var yTop = kbTop - hgt - (dt / LOOKAHEAD) * laneH;
      var pad = geo.black ? 2 : 3;
      var playing = now >= s && now < s + d;
      ctx.shadowColor = noteColor(midi, 0.9);
      ctx.shadowBlur = playing ? 22 : 8;
      var grad = ctx.createLinearGradient(0, yTop, 0, yTop + hgt);
      grad.addColorStop(0, noteColor(midi, 0.95));
      grad.addColorStop(1, "hsla(" + hue(midi) + ",85%,46%,0.95)");
      ctx.fillStyle = grad;
      rr(geo.x + pad, yTop, geo.w - pad * 2, hgt, 5); ctx.fill();
      ctx.shadowBlur = 0;
      // letter inside the block when there's room to read it — white text with
      // a dark outline so it stays legible on any block color (incl. dark hues)
      if (hgt > 15 && geo.w > 13) {
        var lx = geo.x + geo.w / 2, ly = yTop + Math.min(hgt / 2, 15);
        ctx.font = "700 11px " + FONT;
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.lineWidth = 3; ctx.strokeStyle = "rgba(0,0,0,.6)";
        ctx.lineJoin = "round";
        ctx.strokeText(midiName(midi), lx, ly);
        ctx.fillStyle = "#fff";
        ctx.fillText(midiName(midi), lx, ly);
      }
    }

    // keyboard
    var on = active(now);
    ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
    // white keys
    for (var w = 0; w < whites.length; w++) {
      var mw = whites[w], x = w * ww;
      ctx.fillStyle = on[mw] ? noteColor(mw, 0.9) : "#f3eee9";
      rr(x + 1, kbTop, ww - 2, KEY_H, 4); ctx.fill();
      if (on[mw]) { ctx.shadowColor = noteColor(mw); ctx.shadowBlur = 18; ctx.fill(); ctx.shadowBlur = 0; }
      ctx.strokeStyle = "#0008"; ctx.lineWidth = 1; ctx.stroke();
      if (on[mw] && ww > 13) {  // label the lit white key
        ctx.fillStyle = "#15101f"; ctx.font = "700 10px " + FONT;
        ctx.fillText(midiName(mw), x + ww / 2, kbTop + KEY_H - 7);
      }
    }
    // black keys on top
    for (var b = lo; b <= hi; b++) {
      if (WHITE[((b % 12) + 12) % 12]) continue;
      var g = midiX(b), bh = KEY_H * 0.62;
      ctx.fillStyle = on[b] ? noteColor(b, 0.95) : "#1a1326";
      rr(g.x, kbTop, g.w, bh, 3); ctx.fill();
      if (on[b]) {
        ctx.shadowColor = noteColor(b); ctx.shadowBlur = 16; ctx.fill(); ctx.shadowBlur = 0;
        if (g.w > 12) {  // label the lit black key
          ctx.fillStyle = "#15101f"; ctx.font = "700 9px " + FONT;
          ctx.fillText(midiName(b).replace("♯", "#"), g.x + g.w / 2, kbTop + bh - 6);
        }
      }
    }

    // strike line
    ctx.fillStyle = "#ffffff22";
    ctx.fillRect(0, kbTop - 2, W, 2);

    updateReadout(on);
    updateOverlay(now);
    if (clock) clock.textContent = fmt(now) + " / " + fmt(SONG.duration || (audio ? audio.duration : 0));
    requestAnimationFrame(draw);
  }

  function updateOverlay(now) {
    if (!hl || !measures.length) return;
    var idx = -1;
    for (var i = 0; i < measures.length; i++) {
      if (now >= measures[i].t0 && now < measures[i].t1) { idx = i; break; }
    }
    if (idx === hlIndex) return;          // only touch styles when it changes
    hlIndex = idx;
    if (idx < 0) { hl.style.opacity = "0"; return; }
    var m = measures[idx];
    hl.style.left = (m.x * 100) + "%";
    hl.style.top = (m.y * 100) + "%";
    hl.style.width = (m.w * 100) + "%";
    hl.style.height = (m.h * 100) + "%";
    hl.style.opacity = "1";
  }

  function updateReadout(on) {
    if (!readout) return;
    var midis = Object.keys(on).map(Number).sort(function (a, b) { return a - b; });
    var key = midis.join(",");
    if (key === lastReadout) return;       // only touch the DOM when it changes
    lastReadout = key;
    if (!midis.length) {
      readout.innerHTML = '<span class="now-label">Now playing</span>' +
        '<span class="now-empty">—</span>';
      return;
    }
    var chips = midis.map(function (m) {
      return '<span class="chip" style="--c:' + noteColor(m) +
        '">' + midiName(m) + "</span>";
    }).join("");
    readout.innerHTML = '<span class="now-label">Now playing</span>' + chips;
  }

  function fmt(t) {
    if (!t || isNaN(t)) t = 0;
    var m = Math.floor(t / 60), s = Math.floor(t % 60);
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  // ---- controls -------------------------------------------------------
  function setLabel() {
    if (!playBtn) return;
    playBtn.textContent = audio && !audio.paused ? "❚❚ Pause" : "▶ Play";
  }
  if (playBtn && audio) {
    playBtn.addEventListener("click", function () {
      if (audio.paused) audio.play(); else audio.pause();
    });
    audio.addEventListener("play", setLabel);
    audio.addEventListener("pause", setLabel);
    audio.addEventListener("ended", setLabel);
  }

  window.addEventListener("resize", layout);
  layout();
  setLabel();
  requestAnimationFrame(draw);
})();
