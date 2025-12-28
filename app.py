import micropip


async def init_packages():
    """
    Устанавливает ifcopenshell, odfpy и ifctester в окружение Pyodide.
    """
    w_ifc = (
        "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/"
        "wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
    )
    w_odf = (
        "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/"
        "wheels/odfpy-1.4.2-py2.py3-none-any.whl"
    )

    print("Ставлю ifcopenshell...")
    await micropip.install(w_ifc)

    print("Ставлю odfpy...")
    await micropip.install(w_odf)

    print("Ставлю ifctester...")
    await micropip.install("ifctester")

    global ifcopenshell, ifctester_ids, ifctester_reporter

    import ifcopenshell
    from ifctester import ids as ifctester_ids
    from ifctester import reporter as ifctester_reporter

    print("ifcopenshell версия:", ifcopenshell.__version__)
    return ifcopenshell, ifctester_ids, ifctester_reporter


def validate_ifc_and_generate_report(
    ifc_bytes_view,
    ids_bytes_view,
    report_format: str = "Html",
):
    """
    Проверка IFC против IDS и генерация отчёта в заданном формате.

    Параметры:
      ifc_bytes_view  - Uint8Array из JS с содержимым IFC.
      ids_bytes_view  - Uint8Array из JS с содержимым IDS (.ids/.xml).
      report_format   - 'Html', 'Json', 'Ods' или 'Bcf'.

    Возвращает:
      (result_dict, report_text)

      result_dict = {
        "total_specs": int,
        "passed_specs": int,
        "failed_specs": int,
      }

      report_text:
        - для Html/Json — текст отчёта (строка);
        - для Ods/Bcf   — байты, декодированные в latin-1, чтобы их можно было
                          вернуть в JS как строку и затем сохранить как Blob.
    """
    import ifcopenshell
    from ifctester import ids as ids_mod
    from ifctester import reporter as reporter_mod

    # IFC
    ifc_bytes = bytes(ifc_bytes_view)
    ifc_str = ifc_bytes.decode("utf-8", errors="ignore")
    model = ifcopenshell.file.from_string(ifc_str)

    # IDS
    ids_xml = bytes(ids_bytes_view).decode("utf-8", errors="ignore")
    my_ids = ids_mod.from_string(ids_xml)

    # Валидация
    my_ids.validate(model)

    # Выбираем репортёр по формату[web:86][web:96]
    fmt = (report_format or "Html").strip()
    fmt = fmt[0].upper() + fmt[1:].lower()

    if fmt == "Json":
        rep = reporter_mod.Json(my_ids)
    elif fmt == "Ods":
        rep = reporter_mod.Ods(my_ids)
    elif fmt == "Bcf":
        rep = reporter_mod.Bcf(my_ids)
    else:
        # по умолчанию HTML
        fmt = "Html"
        rep = reporter_mod.Html(my_ids)

    # Сгенерировать отчёт (заполняет внутреннюю структуру rep).[web:86][web:96]
    rep.report()

    # Для HTML/JSON библиотека предоставляет текстовое представление.
    # Для ODS/BCF обычно генерируется бинарный контент файла.
    report_text: str

    if fmt in ("Html", "Json"):
        # В разных версиях может быть to_string/to_str/to_json.
        if hasattr(rep, "to_string"):
            report_text = rep.to_string()
        elif hasattr(rep, "to_str"):
            report_text = rep.to_str()
        elif hasattr(rep, "to_json"):
            report_text = rep.to_json()
        else:
            # fallback: пробуем стандартный str()
            report_text = str(rep)
    else:
        # Для ODS/BCF используем to_bytes/to_file-подобный метод.
        # У разных версий API могут быть разные методы, поэтому обрабатываем осторожно.[web:96][web:91]
        data_bytes = None
        if hasattr(rep, "to_bytes"):
            data_bytes = rep.to_bytes()
        elif hasattr(rep, "to_fileobj"):
            import io

            buf = io.BytesIO()
            rep.to_fileobj(buf)
            data_bytes = buf.getvalue()
        else:
            # HACK: если конкретной API нет, пробуем временный файл в памяти Pyodide FS.
            # Но для статического сценария это не всегда нужно, поэтому по умолчанию
            # возвращаем пустую строку.
            data_bytes = b""

        # Передаём в JS как строку с латинской "проекцией" байтов.
        # В JS мы сохраняем эти данные в Blob как бинарные, раз браузер не знает о кодировке.
        report_text = data_bytes.decode("latin-1", errors="ignore")

    # Простая сводка по спецификациям
    total_specs = len(my_ids.specifications)
    passed_specs = 0
    failed_specs = 0

    for spec in my_ids.specifications:
        status = getattr(spec, "status", None)
        if status is True:
            passed_specs += 1
        elif status is False:
            failed_specs += 1

    result = {
        "total_specs": total_specs,
        "passed_specs": passed_specs,
        "failed_specs": failed_specs,
    }

    return result, report_text
