#Assuming you have the cool fancy coqui docker image running, 
#just throw this on there, and then extract a VTT file,
#say, from MS Stream and you can process a voice over 
#replacement with this.
#might want to first:
"""
apt-get -y install vim.tiny ffmpeg sox openssh-client git
pip install --upgrade pip
pip install webvtt-py ssml-builder
git clone https://github.com/jrwarwick/webvttts.git
#or curl -LO the webvttts.py script and vtt source
"""

import webvtt
from datetime import datetime, timedelta
import re
import sys
import subprocess
#going to need ffmpeg anyway, so might not need this
import soundfile 
from ssml_builder.core import Speech

speech = Speech()

def process_sentence(mode, text, duration, index):
    #save off the text for possible rerender
    #attempt the render
    #check for duration, and attempt adjustment if it doesn't match.
    #get the first three and last two words of sentence for a name
    words = re.sub('[^a-z ]','', text.strip().lower()).split(' ')[0:2]
    speech = Speech()
    speech.sub(value="CalGEM", alias="Cal gem") #TODO: find substitution notes in the vtt and/or in config files
    filename_base = str(index)+"_sentence_"+"_".join(words)
    with open(filename_base+".txt", 'w') as textf:
        if mode == "ssml":
            if " does " in text:
                [before,after] = text.split(" does ", 1)
                speech.add_text(before)
                speech.emphasis(" does ", "strong")
                speech.add_text(after)
            else:
                speech.prosody(value=text,rate="110%")
            textf.write(speech.speak()+"\n")
        else:
            textf.write(text+"\n")
    outfile_path ="/tmp/"+filename_base+".wav"
    #254 360
    subprocess.run(["/usr/local/bin/tts", "--text", text, "--model_name", "tts_models/en/vctk/vits", "--speaker_idx", "p360", "--out_path", outfile_path])
    #tts.tts_to_file(text=text, file_path="/usr/tmp/"+filename_base+".wav", language="en", file_path="output.wav")
    ##opusenc --title "bry Amusing Announcment" --artist "bry" --album "BPITS Audio" --genre "Informational" --date $(date "+%Y-%m-%d") /tmp/amusement.wav /media/audio/amusement.opus
    subprocess.run(["ls","-lFth",outfile_path])
    sndf = soundfile.SoundFile(outfile_path)
    print('samples = {}'.format(sndf.frames))
    print('sample rate = {}'.format(sndf.samplerate))
    print('seconds = {}'.format(sndf.frames / sndf.samplerate))
    actual_duration = timedelta(seconds=sndf.frames / sndf.samplerate)
    mismatch = duration - actual_duration
    print("\t\t\texpected duration: "+str(duration))
    print("\t\t\trendered duration: "+str(actual_duration))
    print("\t\t\trendered duration mismatch: "+str(mismatch))
    #TODO: append silence of that amount, if positive. Try a prosody adjustment and reprocess if too long.


# parse vtt, and generate time line that includes interval durations.
# as we go, also split and splice to create a list of sentences, with prorated durations.
vtt_filename = sys.argv[1] if len(sys.argv) > 1 else 'captions.vtt'
current_sentence_index = 0
current_sentence_text  = ""
current_sentence_duration = timedelta()
since_t0 = timedelta()
print(str(since_t0)+"\n____\n")
for caption in webvtt.read(vtt_filename):
    start_stamp = datetime.strptime(caption.start, "%H:%M:%S.%f")
    end_stamp   = datetime.strptime(caption.end, "%H:%M:%S.%f")
    delta_t = end_stamp - start_stamp
    since_t0 = since_t0 + delta_t
    print(str(since_t0) + "  " + caption.start + "-" + caption.end +"\tDuration: "+ str(delta_t))
    clean_caption = " ".join(caption.text.split()).strip()
    #TODO: other common substitutions and tunings for TTS prep.
    print("\t"+clean_caption)
    sentence_conclusion = re.search('[.!?]+',clean_caption)
    if sentence_conclusion:
        print("--sentence split!--"+str(sentence_conclusion.end()))
        current_sentence_text += " " + clean_caption[0:sentence_conclusion.end()]
        if len(clean_caption) > sentence_conclusion.end():
            print("  sentence fragment to deal with !! ")
            prorate = sentence_conclusion.end() / len(clean_caption) 
            print(str(prorate) + "x" +str(delta_t) + "=" + str(prorate*delta_t))
        else:
            current_sentence_duration += delta_t
        print("\t\t finished sentence: " + current_sentence_text)
        print("\t\t   duration: " + str(current_sentence_duration))
        #TODO: eventually just stopping at plaintext should be an option, and parameterized.
        process_sentence("ssml", current_sentence_text, current_sentence_duration, current_sentence_index)
        #reset
        current_sentence_text = ""
        current_sentence_duration = timedelta()
        current_sentence_index += 1
    else:
        current_sentence_text += " " + clean_caption
        current_sentence_duration += delta_t
        print("\t\t running sentence duration: "+str(current_sentence_duration))

# merge and/or break the caption/segemnts up into sentences, accumulating the deltas into a sentence duration. Attempt to roughly prorate the durations when sentence ends mid segment.
# now feed each sentence through a TTS engine. After generation, check the length; it might need silence insertion or it might need trimming or speed-up (SSML? SOX no-pitch-bend-speedup?)

#outside the primary loop, attempt to merge/concat all the rendered audio files together. Hopefully ready for insertion directly into video editor!
#probably attempt a transcode to m4a (ffmpeg); also an option per segment:    -filter:a "atempo=1.7"

# later/eventually: try and add some SSML support in, somehow.
