import flet as ft
import asyncio

import initialize


IFCOPENSHELL_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
ODFPY_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/odfpy-1.4.2-py2.py3-none-any.whl"
# WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"


async def main(page: ft.Page):
	page.title = "IFC-IDS Отчёт"

	header = ft.Text(
		"IFC-IDS Отчёт",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

	# Статус и результаты
	status = ft.Text("Статус: готов", selectable=True)
	results = ft.ListView(expand=True, spacing=8)

	# File pickers
	def _ifc_result(e: ft.FilePickerResultEvent):
		if e.files:
			ifc_label.value = e.files[0].name
		else:
			ifc_label.value = "Отмена"
		ifc_label.update()

	def _ids_result(e: ft.FilePickerResultEvent):
		if e.files:
			ids_label.value = e.files[0].name
		else:
			ids_label.value = "Отмена"
		ids_label.update()

	ifc_picker = ft.FilePicker(on_result=_ifc_result)
	ids_picker = ft.FilePicker(on_result=_ids_result)
	page.overlay.append(ifc_picker)
	page.overlay.append(ids_picker)

	ifc_picker_btn = ft.ElevatedButton("Выбрать IFC файл", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: ifc_picker.pick_files())
	ids_picker_btn = ft.ElevatedButton("Выбрать IDS файл", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: ids_picker.pick_files())

	ifc_label = ft.Text("IFC: не выбран")
	ids_label = ft.Text("IDS: не выбран")

	# Dropdown с типом отчёта
	report_dropdown = ft.Dropdown(
		width=300,
		value="IDS: Сводка",
		options=[
			ft.dropdown.Option("IDS: Сводка"),
			ft.dropdown.Option("Сырые данные (preview)"),
			ft.dropdown.Option("IFC: Сводка сущностей"),
			ft.dropdown.Option("IFC: Свойства (Psets)"),
		],
	)

	run_btn = ft.ElevatedButton("Запустить отчёт", on_click=lambda e: results.controls.append(ft.Text(f"Запуск: {report_dropdown.value}")))

	# Сборка интерфейса
	controls_col = ft.Column([
		header,
		ft.Row([ifc_picker_btn, ifc_label], spacing=20),
		ft.Row([ids_picker_btn, ids_label], spacing=20),
		ft.Row([report_dropdown, run_btn], alignment=ft.MainAxisAlignment.START),
		ft.Divider(),
		ft.Text("Лог установки:", weight=ft.FontWeight.BOLD),
		status,
	], spacing=12)

	page.add(controls_col, results)

	# Запустить фоновую установку модулей (блок UI внутри функции)
	asyncio.create_task(initialize.block_ui_and_install(page, IFCOPENSHELL_WHEEL, ODFPY_WHEEL))




ft.app(target=main)
