from copy import copy
import flet as ft
import asyncio

import initialize


IFCOPENSHELL_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
ODFPY_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/odfpy-1.4.2-py2.py3-none-any.whl"
# WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"
DARK = "#3A3A3A"
LIGHT = "#D9D9D9"


async def main(page: ft.Page):
	page.title = "IFC-IDS-REPORT"
	page.fonts = {
		"PT Sans": "https://raw.githubusercontent.com/google/fonts/master/ofl/ptsans/PT_Sans-Web-Regular.ttf",
	}

	header = ft.Text(
		"IFC-IDS Отчёт",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

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
	ifc_picker.allowed_extensions = ["ifc"]
	ids_picker = ft.FilePicker(on_result=_ids_result)
	ids_picker.allowed_extensions = ["ids", "xml"]
	page.overlay.append(ifc_picker)
	page.overlay.append(ids_picker)

	ifc_picker_btn = ft.ElevatedButton(
		"Выбрать IFC файл", icon=ft.Icons.FILE_UPLOAD, on_click=lambda _: ifc_picker.pick_files())
	ids_picker_btn = ft.ElevatedButton(
		"Выбрать IDS файл", icon=ft.Icons.FILE_UPLOAD, on_click=lambda _: ids_picker.pick_files())

	ifc_label = ft.Text("IFC: не выбран")
	ids_label = ft.Text("IDS: не выбран")

	# Dropdown с типом отчёта
	report_dropdown = ft.Dropdown(
		width=300,
		value="HTML",
		options=[
			ft.dropdown.Option("TXT"),
			ft.dropdown.Option("HTML"),
			ft.dropdown.Option("JSON"),
			ft.dropdown.Option("BCF"),
			ft.dropdown.Option("ODF"),
			ft.dropdown.Option("ODF Summary"),
		],
	)

	results = ft.ListView(expand=True, spacing=8)

	def _results_append(e):
		results.controls.append(ft.Text(f"Запуск: {report_dropdown.value}"))
		page.update()

	run_btn = ft.ElevatedButton("Запустить отчёт", on_click=_results_append)

	# Сборка интерфейса
	controls_col = ft.Column([
		header,
		ft.Row([ifc_picker_btn, ifc_label], spacing=20),
		ft.Row([ids_picker_btn, ids_label], spacing=20),
		ft.Row([report_dropdown, run_btn],
			   alignment=ft.MainAxisAlignment.START),
		ft.Divider(),
		results
	], spacing=12)

	txt_style = ft.TextStyle(
		color=LIGHT,
		font_family="PT Sans",
		size=16
	)
	header_style=copy(txt_style)
	header_style.size=40
	buttons_style = ft.ButtonStyle(
		color=DARK,
		bgcolor=LIGHT,
		overlay_color=LIGHT,
		shape=ft.RoundedRectangleBorder(radius=0),
		text_style=txt_style
	)

	controls = ft.Row(
		controls=[
			ft.Container(
				content=ft.Column(
					[
						ft.Text("IFC-IDS-REPORT",
								theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
								style=header_style),
						ft.Row(
							controls=[
								ft.ElevatedButton(
									"Выбрать IFC файл",
									icon=ft.Icons.FILE_UPLOAD,
									style=buttons_style,
									height=56,
									expand=1000
								),
								ft.Container(
									ft.Text(
										"Модель.ifc",
										style=txt_style,
									),
									alignment=ft.alignment.center_left,
									border=ft.border.all(2,LIGHT),
									border_radius=0,
									height=56,
									padding=ft.Padding(left=16, right=0, top=4, bottom=4),
									expand=1618
								)
								# ft.TextField(
								# 	"IDS СПб ГАУ ЦГЭ (Конструктивные решения).ids",
								# 	text_style=txt_style,
								# 	border_color=LIGHT,
								# 	border_radius=0,
								# 	border_width=2,
								# 	content_padding=ft.Padding(left=16, right=0, top=8, bottom=8),
								# 	# height=56,
								# 	multiline=True,
								# 	read_only=True,
								# 	expand=1618
								# )
							],
							alignment=ft.MainAxisAlignment.CENTER
						)
					],
					horizontal_alignment=ft.CrossAxisAlignment.CENTER
				),
				expand=1000,
				bgcolor=DARK,
				padding=ft.Padding(left=48, right=48, top=0, bottom=0)
			),
			ft.Container(
				content=ft.Column(
					[],
				),
				expand=1618,
				bgcolor=LIGHT,
			),
		],
		spacing=0,
		expand=True
	)

	page.add(controls)
	page.padding = 0
	page.update()

	# Запустить фоновую установку модулей (блок UI внутри функции)
	# asyncio.create_task(initialize.block_ui_and_install(page, IFCOPENSHELL_WHEEL, ODFPY_WHEEL))


ft.app(target=main)
