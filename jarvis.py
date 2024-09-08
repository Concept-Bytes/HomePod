import assist
import time
import tools
from RealtimeSTT import AudioToTextRecorder
from multiprocessing import Queue

def run_voice_assistant(query_queue, response_queue):
    recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.4)
    hot_words = ["jarvis"]
    skip_hot_word_check = False
    print("Say something...")
    
    while True:
        current_text = recorder.text()
        print(current_text)
        if any(hot_word in current_text.lower() for hot_word in hot_words) or skip_hot_word_check:
            if current_text:
                print("User: " + current_text)
                query_queue.put(current_text)  # Send the query to the main loop
                recorder.stop()
                current_text = current_text + " " + time.strftime("%Y-%m-%d %H-%M-%S")
                response = assist.ask_question_memory(current_text)
                print(response)
                speech = response.split('#')[0]
                
                response_queue.put(speech)  # Send the response to the main loop
                
                done = assist.TTS(speech)
                # skip_hot_word_check = True if "?" in response else False
                if len(response.split('#')) > 1:
                    command = response.split('#')[1]
                    tools.parse_command(command)
                recorder.start()
