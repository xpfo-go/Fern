import threading
from unittest import TestCase

from src.stt.audio_recorder2 import AudioToTextRecorder

# 存储录音的内容
recorder_content = ""
# 是否在记录文本状态
recoding_to_content = False

recorder = None
recorder_ready = threading.Event()


class TestAudioToTextRecorder(TestCase):
    def test_stt(self):
        def stt(stop_event):
            global recorder, recoding_to_content, recorder_content
            recorder_config = {
                'spinner': False,
                'use_microphone': False,
                'model': 'large-v2',
                'language': 'zh',
                'silero_sensitivity': 0.4,
                'webrtc_sensitivity': 2,
                'post_speech_silence_duration': 0.7,
                # 指定录制会话应持续的最短持续时间（以秒为单位），以确保有意义的音频捕获，防止录制时间过短或碎片化。
                'min_length_of_recording': 0.5,
                # 在认为录制完成之前，语音之后必须保持沉默的持续时间（以秒为单位）。这可确保演讲过程中的任何短暂停顿都不会过早结束录制。
                'post_speech_silence_duration': 1,
                # 指定一个录制会话结束和另一个录制会话开始之间应存在的最小时间间隔（以秒为单位），以防止快速连续录制。
                'min_gap_between_recordings': 1,
                'enable_realtime_transcription': True,
                # 指定音频块转录后的时间间隔（以秒为单位）。较低的值将导致更“实时”（频繁）的转录更新，但可能会增加计算负载
                'realtime_processing_pause': 0,
                'realtime_model_type': 'tiny',
                # 一个回调函数，每当实时听录中有更新时就会触发，并返回更高质量、稳定的文本作为其参数。
                # 'on_realtime_transcription_stabilized': text_detected,
                # 音频在正式录制之前缓冲的时间跨度（以秒为单位）。这有助于抵消语音活动检测中固有的延迟，确保不会遗漏任何初始音频
                'pre_recording_buffer_duration': 0.2,
    
                # 用于启动录制的唤醒词。可以以逗号分隔的字符串形式提供多个唤醒词。
                # 支持的唤醒词有：
                #   alexa、americano、blueberry、bumblebee、computer、grapefruits、grasshopper、hey google、hey siri、
                #   jarvis、ok google、picovoice、porcupine、terminator
                # 'wake_words': '嘿聪哥',
                # 'wakeword_backend': 'openwakeword',
                # 唤醒词检测的灵敏度级别（0 表示最不敏感，1 表示最敏感）
                # 'wake_words_sensitivity': 0.6,
                # 默认值=0 如果最初未检测到语音，则在系统切换到唤醒词激活之前，监控开始后的持续时间（以秒为单位）。如果设置为零，系统将立即使用唤醒词激活
                # 'wake_word_activation_delay': 0,
                # 默认值=5 识别唤醒词后的持续时间（以秒为单位）。如果在此窗口中未检测到后续语音活动，系统将转换回非活动状态，等待下一个唤醒词或语音激活。
                # 'wake_word_timeout': 5,
            }
    
            recorder = AudioToTextRecorder(**recorder_config)  # 假设每个客户端都有独立的录音器实例
    
            recorder_ready.set()
            try:
                print("start stt..")
                while not stop_event.is_set():
                    full_sentence = recorder.text()  # 假设这个方法读取客户端发送的音频并返回文本

                    # 再次检查stop_event状态
                    if stop_event.is_set():
                        break

                    print(f"【识别内容】：{full_sentence}")

                    # await llm_and_tts(client_id, full_sentence, client_type="text")
            except Exception as e:
                print(e)
            finally:
                print("stop stt..")

        stop_ctx = threading.Event()

        try:
            stt(stop_ctx)
        except Exception:
            stop_ctx.set()

    def test_stt2(self):
        recorder_config = {
            'spinner': False,
            # 'use_microphone': False,
            'model': 'large-v2',
            'language': 'zh',
            'silero_sensitivity': 0.4,
            'webrtc_sensitivity': 2,
            'post_speech_silence_duration': 0.7,
            # 指定录制会话应持续的最短持续时间（以秒为单位），以确保有意义的音频捕获，防止录制时间过短或碎片化。
            'min_length_of_recording': 0.5,
            # 在认为录制完成之前，语音之后必须保持沉默的持续时间（以秒为单位）。这可确保演讲过程中的任何短暂停顿都不会过早结束录制。
            'post_speech_silence_duration': 1,
            # 指定一个录制会话结束和另一个录制会话开始之间应存在的最小时间间隔（以秒为单位），以防止快速连续录制。
            'min_gap_between_recordings': 1,
            'enable_realtime_transcription': True,
            # 指定音频块转录后的时间间隔（以秒为单位）。较低的值将导致更“实时”（频繁）的转录更新，但可能会增加计算负载
            'realtime_processing_pause': 0,
            'realtime_model_type': 'tiny',
            # 一个回调函数，每当实时听录中有更新时就会触发，并返回更高质量、稳定的文本作为其参数。
            # 'on_realtime_transcription_stabilized': text_detected,
            # 音频在正式录制之前缓冲的时间跨度（以秒为单位）。这有助于抵消语音活动检测中固有的延迟，确保不会遗漏任何初始音频
            'pre_recording_buffer_duration': 0.2,

            # 用于启动录制的唤醒词。可以以逗号分隔的字符串形式提供多个唤醒词。
            # 支持的唤醒词有：
            #   alexa、americano、blueberry、bumblebee、computer、grapefruits、grasshopper、hey google、hey siri、
            #   jarvis、ok google、picovoice、porcupine、terminator
            'wake_words': 'hey fern',
            'wakeword_backend': 'openwakeword',
            # 唤醒词检测的灵敏度级别（0 表示最不敏感，1 表示最敏感）
            'wake_words_sensitivity': 0.6,
            # 默认值=0 如果最初未检测到语音，则在系统切换到唤醒词激活之前，监控开始后的持续时间（以秒为单位）。如果设置为零，系统将立即使用唤醒词激活
            'wake_word_activation_delay': 0,
            # 默认值=5 识别唤醒词后的持续时间（以秒为单位）。如果在此窗口中未检测到后续语音活动，系统将转换回非活动状态，等待下一个唤醒词或语音激活。
            'wake_word_timeout': 5,
        }

        def process_text(text):
            print(text)

        recorder = AudioToTextRecorder(**recorder_config)
        print('start')
        while True:
            recorder.text(process_text)



