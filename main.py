import flet as ft

def main(page: ft.Page):
	page.title = "Flet Starter"

	txt = ft.Text("Hello, Flet!")
	tf = ft.TextField(label="Type your name")

	def on_click(e):\
		# tf.value may be None; coerce to empty string before strip
		name = (tf.value or "").strip() or "World"
		txt.value = f"Hello, {name}!"
		page.update()

	btn = ft.ElevatedButton(text="Greet", on_click=on_click)

	page.add(txt, tf, btn)

ft.app(target=main)
