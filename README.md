# dictionary-audio-downloader
Download pronunciation audio from dictionary to include in your Anki decks or elsewhere.

### The so-called installation
You'll need python3 and the following packages: python-wget, traceback, urllib.request and argparse. 

### Running

`python download_dictionary_audio.py examplary_word_list`

downloads audio for words present in the text file called `examplary_word_list`. Each word in the file should be in a separate line.

`python download_dictionary_audio.py examplary_word_list --mode ogg --path /directory/to/store/stuff`

The option `--mode` allows to specify the preferable format of the downloaded files. Currently mp3 and ogg are supported and mp3 is default. In case the audio in the preferable format is not available, the audio in the other format will be downloaded.

`--path` allows to specify in which directory the downloaded files should be saved. The dafault directory is the directory from which the script is run.


In case there is more than one spelling available for a word, which is common when words can be used as a verb or noun (ex. muse), all the audios will be downloaded.

The audio files are named accordingly: word-pos.extension, where pos is the part of speech, ex. muse-verb.mp3.
