const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../sistema_cantina/templates/portaria.html'), 'utf8');
const source = html.slice(html.indexOf('let scanAudio = null;'), html.indexOf('// Configurar scanner'));
const notes = [];
let resumes = 0;
class AudioContext {
    state = 'suspended';
    currentTime = 0;
    destination = {};
    resume() { resumes++; this.state = 'running'; return Promise.resolve(); }
    createOscillator() {
        const note = { frequency: {}, connect() {}, disconnect() {}, start(t) { this.startTime = t; }, stop(t) { this.stopTime = t; } };
        notes.push(note);
        return note;
    }
    createGain() {
        return { gain: { setValueAtTime() {}, linearRampToValueAtTime(v) { assert(v >= 0 && v <= 1); } }, connect() {}, disconnect() {} };
    }
}
const context = vm.createContext({ window: { AudioContext }, console });
vm.runInContext(source, context);
vm.runInContext("prepararAudio(); tocarSomScan('ok')", context);
assert.equal(resumes, 1);
assert.deepEqual(notes.map(n => n.frequency.value), [880, 1320]);
assert(notes.every(n => n.stopTime > n.startTime));
notes.length = 0;
vm.runInContext("tocarSomScan('ja_registrado')", context);
assert.deepEqual(notes.map(n => n.frequency.value), [440, 330, 440]);
notes.length = 0;
vm.runInContext("tocarSomScan('inativo')", context);
assert.equal(notes.length, 0);
vm.runInNewContext(source + "\ntocarSomScan('ok');", { window: {}, console });
console.log('OK: sons distintos, volume limitado, desbloqueio e navegador sem audio.');
