import os
import sys
import tempfile
import flet as ft
import asyncio
import micropip
# import ifctester


# Browser WASM wheel URL and localStorage flag version
WASM_WHEEL_URL = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
WASM_INSTALL_FLAG = "ifcopenshell_wasm_installed_v1"


async def main(page: ft.Page):
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

	status = ft.Text("Статус: ", selectable=True)
	page.add(
		header,
		status,
		ifc_picker_btn,
		results
	)
	async def install_and_import_ifcopenshell():
		try:
			status.value = "Устанавливаю WASM-ifcopenshell:\n		"
			page.update()
			await micropip.install(WASM_WHEEL_URL)
			status.value += "Установка завершена."
		except Exception as e:
			status.value += f"Ошибка установки: {e}."	
		page.update()

		try:
			status.value += "\nУстанавливаю ifctester:\n		"
			page.update()
			await micropip.install("http://localhost:8000/odfpy-1.4.2-py2.py3-none-any.whl")
			await micropip.install('ifctester')
			status.value += "Установка завершена."
		except Exception as e:
			status.value += f"Ошибка установки: {e}."	
		page.update()
		
		try:
			status.value += "\nИмпортирую модуль ifcopenshell:\n		"
			page.update()
			import ifcopenshell
			ifc_file = ifcopenshell.file()
			status.value += "Модуль ifcopenshell импортирован."
		except Exception as e:
			status.value += f"Возникла ошибка при импорте модуля ifcopenshell: {e}."
		page.update()
		
		try:
			status.value += "\nИмпортирую модуль ifctester:\n		"
			page.update()
			import ifctester
			status.value += "Модуль ifctester импортирован."
		except Exception as e:
			status.value += f"Возникла ошибка при импорте модуля ifctester: {e}."
		page.update()
	
	await install_and_import_ifcopenshell()




ft.app(target=main)
