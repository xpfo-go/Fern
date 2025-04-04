import os

from RealtimeSTT import AudioToTextRecorder


class STT:
    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        wake_model_path = os.path.join(
            current_dir, "hey_fei_lin.onnx"
        )
        recorder_config = {
            'spinner': False,
            # 'use_microphone': False,  # 使用麦克风
            'model': 'large-v2',
            'language': 'zh',
            'silero_sensitivity': 0.4,
            'webrtc_sensitivity': 2,
            # 在认为录制完成之前，语音之后必须保持沉默的持续时间（以秒为单位）。这可确保演讲过程中的任何短暂停顿都不会过早结束录制。
            'post_speech_silence_duration': 0.7,
            # 指定录制会话应持续的最短持续时间（以秒为单位），以确保有意义的音频捕获，防止录制时间过短或碎片化。
            'min_length_of_recording': 0.5,
            # 指定一个录制会话结束和另一个录制会话开始之间应存在的最小时间间隔（以秒为单位），以防止快速连续录制。
            'min_gap_between_recordings': 1,
            'enable_realtime_transcription': True,
            'use_main_model_for_realtime': True,  # confirm
            'compute_type': 'float32',

            # 指定音频块转录后的时间间隔（以秒为单位）。较低的值将导致更“实时”（频繁）的转录更新，但可能会增加计算负载
            'realtime_processing_pause': 0,
            'realtime_model_type': 'tiny',
            # 一个回调函数，每当实时听录中有更新时就会触发，并返回更高质量、稳定的文本作为其参数。
            # 'on_realtime_transcription_stabilized': text_detected,
            # 音频在正式录制之前缓冲的时间跨度（以秒为单位）。这有助于抵消语音活动检测中固有的延迟，确保不会遗漏任何初始音频
            'pre_recording_buffer_duration': 0.2,
            # 用于启动录制的唤醒词。可以以逗号分隔的字符串形式提供多个唤醒词。
            # 支持的唤醒词有：
            'wakeword_backend': 'openwakeword',
            'openwakeword_model_paths': wake_model_path,
            # 唤醒词检测的灵敏度级别（0 表示最不敏感，1 表示最敏感）
            'wake_words_sensitivity': 0.1,
            # 默认值=0 如果最初未检测到语音，则在系统切换到唤醒词激活之前，监控开始后的持续时间（以秒为单位）。如果设置为零，系统将立即使用唤醒词激活
            'wake_word_activation_delay': 0,
            # 默认值=5 识别唤醒词后的持续时间（以秒为单位）。如果在此窗口中未检测到后续语音活动，系统将转换回非活动状态，等待下一个唤醒词或语音激活。
            'wake_word_timeout': 5,
            'debug_mode': False,

            'on_recording_start': self._recording_start_callback,
            'on_wakeword_detected': self._on_wakeword_callback,
        }

        self.recorder = AudioToTextRecorder(**recorder_config)

    def _recording_start_callback(self):
        print('开始录制')

    def _on_wakeword_callback(self):
        print('监听。。。')

