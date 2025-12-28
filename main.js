let pyodide = null;
let ifcBytes = null;
let idsBytes = null;

// Результаты валидации
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
    log("Загружаю micropip...");
    await pyodide.loadPackage("micropip");
    log("micropip загружен.");
    log("Загружаю app.py...");
    const resp = await fetch("app.py");
    if (!resp.ok) {
        log("Ошибка app.py: " + resp.status);
        return;
    }
    const appCode = await resp.text();
    await pyodide.runPythonAsync(appCode);
    log("app.py загружен.");
    log("Устанавливаю библиотеки...");
    await pyodide.runPythonAsync("await init_packages()");
    log("Библиотеки установлены.");
    runBtn.disabled = false;
    downloadBtn.disabled = true;
    log("Готов к работе.");
}

async function fileToBytes(file) {
    const arrayBuffer = await file.arrayBuffer();
    return new Uint8Array(arrayBuffer);
}

ifcInput.addEventListener("change", async (event) => {
    const files = event.target.files;
    if (!files?.length) {
        ifcBytes = null;
        log("IFC не выбран.");
        downloadBtn.disabled = true;
        return;
    }
    const file = files[0];
    ifcBytes = await fileToBytes(file);
    log(`IFC: ${file.name}`);
    downloadBtn.disabled = true;
});

idsInput.addEventListener("change", async (event) => {
    const files = event.target.files;
    if (!files?.length) {
        idsBytes = null;
        log("IDS не выбран.");
        downloadBtn.disabled = true;
        return;
    }
    const file = files[0];
    idsBytes = await fileToBytes(file);
    log(`IDS: ${file.name}`);
    downloadBtn.disabled = true;
});

runBtn.addEventListener("click", async () => {
    if (!pyodide) return log("Pyodide не готов.");
    if (!ifcBytes || !idsBytes) return log("Загрузите IFC и IDS.");

    log("=== ПРОВЕРКА (HTML для просмотра) ===");
    
    const pyIfcBytes = pyodide.toPy(ifcBytes);
    const pyIdsBytes = pyodide.toPy(idsBytes);
    
    try {
        pyodide.globals.set("ifc_bytes_global", pyIfcBytes);
        pyodide.globals.set("ids_bytes_global", pyIdsBytes);
        
        await pyodide.runPythonAsync("result_ids, html_report = validate_and_show_html(ifc_bytes_global, ids_bytes_global)");
        
        validationResult = pyodide.globals.get("result_ids").toJs();
        const htmlReportData = pyodide.globals.get("html_report");
        
        log("✓ Результат:");
        log(`  Specs: ${validationResult.total_specs}`);
        log(`  Pass: ${validationResult.passed_specs}`);
        log(`  Fail: ${validationResult.failed_specs}`);
        
        const htmlString = htmlReportData.toJs ? htmlReportData.toJs() : String(htmlReportData);
        const blob = new Blob([htmlString], { type: "text/html" });
        reportFrame.src = URL.createObjectURL(blob);
        
        downloadBtn.disabled = false;
        log("✓ HTML в iframe. Выберите формат для скачивания!");
        
    } catch (err) {
        console.error(err);
        log("Ошибка проверки.");
    } finally {
        pyodide.globals.delete("ifc_bytes_global");
        pyodide.globals.delete("ids_bytes_global");
    }
});

downloadBtn.addEventListener("click", async () => {
    if (!ifcBytes || !idsBytes) return log("Сначала проверьте файлы!");
    
    const format = formatSelect.value;
    log(`=== СКАЧИВАНИЕ: ${format} ===`);
    
    const pyIfcBytes = pyodide.toPy(ifcBytes);
    const pyIdsBytes = pyodide.toPy(idsBytes);
    
    try {
        pyodide.globals.set("ifc_bytes_global", pyIfcBytes);
        pyodide.globals.set("ids_bytes_global", pyIdsBytes);
        pyodide.globals.set("download_format", format);
        
        const reportBytes = await pyodide.runPythonAsync("generate_report(ifc_bytes_global, ids_bytes_global, download_format)");
        
        let mime = "application/octet-stream", ext = "bin";
        if (format === "Html") { mime = "text/html"; ext = "html"; }
        else if (format === "Json") { mime = "application/json"; ext = "json"; }
        else if (format === "Ods") { mime = "application/vnd.oasis.opendocument.spreadsheet"; ext = "ods"; }
        else if (format === "Bcf") { ext = "bcf"; }
        
        const blob = new Blob([reportBytes], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `ids_report.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        log(`✓ ids_report.${ext} (${reportBytes.byteLength} байт)`);
        
    } catch (err) {
        console.error(err);
        log("Ошибка скачивания.");
    } finally {
        pyodide.globals.delete("ifc_bytes_global");
        pyodide.globals.delete("ids_bytes_global");
        pyodide.globals.delete("download_format");
    }
});

window.addEventListener("load", initPyodideAndPackages);
