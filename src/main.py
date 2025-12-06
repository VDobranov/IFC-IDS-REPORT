import flet as ft

import initialize


IFCOPENSHELL_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
ODFPY_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/odfpy-1.4.2-py2.py3-none-any.whl"
# WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"


async def main(page: ft.Page):
	page.title = "IFC-IDS Report"

	header = ft.Text(
		"IFC-IDS Report",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

	status = ft.Text("Статус: ", selectable=True)

	ifc_picker_btn = ft.ElevatedButton(
		"Pick files",
		icon=ft.Icons.UPLOAD_FILE,
	)

	results = ft.ListView(expand=True, spacing=8)

	page.add(
		header,
		status,
		ifc_picker_btn,
		results
	)
	
	await initialize.install_and_import_ifcopenshell()




ft.app(target=main)
