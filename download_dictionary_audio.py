# usage: download_dictionary_audio.py examplary_word_list
# usage: download_dictionary_audio.py examplary_word_list --mode ogg
# usage: download_dictionary_audio.py examplary_word_list --path /directory/to/store/stuff

import sys

import os
import re
import argparse
import traceback
import urllib.request
import wget


dictionary_url = "https://www.dictionary.com/browse/"
prefix = "<audio preload"
sufix = "</audio>"

all_modes = ["mp3", "ogg"]

def download_and_save(url, download_directory):
    ### returns 1 for success, 0 for failure
    try:
        wget.download(url, out=download_directory)
        # TODO some way to make sure the file has been downloaded
        return 1
    except:
        return 0
    

def filename_wrapper(word, path, extension):
    return os.path.join(path, word+"."+extension)


def extract_urls(text):
    pre = "src="
    suf = " t"
    pattern = re.compile(pre+".*?"+suf)
    all_urls = [x.strip(pre).strip(suf).strip("\"") for x in pattern.findall(text)]
    urls = {}
    for mode in all_modes:
        urls[mode] = [x for x in all_urls if mode in x]
        if len(urls[mode]) == 0:
            urls.pop(mode)
        elif len(urls[mode]) == 1:
            urls[mode] = urls[mode][0]
        else:
            print(f"problems, problems, problems with urls,\n{urls[mode]}")
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

    non_default_mode = []
    not_in_dictionary = []
    no_audio = []
    all_went_well = []

    for word in all_words:
        word = word.strip()
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
        pattern = re.compile(prefix+".*?"+sufix)
        audio_lines = pattern.findall(html_content)

        if len(audio_lines) == 1:
            urls = extract_urls(audio_lines[0])
            if args.mode in urls:
                mode = args.mode
            else:
                mode = list(urls.keys())[0]
            success = download_and_save(urls[mode], filename_wrapper(word, args.path, mode))
            if success:
                if mode == args.mode:
                    all_went_well.append(word)
                else:
                    non_default_mode.append(word) 
            
        elif len(audio_lines) > 1:
            print(f"\nproblems, problems, too many audio_lines for word {word}")
            print(audio_lines)
        else:
            # no audio_lines have been found
            no_audio.append(word)
    
    assert (set(all_words) == set(not_in_dictionary+non_default_mode+no_audio+all_went_well)), print(f"Pocha, sth went wrong, \n{set(all_words)},\n{set(not_in_dictionary+non_default_mode+no_audio+all_went_well)}")

    print(f"the following words are not in the dictionary: {not_in_dictionary}")
    print(f"the following words exist in the dictionary but could not be downloaded:; {no_audio}")
    print(f"the following words were downloaded in the preferable format: {all_went_well}")
    print(f"the following words were downloaded in other supported formats: {non_default_mode}")
