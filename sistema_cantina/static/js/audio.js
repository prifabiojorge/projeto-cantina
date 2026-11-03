let audioCtx = null;
let alarmeOscillator = null;
let alarmeGain = null;
let alarmeInterval = null;

function initAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  // Retomar contexto se estiver suspenso (política de autoplay)
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
}

function playBipSucesso() {
  if (!audioCtx) return;
  try {
    [880, 1320].forEach((frequencia, i) => {
      const inicio = audioCtx.currentTime + i * 0.24;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.value = frequencia;
      gain.gain.setValueAtTime(0, inicio);
      gain.gain.linearRampToValueAtTime(0.8, inicio + 0.01);
      gain.gain.setValueAtTime(0.8, inicio + 0.14);
      gain.gain.linearRampToValueAtTime(0, inicio + 0.16);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.onended = () => { osc.disconnect(); gain.disconnect(); };
      osc.start(inicio);
      osc.stop(inicio + 0.16);
    });
  } catch (err) {
    console.warn('Som de confirmação indisponível:', err);
  }
}

function playAlarme() {
  if (!audioCtx) return;
  stopAlarme();
  alarmeOscillator = audioCtx.createOscillator();
  alarmeGain = audioCtx.createGain();
  alarmeOscillator.type = 'sawtooth';
  alarmeGain.gain.value = 1.0;
  alarmeOscillator.connect(alarmeGain);
  alarmeGain.connect(audioCtx.destination);
  alarmeOscillator.frequency.setValueAtTime(600, audioCtx.currentTime);
  // Sirene: oscila entre 600 e 1000 Hz
  const now = audioCtx.currentTime;
  for (let i = 0; i < 100; i++) {
    alarmeOscillator.frequency.setValueAtTime(600, now + i);
    alarmeOscillator.frequency.linearRampToValueAtTime(1000, now + i + 0.5);
    alarmeOscillator.frequency.linearRampToValueAtTime(600, now + i + 1.0);
  }
  alarmeOscillator.start();
  // Adicionar efeito visual de alarme
  document.body.classList.add('alarme-ativo');
  document.getElementById('alarm-indicator').classList.add('alarm-red');
}

function stopAlarme() {
  if (alarmeOscillator) {
    alarmeOscillator.stop();
    alarmeOscillator.disconnect();
    alarmeOscillator = null;
  }
  if (alarmeGain) {
    alarmeGain.disconnect();
    alarmeGain = null;
  }
  // Remover efeito visual de alarme
  document.body.classList.remove('alarme-ativo');
  const indicator = document.getElementById('alarm-indicator');
  if (indicator) {
    indicator.classList.remove('alarm-red');
    indicator.classList.add('alarm-green');
    indicator.innerHTML = '<i class="bi bi-check-circle"></i>';
  }
}

// Função para testar o alarme
function testarAlarme() {
  initAudio();
  playAlarme();
  // Parar após 2 segundos
  setTimeout(() => {
    stopAlarme();
  }, 2000);
}
