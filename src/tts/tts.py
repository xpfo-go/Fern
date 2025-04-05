import time

from RealtimeTTS import TextToAudioStream, SystemEngine


class TTS:
    def __init__(self):
        self.engine = SystemEngine()
        self.stream = TextToAudioStream(
            self.engine,
            language='zh',
        )

        self.is_playing = False

    def play(self, text):
        if self.stream.is_playing():
            print('is playing, skip')
            return
        self.stream.feed(text)
        self.stream.play()

    def play_async(self, text):
        if self.stream.is_playing():
            print('is playing, skip')
            return
        self.stream.feed(text)
        # 不阻塞
        self.stream.play_async()


if __name__ == '__main__':
    import pyttsx3

    engine = pyttsx3.init()
    engine.say("你好你好")
    engine.runAndWait()

