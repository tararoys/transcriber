from talon import imgui, Module, speech_system, scope, actions, app, cron, ui

import sys, os, subprocess, time, math

# We keep command_history_size lines of history, but by default display only
# command_history_display of them.
mod = Module()
setting_command_history_size = mod.setting("command_history_size", int, default=50)
setting_command_history_display = mod.setting(
    "command_history_display", int, default=10
)

hist_more = False
history = []




transcribing = 0 

markdown_transcript = None
subtitles_transcript = None
linked_markdown_transcript = None

movie_url = ""

markdown_transcript_name = ""
subtitles_transcript_name = ""
linked_markdown_transcript_name = ""

subtitle_counter = 1
subtitle_start_time = 0

movie_begins_time = 0
movie_begins_time_milliseconds = 0

start_of_current_pause = 0

paused = 1
movie_pause_beginning_time = 0 
pause_begin_time_in_milliseconds = 0
total_milliseconds_of_pause = 0

penultimate_command_end_time = 0
penultimate_command_end_time_milliseconds = 0

last_command_end_time = 0
last_command_end_time_milliseconds = 0


##let me launch obs studio

class Pwd:
    dir_stack = []
    def __init__(self, dirname):
        self.dirname = dirname
        self.dirname = os.path.realpath(os.path.expanduser(self.dirname))
    def __enter__(self):
        Pwd.dir_stack.append(self.dirname)
        return self
    def __exit__(self,  type, value, traceback):
        Pwd.dir_stack.pop()
    def run(self, cmdline, **kwargs):
        return subprocess.Popen(cmdline, cwd=Pwd.dir_stack[-1], shell=True, **kwargs)

def create_markdown_transcript(name):
    global markdown_transcript
    this_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(this_dir, name + ".md")
    markdown_transcript = open(file_path,"a+") 


def close_markdown_transcript():
    global markdown_transcript
    markdown_transcript.close()

def parse_phrase(word_list):
    return " ".join(word.split("\\")[0] for word in word_list)

def print_markdown_transcript(phrase):
    print("-----------markdown transcript written:" + phrase + "----------")
    global markdown_transcript

    if "command" in scope.get("mode"):
        markdown_transcript.write(">" + phrase + "\n")
    elif "sleep" in scope.get("mode") :
        if phrase == "talon wake":
            markdown_transcript.write("\n\n\n>" + phrase + "\n")
        else:
            #markdown_transcript.write(phrase)
            markdown_transcript.write(taras_formatter.format(phrase)+".\n")
    if phrase=="talon sleep":
        markdown_transcript.write("\n\n\n")


def convertMillis(millis):
     miliseconds="{:03d}".format(math.floor(millis)%1000)
     seconds="{:02d}".format((math.floor(millis/1000))%60)
     minutes="{:02d}".format((math.floor(millis/(1000*60)))%60)
     hours = "{:02d}".format((math.floor(millis/(1000*60*60)))%24)



     return miliseconds, seconds, minutes, hours

def create_subtitles_transcript(name):
    global subtitles_transcript
    this_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(this_dir, name + ".md")
    subtitles_transcript = open(file_path,"a+") 
    print("SUUUUUBTITLES OPENNNN!!!")

def close_subtitles_transcript():
    global subtitles_transcript
    subtitles_transcript.close()

def print_subtitles_transcript(phrase):
    print("-----------subtitles transcript written:" + phrase + "----------")
    global subtitles_transcript 
    global last_command_end_time
    global last_command_end_time_milliseconds
    global subtitle_counter
    global movie_begins_time
    global penultimate_command_end_time
    global penultimate_command_end_time_milliseconds
    global total_milliseconds_of_pause

    penultimate_command_end_time = last_command_end_time
    penultimate_command_end_time_milliseconds = last_command_end_time_milliseconds
    
    current_time = time.time()
    last_command_end_time = time.gmtime(current_time) 
    last_command_end_time_milliseconds = current_time

    current_runtime_milliseconds = math.floor((last_command_end_time_milliseconds - movie_begins_time_milliseconds + total_milliseconds_of_pause)*1000) 
    
    #subtitles_transcript.write("\nMILLIseconds: " + str(current_runtime_milliseconds) + "\n")

    milliseconds, seconds, minutes, hours = convertMillis(current_runtime_milliseconds)


    if phrase != "let the movie begin":

        subtitles_transcript.write(f"{hours}:{minutes}:{seconds},{milliseconds}\n")

        if phrase != "terminate the movie":
            subtitles_transcript.write(taras_formatter.format(phrase))
            subtitles_transcript.write("\n\n" + str(subtitle_counter) + "\n")
            subtitle_counter = subtitle_counter + 1
            subtitles_transcript.write(f"{hours}:{minutes}:{seconds},{milliseconds} --> ")
        #subtitles_transcript.write("movie_begins_time-----" + str(movie_begins_time) + "\n")
        #subtitles_transcript.write("last_command_end_time-----" + str(last_command_end_time) + "\n")
    
        #subtitles_transcript.write(last_command_end_time)

def create_linked_markdown_transcript(name):
    global linked_markdown_transcript
    this_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(this_dir, name + ".md")
    linked_markdown_transcript = open(file_path,"a+") 
    print("Creating Linked Markdown Transcript!!!")

def close_linked_markdown_transcript():
    global linked_markdown_transcript
    linked_markdown_transcript.close()

def print_linked_markdown_transcript(phrase):
    print("-----------subtitles transcript written:" + phrase + "----------")
    global linked_markdown_transcript 
    global last_command_end_time
    global last_command_end_time_milliseconds
    global movie_begins_time
    global movie_url
    global penultimate_command_end_time
    global penultimate_command_end_time_milliseconds
    global total_milliseconds_of_pause
 

    #current_time = time.time()
    #last_command_end_time = time.gmtime(current_time) 
    #last_command_end_time_milliseconds = current_time

    current_runtime_milliseconds = math.floor((penultimate_command_end_time_milliseconds - movie_begins_time_milliseconds + total_milliseconds_of_pause )*1000) 
    
    #subtitles_transcript.write("\nMILLIseconds: " + str(current_runtime_milliseconds) + "\n")

    milliseconds, seconds, minutes, hours = convertMillis(current_runtime_milliseconds)

    current_runtime_seconds = math.floor(current_runtime_milliseconds/1000)

    #last_utterance_recording = actions.user.get_last_filename()
    linked_markdown_transcript.write(f"[{hours}:{minutes}:{seconds},{milliseconds} {taras_formatter.format(phrase)}]({movie_url}&t={current_runtime_seconds}s)\n")


replacement_words = {
    "i":"I",
    "i'm":"I'm",
    "i've":"I've",
    "i'll":"I'll",
    "i'd":"I'd"
}

def on_phrase(j):
    global history
    global transcribing
    global markdown_transcript_name
    global subtitles_transcript_name
    global linked_markdown_transcript_name

    print("--!!!-----wtf kind of data structure am I" + str(j))

    try:
        val = parse_phrase(getattr(j["parsed"], "_unmapped", j["phrase"]))
    except:
        val = parse_phrase(j["phrase"])

    if val != "":
        history.append(val)
        history = history[-setting_command_history_size.get() :]
        print("--------------peek into onphrase -----")
        print(dir(j))
        print(j.__class__)
        print(j)
        
        if transcribing == 1:

            create_markdown_transcript(markdown_transcript_name)
            print_markdown_transcript(val)
            close_markdown_transcript()

            if paused == 0:
                create_subtitles_transcript(subtitles_transcript_name)
                print_subtitles_transcript(val)
                close_subtitles_transcript()

                create_linked_markdown_transcript(linked_markdown_transcript_name)
                print_linked_markdown_transcript(val)
                close_linked_markdown_transcript()
    
    print("----------you made a sound----------")



sentence_ends = {
    ".": ".",
    "?": "?",
    "!": "!",
    # these are mapped with names since passing "\n" didn't work for reasons
    "new-paragraph": "\n\n",
    "new-line": "\n",
}

# dictionary of punctuation. no space before these.
punctuation = {
    ",": ",",
    ":": ":",
    ";": ";",
    "-": "-",
    "/": "/",
    "-": "-",
    ")": ")",
}

no_space_after_these = set("-/(")


class TarasFormat:
    def __init__(self):
        self.reset()
        self.paused = False
        ui.register("app_deactivate", lambda app: self.reset())
        ui.register("win_focus", lambda win: self.reset())

    def reset(self):
        self.caps = True
        self.space = False

    def pause(self, paused):
        self.paused = paused

    def format(self, text):
        if self.paused:
            return text

        result = ""
        first_word = True

        for word in text.split():
            if first_word == True:
                word = word.capitalize()
                first_word = False

            is_sentence_end = False
            is_punctuation = False

            if word in replacement_words:
                word = replacement_words[word]
            
            #sentence ending words
            if word in sentence_ends:
                word = sentence_ends[word]
                is_sentence_end = True
            #punctuation words.  Gonna igore this
            elif word in punctuation:
                word = punctuation[word]
                # do  nothing
                is_punctuation = True

            elif self.space:
                result += " "

            if self.caps:
                word = word.capitalize()

            result += word
            self.space = "\n" not in word and word[-1] not in no_space_after_these
            self.caps = is_sentence_end

        return result

taras_formatter = TarasFormat()

# todo: dynamic rect?
@imgui.open(y=0)
def gui(gui: imgui.GUI):
    global history
    
    text = (
        history[:] if hist_more else history[-setting_command_history_display.get() :]
    )
    for line in text:
        gui.text(line)


speech_system.register("phrase", on_phrase)


@mod.action_class
class Actions:
    def history_toggle():
        """Toggles viewing the history"""
        if gui.showing:
            gui.hide()
        else:
            gui.show()

    def history_enable():
        """Enables the history"""
        gui.show()

    def history_disable():
        """Disables the history"""
        gui.hide()

    def history_clear():
        """Clear the history"""
        global history
        history = []

    def history_more():
        """Show more history"""
        global hist_more
        hist_more = True

    def history_less():
        """Show less history"""
        global hist_more
        hist_more = False

    def transcript(name:str ="test_markdown_transcript"):
        """create transcript of what is going on"""
        global markdown_transcript_name
        markdown_transcript_name = name 
        create_markdown_transcript(name)

    def close_transcript():
        """create transcript of what is going on"""
        close_markdown_transcript()

    def subtitles_transcript(name:str ="test_subtitles_transcript"):
        """create a subtitles file of what is going on"""
        global movie_begins_time
        global subtitles_transcript
        global subtitle_counter
        global movie_begins_time_milliseconds
        global transcribing
        global subtitles_transcript_name
        subtitles_transcript_name = name 

        print("\nLET THE MOVIE BEGINN!!!\n\n")

        #starts obs studio automagically
        #with Pwd(r"C:\\Program Files\\obs-studio\\bin\\64bit\\") as shell:
            #shell.run(r'obs64.exe --startrecording --minimize-to-tray')

        create_subtitles_transcript(name)

        subtitle_counter = 1

        subtitles_transcript.write(str(subtitle_counter) + "\n")
        subtitle_counter = subtitle_counter + 1
        subtitles_transcript.write("00:00:00,000 --> ")
    
        close_subtitles_transcript()


    def close_sub_transcript():
        """create transcript of what is going on"""
        global last_command_end_time_milliseconds
        close_subtitles_transcript()
    
    def linked_markdown_transcript(name:str = "test_linked_markdown_transcript"):
        """creat a linked markdown transcript of what is going on"""
        global linked_markdown_transcript
        global linked_markdown_transcript_name 
        linked_markdown_transcript_name = name

        create_linked_markdown_transcript(name)
        #subtitles_transcript.write(f"{hours}:{minutes}:{seconds},{milliseconds}")
        close_linked_markdown_transcript()

    def close_linked_markdown_transcript():
        """create transcript of what is going on"""
        global last_command_end_time_milliseconds
        global transcribing 
        transcribing = 0
        close_linked_markdown_transcript()
    

    def transcribe_youtube_video():
        """create a transcript of a youtube video"""
        global markdown_transcript_name
        global subtitles_transcript_name
        global linked_markdown_transcript_name
        actions.user.subtitles_transcript(subtitles_transcript_name)
        actions.user.linked_markdown_transcript(linked_markdown_transcript_name)
        actions.user.transcript(markdown_transcript_name)
    

    def stop_transcription():
        """stops all transcribing"""
        actions.user.close_sub_transcript()
        actions.user.close_linked_markdown_transcript()
        actions.user.close_transcript()
        global transcribing
        global markdown_transcript
        global subtitles_transcript
        global linked_markdown_transcript
        
        global movie_url
        global markdown_transcript_name
        global subtitles_transcript_name
        global linked_markdown_transcript_name
        
        global subtitle_counter
        global subtitle_start_time
        global movie_begins_time
        global movie_begins_time_milliseconds
        global start_of_current_pause
        global paused
        global movie_pause_beginning_time 
        global pause_begin_time_in_milliseconds
        global total_milliseconds_of_pause
        global penultimate_command_end_time
        global penultimate_command_end_time_milliseconds

        global last_command_end_time
        global last_command_end_time_milliseconds
        
        transcribing = 0 
        markdown_transcript = None
        subtitles_transcript = None
        linked_markdown_transcript = None
        
        movie_url = ""
        markdown_transcript_name = ""
        subtitles_transcript_name = ""
        linked_markdown_transcript_name = ""
        
        subtitle_counter = 1
        subtitle_start_time = 0
        movie_begins_time = 0
        movie_begins_time_milliseconds = 0
        start_of_current_pause = 0
        paused = 1
        movie_pause_beginning_time = 0 
        pause_begin_time_in_milliseconds = 0
        total_milliseconds_of_pause = 0
        penultimate_command_end_time = 0
        penultimate_command_end_time_milliseconds = 0
        last_command_end_time = 0
        last_command_end_time_milliseconds = 0



    def toggle_transcription():
        """toggles transcription on and off"""
        global transcribing
        global paused
        global movie_pause_beginning_time
        global pause_begin_time_in_milliseconds
        global total_milliseconds_of_pause

        
        #actions.sleep('2000ms')
        if paused == 1:
            total_time_paused = time.time() - pause_begin_time_in_milliseconds
            print(pause_begin_time_in_milliseconds)
            print(total_time_paused)
            total_milliseconds_of_pause = total_milliseconds_of_pause + total_time_paused
            print(total_milliseconds_of_pause)
            paused = 0
            actions.user.play_pause()
            #actions.user.start_transcribing()
            actions.user.transcribe_youtube_video()
        else: 
            paused = 1
            actions.user.play_pause()
            movie_pause_beginning_time = time.gmtime(time.time())
            pause_begin_time_in_milliseconds = time.time()
            #actions.user.stop_transcription()
            # actions.user.finish_transcribing()


    def start_transcribing():
        """transcription currently begins, starting at zero"""
        global movie_begins_time
        global movie_begins_time_milliseconds
        global transcribing
        global movie_url 
        global markdown_transcript_name
        global subtitles_transcript_name
        global linked_markdown_transcript_name 
        global pause_begin_time_in_milliseconds   
        
        word = actions.user.time_format("%Y-%m-%d---%H-%M-%S")
        markdown_transcript_name = word + "-markdown"
        subtitles_transcript_name = word + "-subtitles"
        linked_markdown_transcript_name = word + "-linked"
        movie_url = actions.clip.text()
        transcribing = 1
        #time.time is in seconds since the epoch
        current_time = time.time()
        movie_begins_time = time.gmtime(current_time)
        movie_begins_time_milliseconds = time.time()
        pause_begin_time_in_milliseconds = movie_begins_time_milliseconds
        actions.user.toggle_transcription()

    def finish_transcribing(): 
        """considered the transcription over instead of merely paused, and dumps the current time counters"""
        transcribing = 0 
        

    def copy_url(): 
        """copy url to global variable"""
        global movie_url
        movie_url = actions.clip.text()

    def paste_url(): 
        """show url global variable"""
        global movie_url
        actions.insert(movie_url)







