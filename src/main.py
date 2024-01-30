import os
import queue
import threading
import time
import keyboard
import yaml
from pynput.keyboard import Controller
from transcription import create_local_model, record_and_transcribe
from status_window import StatusWindow
from settings import Settings

class ResultThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ResultThread, self).__init__(*args, **kwargs)
        self.result = None
        self.stop_transcription = False

    def run(self):
        self.result = self._target(*self._args, cancel_flag=lambda: self.stop_transcription, **self._kwargs)

    def stop(self):
        self.stop_transcription = True

def clear_status_queue():
    while not status_queue.empty():
        try:
            status_queue.get_nowait()
        except queue.Empty:
            break

def on_shortcut():
    global status_queue, local_model
    clear_status_queue()

    status_queue.put(('recording', 'Recording...'))
    recording_thread = ResultThread(target=record_and_transcribe, 
                                    args=(status_queue,),
                                    kwargs={'config': config,
                                            'local_model': local_model if local_model and not config['model_options']['use_api'] else None},)
    
    if not config['misc']['hide_status_window']:
        status_window = StatusWindow(status_queue)
        status_window.recording_thread = recording_thread
        status_window.start()
    
    recording_thread.start()
    recording_thread.join()
    
    if not config['misc']['hide_status_window']:
        if status_window.is_alive():
            status_queue.put(('cancel', ''))

    transcribed_text = recording_thread.result

    if transcribed_text:
        typewrite(transcribed_text, interval=config['post_processing']['writing_key_press_delay'])

def format_keystrokes(key_string):
    return '+'.join(word.capitalize() for word in key_string.split('+'))

def typewrite(text, interval):
    for letter in text:
        pyinput_keyboard.press(letter)
        pyinput_keyboard.release(letter)
        time.sleep(interval)


# Main script

default_config_path = os.path.join('src', 'default_config.yaml')
user_config_path = os.path.join('src', 'config.yaml')
settings = Settings(default_config_path, user_config_path)
config = settings.config

model_method = 'OpenAI\'s API' if config['model_options']['use_api'] else 'a local model'
print(f'Script activated. Whisper is set to run using {model_method}. To change this, modify the "use_api" value in the src\\config.yaml file.')

# Set up local model if needed
local_model = None
if not config['model_options']['use_api']:
    print('Creating local model...')
    local_model = create_local_model(config)
    print('Local model created.')

recording_mode = settings.config['recording_options']['recording_mode']
activation_key = settings.config['recording_options']['activation_key']
print(f'WhisperWriter is set to record using {recording_mode}. To change this, modify the "recording_mode" value in the src\\config.yaml file.')
print(f'The activation key combo is set to {format_keystrokes(activation_key)}.', end='')
if recording_mode == 'voice_activity_detection':
    print(' When it is pressed, recording will start, and will stop when you stop speaking.')
elif recording_mode == 'press_to_toggle':
    print(' When it is pressed, recording will start, and will stop when you press the key combo again.')
elif recording_mode == 'hold_to_record':
    print(' When it is pressed, recording will start, and will stop when you release the key combo.')
print('Press Ctrl+C on the terminal window to quit.')

# Set up status window and keyboard listener
status_queue = queue.Queue()
pyinput_keyboard = Controller()
keyboard.add_hotkey(activation_key, on_shortcut)
try:
    keyboard.wait()  # Keep the script running to listen for the shortcut
except KeyboardInterrupt:
    print('\nExiting the script...')
    os.system('exit')
