/**
 * Leitura de balança via Web Serial API (Chrome/Edge, HTTPS ou localhost).
 * Suporta linhas ASCII comuns (ex.: "1.234 kg", "ST,GS,+001.234kg").
 */
(function initScaleReader(global) {
  const DEFAULT_BAUD = 9600;

  function parseWeightFromLine(line) {
    const text = String(line || "").trim();
    if (!text) return null;

    const kgMatch = text.match(/([+-]?\d+[.,]\d+)\s*kg/i);
    if (kgMatch) return normalizeNumber(kgMatch[1]);

    const generic = text.match(/([+-]?\d+[.,]\d+)/);
    if (generic) return normalizeNumber(generic[1]);

    return null;
  }

  function normalizeNumber(raw) {
    const normalized = String(raw).replace(",", ".").replace(/[^\d.+-]/g, "");
    const value = Number.parseFloat(normalized);
    if (!Number.isFinite(value) || value <= 0) return null;
    return Math.round(value * 1000) / 1000;
  }

  async function readWeight(options = {}) {
    if (!("serial" in navigator)) {
      throw new Error(
        "Seu navegador não suporta balança serial. Use Chrome ou Edge em HTTPS/localhost, ou digite o peso manualmente."
      );
    }

    const baudRate = options.baudRate || DEFAULT_BAUD;
    const timeoutMs = options.timeoutMs || 8000;
    const port = await navigator.serial.requestPort();

    await port.open({ baudRate });

    const reader = port.readable.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    const started = Date.now();

    try {
      while (Date.now() - started < timeoutMs) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() || "";

        for (const line of lines) {
          const weight = parseWeightFromLine(line);
          if (weight != null) return weight;
        }

        const inline = parseWeightFromLine(buffer);
        if (inline != null) return inline;
      }
      throw new Error("Não foi possível ler um peso estável da balança. Tente novamente.");
    } finally {
      reader.releaseLock();
      try {
        await port.close();
      } catch {
        /* ignore */
      }
    }
  }

  global.ScaleReader = {
    isSupported: () => "serial" in navigator,
    readWeight,
    parseWeightFromLine,
  };
})(window);
