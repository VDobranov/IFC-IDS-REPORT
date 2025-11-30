import os
import sys
import tempfile
import flet as ft


def main(page: ft.Page):
	page.title = "IFC-IDS Report"

	header = ft.Text(
		"IFC-IDS Report",
		style=ft.TextThemeStyle.HEADLINE_MEDIUM,
	)

	results = ft.ListView(expand=True, spacing=8)

	async def load_modules(e: ft.ControlEvent):
		try:
			# micropip exists only in Pyodide/browser environments
			import importlib
			import micropip
			results.controls.append(ft.Text("Installing WASM ifcopenshell in browser (micropip)..."))
			page.update()
			# URL provided for on-prem / local-hosted wheel — install it in-browser
			# wasm_wheel = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.3+34a1bc6-cp313-cp313-emscripten_4_0_9_wasm32.whl"
			wasm_wheel = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
			try:
				await micropip.install(wasm_wheel)
			except Exception as ex:
				results.controls.append(ft.Text(f"Failed to load WASM ifcopenshell: {ex}", selectable=True))
				results.controls.append(ft.Text(f"Trying to load usual ifcopenshell"))

			# reload modules
			# ifctester = importlib.import_module("ifctester")

			ios = importlib.import_module("ifcopenshell")
			# also bind ifcopenshell name used below
			sys.modules["ifcopenshell"] = ios
			results.controls.append(ft.Text(f"Ifcopenshell Version: {ios.__version__}"))
			load_modules_btn.visible = False
			page.update()
		except Exception as ex:
			results.controls.append(ft.Text(f"Failed to load wasm/browser dependencies: {ex}"))
			page.update()
			return

	load_modules_btn = ft.ElevatedButton("Load ifcopenshell", on_click=load_modules)

	page.add(
		header,
		load_modules_btn,
		results
	)


ft.app(target=main)
