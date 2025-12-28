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
    """Генерирует HTML для просмотра + статистика (HTML как СТРОКА)."""
    import ifcopenshell
    from ifctester import ids as ids_mod
    from ifctester import reporter as reporter_mod
    
    ifc_bytes = bytes(ifc_bytes_view)
    ifc_str = ifc_bytes.decode("utf-8", errors="ignore")
    model = ifcopenshell.file.from_string(ifc_str)
    
    ids_xml = bytes(ids_bytes_view).decode("utf-8", errors="ignore")
    my_ids = ids_mod.from_string(ids_xml)
    my_ids.validate(model)
    
    rep = reporter_mod.Html(my_ids)
    rep.report()
    html_report = rep.to_string() if hasattr(rep, "to_string") else str(rep)
    
    total = len(my_ids.specifications)
    passed = sum(1 for s in my_ids.specifications if getattr(s, "status", None) is True)
    failed = sum(1 for s in my_ids.specifications if getattr(s, "status", None) is False)
    
    result = {"total_specs": total, "passed_specs": passed, "failed_specs": failed}
    print(f"HTML готов: {len(html_report)} символов")
    return result, html_report


def generate_report(ifc_bytes_view, ids_bytes_view, report_format):
    """Генерирует отчёт в нужном формате. HTML — строка, JSON — UTF‑8 с кириллицей, ODS/BCF — бинарно."""
    import ifcopenshell
    from ifctester import ids as ids_mod
    from ifctester import reporter as reporter_mod
    import json
    import os
    
    fmt = (report_format or "").strip()
    print(f"=== ГЕНЕРАЦИЯ ОТЧЁТА: {fmt} ===")
    
    ifc_bytes = bytes(ifc_bytes_view)
    ifc_str = ifc_bytes.decode("utf-8", errors="ignore")
    model = ifcopenshell.file.from_string(ifc_str)
    
    ids_xml = bytes(ids_bytes_view).decode("utf-8", errors="ignore")
    my_ids = ids_mod.from_string(ids_xml)
    my_ids.validate(model)
    
    if fmt == "Json":
        rep = reporter_mod.Json(my_ids)
    elif fmt == "Ods":
        rep = reporter_mod.Ods(my_ids)
    elif fmt == "Bcf":
        rep = reporter_mod.Bcf(my_ids)
    else:
        fmt = "Html"
        rep = reporter_mod.Html(my_ids)
    
    rep.report()
    
    if fmt == "Json":
        # аккуратно пересобираем JSON, чтобы кириллица была нормальной
        if hasattr(rep, "to_json"):
            raw = rep.to_json()
        elif hasattr(rep, "to_string"):
            raw = rep.to_string()
        else:
            raw = str(rep)
        obj = json.loads(raw)
        return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    
    if fmt == "Html":
        # ВОЗВРАЩАЕМ БАЙТЫ UTF‑8, но внутри Python это СТРОКИ
        html = rep.to_string() if hasattr(rep, "to_string") else str(rep)
        return html.encode("utf-8")
    
    # Ods / Bcf
    if hasattr(rep, "to_file"):
        ext = ".ods" if fmt == "Ods" else ".bcf"
        tmp_path = "/tmp/ids_report" + ext
        rep.to_file(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        os.remove(tmp_path)
        print(f"{fmt}: {len(data)} байт через to_file()")
        return data
    
    # резервный вариант
    if hasattr(rep, "to_string"):
        return rep.to_string().encode("utf-8")
    return str(rep).encode("utf-8")
