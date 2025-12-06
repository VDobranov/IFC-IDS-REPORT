import os
import sys
import tempfile
import flet as ft
import asyncio
import micropip


# Browser WASM wheel URL and localStorage flag version
WASM_WHEEL_URL = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"


async def install_and_import_ifcopenshell():
	try:
		status.value = "Устанавливаю ifcopenshell..."
		page.update()
		await micropip.install(WASM_WHEEL_URL)
	except Exception as e:
		print(f"Ошибка установки: {e}")
	try:
		import ifcopenshell
		ifc_file = ifcopenshell.file()
		status.value += "\nСоздан пустой IFC-файл."
		page.update()
	except:
		pass


async def main(page: ft.Page):
	await install_and_import_ifcopenshell()


	page.title = "IFC-IDS Report"

	header = ft.Text(
		"IFC-IDS Report",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

	results = ft.ListView(expand=True, spacing=8)

	ifc_picker_btn = ft.ElevatedButton(
		"Pick files",
		icon=ft.Icons.UPLOAD_FILE,
	)

	status = ft.Text("Статус: ")
	page.add(status)

	page.add(
		header,
		status,
		ifc_picker_btn,
		results
	)


ft.app(target=main)
