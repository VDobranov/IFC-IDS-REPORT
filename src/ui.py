from copy import copy
from typing import Sequence
import flet as ft
# import js

DARK = "#3A3A3A"
LIGHT = "#D9D9D9"
ACCENT = "#D4AF82"


def ui_init(page: ft.Page):

	header = ft.Text(
		"IFC-IDS Отчёт",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

	def _ifc_result(e: ft.FilePickerResultEvent):
		if e.files:
			ifcButtonRow.filename.value = e.files[0].name
		else:
			ifcButtonRow.filename.value = "<…>"
		ifcButtonRow.update()

	def _ids_result(e: ft.FilePickerResultEvent):
		if e.files:
			idsButtonRow.filename.value = e.files[0].name
		else:
			idsButtonRow.filename.value = "<…>"
		idsButtonRow.update()

	ifc_picker = ft.FilePicker(on_result=_ifc_result)
	ifc_picker.allowed_extensions = ["ifc"]
	ids_picker = ft.FilePicker(on_result=_ids_result)
	ids_picker.allowed_extensions = ["ids", "xml"]
	page.overlay.append(ifc_picker)
	page.overlay.append(ids_picker)
	
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
		# page.update()

	run_btn = ft.Button("Запустить отчёт", on_click=_results_append)
	# Сборка интерфейса
	controls_col = ft.Column([
		header,
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
	header_style = copy(txt_style)
	header_style.size = 40
	lbl_style = copy(txt_style)
	lbl_style.size = 14
	buttons_style = ft.ButtonStyle(
		color=DARK,
		overlay_color=ACCENT,
		bgcolor=LIGHT,
		# overlay_color=LIGHT,
		shape=ft.RoundedRectangleBorder(radius=0),
		text_style=txt_style
	)

	class ButtonRow(ft.Row):
		def __init__(
				self,
				controls: Sequence[ft.Control] | None = None,
				alignment: ft.MainAxisAlignment | None = None,
				label: str = "label",
				placeholder: str = "placeholder",
				icon: ft.Icons | None = None,
				on_clck: ft.OptionalControlEventCallable | None = None
		):
			super().__init__(controls, alignment)
			self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
			self.filename = ft.Text(placeholder, style=txt_style)
			self.controls = [
				ft.Button(
					label,
					icon=icon,
					style=buttons_style,
					height=56,
					on_click=on_clck,
					expand=1000
				),
				ft.Container(
					self.filename,
					alignment=ft.alignment.center_left,
					border=ft.border.all(1, LIGHT),
					border_radius=0,
					height=56,
					padding=ft.Padding(left=16, right=0, top=4, bottom=4),
					expand=1618
				)
			]
	
	ifcButtonRow = ButtonRow(label="Загрузить IFC-файл",
							placeholder="<Модель.ifc>",
							icon=ft.Icons.FILE_UPLOAD,
							on_clck=lambda _: ifc_picker.pick_files()
							)
	idsButtonRow = ButtonRow(label="Загрузить IDS-файл",
							placeholder="<Спецификация.ids>",
							icon=ft.Icons.FILE_UPLOAD,
							on_clck=lambda _: ids_picker.pick_files()
							)

	report_formats = [
		"TXT",
		"HTML",
		"JSON",
		"ODF",
		"ODF Summary",
		"BCF"
	]

	def get_options():
		options = []
		for report in report_formats:
			options.append(
				ft.DropdownOption(
					key=report,
					content=ft.Text(
						value=report,
					),
					style=buttons_style
				)
			)
		return options

	def dropdown_changed(e):
		# e.control.color = e.control.value
		page.update()

	cntrls = ft.Row(
		controls=[
			ft.Container(
				content=ft.Column(
					[
						ft.Column(
							[
								ft.Container(
									ft.Text("IFC-IDS-REPORT",
											theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
											style=header_style),
									# height=100,
									alignment=ft.alignment.center,
								),
								ifcButtonRow,
								idsButtonRow,
								ft.Row([ft.Button(
									"Запустить валидацию",
									icon=ft.Icons.CHECK,
									style=buttons_style,
									height=56,
									# on_click=on_click,
									expand=1000
								)]),
								ft.Row([
									ft.Button(
										"Скачать отчёт",
										icon=ft.Icons.FILE_DOWNLOAD,
										style=buttons_style,
										height=56,
										disabled=True,
										# on_click=on_click,
										expand=1000
									),
									ft.Dropdown(
										label="формат отчёта",
										value="HTML",
										label_style=lbl_style,
										text_style=txt_style,
										color=LIGHT,
										trailing_icon=ft.Icon(
											name=ft.Icons.ARROW_DROP_DOWN, color=LIGHT),
										selected_trailing_icon=ft.Icon(
											name=ft.Icons.ARROW_DROP_UP, color=LIGHT),
										alignment=ft.alignment.center_left,
										border_color=LIGHT,
										border_width=1,
										border_radius=0,
										# content_padding=ft.Padding(left=16, right=0, top=4, bottom=4),
										options=get_options(),
										on_change=dropdown_changed,
										expand=1618
									)
								], vertical_alignment=ft.CrossAxisAlignment.END),
							],
							alignment=ft.MainAxisAlignment.SPACE_EVENLY,
							expand=1000
				   		),
					ft.Container(expand=1618)],
					horizontal_alignment=ft.CrossAxisAlignment.STRETCH
				),
				expand=1000,
				bgcolor=DARK,
				padding=ft.Padding(left=56, right=56, top=0, bottom=0)
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

	return cntrls
