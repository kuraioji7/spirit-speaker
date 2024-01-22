import easyocr
import numpy as np
import pyautogui
from pynput import keyboard
import threading
import pyttsx3


class ScreenSnipper:
    def __init__(self):
        self.start_x, self.start_y = 0, 0
        self.button_pressed = False
        self.reader = easyocr.Reader(['en'])
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', self.voices[1].id)

    def screenshot_ocr(self, end_x, end_y):
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)
        x = min(self.start_x, end_x)
        y = min(self.start_y, end_y)
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        image = np.array(screenshot)
        ocr_texts = self.reader.readtext(image, detail=0)
        tts_string = " ".join(ocr_texts)
        print("Text:", tts_string)
        return tts_string

    def generate_and_play_audio(self, tts_string):
        if self.engine._inLoop:
            self.engine.endLoop()
        self.engine.say(text=tts_string)
        self.engine.runAndWait()

    def keypress_listener(self):
        def on_press(key):
            if key == keyboard.Key.pause:
                if not self.button_pressed:
                    print("Move your mouse to next position and press the button again")
                    self.start_x, self.start_y = pyautogui.position()
                    self.button_pressed = True
                else:
                    end_x, end_y = pyautogui.position()
                    if abs(self.start_x - end_x) < 50:
                        print("Region too small, please try again and select region with bigger area")
                    else:
                        tts_string = self.screenshot_ocr(end_x, end_y)
                        threading.Thread(target=self.generate_and_play_audio, args=(tts_string,)).start()
                    self.button_pressed = False

        def on_release(_):
            pass

        with keyboard.Listener(on_press=on_press, on_release=on_release) as key_listener:
            print("Keyboard listener running!")
            key_listener.join()


if __name__ == "__main__":
    screen_snipper = ScreenSnipper()
    threading.Thread(target=screen_snipper.keypress_listener).start()
