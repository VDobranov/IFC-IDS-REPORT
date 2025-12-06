import micropip

async def install_and_import_ifcopenshell():
	try:
		status.value = "Устанавливаю ifcopenshell:\n		"
		page.update()
		await micropip.install(IFCOPENSHELL_WHEEL)
		status.value += "Установка завершена."
	except Exception as e:
		status.value += f"Ошибка установки: {e}."
	page.update()
	try:
		status.value += "\nУстанавливаю ifctester:\n		"
		page.update()
		await micropip.install(ODFPY_WHEEL)
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
