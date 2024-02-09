# webvttTS
(or maybe could have been called: "revoiceover" or "renarrotorious")
In a nutshell: 
```
video w/ narration/voiceover 
   |_---' 
STT -> webvtt -> sentences + rough timeline -> SSML -> TTS/wav -> ffmpeg concat + transcode -> replace original audio track in video.
                 '--a few manual edits /     '-- prosody <--'
                    since I don't              + silence injection
                    speak very eloquently     adjustments to fit timeline better
```
