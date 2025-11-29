import flet as ft

def main(page: ft.Page):
    page.title = "Flet Starter"

    txt = ft.Text("Hello, Flet!")
    tf = ft.TextField(label="Type your name")

    def on_click(e):
        # tf.value may be None; coerce to empty string before strip
        name = (tf.value or "").strip() or "World"
        txt.value = f"Hello, {name}!"
        page.update()

    btn = ft.ElevatedButton(text="Greet", on_click=on_click)

    page.add(txt, tf, btn)

if __name__ == "__main__":
    # Launch the Flet app in the default web browser
    # type: ignore[arg-type] -- some type checkers flag the literal constant here
    ft.app(target=main, view=ft.WEB_BROWSER)  # type: ignore[arg-type]
