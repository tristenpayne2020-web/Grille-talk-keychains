// Procedural V8 cold start (Web Audio, no audio file, nothing licensed): starter crank with compression chugs, the
// catch with an exhaust bark, a rev flare to ~2800 rpm, then a lumpy cold high idle that fades out. About 4 s.
// Browsers only allow sound after a user gesture, so the loader calls this from its "start" button.

const firing = (rpm) => (rpm / 60) * 4;          // V8: four firing pulses per crank revolution

function noiseBuffer(ctx, seconds) {
  const b = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * seconds), ctx.sampleRate);
  const d = b.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  return b;
}

function shaper(ctx, amount) {
  const n = 1024, curve = new Float32Array(n);
  for (let i = 0; i < n; i++) { const x = (i / (n - 1)) * 2 - 1; curve[i] = Math.tanh(x * amount); }
  const s = ctx.createWaveShaper(); s.curve = curve; s.oversample = '2x';
  return s;
}

export function playColdStart(ctx, { volume = 0.5 } = {}) {
  const t0 = ctx.currentTime + 0.05;
  const out = ctx.createGain(); out.gain.value = volume;
  const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 4;
  out.connect(comp).connect(ctx.destination);
  const nodes = [];
  const keep = (n) => { nodes.push(n); return n; };

  // ---- starter: whine + chugging compression strokes (0 to 0.9 s)
  const whine = keep(ctx.createOscillator()); whine.type = 'triangle';
  whine.frequency.setValueAtTime(380, t0); whine.frequency.linearRampToValueAtTime(460, t0 + 0.85);
  const whineGain = ctx.createGain();
  whineGain.gain.setValueAtTime(0, t0); whineGain.gain.linearRampToValueAtTime(0.05, t0 + 0.08);
  whineGain.gain.setValueAtTime(0.05, t0 + 0.8); whineGain.gain.linearRampToValueAtTime(0, t0 + 0.95);
  whine.connect(whineGain).connect(out);

  const crank = keep(ctx.createOscillator()); crank.type = 'sawtooth';
  crank.frequency.setValueAtTime(firing(200), t0); crank.frequency.linearRampToValueAtTime(firing(260), t0 + 0.85);
  const crankFilter = ctx.createBiquadFilter(); crankFilter.type = 'lowpass'; crankFilter.frequency.value = 260;
  const crankGain = ctx.createGain();
  crankGain.gain.setValueAtTime(0, t0); crankGain.gain.linearRampToValueAtTime(0.5, t0 + 0.1);
  crankGain.gain.setValueAtTime(0.5, t0 + 0.82); crankGain.gain.linearRampToValueAtTime(0, t0 + 0.92);
  crank.connect(shaper(ctx, 3)).connect(crankFilter).connect(crankGain).connect(out);

  // ---- engine: rpm curve drives three oscillators (fundamental, cam lope below, harmonic above)
  const catchAt = t0 + 0.86, flare = catchAt + 0.42, settle = flare + 1.1, end = t0 + 4.2;
  const rpmPoints = [[catchAt, 600], [catchAt + 0.12, 1500], [flare, 2800], [settle, 1350], [end, 1150]];
  const engineIn = ctx.createGain();
  const tone = ctx.createBiquadFilter(); tone.type = 'lowpass'; tone.Q.value = 0.8;
  tone.frequency.setValueAtTime(500, catchAt); tone.frequency.linearRampToValueAtTime(2600, flare); tone.frequency.exponentialRampToValueAtTime(900, settle);
  const engineGain = ctx.createGain();
  engineGain.gain.setValueAtTime(0, t0); engineGain.gain.setValueAtTime(0, catchAt);
  engineGain.gain.linearRampToValueAtTime(0.9, catchAt + 0.06); engineGain.gain.setValueAtTime(0.9, flare);
  engineGain.gain.linearRampToValueAtTime(0.55, settle); engineGain.gain.setValueAtTime(0.55, end - 1.1);
  engineGain.gain.linearRampToValueAtTime(0.0001, end);
  engineIn.connect(shaper(ctx, 2.4)).connect(tone).connect(engineGain).connect(out);

  const voices = [['sawtooth', 1, 0.55], ['square', 0.5, 0.35], ['sawtooth', 2, 0.18]];
  for (const [type, mult, amp] of voices) {
    const o = keep(ctx.createOscillator()); o.type = type;
    rpmPoints.forEach(([t, rpm], i) => {
      const f = firing(rpm) * mult;
      if (i === 0) o.frequency.setValueAtTime(f, t); else o.frequency.exponentialRampToValueAtTime(f, t);
    });
    const g = ctx.createGain(); g.gain.value = amp;
    o.connect(g).connect(engineIn);
  }
  // lope: cross-plane style amplitude wobble at a quarter of the firing rate
  const lope = keep(ctx.createOscillator()); lope.type = 'sine';
  rpmPoints.forEach(([t, rpm], i) => { const f = firing(rpm) / 4; if (i === 0) lope.frequency.setValueAtTime(f, t); else lope.frequency.exponentialRampToValueAtTime(f, t); });
  const lopeDepth = ctx.createGain(); lopeDepth.gain.value = 0.28;
  lope.connect(lopeDepth).connect(engineIn.gain);

  // ---- exhaust: filtered noise, plus a bark on the catch
  const hiss = keep(ctx.createBufferSource()); hiss.buffer = noiseBuffer(ctx, 5);
  const hissFilter = ctx.createBiquadFilter(); hissFilter.type = 'bandpass'; hissFilter.frequency.value = 700; hissFilter.Q.value = 0.7;
  const hissGain = ctx.createGain();
  hissGain.gain.setValueAtTime(0, t0); hissGain.gain.setValueAtTime(0, catchAt);
  hissGain.gain.linearRampToValueAtTime(0.16, flare); hissGain.gain.linearRampToValueAtTime(0.06, settle); hissGain.gain.linearRampToValueAtTime(0.0001, end);
  hiss.connect(hissFilter).connect(hissGain).connect(out);

  const bark = keep(ctx.createBufferSource()); bark.buffer = noiseBuffer(ctx, 0.5);
  const barkFilter = ctx.createBiquadFilter(); barkFilter.type = 'lowpass'; barkFilter.frequency.value = 420;
  const barkGain = ctx.createGain();
  barkGain.gain.setValueAtTime(0, t0); barkGain.gain.setValueAtTime(0.0001, catchAt);
  barkGain.gain.exponentialRampToValueAtTime(1.1, catchAt + 0.02); barkGain.gain.exponentialRampToValueAtTime(0.001, catchAt + 0.35);
  bark.connect(barkFilter).connect(barkGain).connect(out);

  nodes.forEach((n) => { n.start(t0); n.stop(end + 0.1); });
  return {
    duration: end - t0,
    stop() {   // quick fade, used by mute
      const now = ctx.currentTime;
      out.gain.cancelScheduledValues(now); out.gain.setValueAtTime(out.gain.value, now); out.gain.linearRampToValueAtTime(0, now + 0.15);
    },
  };
}
