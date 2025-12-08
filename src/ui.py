from copy import copy
from typing import Sequence
import flet as ft

DARK = "#3A3A3A"
LIGHT = "#D9D9D9"


def ui_init(page: ft.Page):

    header = ft.Text(
        "IFC-IDS Отчёт",
        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
    )

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
    # page.overlay.append(ifc_picker)
    # page.overlay.append(ids_picker)
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
        # page.update()

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
    header_style = copy(txt_style)
    header_style.size = 40
    buttons_style = ft.ButtonStyle(
        color=DARK,
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
                on_click: ft.OptionalControlEventCallable | None = None
        ):
            super().__init__(controls, alignment)
            self.alignment = ft.MainAxisAlignment.CENTER
            self.controls = [
                ft.ElevatedButton(
                    label,
                    icon=icon,
                    style=buttons_style,
                    height=56,
                    on_click=on_click,
                    expand=1000
                ),
                ft.Container(
                    ft.Text(
                        placeholder,
                        style=txt_style,
                    ),
                    alignment=ft.alignment.center_left,
                    border=ft.border.all(1, LIGHT),
                    border_radius=0,
                    height=56,
                    padding=ft.Padding(left=16, right=0, top=4, bottom=4),
                    expand=1618
                )
            ]

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
                    [ft.Column([
                        ft.Container(
                            ft.Text("IFC-IDS-REPORT",
                                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                    style=header_style),
                            height=100,
                            alignment=ft.alignment.center,
                        ),
                        ButtonRow(label="Загрузить IFC-файл",
                                  placeholder="Модель.ifc", icon=ft.Icons.FILE_UPLOAD),
                        ButtonRow(label="Загрузить IDS-файл",
                                  placeholder="Спецификация.ids", icon=ft.Icons.FILE_UPLOAD),
                        ft.Row([ft.ElevatedButton(
                            "Запустить валидацию",
                            icon=ft.Icons.CHECK,
                            style=buttons_style,
                            height=56,
                            # on_click=on_click,
                            expand=1000
                        )]),
                        ft.Row([
                            ft.ElevatedButton(
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
                                color=LIGHT,
                                trailing_icon=ft.Icon(
                                    name=ft.Icons.ARROW_DROP_DOWN, color=LIGHT),
                                selected_trailing_icon=ft.Icon(
                                    name=ft.Icons.ARROW_DROP_UP, color=LIGHT),
                                alignment=ft.alignment.center_left,
                                border_color=LIGHT,
                                border_width=1,
                                border_radius=0,
                                # height=56,
                                # content_padding=ft.Padding(left=16, right=0, top=4, bottom=4),
                                options=get_options(),
                                on_change=dropdown_changed,
                                expand=1618
                            )
                        ], vertical_alignment=ft.CrossAxisAlignment.END),
                    ],expand=1000),
                    ft.Container(expand=1618)],
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

    return cntrls
