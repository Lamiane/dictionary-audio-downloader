# usage: download_dictionary_audio.py word_list words.txt
# usage: download_dictionary_audio.py word_list words.txt --mode ogg
# usage: download_dictionary_audio.py word_list words.txt --path /dictionary/to/store/stuff


import os
import argparse
import traceback
import urllib2
import wget


dictionary_url = "https://www.dictionary.com/browse/"


def download_and_save(url, download_directory):
    ### returns 1 for success, 0 for failure
    try:
        wget.download(url, out=download_directory)
        # TODO some way to make sure the file has been downloaded
        return 1
    except:
        return 0
    

def filename_wrapper(word, path):
    return os.path.join([path, word+"."+mode])


if __name__=="__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("word_list", type=str, help="text file with each word in seperate line")
    parser.add_argument("--mode", type=str, default="mp3", help="preferable type of downloaded files, currently only mp3 and ogg are supported, default is mp3")
    parser.add_argument("--path", type=str, default=".", help="dictionary where files shall be saved, must exist, default is the directory containing the script")
    
    args = parser.parse_args()

    supplementary_modes = ["mp3", "ogg"]
    supplementary_modes.remove(args.mode)
    
    # read words from file
    with open(args.word_list, "r") as f:
        all_words = f.readlines()

    print("all_words", all_words)

    non_default_mode = []
    not_in_dictionary = []
    no_audio = []
    all_went_well = []

    for word in all_words:
        word = word.strip()
        # get the dictionary.com HTML
        try:
            # retreive HTML
            responose = urllib2.urlopen(dictionary_url+word)
            html_content = responose.read()
        except:
            traceback.print_exc()
            not_in_dictionary.append(word)
            continue
        
        # parse HTML
        audio_lines = []
        for line in html_content:
            if args.mode in line:
                print(line)  # TODO remove this debug
                audio_lines.add(line)
        
        if len(audio_lines) == 1:
            success = download_and_save(filename_wrapper(audio_lines[0], args.path))
            if success:
                all_went_well.add(word)
                continue
            
        elif len(audio_lines) > 1:
            print("problems, problems, too many audio_lines")
            print(audio_lines)
            continue
        
        else:
            # no audio_lines have been found
            for m in supplementary_modes:
                for line in html_content:
                    if m in line:
                        audio_lines.add(line)
        
            if len(audio_lines) < 1:
                no_audio.add(word)
            else:
                success = download_and_save(filename_wrapper(audio_lines, args.path))
                if success:
                    non_default_mode.add(word)
                else:
                    no_audio.add(word)
        
    assert (set(all_words) == set(not_in_dictionary+non_default_mode+no_audio+all_went_well)), print(f"Pocha, sth went wrong, \n{set(all_words)},\n{set(not_in_dictionary+non_default_mode+no_audio+all_went_well)}")

    print(f"the following words are not in the dictionary: {not_in_dictionary}")
    print(f"the following words exist in the dictionary but could not be downloaded:; {no_audio}")
    print(f"the following words were downloaded in the preferable format: {all_went_well}")
    print(f"the following words were downloaded in other supported formats: {non_default_mode}")
