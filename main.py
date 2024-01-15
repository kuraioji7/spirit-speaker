import easyocr
import numpy as np
import pyautogui
from audioplayer import AudioPlayer
from gtts import gTTS
from pynput import mouse, keyboard
import threading

reader = easyocr.Reader(['en'])
COMBINATION = {keyboard.Key.pause}
pressed_key = set()
start_x, start_y = 0, 0


def screenshot_ocr(start_x, start_y, end_x, end_y):
    width = abs(end_x - start_x)
    height = abs(end_y - start_y)
    x = min(start_x, end_x)
    y = min(start_y, end_y)
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    image = np.array(screenshot)
    ocr_texts = reader.readtext(image, detail=0)
    print(ocr_texts)
    tts_string = " ".join(ocr_texts)  # Combine the OCR texts into a single string
    return tts_string


def on_click(press_x, press_y, button, pressed):
    global start_x, start_y
    if pressed and button == mouse.Button.left:
        start_x, start_y = press_x, press_y
    if not pressed:
        tts_string = screenshot_ocr(start_x, start_y, press_x, press_y)
        threading.Thread(target=generate_and_play_audio, args=(tts_string,)).start()
        return False


def generate_and_play_audio(tts_string):
    tts = gTTS(text=tts_string, lang='en', slow=False)
    tts.save("output.mp3")
    AudioPlayer("output.mp3").play(block=True)


def keypress_listener():
    def on_press(key):
        pressed_key.add(key)
        if all(k in pressed_key for k in COMBINATION):
            with mouse.Listener(on_click=on_click) as mouse_listener:
                print("Click and drag mouse to take screenshot!")
                mouse_listener.join()
                pressed_key.remove(key)

    def on_release(key):
        if key == keyboard.Key.esc:
            return False
        try:
            pressed_key.remove(key)
        except KeyError:
            pass

    with keyboard.Listener(on_press=on_press, on_release=on_release) as key_listener:
        print("Keyboard listener running!")
        key_listener.join()


if __name__ == "__main__":
    threading.Thread(target=keypress_listener).start()
