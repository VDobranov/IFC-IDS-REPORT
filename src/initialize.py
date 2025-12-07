import flet as ft
import micropip
import js


async def install_and_import_ifcopenshell(page: ft.Page, status: ft.Text, IFCOPENSHELL_WHEEL: str, ODFPY_WHEEL: str):
	try:
		js.console.log("Устанавливаю ifcopenshell")
		status.value += "Устанавливаю ifcopenshell\n"
		page.update()
		await micropip.install(IFCOPENSHELL_WHEEL)
		js.console.log("Установка завершена.")
		status.value += "Установка завершена.\n"
	except Exception as e:
		js.console.log(f"Ошибка установки: {e}.")
		status.value += f"Ошибка установки: {e}.\n"
	page.update()
	try:
		js.console.log("Устанавливаю ifctester")
		status.value += "Устанавливаю ifctester\n"
		page.update()
		await micropip.install(ODFPY_WHEEL)
		await micropip.install('ifctester')
		js.console.log("Установка завершена.")
		status.value += "Установка завершена.\n"
	except Exception as e:
		js.console.log(f"Ошибка установки: {e}.")
		status.value += f"Ошибка установки: {e}.\n"
	page.update()
	try:
		js.console.log("Импортирую модуль ifcopenshell")
		status.value += "Импортирую модуль ifcopenshell\n"
		page.update()
		import ifcopenshell
		# ifc_file = ifcopenshell.file()
		js.console.log("Модуль ifcopenshell импортирован.")
		status.value += "Модуль ifcopenshell импортирован.\n"
	except Exception as e:
		js.console.log(
			f"Возникла ошибка при импорте модуля ifcopenshell: {e}.")
		status.value += f"Возникла ошибка при импорте модуля ifcopenshell: {e}."
	page.update()
	try:
		js.console.log("Импортирую модуль ifctester")
		status.value += "Импортирую модуль ifctester\n"
		page.update()
		import ifctester
		js.console.log("Модуль ifctester импортирован.")
		status.value += "Модуль ifctester импортирован.\n"
	except Exception as e:
		js.console.log(f"Возникла ошибка при импорте модуля ifctester: {e}.")
		status.value += f"Возникла ошибка при импорте модуля ifctester: {e}.\n"
	page.update()


async def block_ui_and_install(page: ft.Page, IFCOPENSHELL_WHEEL: str, ODFPY_WHEEL: str):
	for c in page.controls:
		c.disabled = True
	page.update()

	status = ft.Text("Пожалуйста, подождите окончания установки…\n")
	busy_overlay = ft.AlertDialog(
		title=ft.Text("Установка библиотек Python"),
		content=ft.Container(
			content=ft.Column(
				[ft.ProgressRing(), status],
				alignment=ft.MainAxisAlignment.START,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER),
			height=page.height/3),
		actions=[],
		modal=True
	)
	page.open(busy_overlay)

	try:
		await install_and_import_ifcopenshell(page, status, IFCOPENSHELL_WHEEL, ODFPY_WHEEL)
	except Exception as e:
		# show error in UI and console
		status.value += f"\nInstall error: {e}"
		page.update()
	finally:
		page.close(busy_overlay)
		for c in page.controls:
			c.disabled = False
		page.update()
