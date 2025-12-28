import micropip

async def init_packages():
    w_ifc = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
    w_odf = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/odfpy-1.4.2-py2.py3-none-any.whl"
    
    print("ifcopenshell...")
    await micropip.install(w_ifc)
    print("odfpy...")
    await micropip.install(w_odf)
    print("ifctester...")
    await micropip.install("ifctester")
    
    global ifcopenshell, ifctester_ids, ifctester_reporter
    import ifcopenshell
    from ifctester import ids as ifctester_ids
    from ifctester import reporter as ifctester_reporter
    print("ifcopenshell:", ifcopenshell.__version__)
    return ifcopenshell, ifctester_ids, ifctester_reporter

def validate_and_show_html(ifc_bytes_view, ids_bytes_view):
    """Генерирует HTML для просмотра + статистика"""
    import ifcopenshell
    from ifctester import ids as ids_mod
    from ifctester import reporter as reporter_mod
    
    ifc_bytes = bytes(ifc_bytes_view)
    ifc_str = ifc_bytes.decode("utf-8", errors="ignore")
    model = ifcopenshell.file.from_string(ifc_str)
    
    ids_xml = bytes(ids_bytes_view).decode("utf-8", errors="ignore")
    my_ids = ids_mod.from_string(ids_xml)
    my_ids.validate(model)
    
    # HTML для iframe
    rep = reporter_mod.Html(my_ids)
    rep.report()
    html_report = rep.to_string() if hasattr(rep, "to_string") else str(rep)
    
    # Статистика
    total = len(my_ids.specifications)
    passed = sum(1 for s in my_ids.specifications if getattr(s, "status", None) is True)
    failed = sum(1 for s in my_ids.specifications if getattr(s, "status", None) is False)
    
    result = {"total_specs": total, "passed_specs": passed, "failed_specs": failed}
    print(f"HTML готов: {len(html_report)} символов")
    return result, html_report

def generate_report(ifc_bytes_view, ids_bytes_view, report_format):
    """Генерирует отчёт в любом формате"""
    import ifcopenshell
    from ifctester import ids as ids_mod
    from ifctester import reporter as reporter_mod
    
    print(f"=== ГЕНЕРАЦИЯ ОТЧЁТА: {report_format} ===")
    
    ifc_bytes = bytes(ifc_bytes_view)
    ifc_str = ifc_bytes.decode("utf-8", errors="ignore")
    model = ifcopenshell.file.from_string(ifc_str)
    
    ids_xml = bytes(ids_bytes_view).decode("utf-8", errors="ignore")
    my_ids = ids_mod.from_string(ids_xml)
    my_ids.validate(model)
    
    fmt = report_format.strip()
    print(f"Создаю reporter.{fmt}(my_ids)...")
    
    if fmt == "Json":
        rep = reporter_mod.Json(my_ids)
    elif fmt == "Ods":
        rep = reporter_mod.Ods(my_ids)
    elif fmt == "Bcf":
        rep = reporter_mod.Bcf(my_ids)
    else:
        rep = reporter_mod.Html(my_ids)
    
    print("Выполняю rep.report()...")
    rep.report()
    
    print(f"Методы: to_file={hasattr(rep, 'to_file')}, to_string={hasattr(rep, 'to_string')}")
    
    if fmt == "Json":
        if hasattr(rep, "to_json"):
            result = rep.to_json().encode('utf-8')
        elif hasattr(rep, "to_string"):
            result = rep.to_string().encode('utf-8')
        else:
            result = str(rep).encode('utf-8')
    elif fmt == "Html":
        result = rep.to_string().encode('utf-8') if hasattr(rep, "to_string") else str(rep).encode('utf-8')
    else:  # Ods, Bcf - бинарные форматы
        # Ods использует to_file(filename), делаем временный файл в памяти
        if hasattr(rep, "to_file"):
            import io
            # Создаём временный файл в Pyodide FS
            import os
            tmp_path = "/tmp/ods_report.ods"
            rep.to_file(tmp_path)
            # Читаем обратно
            with open(tmp_path, "rb") as f:
                result = f.read()
            os.remove(tmp_path)
            print(f"✓ to_file(): {len(result)} байт")
        elif hasattr(rep, "to_string"):
            # Fallback для Ods - текстовое представление
            result = rep.to_string().encode('utf-8')
            print(f"✓ to_string() fallback: {len(result)} байт")
        else:
            result = str(rep).encode('utf-8')
            print(f"❌ Fallback str(): {len(result)} байт")
    
    print(f"ИТОГО: {len(result)} байт")
    return result
