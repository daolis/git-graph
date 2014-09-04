#!/usr/bin/python3
__author__ = 'Stephan Bechter <stephan@apogeum.at>'
import subprocess
import re

pattern = re.compile(r'^\[(\d+)\|(.*)\|(.*)\|\s?(.*)\]\s([0-9a-f]*)\s?([0-9a-f]*)\s?([0-9a-f]*)$')
output = subprocess.Popen('git log --pretty=format:"[%ct|%cn|%s|%d] %h %p" --all', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
(out, err) = output.communicate()
lines = out.split("\n")
dates = {}
messages = {}
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
        nodeColor="cornsilk"
        if parentHash1:
            link = " \"" + parentHash1 + "\"->\"" + hash + "\";"
        else:
            #initial commit
            nodeColor = "cornflowerblue"
        if parentHash2:
            link2 = " \"" + parentHash2 + "\"->\"" + hash + "\";"

        labelExt = ""
        if message in messages:
            existingHash = messages[message]
            if hash is not existingHash and date > dates[existingHash]:
                print('    "' + str(existingHash) + '"->"' + hash + '"[label="C-P",style=dotted]')
                nodeColor = "burlywood1"
                labelExt = "\\nCherryPick"
        print("    \"" + hash + "\"[label=\"" + hash + labelExt + "\\n(" + user + ")\",shape=box,style=filled,fillcolor=" + nodeColor + "];" + link + link2)
        if ref:
            refEntries = ref.replace("(", "").replace(")", "").split(",")
            for refEntry in refEntries:
                style = "shape=box,fillcolor=orange"
                if "HEAD" in refEntry:
                    style = "shape=diamond,fillcolor=darkgreen"
                elif "tag" in refEntry:
                    refEntry = refEntry.replace("tag: ", "")
                    style = "shape=oval,fillcolor=yellow2"
                else:
                    if "origin" in refEntry:
                        continue
                print('    "' + refEntry + '"[style=filled,' + style + ']; "' + refEntry + '" -> "' + hash + '"')
print("}")

