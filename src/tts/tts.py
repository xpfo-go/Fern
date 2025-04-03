from RealtimeTTS import TextToAudioStream, SystemEngine


class TTS:
    def __init__(self):
        engine = SystemEngine()
        self.stream = TextToAudioStream(
            engine,
            on_audio_stream_start=self._audio_stream_start_callback,
            on_audio_stream_stop=self._audio_stream_end_callback,
            language='zh-cn',
        )

        self.is_playing = False

    def _audio_stream_start_callback(self):
        self.is_playing = True

    def _audio_stream_end_callback(self):
        self.is_playing = False

    def play(self, text):
        if self.is_playing:
            print('is playing, skip')
            return
        self.stream.feed(text)
        self.stream.play()

    def play_async(self, text):
        if self.is_playing:
            print('is playing, skip')
            return
        self.stream.feed(text)
        # 不阻塞
        self.stream.play_async()



