import os
import sys
import tempfile
import flet as ft
import asyncio
import micropip


# Browser WASM wheel URL and localStorage flag version
WASM_WHEEL_URL = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"


async def install_ifcopenshell():
	try:
		await micropip.install(WASM_WHEEL_URL)
		print("ifcopenshell установлен успешно!")
	except Exception as e:
		print(f"Ошибка установки: {e}")


def main(page: ft.Page):
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

	page.add(
		header,
		ifc_picker_btn,
		results
	)
	asyncio.run(install_ifcopenshell())


ft.app(target=main)
