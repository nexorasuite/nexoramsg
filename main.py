from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from sender import send_whatsapp_messages_with_log
import uuid
import os
import threading
import time

def clean_number(num):
    return ''.join(filter(str.isdigit, num))

class WhatsAppUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.numbers_input = TextInput(hint_text='Paste numbers (one per line)', multiline=True, size_hint_y=0.4)
        self.message_input = TextInput(hint_text='Enter your message', multiline=True, size_hint_y=0.3)
        self.status_label = Label(text='', size_hint_y=0.1)

        self.start_button = Button(text='Start', size_hint_y=0.1)
        self.pause_button = Button(text='Pause', size_hint_y=0.1, disabled=True)
        self.resume_button = Button(text='Resume', size_hint_y=0.1, disabled=True)
        self.stop_button = Button(text='Stop', size_hint_y=0.1, disabled=True)

        self.start_button.bind(on_press=self.start_sending)
        self.pause_button.bind(on_press=self.pause_sending)
        self.resume_button.bind(on_press=self.resume_sending)
        self.stop_button.bind(on_press=self.stop_sending)

        self.add_widget(self.numbers_input)
        self.add_widget(self.message_input)
        self.add_widget(self.start_button)
        self.add_widget(self.pause_button)
        self.add_widget(self.resume_button)
        self.add_widget(self.stop_button)
        self.add_widget(self.status_label)

        self._stop_flag = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._thread = None

    def start_sending(self, instance):
        raw_numbers = self.numbers_input.text
        message = self.message_input.text

        if not raw_numbers.strip() or not message.strip():
            self.status_label.text = "❌ Please enter numbers and message"
            return

        self.numbers = [clean_number(num.strip()) for num in raw_numbers.split('\n') if num.strip()]
        self.message = message
        self.log_filename = f'whatsapp_log_{uuid.uuid4().hex[:6]}.xlsx'
        self.log_path = os.path.join('logs', self.log_filename)
        os.makedirs('logs', exist_ok=True)

        self._stop_flag = False
        self._pause_event.set()

        self.start_button.disabled = True
        self.pause_button.disabled = False
        self.resume_button.disabled = True
        self.stop_button.disabled = False
        self.status_label.text = "📤 Sending messages..."

        self._thread = threading.Thread(target=self._send_loop)
        self._thread.start()

    def pause_sending(self, instance):
        self._pause_event.clear()
        self.status_label.text = "⏸️ Paused"
        self.pause_button.disabled = True
        self.resume_button.disabled = False

    def resume_sending(self, instance):
        self._pause_event.set()
        self.status_label.text = "▶️ Resumed"
        self.pause_button.disabled = False
        self.resume_button.disabled = True

    def stop_sending(self, instance):
        self._stop_flag = True
        self._pause_event.set()  # In case it was paused
        self.status_label.text = "⏹️ Stopping..."

    def _send_loop(self):
        try:
            results = []
            for idx, num in enumerate(self.numbers):
                if self._stop_flag:
                    self.status_label.text = f"⏹️ Stopped at {idx} / {len(self.numbers)}"
                    break

                self._pause_event.wait()  # Wait if paused

                send_whatsapp_messages_with_log([num], self.message, self.log_path, append=True)
                self.status_label.text = f"✅ Sent {idx + 1} / {len(self.numbers)}"
                time.sleep(1)

            if not self._stop_flag:
                self.status_label.text = f"✅ All messages sent!\nLog saved: {self.log_filename}"
        except Exception as e:
            self.status_label.text = f"❌ Error: {e}"
        finally:
            self.start_button.disabled = False
            self.pause_button.disabled = True
            self.resume_button.disabled = True
            self.stop_button.disabled = True

class RelayStackApp(App):
    def build(self):
        self.title = 'RelayStack - WhatsApp Sender'
        return WhatsAppUI()

if __name__ == '__main__':
    RelayStackApp().run()
