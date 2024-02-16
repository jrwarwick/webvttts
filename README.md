# webvttTS
(or maybe could have been called: "revoiceover" or "renarrotorious")
In a nutshell: 
```
video w/ narration/voiceover               <-- replace original audio track in video (refined VTT, too) ----------___
   |_---'                                                                                                            \
 STT -> webvtt -> sentences + rough timeline -> SSML -> TTS/wav -> ffmpeg tempo filter -> ffmpeg concat + transcode ->' 
                  '--a few manual edits /     '-- prosody <--'         (if no prosody)
                     since I don't              + silence injection
                     speak very eloquently     adjustments to fit timeline better
                     (also maybe phonetic
                      hacks)
                     (also maybe language
                      translations)
```

There isn't any fancy grammar parsing or anything going on here. It it will split into sentences strictly on the presence of the period/full-stop character.
Therefore, you will probably want to go through the vtt file and hand edit it a little so that the period character appears everywhere appropriate, which would be a good chance to clean up slight mis-transcriptions or homophonical confusions.


## Quickstart 
from within the coqui docker image:
```
apt-get update ; pt-get install coreutils vim.tiny ffmpeg sox openssh-client git
pip install --upgrade pip ; pip install webvtt-py ssml-builder
git clone https://github.com/jrwarwick/webvttts.git
cd webvttts/ ; ls
# cat > demo_captions.vtt
# python3 webvttts.py demo_captions.vtt

printf "file '%s'\n" /tmp/*.wav | sort -V > sentence_audio_files_sequence.txt 
ffmpeg -f concat -safe 0 -i sentence_audio_files_sequence.txt -c copy voiceover.wav && ffmpeg -i voiceover.wav -c:a aac -b:a 192k voiceover.m4a

#optional bonus stuff
for F in $( ls -1rt *.txt ) ; do cat $F >> all_sentences.txt ; done
pr --double-space --omit-header all_sentences.txt | fmt --width=85 > readable_script.txt

```


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
 - maybe just wrap the quickstart stuff into a dockerfile and a launch.sh
