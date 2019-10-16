# usage: download_dictionary_audio.py examplary_word_list
# usage: download_dictionary_audio.py examplary_word_list --mode ogg
# usage: download_dictionary_audio.py examplary_word_list --path /directory/to/store/stuff

import os
import re
import argparse
import traceback
import urllib.request
import wget


# variables needed to work with dictionary.com
dictionary_url = "https://www.dictionary.com/browse/"
word_pre = "css-1jzk4d9 e1rg2mtf8\">"
word_suf = "</h"
audio_pre = "<audio preload"
audio_suf = "</audio>"
pos_pre = "class=\"luna-pos\">"
pos_suf = "</span>"
pattern = re.compile(word_pre+"(.*?)"+word_suf+".*?"+audio_pre+"(.*?)"+audio_suf+".*?"+pos_pre+"(.*?)"+pos_suf)

all_modes = ["mp3", "ogg"]

def download_and_save(url, download_directory):
    ### returns 1 for success, 0 for failure
    try:
        wget.download(url, out=download_directory, bar=wget.bar_thermometer)
        # TODO some way to make sure the file has been downloaded
        return 1
    except:
        return 0
    

def filename_wrapper(word, pos, path, extension):
    return os.path.join(path, word+"-"+pos+"."+extension)


def extract_urls(list_of_fragments):
    pre_audio = "src="
    suf_audio = " t"
    pattern = re.compile(pre_audio+".*?"+suf_audio)
    urls = {}

    for html_fragment in list_of_fragments:
        # get part of speech
        pos = html_fragment[2].split(' ')[0].strip(',')
        urls[pos] = {}
        
        # get urls
        all_urls = [x.strip(pre_audio).strip(suf_audio).strip("\"") for x in pattern.findall(html_fragment[1])]
        
        for mode in all_modes:
           mode_urls = [x for x in all_urls if mode in x]
           if len(mode_urls) == 1:
               urls[pos][mode] = mode_urls[0]
           elif len(mode_urls) > 1:
               print(f"problems, problems, for debugging, mode_urls is: {mode_urls}")
    return urls


if __name__=="__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("word_list", type=str, help="text file with each word in seperate line")
    parser.add_argument("--mode", type=str, default="mp3", help="preferable type of downloaded files, currently only mp3 and ogg are supported, default is mp3")
    parser.add_argument("--path", type=str, default=".", help="dictionary where files shall be saved, must exist, default is the directory containing the script")
    
    args = parser.parse_args()
    
    supplementary_modes = list(all_modes)
    supplementary_modes.remove(args.mode)
    
    # read words from file
    with open(args.word_list, "r") as f:
        all_words = f.readlines()
    all_words = [w.strip().lower() for w in all_words]

    downloaded = []
    non_exact = []
    not_in_dictionary = []
    no_audio = []

    for word in all_words:
        # get the dictionary.com HTML
        try:
            # retreive HTML
            responose = urllib.request.urlopen(dictionary_url+word)
            html_content = responose.read().decode('utf-8')
        except:
            traceback.print_exc()
            not_in_dictionary.append(word)
            continue
       
        # parse html
        audio_occurences = pattern.findall(html_content)
        
        word_was_downloaded_sumator = 0
        if len(audio_occurences) >= 1:
            # sometimes the word returned by dictionary.com is not the exact one
            exact = True
            processed_word = audio_occurences[0][0].lower()
            if processed_word != word:
                exact = False
            
            urls = extract_urls(audio_occurences)
            for pos in urls.keys():
                if args.mode in urls[pos]:
                    mode = args.mode
                else:
                    mode = list(urls[pos].keys())[0]
                success = download_and_save(urls[pos][mode], filename_wrapper(processed_word, pos, args.path, mode))
                word_was_downloaded_sumator += success
            if word_was_downloaded_sumator:
                downloaded.append(word)
                if not exact:
                    non_exact.append((word, processed_word))
            else:
                no_audio.append(word)
        else:
            # no audio_lines have been found
            no_audio.append(word)
    
    print('\n')  # due to wget progess bar
    assert (set(all_words) == set(not_in_dictionary+no_audio+downloaded)), print(f"well, well, sth went wrong, \n{set(all_words)},\n{set(not_in_dictionary+no_audio+downloaded)}")
    
    if len(not_in_dictionary) > 0:
        print(f"the following words are not in the dictionary: {not_in_dictionary}")
    if len(no_audio) > 0:    
        print(f"the following words exist in the dictionary but could not be downloaded: {no_audio}")
    if len(non_exact) > 0:
        print(f"instead of some words which were not in the dictionary, similar words have been downloaded: {non_exact}")
