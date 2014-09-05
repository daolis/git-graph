#!/usr/bin/python3
__author__ = 'Stephan Bechter <stephan@apogeum.at>'
import subprocess
import re
import hashlib
import sys

# colors
COLOR_NODE = "cornsilk"
COLOR_NODE_FIRST = "cornflowerblue"
COLOR_NODE_CHERRY_PICK = "burlywood1"
COLOR_HEAD = "darkgreen"
COLOR_TAG = "yellow2"
COLOR_BRANCH = "orange"
COLOR_STASH = "red"

showLog = False

pattern = re.compile(r'^\[(\d+)\|(.*)\|(.*)\|\s?(.*)\]\s([0-9a-f]*)\s?([0-9a-f]*)\s?([0-9a-f]*)$')

output = subprocess.Popen('git log --pretty=format:"[%ct|%cn|%s|%d] %h %p" --all', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
(out, err) = output.communicate()
lines = out.split("\n")

dates = {}
messages = {}

def log(message):
    if showLog:
        print(message, file=sys.stderr)

def getCommitDiffHash(hash):
    # get only the changed lines (starting with + or -), no line numbers, hashes, ...
    command = 'git diff ' + hash + '^ ' + hash + ' | grep "^[-+]"'
    log("Hash Command: " + command)
    diffOutput = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    (diff, err) = diffOutput.communicate()
    sha = hashlib.sha1(diff.encode('utf-8'))
    return sha.hexdigest()

print("digraph G {")
#first extract messages
for line in lines:
    match = re.match(pattern, line)
    if match:
        date = match.group(1)
        message = match.group(3)
        hash = match.group(5)
        if message in messages:
            existing = messages[message]
            #print(dates[existing]+" - "+date)
            if dates[existing] > date:
                #print("setting message ["+message+"] with ["+hash+"]")
                messages[message] = hash
        else:
            messages[message] = hash
        dates[hash] = date

for line in lines:
    #print(line)
    match = re.match(pattern, line)
    if match:
        date = match.group(1)
        user = match.group(2)
        message = match.group(3)
        ref = match.group(4)
        hash = match.group(5)
        parentHash1 = match.group(6)
        parentHash2 = match.group(7)

        link = ""
        link2 = ""
        nodeColor=COLOR_NODE
        if parentHash1:
            link = " \"" + parentHash1 + "\"->\"" + hash + "\";"
        else:
            #initial commit
            nodeColor = COLOR_NODE_FIRST
        if parentHash2:
            link2 = " \"" + parentHash2 + "\"->\"" + hash + "\";"

        labelExt = ""
        if message in messages:
            existingHash = messages[message]
            if hash is not existingHash and date > dates[existingHash]:
                diffHashOld = getCommitDiffHash(existingHash)
                diffHashActual = getCommitDiffHash(hash)
                log("M [" + message + "]")
                log("1 [" + diffHashOld + "]")
                log("2 [" + diffHashActual + "]")
                if diffHashOld == diffHashActual:
                    log("equal")
                    print('    "' + str(existingHash) + '"->"' + hash + '"[label="Cherry\\nPick",style=dotted,fontcolor="red",color="red"]')
                    nodeColor = COLOR_NODE_CHERRY_PICK
                    #labelExt = "\\nCherry Pick"
                log("")
        print("    \"" + hash + "\"[label=\"" + hash + labelExt + "\\n(" + user + ")\",shape=box,style=filled,fillcolor=" + nodeColor + "];" + link + link2)
        if ref:
            refEntries = ref.replace("(", "").replace(")", "").split(",")
            for refEntry in refEntries:
                style = "shape=box,fillcolor=" + COLOR_BRANCH
                if "HEAD" in refEntry:
                    style = "shape=diamond,fillcolor=" + COLOR_HEAD
                elif "tag" in refEntry:
                    refEntry = refEntry.replace("tag: ", "")
                    style = "shape=oval,fillcolor=" + COLOR_TAG
                elif "stash" in refEntry:
                    style = "shape=box,fillcolor=" + COLOR_STASH
                else:
                    if "origin" in refEntry:
                        continue
                print('    "' + refEntry + '"[style=filled,' + style + ']; "' + refEntry + '" -> "' + hash + '"')
print("}")

