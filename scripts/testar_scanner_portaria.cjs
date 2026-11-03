const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../sistema_cantina/templates/portaria.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elementos = new Map();
const requests = [];
const sons = [];
const erros = [];
let instancia;
let focoDisponivel = true;
let focoFalha = false;
let instante = 10000;
let proximaResposta;
class Relogio extends Date { static now() { return instante; } }
class Scanner {
    static getCameras() { return Promise.resolve([{ id: 'camera-teste', label: 'Back camera' }]); }
    constructor(id, config) { this.id = id; this.config = config; this.ajustes = []; instancia = this; }
    start(id, config) { this.camera = id; this.scanConfig = config; return Promise.resolve(); }
    getRunningTrackCapabilities() { return focoDisponivel ? { focusMode: ['continuous'] } : {}; }
    applyVideoConstraints(config) {
        this.ajustes.push(config);
        return focoFalha ? Promise.reject(new Error('Foco nao ajustavel')) : Promise.resolve();
    }
}
const contexto = vm.createContext({
    Date: Relogio,
    window: { addEventListener() {} },
    document: { getElementById(id) {
        if (!elementos.has(id)) elementos.set(id, { addEventListener() {}, disabled: false });
        return elementos.get(id);
    } },
    Html5Qrcode: Scanner,
    Html5QrcodeSupportedFormats: { QR_CODE: 0 },
    setInterval() {}, setTimeout,
    console: { log() {}, warn() {}, error() {} },
    alert(message) { throw new Error(message); },
    fetch(url, options) {
        if (url === '/api/portaria/contagem-hoje') return Promise.resolve({ json: () => Promise.resolve({ total: 0 }) });
        requests.push(JSON.parse(options.body).qrcode_hash);
        const resposta = proximaResposta || Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'ok' }) });
        proximaResposta = undefined;
        return resposta;
    }
});
vm.runInContext(script, contexto);
contexto.exibirResultado = () => {};
contexto.adicionarUltimoRegistro = () => {};
contexto.tocarSomScan = status => sons.push(status);
contexto.exibirErro = mensagem => erros.push(mensagem);

async function main() {
    await contexto.iniciarScanner();
    assert.deepEqual(Array.from(instancia.config.formatsToSupport), [0]);
    assert.equal(instancia.scanConfig.qrbox, undefined);
    assert.equal(instancia.scanConfig.fps, 15);
    assert.equal(instancia.scanConfig.videoConstraints.deviceId.exact, 'camera-teste');
    assert.equal(instancia.scanConfig.videoConstraints.width.ideal, 1280);
    assert.equal(instancia.scanConfig.videoConstraints.height.ideal, 720);
    assert.equal(instancia.ajustes[0].advanced[0].focusMode, 'continuous');
    focoDisponivel = false;
    await contexto.iniciarScanner();
    assert.equal(instancia.ajustes.length, 0);
    focoDisponivel = true;
    focoFalha = true;
    await contexto.iniciarScanner();
    assert.equal(elementos.get('btn-stop').disabled, false);

    let concluir;
    proximaResposta = new Promise(resolve => { concluir = resolve; });
    const pendente = contexto.onScanSuccess('aluno-a');
    contexto.onScanSuccess('aluno-b');
    assert.deepEqual(requests, ['aluno-a']);
    concluir({ ok: true, json: () => Promise.resolve({ status: 'ok' }) });
    await pendente;
    await contexto.onScanSuccess('aluno-b');
    contexto.onScanSuccess('aluno-b');
    assert.deepEqual(requests, ['aluno-a', 'aluno-b']);
    instante += 2000;
    proximaResposta = Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'ja_registrado' }) });
    await contexto.onScanSuccess('aluno-b');
    assert.deepEqual(sons, ['ok', 'ok', 'ja_registrado']);
    proximaResposta = Promise.resolve({ ok: false });
    await contexto.onScanSuccess('aluno-c');
    assert.equal(erros.length, 1);
    assert.equal(sons.length, 3);
    await contexto.onScanSuccess('aluno-d');
    assert.equal(requests.at(-1), 'aluno-d');
    console.log('OK: area total, HD preferencial, foco opcional, proximo aluno imediato, repeticao protegida e falha sem travamento.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
