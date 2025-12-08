from copy import copy
from typing import Sequence
import flet as ft
import asyncio

import initialize
import ui
# from ui import cntrls


IFCOPENSHELL_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/ifcopenshell-0.8.2+d50e806-cp312-cp312-emscripten_3_1_58_wasm32.whl"
ODFPY_WHEEL = "https://raw.githubusercontent.com/vdobranov/ifc-ids-report/main/wheels/odfpy-1.4.2-py2.py3-none-any.whl"


async def main(page: ft.Page):
	cntrls = ui.ui_init(page)
	page.title = "IFC-IDS-REPORT"
	page.fonts = {
		"PT Sans": "https://raw.githubusercontent.com/google/fonts/master/ofl/ptsans/PT_Sans-Web-Regular.ttf",
	}
	page.add(cntrls)
	page.padding = 0
	page.update()

	# Запустить фоновую установку модулей (блок UI внутри функции)
	# asyncio.create_task(initialize.block_ui_and_install(page, IFCOPENSHELL_WHEEL, ODFPY_WHEEL))


ft.app(target=main)
