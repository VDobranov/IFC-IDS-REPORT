let pyodide = null;
let ifcBytes = null;
let idsBytes = null;

const outputEl = document.getElementById("output");
const ifcInput = document.getElementById("ifc-upload");
const idsInput = document.getElementById("ids-upload");
const runBtn = document.getElementById("run-btn");
const formatSelect = document.getElementById("format-select");
const downloadBtn = document.getElementById("download-btn");
const reportFrame = document.getElementById("report-frame");

// последняя сгенерированная строка отчёта и формат
let lastReportText = "";
let lastReportFormat = "Html";

function log(text) {
  outputEl.textContent += text + "\n";
}

async function initPyodideAndPackages() {
  log("Загружаю Pyodide...");
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.0/full/",
  });
  log("Pyodide загружен.");

  log("Загружаю пакет 'micropip' из Pyodide...");
  await pyodide.loadPackage("micropip");
  log("micropip загружен.");

  log("Загружаю Python-скрипт app.py...");
  const resp = await fetch("app.py");
  if (!resp.ok) {
    log("Не удалось загрузить app.py: " + resp.status);
    return;
  }
  const appCode = await resp.text();
  await pyodide.runPythonAsync(appCode);
  log("app.py загружен.");

  log("Устанавливаю ifcopenshell / odfpy / ifctester (может занять время)...");
  await pyodide.runPythonAsync("await init_packages()");
  log("Библиотеки установлены.");

  runBtn.disabled = false;
  log("Можно загружать IFC и IDS и запускать проверку.");
}

async function fileToBytes(file) {
  const arrayBuffer = await file.arrayBuffer();
  return new Uint8Array(arrayBuffer);
}

ifcInput.addEventListener("change", async (event) => {
  const files = event.target.files;
  if (!files || !files.length) {
    ifcBytes = null;
    log("IFC не выбран.");
    return;
  }
  const file = files[0];
  ifcBytes = await fileToBytes(file);
  log(`IFC загружен (JS): ${file.name}`);
});

idsInput.addEventListener("change", async (event) => {
  const files = event.target.files;
  if (!files || !files.length) {
    idsBytes = null;
    log("IDS не выбран.");
    return;
  }
  const file = files[0];
  idsBytes = await fileToBytes(file);
  log(`IDS загружен (JS): ${file.name}`);
});

runBtn.addEventListener("click", async () => {
  if (!pyodide) {
    log("Pyodide ещё не инициализирован.");
    return;
  }
  if (!ifcBytes || !idsBytes) {
    log("Нужно выбрать и IFC, и IDS файл перед запуском проверки.");
    return;
  }

  const format = formatSelect.value; // Html / Json / Ods / Bcf
  lastReportFormat = format;

  log(
    "Передаю IFC и IDS в Python и запускаю проверку (формат: " + format + ")..."
  );

  const pyIfcBytes = pyodide.toPy(ifcBytes);
  const pyIdsBytes = pyodide.toPy(idsBytes);

  try {
    pyodide.globals.set("_ifc_bytes", pyIfcBytes);
    pyodide.globals.set("_ids_bytes", pyIdsBytes);
    pyodide.globals.set("_report_format", format);

    await pyodide.runPythonAsync(
      "result_ids, report_text = validate_ifc_and_generate_report(_ifc_bytes, _ids_bytes, _report_format)"
    );

    const resultIds = pyodide.globals.get("result_ids").toJs();
    lastReportText = pyodide.globals.get("report_text");

    log("Результаты проверки IFC против IDS:");
    log(
      `  Спецификаций: ${resultIds.total_specs}, ` +
        `пройдено: ${resultIds.passed_specs}, ` +
        `провалено: ${resultIds.failed_specs}`
    );

    // если HTML — показываем в iframe
    if (format === "Html") {
      const blob = new Blob([lastReportText], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      reportFrame.src = url;
    } else {
      // для других форматов очищаем iframe
      reportFrame.src = "about:blank";
    }

    downloadBtn.disabled = false;
  } catch (err) {
    console.error(err);
    log("Ошибка при валидации / генерации отчёта (см. консоль).");
  } finally {
    pyodide.globals.delete("_ifc_bytes");
    pyodide.globals.delete("_ids_bytes");
    pyodide.globals.delete("_report_format");
  }
});

downloadBtn.addEventListener("click", () => {
  if (!lastReportText) {
    log("Нет отчёта для скачивания. Сначала запустите проверку.");
    return;
  }

  let mime = "text/plain";
  let ext = "txt";

  if (lastReportFormat === "Html") {
    mime = "text/html";
    ext = "html";
  } else if (lastReportFormat === "Json") {
    mime = "application/json";
    ext = "json";
  } else if (lastReportFormat === "Ods") {
    mime = "application/vnd.oasis.opendocument.spreadsheet";
    ext = "ods";
  } else if (lastReportFormat === "Bcf") {
    mime = "application/octet-stream";
    ext = "bcf";
  }

  const blob = new Blob([lastReportText], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ids_report." + ext;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

window.addEventListener("load", () => {
  initPyodideAndPackages().catch((e) => {
    console.error(e);
    log("Ошибка инициализации Pyodide/библиотек (см. консоль).");
  });
});
