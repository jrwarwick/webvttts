#Assuming you have the cool fancy coqui docker image running, 
#just throw this on there, and then extract a VTT file,
#say, from MS Stream and you can process a voice over 
#replacement with this.
#might want to first:
"""
apt-get install vim.tiny ffmpeg sox openssh-client #git?
pip install webvtt ssml-builder
git clone https://github.com/jrwarwick/webvttts.git
#or curl -LO the webvttts.py script and vtt source
"""

import webvtt
from datetime import datetime, timedelta
import re
import subprocess
#going to need ffmpeg anyway, so might not need this
import soundfile 



def process_sentence(text,duration,index):
    #save off the text for possible rerender
    #attempt the render
    #check for duration, and attempt adjustment if it doesn't match.
    #get the first three and last two words of sentence for a name
    words = re.sub('[^a-z]','', text.strip().split(' ')[0].lower() )
    filename_base = str(index)+"_sentence_"+words
    with open(filename_base+".txt", 'w') as textf:
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
    print("\t\t\trendered duration mismatch: "+str(mismatch))
    #TODO: append silence of that amount.


# parse vtt, and generate time line that includes interval durations.
# as we go, also split and splice to create a list of sentences, with prorated durations.
current_sentence_index = 0
current_sentence_text  = ""
current_sentence_duration = timedelta()
since_t0 = timedelta()
print(str(since_t0)+"\n____\n")
for caption in webvtt.read('captions.vtt'):
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
        print("<sentence split!>"+str(sentence_conclusion.end()))
        current_sentence_text += " " + clean_caption[0:sentence_conclusion.end()]
        if len(clean_caption) > sentence_conclusion.end():
            print("  sentence fragment to deal with !! ")
            prorate = sentence_conclusion.end() / len(clean_caption) 
            print(str(prorate) + "x" +str(delta_t) + "=" + str(prorate*delta_t))
        else:
            current_sentence_duration += delta_t
        print("\t\t finished sentence: " + current_sentence_text)
        print("\t\t   duration: " + str(current_sentence_duration))
        process_sentence(current_sentence_text, current_sentence_duration, current_sentence_index) 
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

#outside the loop, attempt to merge/concat all the audio files together. Hopefully ready for insertion directly into video editor!
#probably attempt a transcode to m4a (ffmpeg)

# later/eventually: try and add some SSML support in, somehow.
