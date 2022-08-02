#!/usr/bin/python
#Pseudocode
#1. Request input sequence and minimum palindrome length from user 
#2. Compute the reverse complement for the sequence 
#3. Extract all the common sequences from sequence and its reverse complement 
#4. Extract all the palindromes from the common sequences 
#5. Extract and output all the normal palindromes
#6. Extract and output all the spacer palindromes

import cgi, cgitb #import modules for CGI handling
cgitb.enable() #debugger
import re

#create instance of FieldStorage
form = cgi.FieldStorage()

#get data from field
rawFasta = form.getvalue('fastaRaw')
rawGenbank = form.getvalue('genbankRaw') 
sequence =  form.getvalue('sequence')
minLength = int(form.getvalue('minLength'))
filename = form.getvalue('filename')

print "Content-type: text/html\r\n\r\n";
print "<html><head><title>Result</title></head><body>";
print "<body>";
print "<html><head><title>Result</title></head><body>";
print "<link rel=stylesheet href=/./siv3009/idzhar/style/result.css>";

def rawInput(rawFasta, rawGenbank, sequence): #function to extract sequence from raw input
    if rawFasta == 'on': #if "raw fasta" button is checked
        sequence = sequence.split("\n",1)[1] #remove the header line
        sequence = re.sub('\s','', sequence) #replace whitespace with nothing

    if rawGenbank == 'on': #if "raw genbank" button is checked
        sequence = re.sub('\d','',sequence) #replace all digits with nothing
        gb_seq = 'ORIGIN\s+([agct_\s]+)' #re pattern to match sequence 
        sequenceline = re.search(gb_seq, sequence, re.MULTILINE) #use re pattern to search for sequence
        if sequenceline: #if pattern found
            grp1 = sequenceline.group(1) #extract group 1
            sequence = re.sub('\s','',grp1) #replace whitespace with nothing

    return sequence

def readFASTA(filename): #function to extract sequence from FASTA
    fo = open(filename)
    lines = fo.readlines() #read all lines in file
    seq = '' #empty string to store extracted sequence
    
    for line in lines:
        if line.startswith('>'): #ignore the header line which starts with '>'
            pass
        else:
            line = re.sub('\n','',line) #replace newlines with nothing
            seq += line #update seq variable with lines

    return seq #return extracted sequence from fasta
    
def readGB(filename): #function to extract sequence from Genbank
    gb_seq = '^\s+\d+\s+(([a-z_]+\s*)+)' #regular expression (re) pattern to match sequence part 
    fo = open(filename)
    lines = fo.readlines() #read all lines in file
    seq = '' #empty string to store extracted sequence
    
    for line in lines:
        sequenceline = re.search(gb_seq,line) #use re pattern to search for sequence in file
        if sequenceline: #if pattern found
            grp1 = sequenceline.group(1) #for the first subgroup
            sequenceline1 = re.sub('[\s]','',grp1) #replace whitespace with nothing
            seq += sequenceline1 #update seq variable with lines

    return seq #return extracted sequence from genbank

def reverseComplement(seq): #function to commpute reverse complement
    Base = {'A':'T','T':'A','G':'C','C':'G', '_':'_'} #dictionary to store base pair for A,G,C,T and spacer region
    ComplementSeq = "" #empty string to store complement sequence

    for i in range(0, len(seq)): #for every base in the whole original sequence length
        pair = seq[i] #new variable to store each base in original sequence
        ComplementSeq = ComplementSeq + Base[pair] #concatenate the complement base pair together using values from dictionary
    reverseComplementSeq = ComplementSeq[::-1] #reverse the ComplementSeq
    
    return reverseComplementSeq #return the reverse complement sequence

def CommonSequence(seq,revCom,minLength): #function to extract common sequence between the original and reverse complement
    seqLength = len(seq) #compute the sequence length
    commonSequence = [] #empty list to store common sequence

    for i in range(seqLength,minLength-1,-1): #loop from the reverse of sequence
    #until min palindrome length
        for k in range(seqLength-i+1): #loop in the length of short sequence
            if (seq[k:i+k] in revCom): #true if base present in reverse complement
                flag = 1
                for m in range(len(commonSequence)): #loop in the length of list
                    if seq[k:i+k] in commonSequence[m]: #if base is already present in list
                        flag = 0 
                        break #break the loop

                if flag == 1: #if base is not already present in list
                    commonSequence.append(seq[k:i+k]) #add base to the list

    if len(commonSequence): #true if list is not empty
        return(commonSequence) #return list that contains common sequences
    else: #false if list is empty
	    print "<b>There are no normal palindromes that can be detected. </b><br>"
	    exit()

def AllPalindrome(allMatches): #function to find all palindromes
    allPalindrome = [] #empty list to store all palindromes
    for sequence in allMatches: #for every sequence in all the common sequence
        #check if that particular sequence is equivalent to its reverse complement (means its a palindrome)
        #and if that sequence does not exist in the list already
        if sequence == reverseComplement(sequence) and sequence not in allPalindrome: #true
            allPalindrome.append(sequence) #add that sequence to the list


    return allPalindrome #return all the palindromes in the whole sequence

def NormalPalindrome(allPalindrome): #function to find normal palindromes (without spacer region)
    normalPalindrome = [] #empty list to store normal palindromes
    for sequence in allPalindrome: #for every sequence in all the palindromes
        if '_' not in sequence: #filter out palindromes that doesnt contain '_'
            normalPalindrome.append(sequence) #add that palindrome to the list

    if len(normalPalindrome): #print out all the normal palindromes if available
        normalPalindrome = ', '.join(normalPalindrome) #convert normal palindrome list to string for output
	print "<b><br>Normal palindromes (non-repeating): %s</b><br>" % (normalPalindrome)
    else:
        print "<b>There are no normal palindromes that can be detected. %s</b><br>"

def SpacerPalindrome(allPalindrome): #function to find spacer palindromes
    allPalindrome = ' '.join(allPalindrome) #convert list of all palindromes to string for re
    spacerPalindrome = re.findall(r'[AGCT]+_+[AGCT]+',allPalindrome) #find all spacer palindromes using re

    if len(spacerPalindrome): #print out all the spacer palindromes if available
        spacerPalindrome = ', '.join(spacerPalindrome) #convert spacer palindrome list to string for output
	print "<b><br>Reverse-complement non-repeating palindromes with an intervening spacer region: %s</b><br>" % (spacerPalindrome)    
    else:
        print "<b>There is no reverse-complement non-repeating palindromes with an intervening spacer region that can be detected. %s</b><br>"

#program starts here----------------------------------------------------------------------------------------------------------------------------------
if rawFasta == 'on' or rawGenbank == 'on': #if either one of the button is checked
    sequence = rawInput(rawFasta, rawGenbank, sequence) #extract sequence from raw input

else: #if no button is checked
    if filename.endswith('.fasta'): 
        sequence = readFASTA(filename) #extract sequence from fasta file

    if filename.endswith('.gb'):
        sequence = readGB(filename) #extract sequence from genbank file


print "<div align= center>";
print "<img src=/./siv3009/idzhar/image/dna.png class=icon>";
print "<h2><b>DNAPalin</b></h2>";
print "</div>";
print "<div class=topnav>";
print "<a href=/./siv3009/idzhar/index.html target=_self>DNAPalin</a>";
print "<a href=/./siv3009/idzhar/seq.html target=_self>Sequence Analysis</a>";
print "<a onclick=alert('Coming soon!')>Contact</a>";
print "</div><br><br>";
print "<div align=left>";
print "<legend>Result</legend><br>";
print "<fieldset id=form1>";
seq = sequence.upper() #convert sequence to uppercase
print "<p><b>Your input sequence is: %s</b></p><br>" % (seq) #print extracted sequence for confirmation
revCom = reverseComplement(seq) #call function reverseComplement
allMatches = CommonSequence(seq,revCom,minLength) #call function CommonSequence
allPalindrome = AllPalindrome(allMatches) #call function AllPalindrome
NormalPalindrome(allPalindrome) #call function NormalPalindrome
SpacerPalindrome(allPalindrome) #call function SpacerPalindrome
print "</fieldset>";
print "</body></html>";
