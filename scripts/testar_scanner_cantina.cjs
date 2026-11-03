const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '../sistema_cantina/templates/cantina.html'), 'utf8');
const elementos = new Map(), requests = [], sons = [];
let instancia, proximaResposta;
let instante = 10000, focoDisponivel = true, focoFalha = false;
function elemento(id) {
    if (!elementos.has(id)) elementos.set(id, {
        style: {}, value: '', disabled: false, classList: { add() {}, remove() {} }, addEventListener() {}
    });
    return elementos.get(id);
}
function resposta(status, qr = 'teste') {
    return { ok: true, json: () => Promise.resolve({ status,
        aluno: { nome: 'Aluno de teste', matricula: 'TESTE', turma: '101', turno: 'Integral', ativo: true, qrcode_hash: qr }
    }) };
}
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
    Date: Relogio, document: { getElementById: elemento }, window: {},
    Html5Qrcode: Scanner, Html5QrcodeSupportedFormats: { QR_CODE: 0 },
    initAudio() {}, playBipSucesso() { sons.push('sucesso'); }, playAlarme() { sons.push('alarme'); },
    stopAlarme() { sons.push('parar'); },
    setInterval() {}, setTimeout,
    console: { log() {}, warn() {}, error() {} },
    alert(message) { throw new Error(message); },
    fetch(url, options) {
        if (url === '/api/cantina/contagem-hoje') return Promise.resolve({ json: () => Promise.resolve({ total: 0 }) });
        if (url === '/api/cantina/estatisticas') return Promise.resolve({ json: () => Promise.resolve({ data: '2026-11-03' }) });
        const payload = JSON.parse(options.body);
        requests.push({ url, ...payload });
        const pendente = proximaResposta || Promise.resolve(resposta('ok', payload.qrcode_hash));
        proximaResposta = undefined;
        return pendente;
    }
});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], contexto);

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
    assert.equal(elemento('btn-stop').disabled, false);

    let concluir;
    proximaResposta = new Promise(resolve => { concluir = resolve; });
    const pendente = contexto.onScanSuccess('aluno-a');
    contexto.onScanSuccess('aluno-b');
    contexto.registrarLiberacaoForcada();
    assert.equal(requests.length, 1);
    concluir(resposta('ok', 'aluno-a'));
    await pendente;
    await contexto.onScanSuccess('aluno-b');
    contexto.onScanSuccess('aluno-b');
    assert.deepEqual(requests.map(r => r.qrcode_hash), ['aluno-a', 'aluno-b']);
    instante += 2000;
    proximaResposta = Promise.resolve(resposta('ja_almocou', 'aluno-b'));
    await contexto.onScanSuccess('aluno-b');
    assert.deepEqual(sons, ['parar', 'sucesso', 'parar', 'sucesso', 'alarme']);
    assert.equal(elemento('alarm-text').textContent, 'BLOQUEADO - Verificar situação');

    proximaResposta = Promise.resolve(resposta('sem_checkin_portaria', 'aluno-c'));
    await contexto.onScanSuccess('aluno-c');
    assert.equal(elemento('liberacao-forcada-box').style.display, 'block');
    elemento('liberacao-motivo').value = 'Esquecimento na portaria';
    elemento('liberacao-responsavel').value = 'Teste';
    proximaResposta = new Promise(resolve => { concluir = resolve; });
    const liberacao = contexto.registrarLiberacaoForcada();
    const quantidade = requests.length;
    contexto.onScanSuccess('aluno-d');
    contexto.registrarLiberacaoForcada();
    assert.equal(requests.length, quantidade);
    assert.equal(requests.at(-1).url, '/api/cantina/liberacao-forcada');
    assert.equal(requests.at(-1).qrcode_hash, 'aluno-c');
    concluir(resposta('liberado_forcado', 'aluno-c'));
    await liberacao;
    assert.equal(elemento('liberacao-forcada-box').style.display, 'none');
    assert.equal(elemento('liberacao-motivo').value, '');
    assert.equal(elemento('btn-liberacao-forcada').disabled, false);
    assert.equal(sons.at(-1), 'sucesso');
    assert(elemento('alarm-text').textContent.startsWith('LIBERADO MANUALMENTE'));
    contexto.onScanSuccess('aluno-c');
    assert.equal(requests.length, quantidade);

    proximaResposta = Promise.resolve({ ok: false });
    const sonsAntes = sons.length;
    await contexto.onScanSuccess('aluno-d');
    assert.equal(sons.length, sonsAntes);
    assert.equal(elemento('aluno-nome').textContent, 'ERRO');
    await contexto.onScanSuccess('aluno-e');
    assert.equal(requests.at(-1).qrcode_hash, 'aluno-e');
    proximaResposta = Promise.resolve(resposta('sem_checkin_portaria', 'aluno-f'));
    await contexto.onScanSuccess('aluno-f');
    elemento('liberacao-motivo').value = 'Teste de falha';
    proximaResposta = Promise.reject(new Error('Falha de rede simulada'));
    await contexto.registrarLiberacaoForcada();
    assert.equal(elemento('btn-liberacao-forcada').disabled, false);
    assert.equal(elemento('aluno-nome').textContent, 'ERRO');
    await contexto.onScanSuccess('aluno-g');
    assert.equal(requests.at(-1).qrcode_hash, 'aluno-g');
    contexto.toggleSound();
    assert.equal(elemento('sound-status').textContent, 'Som: OFF');
    const confirmacoes = sons.filter(s => s === 'sucesso').length;
    const alarmes = sons.filter(s => s === 'alarme').length;
    await contexto.onScanSuccess('aluno-h');
    proximaResposta = Promise.resolve(resposta('ja_almocou', 'aluno-i'));
    await contexto.onScanSuccess('aluno-i');
    assert.equal(sons.filter(s => s === 'sucesso').length, confirmacoes);
    assert.equal(sons.filter(s => s === 'alarme').length, alarmes);
    contexto.toggleSound();
    await contexto.onScanSuccess('aluno-j');
    assert.equal(sons.at(-1), 'sucesso');
    console.log('OK: scanner ampliado, HD, foco opcional, proximo aluno, repeticao, alarme, liberacao manual e falha sem travamento.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
