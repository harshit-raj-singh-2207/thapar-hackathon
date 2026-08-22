// Sound Effects Utility using Web Audio API Synthesizer with Audio HTML fallback

let audioCtx = null;

function getAudioContext() {
  if (typeof window === 'undefined') return null;
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

/**
 * Play a synthesized sound effect using Web Audio API
 */
function playSynthSound(freqs = [523.25, 659.25], duration = 0.18, type = 'sine') {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);
    gain.connect(ctx.destination);

    const stepDuration = duration / freqs.length;
    freqs.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, now + idx * stepDuration);
      osc.connect(gain);
      osc.start(now + idx * stepDuration);
      osc.stop(now + (idx + 1) * stepDuration);
    });
  } catch (err) {
    console.warn('Synth sound error:', err);
  }
}

/**
 * Plays a sound effect from a backend WAV/MP3 URL with synth fallback
 */
export async function playSoundFromUrl(soundUrl, fallbackType = 'notification') {
  if (typeof window === 'undefined') return;

  try {
    const audio = new Audio(soundUrl);
    audio.volume = 0.5;
    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise.catch((err) => {
        // Fallback to synth audio if autoplay blocked or network fails
        if (fallbackType === 'like') playLikeSound();
        else if (fallbackType === 'comment') playCommentSound();
        else playNotificationSound();
      });
    }
  } catch (e) {
    if (fallbackType === 'like') playLikeSound();
    else if (fallbackType === 'comment') playCommentSound();
    else playNotificationSound();
  }
}

/**
 * Sound effect when user likes a post
 */
export function playLikeSound() {
  playSynthSound([523.25, 659.25, 783.99], 0.20, 'sine');
}

/**
 * Sound effect when user submits a comment
 */
export function playCommentSound() {
  playSynthSound([440.0, 880.0], 0.15, 'triangle');
}

/**
 * Sound effect when a real-time notification arrives
 */
export function playNotificationSound() {
  playSynthSound([659.25, 880.0, 1046.50], 0.32, 'sine');
}

/**
 * High-priority separation alarm siren sound
 */
export function playSeparationAlarmSound() {
  playSynthSound([880.0, 440.0, 880.0, 440.0, 987.77], 0.65, 'sawtooth');
}

/**
 * Bluetooth Radar Ping sound
 */
export function playRadarPingSound() {
  playSynthSound([1200.0, 1800.0], 0.12, 'sine');
}

/**
 * Wearable Band Buzzer sound
 */
export function playBuzzerSound() {
  playSynthSound([600.0, 600.0, 600.0], 0.40, 'square');
}
