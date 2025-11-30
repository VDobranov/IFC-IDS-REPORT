import os
import tempfile
import flet as ft

# import ifcopenshell


def main(page: ft.Page):
    page.title = "IFC-IDS Report"

    header = ft.Text(
        "IFC-IDS Report — upload IFC models",
        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
    )

    # Results area
    results = ft.ListView(expand=True, spacing=8)

    # Report type selector (dropdown)
    report_options = [
        "IFC: Entity summary",
        "IFC: Property sets",
        "IDS: Summary",
        "Raw preview",
    ]
    report_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(o) for o in report_options],
        value=report_options[0],
        label="Report type",
    )

    # visible labels showing the last chosen filenames
    ifc_label = ft.Text("No IFC selected", style=ft.TextThemeStyle.BODY_SMALL)
    ids_label = ft.Text("No IDS selected", style=ft.TextThemeStyle.BODY_SMALL)

    # store latest uploaded file paths so user can run reports
    current_ifc_path = None
    current_ids_path = None
    current_ids_text = None
    # remember last directory used by pickers (desktop only)
    last_dir = None

    # helper: save uploaded file object to disk (handles desktop/web variants)
    def _save_picker_file(f, filename, default_suffix):
        # return path
        if getattr(f, "path", None):
            return f.path
        suffix = os.path.splitext(filename)[1] or default_suffix
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tf.close()
        # runtime guards for different Flet versions
        if getattr(f, "save", None):
            f.save(tf.name)
        elif getattr(f, "content", None) is not None:
            with open(tf.name, "wb") as fh:
                fh.write(f.content)
        else:
            read = getattr(f, "read", None)
            if callable(read):
                with open(tf.name, "wb") as fh:
                    fh.write(read())
            else:
                raise RuntimeError("File object has no save(), content, or read()")
        return tf.name

    # FilePicker (IFC)
    def on_file_picker_result(e: ft.FilePickerResultEvent):
        nonlocal current_ifc_path, last_dir
        if e.files is None:
            return
        for f in e.files:
            filename = f.name
            try:
                path = _save_picker_file(f, filename, ".ifc")
                # remember last uploaded IFC path and directory (only update dir if original path exists)
                current_ifc_path = path
                if getattr(f, "path", None):
                    last_dir = os.path.dirname(path)
                # try to parse basic info with ifcopenshell
                entity_count = None
                try:
                    model = ifcopenshell.open(path)
                    try:
                        entity_count = sum(1 for _ in model)
                    except Exception:
                        entity_count = sum(
                            len(model.by_type(t))
                            for t in ["IfcProject", "IfcSite", "IfcBuilding"]
                            if model.by_type(t) is not None
                        )
                except Exception:
                    entity_count = None
                txt = f"{filename}"
                if entity_count is not None:
                    txt += f" — entities: {entity_count}"
                else:
                    txt += " — uploaded (IFC parsing unavailable or failed)"
                # update label
                try:
                    ifc_label.value = filename
                except Exception:
                    try:
                        ifc_label.text = filename
                    except Exception:
                        pass
                results.controls.append(ft.Text(txt))
                page.update()
            except Exception as err:
                results.controls.append(ft.Text(f"Failed to process {filename}: {err}"))
                page.update()

    ifc_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(ifc_picker)

    def on_upload_ifc(e: ft.ControlEvent):
        ifc_picker.pick_files(
            allow_multiple=False, allowed_extensions=["ifc"], initial_directory=last_dir
        )

    upload_btn = ft.ElevatedButton("Upload IFC file", on_click=on_upload_ifc)

    # IDS upload area
    ids_results = ft.ListView(expand=True, spacing=6)

    def on_ids_file_picker_result(e: ft.FilePickerResultEvent):
        nonlocal current_ids_path, current_ids_text, last_dir
        if e.files is None:
            return
        for f in e.files:
            filename = f.name
            try:
                path = _save_picker_file(f, filename, ".ids")
                current_ids_path = path
                if getattr(f, "path", None):
                    last_dir = os.path.dirname(path)
                # update visible label
                try:
                    ids_label.value = filename
                except Exception:
                    try:
                        ids_label.text = filename
                    except Exception:
                        pass
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        current_ids_text = fh.read()
                except Exception:
                    current_ids_text = None

                # Try parsing using ifctester.ids.from_string when available for a short summary
                try:
                    from ifctester import ids as ids_module

                    parsed_ids = ids_module.from_string(current_ids_text)
                    ids_dict = parsed_ids.asdict()
                    title = ids_dict.get("info", {}).get("title", "(no title)")
                    specs = ids_dict.get("specifications", {}).get("specification", [])
                    summary = f"title: {title}; specifications: {len(specs)}"
                except Exception as ex:
                    summary = f"parsing failed: {ex}"

                if summary is None:
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            lines = [next(fh).rstrip("\n") for _ in range(10)]
                        preview = "\n".join(lines)
                    except Exception:
                        preview = "(binary or unreadable preview)"
                    summary = f"preview:\n{preview}"

                ids_results.controls.append(ft.Text(f"{filename} — {summary}"))
                page.update()
            except Exception as err:
                ids_results.controls.append(ft.Text(f"Failed to process IDS {filename}: {err}"))
                page.update()

    ids_picker = ft.FilePicker(on_result=on_ids_file_picker_result)
    page.overlay.append(ids_picker)

    def on_upload_ids(e: ft.ControlEvent):
        ids_picker.pick_files(
            allow_multiple=False, allowed_extensions=["ids", "xml"], initial_directory=last_dir
        )

    ids_upload_btn = ft.ElevatedButton("Upload IDS file", on_click=on_upload_ids)

    # Run report action: will use ifctester to check IFC against IDS and produce the chosen report
    async def run_report(e: ft.ControlEvent):
        nonlocal current_ifc_path, current_ids_path, current_ids_text
        if not current_ifc_path:
            results.controls.append(ft.Text("No IFC file uploaded. Please upload an IFC model first."))
            page.update()
            return
        if not current_ids_path or not current_ids_text:
            results.controls.append(ft.Text("No IDS file uploaded. Please upload an IDS file first."))
            page.update()
            return

        sel = report_dropdown.value or "IFC: Entity summary"
        results.controls.append(ft.Text(f"Running report: {sel} — this may take a moment..."))
        page.update()

        # Try desktop imports first; on web (pyodide) fallback to micropip installing WASM wheel
        try:
            import ifctester
            # import ifcopenshell as _ifc
        except Exception:
            try:
                # micropip exists only in Pyodide/browser environments
                import importlib
                import micropip
                results.controls.append(ft.Text("Installing WASM ifcopenshell in browser (micropip)..."))
                page.update()
                # URL provided for on-prem / local-hosted wheel — install it in-browser
                wasm_wheel = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.3+34a1bc6-cp313-cp313-emscripten_4_0_9_wasm32.whl"
                try:
                    await micropip.install(wasm_wheel)
                except Exception:
                    # try installing just the package name as a fallback
                    try:
                        await micropip.install("ifcopenshell")
                    except Exception:
                        pass
                # try to install ifctester too (pure-python)
                try:
                    await micropip.install("ifctester")
                except Exception:
                    pass
                # reload modules
                ifctester = importlib.import_module("ifctester")
                # _ifc = importlib.import_module("ifcopenshell")
                # also bind ifcopenshell name used below
                import sys
                sys.modules["ifcopenshell"] = _ifc
            except Exception as ex:
                results.controls.append(ft.Text(f"Failed to load wasm/browser dependencies: {ex}"))
                page.update()
                return

        # Parse IDS and open IFC model
        try:
            ids_obj = ifctester.ids.from_string(current_ids_text)
        except Exception as ex:
            results.controls.append(ft.Text(f"Failed to parse IDS: {ex}"))
            page.update()
            return

        try:
            model = ifcopenshell.open(current_ifc_path)
        except Exception as ex:
            results.controls.append(ft.Text(f"Failed to open IFC model: {ex}"))
            page.update()
            return

        # IDS summary
        if sel == "IDS: Summary":
            try:
                idsd = ids_obj.asdict()
                title = idsd.get("info", {}).get("title", "(no title)")
                specs = idsd.get("specifications", {}).get("specification", [])
                results.controls.append(ft.Text(f"IDS title: {title}; specifications: {len(specs)}"))
            except Exception as ex:
                results.controls.append(ft.Text(f"Failed to summarize IDS: {ex}"))
            page.update()
            return

        # Raw preview
        if sel == "Raw preview":
            try:
                with open(current_ids_path, "r", encoding="utf-8", errors="ignore") as fh:
                    lines = [next(fh).rstrip("\n") for _ in range(20)]
                preview = "\n".join(lines)
                results.controls.append(ft.Text(f"IDS preview:\n{preview}"))
            except Exception as ex:
                results.controls.append(ft.Text(f"Failed to create preview: {ex}"))
            page.update()
            return

        # Validate IDS against IFC model (populates Specification status)
        try:
            ids_obj.validate(model, should_filter_version=False, filepath=current_ids_path)
        except Exception as ex:
            results.controls.append(ft.Text(f"Validation failed: {ex}"))
            page.update()
            return

        # IFC: Entity summary
        if sel == "IFC: Entity summary":
            try:
                counts = {}
                for inst in model:
                    t = inst.is_a()
                    counts[t] = counts.get(t, 0) + 1
                items = sorted(counts.items(), key=lambda x: -x[1])[:20]
                for t, c in items:
                    results.controls.append(ft.Text(f"{t}: {c}"))
            except Exception as ex:
                results.controls.append(ft.Text(f"Failed to compute entity summary: {ex}"))
            page.update()
            return

        # IFC: Property sets (detailed validation report)
        if sel == "IFC: Property sets":
            try:
                specs = ids_obj.specifications
                if not specs:
                    results.controls.append(ft.Text("No specifications found in IDS."))
                    page.update()
                    return
                for spec in specs:
                    name = getattr(spec, "name", "(unnamed)")
                    status = getattr(spec, "status", None)
                    app_count = len(getattr(spec, "applicable_entities", []))
                    passed = len(getattr(spec, "passed_entities", []))
                    failed = len(getattr(spec, "failed_entities", []))
                    results.controls.append(
                        ft.Text(
                            f"Specification: {name} — status: {status} — applicable: {app_count} passed: {passed} failed: {failed}"
                        )
                    )
                    # show up to 5 failure examples across requirement facets
                    shown = 0
                    for facet in getattr(spec, "requirements", []):
                        for f in getattr(facet, "failures", [])[:5]:
                            # f is TypedDict with 'element' and 'reason'
                            try:
                                elt = f.get("element") if isinstance(f, dict) else None
                                reason = f.get("reason") if isinstance(f, dict) else None
                            except Exception:
                                elt = None
                                reason = None
                            try:
                                eid = None
                                if elt is not None:
                                    eid = getattr(elt, "GlobalId", None) or (getattr(elt, "id", None) and elt.id())
                            except Exception:
                                eid = str(elt)
                            results.controls.append(ft.Text(f"  failure: element={eid} reason={reason}"))
                            shown += 1
                            if shown >= 5:
                                break
                        if shown >= 5:
                            break
                page.update()
                return
            except Exception as ex:
                results.controls.append(ft.Text(f"Failed to generate property-set report: {ex}"))
                page.update()
                return

        results.controls.append(ft.Text("Selected report type not implemented."))
        page.update()

    run_report_btn = ft.ElevatedButton("Run report", on_click=run_report)

    # Simple instructions
    instructions = ft.Text("Click 'Upload IFC file' (*.ifc) and 'Upload IDS file' (*.ids, *.xml).")

    page.add(
        header,
        report_dropdown,
        instructions,
        upload_btn,
        ifc_label,
        ft.Divider(),
        ft.Text("IDS uploads", style=ft.TextThemeStyle.BODY_MEDIUM),
        ids_upload_btn,
        ids_label,
        ids_results,
        ft.Divider(),
        run_report_btn,
        results,
    )


ft.app(target=main)
