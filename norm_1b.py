#!/usr/local/bin/python
# -*- coding:utf-8 -*-

#############################################
# This script is solely dedicated to normalize 1-billion-word-benchmarking corpus
# https://github.com/ciprian-chelba/1-billion-word-language-modeling-benchmark

import re, os, json, pdb, bz2, subprocess, num2words

def run(command):
    '''for retrieving outpus from executed shell commands'''
    output = subprocess.check_output(command, shell=True)
    return output

input_folder        = '/home/RT11/khassan/corpora/1-billion-word-language-modeling-benchmark-r13output/training-monolingual.tokenized.shuffled'   # input folder
output_folder       = '/home/RT11/khassan/corpora/1-billion-word-language-modeling-benchmark-r13output/training-monolingual.tokenized.shuffled.normalized'   # output folder
#output_folder_docs  = os.path.dirname(wiki_folder)+'/cleanWiki_docs.bz2'    # output folder
min_doc_size        = 0        # minimum number of tokens in document
min_sent_size       = 0         # minimum number of tokens in sentence

def cleanText(text, acronymFile):
    #Convert text into lowercase
    text = text.lower()
    text = ' '+text;    # insert space in the begining, because text may start with acronyms, and acronym search assumes whitespace symbol in front of acronyms
    text = re.sub('[\s]',' ',text)   # replace all \s=[ \t\n\r\f\v] symbols with single space ' '
    #Load dictionary of acronyms and abbrs
    if not os.path.isfile(acronymFile):
        pass
        #print('***Acronym/abbreviation file does not exist! Acronyms and abbrs will not be expanded! (In normalize.py)***')
    else:
        temp_reader = open(acronymFile,'r')
        abbr_list   = json.load(temp_reader)
        temp_reader.close()
        #Expand abbreviations and acronyms
        for abbr in abbr_list:
            if abbr in text:
                text = text.replace(abbr,abbr_list[abbr])

    #Protect not identified (not in our list) abbrs and acronynms, by replacing periods with underscore, A.B.C.D.E.F .=> A_B_C_D_E_F_
    #text    = re.sub('_',' ',text)  # remove underscores before Abbr/Acronym protection
    #text    = re.sub(' [a-z]\. ',' ',text)  # Remove single characters with period, Ex: 'M. Jordan' =>' Jordan'
    #text    = re.sub(' [a-z]\. ',' ',text)  # one more time for cases: 'A. M. Jordan' =>' Jordan'
    #text    = re.sub(' [a-z]\.\'s ',' ',text)                   # Ex: ' T.'s '=>' '
    #text    = re.sub('([a-z])\.([a-z])','\g<1>_\g<2>',text)     # Ex: A.B. => A_B., A.B.C. => A_B.C., A.B.C.D. => A_B.C_D., A.B.C.D.E. => A_B.C_D.E.,
    #text    = re.sub('_([a-z])\.','_\g<1>_',text)               # Ex: (after preprocessing of previous line) A_B. => A_B_, A_B.C. => A_B_C., A_B.C_D. => A_B_C_D_, A_B.C_D.E. => A_B_C_D_E, will cover all even number of letter abbs
    #text    = re.sub('_([a-z])\.','_\g<1>_',text)               # Ex: (after preprocessing of two previous lines) A_B_C. => A_B_C_, A_B_C_D_E. => A_B_C_D_E_, will cover all odd number of letters abbs

    #Convert roman numbers
    #text    = re.sub(' ii ',' 2 ',text)
    #text    = re.sub(' iii ',' 3 ',text)
    #text    = re.sub(' iv ',' 4 ',text)
    #text    = re.sub(' vi ',' 6 ',text)
    #text    = re.sub(' vii ',' 7 ',text)
    #text    = re.sub(' viii ',' 8 ',text)
    #text    = re.sub(' ix ',' 9 ',text)

    #Remove phrases enclosed in the brackers, eg: (word1 word2), <word3 word4> and etc. Non-greedy approach
    text    = re.sub('(\[.*?\]|\(.*?\)|\{.*?\}|<.*?>)','',text)
    text    = re.sub(' +',' ',text)     #remove multiple spaces

    #Seperate floating numbers by 'point', eg: 1.4 => 1 point 4, .5  => 0 point 5
    text    = re.sub('(\d)\.(\d)','\g<1> point \g<2>',text)
    text    = re.sub('( +)\.(\d)',' 0 point \g<2>',text)
    #OR protect decimal points
    #text    = re.sub('(\d)\.(\d)','\g<1>_\g<2>',text)
    #OR remove decimal points
    #text    = re.sub('(\d+)\.(\d+)','',text)

    #Join thousands, eg: 1,000,000 => 1000000
    text    = re.sub('(\d),(\d)','\g<1>\g<2>',text)

    #Put space between decimal and non decimal, eg: 50%=>5 %, 4am=>4 am, 100$=>100 $, $1=>1 $,  #5=># 5, 0s => 0 s $
    text    = re.sub('(\d)(\D)','\g<1> \g<2>',text)
    text    = re.sub('(\$)(\d+)','\g<2> \g<1>',text)
    text    = re.sub('([^\s\d]+)(\d)','\g<1> \g<2>',text)
    text    = re.sub(' +',' ',text)     #remove multiple spaces

    #Replace symbols, eg: 2 $=>2 dollars,1 $=>1 dollars, 5 %=>5 percents, G&G =>G and G,  etc.
    text    = re.sub('\$','dollars', text)
    #text    = re.sub('','euros', text)
    #text    = re.sub('','pounds', text)
    #text    = re.sub('','yuans', text)
    text    = re.sub('%','percents', text)
    #text    = re.sub(' +',' ',text)            #remove multiple spaces
    #text    = re.sub(' &amp; ','and', text)     #TDT2 uses '&AMP;' symbol for ampersand
    text    = re.sub(' & ',' and ', text)
    #text    = re.sub(' +',' ',text)             #remove multiple spaces

    #Math equations, eg: 4 + 5 = 9, 4 plus 5 equals 9, 1/1 => 1 over 1
    #text    = re.sub('(\d) *\+ *(\d)','\g<1> plus \g<2>', text)
    #text    = re.sub('(\d) *- *(\d)','\g<1> minus \g<2>', text)
    #text    = re.sub('(\d) *\* *(\d)','\g<1> product \g<2>', text)
    #text    = re.sub('(\d) */ *(\d)','\g<1> over \g<2>', text)
    #text    = re.sub('(\d) *= *(\d)','\g<1> equals \g<2>', text)
    #text    = re.sub('(\d) *> *(\d)','\g<1> more than \g<2>', text)
    #text    = re.sub('(\d) *< *(\d)','\g<1> less than \g<2>', text)
    #text    = re.sub('(\d) >= (\d)','\g<1> more or equal to \g<2>', text)
    #text    = re.sub('(\d) <= (\d)','\g<1> less or equal to \g<2>', text)
    #text    = re.sub(' +',' ',text)     #remove multiple spaces

    #Extend some words
    #text    = re.sub("( |^)\'cause( |$)",' because ',text)
    #text    = re.sub("\'ll( |$)",' will ', text)
    #text    = re.sub("( |^)can\'t( |$)",' can not ', text)
    #text    = re.sub('( |^)cannot( |$)',' can not ', text)
    #text    = re.sub("\'re( |$)",' are ', text)
    #text    = re.sub("( |^)he\'s( |$)",' he is ', text)
    #text    = re.sub("( |^)she\'s( |$)",' she is ', text)
    #text    = re.sub("it\'s",'it is', text)
    #text    = re.sub("( |^)i\'m( |$)",' i am ', text)
    #text    = re.sub("( |^)isn\'t( |$)",' is not ', text)
    #text    = re.sub("( |^)aren\'t( |$)",' are not ', text)
    #text    = re.sub("( |^)doesn\'t( |$)",' does not ', text)
    #text    = re.sub("( |^)don\'t( |$)",' do not ', text)
    #text    = re.sub("( |^)didn\'t( |$)",' did not ', text)
    #text    = re.sub("( |^)wasn\'t( |$)",' was not ', text)
    #text    = re.sub("( |^)won\'t( |$)",' will not ', text)
    #text    = re.sub("( |^)shouldn\'t( |$)",' should not ', text)
    #text    = re.sub("( |^)haven\'t( |$)",' have not ', text)
    #text    = re.sub("( |^)hasn\'t( |$)",' has not ', text)
    #text    = re.sub("( |^)couldn\'t( |$)",' could not ', text)
    #text    = re.sub("( |^)wouldn\'t( |$)",' would not ', text)
#   #text    = re.sub("i\'d",'i would', text)
#   #text    = re.sub("i\'d",'i had', text)


    #Number to words conversion
    for word in text.split():
        if str(word.encode('utf-8')).isdigit():
            text = text.replace(word, num2words.num2words(float(word)),1)

    text    = re.sub('\d+',' ',text)   # remove all the rest numbers
    text    = re.sub(',','',text)

    #Replaces other symbols with whitespace, symbols untouched: NONE
    #text    = re.sub('(\++|-+|,+|\*+|:+|/+|>+|<+|=+|\^+|%+|\$+|#+|@+|\|+|~+|`+|\"+|`+|\'s|\(+|\)+|\[+|\]+|{+|}+|<+|>+|&lr|&ur|&qc|&qr|\'+)',' ',text)
    #text    = re.sub('(\++|-+|,+|\*+|:+|/+|>+|<+|=+|\^+|%+|\$+|#+|@+|\|+|~+|`+|\"+|`+|\(+|\)+|\[+|\]+|{+|}+|<+|>+|&lr|&ur|&qc|&qr| \' |\'\'+)',' ',text)
    text    = re.sub('(,+|/+|>+|<+|\^+|#+|@+|\|+|~+|`+|\"+|`+|\(+|\)+|\[+|\]+|{+|}+|&lr|&ur|&qc|&qr| \' |\'\'+|-+|\++|\\\\|=+|&+|\*+)',' ',text)
    text    = re.sub(' +',' ',text) #replace multiple spaces with single space
    #text    = re.sub('(^\'+ | \'+ | \'+ +\'+ | \'+$)',' ',text) # remove quotes
    text    = re.sub('(\'[^s]| \'+|^\'+|\'+$)',' ',text) # remove quotes
    text    = re.sub('(\'[^s]| \'+|^\'+|\'+$)',' ',text) # one more time remove quotes
    text    = re.sub(' +',' ',text) #replace multiple spaces with single space

    #Remove multiple periods, eg: '...'=> ''
    text    = re.sub('\.\.+','.',text)
    text    = re.sub(' +',' ',text)     #replace multiple spaces with single space

    #Replace the rest symbols with the period, in order to split sentences by period later.
    #text    = re.sub('(!+|\?+|;+|:+|\.+)','.', text)
    #text    = re.sub(' +',' ',text)     #remove multiple spaces
    #OR Remove the rest punctuation symbols.
    text    = re.sub('(!+|\?+|;+|:+|\.+)','', text)
    text    = re.sub(' +',' ',text)     #remove multiple spaces

    #Remove leading and trailing whitespaces
    text = text.strip();

    #Stemming and lemmatization
    '''
    porter  = nltk.PorterStemmer()
    text    = [porter.stem(t) for t in text.split()]
    wnl     = nltk.WordNetLemmatizer()
    text    = [wnl.lemmatize(t) for t in text]
    text    = ' '.join(text)
    '''
    '''
    #Convert to one line per sentence manner
    text    = text.replace('.','\n')
    text    = re.sub(' +',' ',text)     #remove multiple spaces
    text    = text.splitlines()
    text_tmp= list(text)
    for line in text:
        if len(line.split()) >= min_sent_size and 'isbn' not in line:
            line_tmp = re.sub('^\'s ','',line)      #remove "'s" in the beginning of sentence
            line_tmp = re.sub(' +',' ',line_tmp)
            #line_tmp = re.sub('_','.',line_tmp)     #put back periods for abbs/acros and floatin point numbers
            line_tmp = re.sub('_','',line_tmp)     #remove period holders for abbs/acros and floatin point numbers
            if line_tmp.strip() != '':
                text[text.index(line)] = topic_id+' '+line_tmp.strip()
                text_tmp[text_tmp.index(line)] = line_tmp.strip()
            else:
                text[text.index(line)] = ''
                text_tmp[text_tmp.index(line)] = ''
        else:
            text[text.index(line)] = ''
            text_tmp[text_tmp.index(line)] = ''
    text = [line for line in text if line.strip() != '']
    text_tmp = [line for line in text_tmp if line.strip() != '']
    text_sent = '\n'.join(text)
    text_doc = '. '.join(text_tmp)
    return (text_sent.strip(),text_doc.strip())
    '''
    return (text)


if __name__ == '__main__':
    if not os.path.exists(output_folder):
        os.system('mkdir '+output_folder)

    #output_file         = bz2.BZ2File(output_folder, 'wb')
    #output_file_docs    = bz2.BZ2File(output_folder_docs, 'wb')
    input_file_list     = run('ls '+input_folder).split()
    for file_name in input_file_list:
        print("file name: "+file_name)
        output_file = open(output_folder+'/'+file_name, 'w')
        with open(input_folder+'/'+file_name, 'r') as input_file:
            for raw_sent in input_file:
                clean_sent = cleanText(raw_sent.decode('unicode_escape').encode('ascii','ignore'),'')
                if clean_sent.strip() == '':
                    continue
                output_file.write(clean_sent+'\n')
        output_file.close()

exit()
