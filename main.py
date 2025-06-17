import os
import fitz  # PyMuPDF
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

# Android-specific imports
if platform == "android":
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class PDFApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.label = Label(text="Enter your name:")
        self.text_input = TextInput(hint_text='Name', multiline=False)
        submit_button = Button(text='Generate PDF')
        submit_button.bind(on_press=self.generate_pdf)

        layout.add_widget(self.label)
        layout.add_widget(self.text_input)
        layout.add_widget(submit_button)

        return layout

    def generate_pdf(self, instance):
        name = self.text_input.text.strip()
        if not name:
            self.show_popup("Error", "Please enter a name.")
            return

        try:
            # Set PDF path based on platform
            if platform == "android":
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
                folder = primary_external_storage_path()
                pdf_path = os.path.join(folder, "output.pdf")
            else:
                pdf_path = "output.pdf"

            # Open base PDF and insert name
            doc = fitz.open("demo copy.pdf")
            page = doc[0]
            position = fitz.Point(220, 350)
            page.insert_text(position, name, fontsize=22, fontname="helv", color=(1, 0, 0))
            doc.save(pdf_path)
            doc.close()

            self.open_pdf(pdf_path)

        except Exception as e:
            self.show_popup("Error", f"Failed to create PDF: {str(e)}")

    def open_pdf(self, path):
        if platform == "android":
            try:
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                file = File(path)
                uri = Uri.fromFile(file)

                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, "application/pdf")
                intent.setFlags(Intent.FLAG_ACTIVITY_NO_HISTORY | Intent.FLAG_GRANT_READ_URI_PERMISSION)

                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(intent)

            except Exception as e:
                self.show_popup("Error", f"Could not open PDF: {str(e)}")
        else:
            # For desktop testing
            try:
                os.startfile(path)  # Windows
            except:
                os.system(f'xdg-open "{path}"')  # Linux/macOS

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

if __name__ == '__main__':
    PDFApp().run()
