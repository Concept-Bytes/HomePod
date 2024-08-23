import assist
import time
import tools
from RealtimeSTT import AudioToTextRecorder

def run_voice_assistant():
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
                recorder.stop()
                current_text = current_text + " " + time.strftime("%Y-%m-%d %H-%M-%S")
                response = assist.ask_question_memory(current_text)
                print(response)
                speech = response.split('#')[0]
                
                # Write response to response.txt
                with open("response.txt", "w") as file:
                    file.write(speech)
                
                done = assist.TTS(speech)
                skip_hot_word_check = True if "?" in response else False
                if len(response.split('#')) > 1:
                    command = response.split('#')[1]
                    tools.parse_command(command)
                recorder.start()

if __name__ == '__main__':
    run_voice_assistant()
