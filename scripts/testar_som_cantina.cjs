const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const notas = [], volumes = [];
let resumes = 0, falhar = false;
class AudioContext {
    state = 'suspended';
    currentTime = 10;
    destination = {};
    resume() { resumes++; this.state = 'running'; return Promise.resolve(); }
    createOscillator() {
        if (falhar) throw new Error('Audio indisponivel');
        const nota = { frequency: {}, connect() {}, disconnect() { this.desconectado = true; },
            start(t) { this.inicio = t; }, stop(t) { this.fim = t; } };
        notas.push(nota);
        return nota;
    }
    createGain() {
        const volume = { gain: { setValueAtTime(v) { assert(v >= 0 && v <= 0.8); },
            linearRampToValueAtTime(v) { assert(v >= 0 && v <= 0.8); } },
            connect() {}, disconnect() { this.desconectado = true; } };
        volumes.push(volume);
        return volume;
    }
}
const contexto = vm.createContext({ window: { AudioContext }, console: { warn() {} } });
vm.runInContext(fs.readFileSync(path.join(__dirname, '../sistema_cantina/static/js/audio.js'), 'utf8'), contexto);
contexto.playBipSucesso();
assert.equal(notas.length, 0);
contexto.initAudio();
contexto.playBipSucesso();
assert.equal(resumes, 1);
assert.deepEqual(notas.map(n => n.frequency.value), [880, 1320]);
assert(notas.every(n => n.type === 'square' && n.fim > n.inicio));
assert(notas[1].inicio > notas[0].fim);
notas.forEach(n => n.onended());
assert(notas.every(n => n.desconectado));
assert(volumes.every(v => v.desconectado));
falhar = true;
assert.doesNotThrow(() => contexto.playBipSucesso());
console.log('OK: confirmacao com dois bipes, volume alto, limpeza do audio e falha sonora sem interromper o check-in.');
