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

There isn't any fancy grammar parsing or anything going on here. It it will split into sentences strictly on the presence of the period/full-stop character.
Therefore, you will probably want to go through the vtt file and hand edit it a little so that the period character appears everywhere appropriate, which would be a good chance to clean up slight mis-transcriptions or homophonical confusions.

## TODO:
 - generate a demo vtt file and include it.
 - include some kind of test framework test case file. Probably "PyUnit" aka unittest since it is built in.
 - ellipsis handling/ignoring.
 - get some salt and PEP8 on this thing.
 - maybe start looking into recognizing where/when/what prosody modulations are appropriate, and put them into sentence processing method.
 - proper real "python oop"?
 - it kind of looks like coqui never got around to actual SSML prosody support. So maybe need think about that a bit, explore some options.
 - at some point it might be kind of cool to have the option of attempting to extract/generate the VTT file from a local on-disk video file in the first place. No idea how hard or work intensive that might be. It may be worth it to provide a "local-by-default" option but also include a TTS-as-a-service option.
 - if we are already doing a little bit of grammar stuff, we could possibly, maybe, very optionally, use some high-confidence grammar correction to clean up errors, and/or try a very constrained LLM "clean-up" assist or whatever. That could really mess with the timing, though so something to really thinkabout and play around with.
