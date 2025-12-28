let pyodide = null;
let ifcBytes = null;
let idsBytes = null;
let validationResult = null;

const outputEl = document.getElementById("output");
const ifcInput = document.getElementById("ifc-upload");
const idsInput = document.getElementById("ids-upload");
const runBtn = document.getElementById("run-btn");
const formatSelect = document.getElementById("format-select");
const downloadBtn = document.getElementById("download-btn");
const reportFrame = document.getElementById("report-frame");

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
    downloadBtn.disabled = true;
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
        downloadBtn.disabled = true;
        return;
    }
    const file = files[0];
    ifcBytes = await fileToBytes(file);
    log(`IFC загружен (JS): ${file.name}`);
    downloadBtn.disabled = true;
});

idsInput.addEventListener("change", async (event) => {
    const files = event.target.files;
    if (!files || !files.length) {
        idsBytes = null;
        log("IDS не выбран.");
        downloadBtn.disabled = true;
        return;
    }
    const file = files[0];
    idsBytes = await fileToBytes(file);
    log(`IDS загружен (JS): ${file.name}`);
    downloadBtn.disabled = true;
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
    log("=== ПРОВЕРКА (HTML для просмотра) ===");
    const pyIfcBytes = pyodide.toPy(ifcBytes);
    const pyIdsBytes = pyodide.toPy(idsBytes);
    try {
        pyodide.globals.set("ifc_bytes_global", pyIfcBytes);
        pyodide.globals.set("ids_bytes_global", pyIdsBytes);
        await pyodide.runPythonAsync(
            "result_ids, html_report = validate_and_show_html(ifc_bytes_global, ids_bytes_global)"
        );
        validationResult = pyodide.globals.get("result_ids").toJs();
        const htmlReportData = pyodide.globals.get("html_report");
        log("Результаты проверки IFC против IDS:");
        log(
            ` Спецификаций: ${validationResult.total_specs}, ` +
            `пройдено: ${validationResult.passed_specs}, ` +
            `провалено: ${validationResult.failed_specs}`
        );
        const htmlString = htmlReportData.toJs ? htmlReportData.toJs() : String(htmlReportData);
        const blob = new Blob([htmlString], { type: "text/html;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        reportFrame.src = url;
        downloadBtn.disabled = false;
    } catch (err) {
        console.error(err);
        log("Ошибка при валидации / генерации отчёта (см. консоль).");
    } finally {
        pyodide.globals.delete("ifc_bytes_global");
        pyodide.globals.delete("ids_bytes_global");
    }
});

downloadBtn.addEventListener("click", async () => {
    if (!ifcBytes || !idsBytes) {
        log("Нет отчёта для скачивания. Сначала запустите проверку.");
        return;
    }
    const format = formatSelect.value;
    log(`=== СКАЧИВАНИЕ: формат ${format} ===`);
    const pyIfcBytes = pyodide.toPy(ifcBytes);
    const pyIdsBytes = pyodide.toPy(idsBytes);
    try {
        pyodide.globals.set("ifc_bytes_global", pyIfcBytes);
        pyodide.globals.set("ids_bytes_global", pyIdsBytes);
        
        // ИСПРАВЛЕНО: сохраняем результат в глобальную переменную report_bytes
        await pyodide.runPythonAsync(
            `report_bytes = generate_report(ifc_bytes_global, ids_bytes_global, "${format}")`
        );
        
        // Извлекаем байты как Uint8Array
        const bytesResult = pyodide.globals.get("report_bytes").toJs();
        
        let mime = "application/octet-stream";
        let ext = "bin";
        if (format === "Html") {
            mime = "text/html;charset=utf-8";
            ext = "html";
        } else if (format === "Json") {
            mime = "application/json;charset=utf-8";
            ext = "json";
        } else if (format === "Ods") {
            mime = "application/vnd.oasis.opendocument.spreadsheet";
            ext = "ods";
        } else if (format === "Bcf") {
            mime = "application/octet-stream";
            ext = "bcf";
        }
        
        if (bytesResult && bytesResult.byteLength > 0) {
            const blob = new Blob([bytesResult], { type: mime });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `ids_report.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            log(`✅ Отчёт ${format} успешно скачан!`);
        } else {
            log("❌ Отчёт пустой - ошибка генерации.");
        }
    } catch (err) {
        console.error(err);
        log("❌ Ошибка при скачивании отчёта (см. консоль): " + err.message);
    } finally {
        pyodide.globals.delete("ifc_bytes_global");
        pyodide.globals.delete("ids_bytes_global");
        pyodide.globals.delete("report_bytes");
    }
});

window.addEventListener("load", () => {
    initPyodideAndPackages().catch((e) => {
        console.error(e);
        log("Ошибка инициализации Pyodide/библиотек (см. консоль).");
    });
});
