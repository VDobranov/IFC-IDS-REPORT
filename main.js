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

let lastReportData = null;
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

  const format = formatSelect.value;
  lastReportFormat = format;
  log("Передаю IFC и IDS в Python и запускаю проверку (формат: " + format + ")...");

  const pyIfcBytes = pyodide.toPy(ifcBytes);
  const pyIdsBytes = pyodide.toPy(idsBytes);

  try {
    pyodide.globals.set("_ifc_bytes", pyIfcBytes);
    pyodide.globals.set("_ids_bytes", pyIdsBytes);
    pyodide.globals.set("_report_format", format);

    await pyodide.runPythonAsync(
      "result_ids, report_data = validate_ifc_and_generate_report(_ifc_bytes, _ids_bytes, _report_format)"
    );

    const resultIds = pyodide.globals.get("result_ids").toJs();
    lastReportData = pyodide.globals.get("report_data");

    log("Результаты проверки IFC против IDS:");
    log(` Спецификаций: ${resultIds.total_specs}, ` +
        `пройдено: ${resultIds.passed_specs}, ` +
        `провалено: ${resultIds.failed_specs}`);

    if (format === "Html") {
      const htmlString = lastReportData.toJs ? lastReportData.toJs() : String(lastReportData);
      const blob = new Blob([htmlString], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      reportFrame.src = url;
    } else {
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

downloadBtn.addEventListener("click", async () => {
  if (!lastReportData) {
    log("Нет отчёта для скачивания. Сначала запустите проверку.");
    return;
  }

  try {
    if (lastReportFormat === "Html") {
      const htmlString = lastReportData.toJs ? lastReportData.toJs() : String(lastReportData);
      const blob = new Blob([htmlString], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ids_report.html";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      // Бинарные форматы: конвертируем через Python в Uint8Array
      pyodide.globals.set("_report_data", lastReportData);
      pyodide.globals.set("_report_format", lastReportFormat);
      
      const bytesResult = await pyodide.runPythonAsync(`
        import io
        if _report_format == "Json":
          data = _report_data.tojson().encode('utf-8')
        elif _report_format == "Ods":
          buf = io.BytesIO()
          _report_data.tofileobj(buf)
          data = buf.getvalue()
        elif _report_format == "Bcf":
          buf = io.BytesIO()
          _report_data.tofileobj(buf)
          data = buf.getvalue()
        else:
          data = b""
        data
      `);
      
      let mime = "application/octet-stream";
      let ext = "bin";
      
      if (lastReportFormat === "Json") {
        mime = "application/json";
        ext = "json";
      } else if (lastReportFormat === "Ods") {
        mime = "application/vnd.oasis.opendocument.spreadsheet";
        ext = "ods";
      } else if (lastReportFormat === "Bcf") {
        ext = "bcf";
      }
      
      if (bytesResult.byteLength > 0) {
        const blob = new Blob([bytesResult], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "ids_report." + ext;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      
      pyodide.globals.delete("_report_data");
      pyodide.globals.delete("_report_format");
    }
  } catch (err) {
    console.error(err);
    log("Ошибка при скачивании отчёта (см. консоль).");
  }
});

window.addEventListener("load", () => {
  initPyodideAndPackages().catch((e) => {
    console.error(e);
    log("Ошибка инициализации Pyodide/библиотек (см. консоль).");
  });
});
