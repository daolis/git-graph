#!/usr/bin/python3
__author__ = 'Stephan Bechter <stephan@apogeum.at>'
import subprocess
import re
import hashlib
import sys
import argparse

# colors
COLOR_NODE = "cornsilk"
COLOR_NODE_FIRST = "cornflowerblue"
COLOR_NODE_CHERRY_PICK = "burlywood1"
COLOR_HEAD = "darkgreen"
COLOR_TAG = "yellow2"
COLOR_BRANCH = "orange"
COLOR_STASH = "red"

def log(message):
    if dubug:
        print(message, file=sys.stderr)

pattern = re.compile(r'^\[(\d+)\|(.*)\|(.*)\|\s?(.*)\]\s([0-9a-f]*)\s?([0-9a-f]*)\s?([0-9a-f]*)$')
parser = argparse.ArgumentParser()

parser.add_argument("-x", "--debug", dest="debug", action="store_true", help="Show debug messages on stderr")
parser.add_argument("-r", "--range", help="git commit range" )

args = parser.parse_args()
dubug = args.debug
revRange = ""
if args.range:
    revRange = " " + args.range
    log("Range: " + revRange)

gitLogCommand = 'git log --pretty=format:"[%ct|%cn|%s|%d] %h %p" --all ' + revRange
log('Git log command: ' + gitLogCommand)
output = subprocess.Popen(gitLogCommand, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
(out, err) = output.communicate()
lines = out.split("\n")

dates = {}
messages = {}
predefinedNodeColor = {}

def getCommitDiff(hash):
    # get only the changed lines (starting with + or -), no line numbers, hashes, ...
    command = 'git diff ' + hash + '^ ' + hash + ' | grep "^[-+]"'
    log("Hash Command: " + command)
    diffOutput = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    (diff, err) = diffOutput.communicate()
    return diff

def getCommitDiffHash(hash):
    diff = getCommitDiff(hash)
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
        labelExt = ""
        if hash in predefinedNodeColor:
            labelExt = "\\nSTASH INDEX"
            nodeColor = predefinedNodeColor[hash]

        else:
            nodeColor=COLOR_NODE
        if parentHash1:
            link = " \"" + parentHash1 + "\"->\"" + hash + "\";"
        else:
            #initial commit
            nodeColor = COLOR_NODE_FIRST
        if parentHash2:
            link2 = " \"" + parentHash2 + "\"->\"" + hash + "\";"

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
        nodeInfo = ""
        if ref:
            refEntries = ref.replace("(", "").replace(")", "").split(",")
            for refEntry in refEntries:
                style = "shape=oval,fillcolor=" + COLOR_BRANCH
                if "HEAD" in refEntry:
                    style = "shape=diamond,fillcolor=" + COLOR_HEAD
                elif "tag" in refEntry:
                    refEntry = refEntry.replace("tag: ", "")
                    style = "shape=oval,fillcolor=" + COLOR_TAG
                elif "stash" in refEntry:
                    style = "shape=box,fillcolor=" + COLOR_STASH
                    nodeColor = COLOR_STASH
                    labelExt = "\\nSTASH"
                    log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    if getCommitDiff(parentHash1) == "":
                        log('>>> "' + parentHash1 + '"[color=red]')
                        predefinedNodeColor[parentHash1] = COLOR_STASH
                    elif getCommitDiff(parentHash2) == "":
                        log('>>> "' + parentHash2 + '"[color=red]')
                        predefinedNodeColor[parentHash2] = COLOR_STASH
                    continue
                #else:
                    #if "origin" in refEntry:
                    #    continue
                nodeInfo += '    "' + refEntry + '"[style=filled,' + style + ']; "' + refEntry + '" -> "' + hash + '"\n'
        print("    \"" + hash + "\"[label=\"" + hash + labelExt + "\\n(" + user + ")\",shape=box,style=filled,fillcolor=" + nodeColor + "];" + link + link2)
        if nodeInfo:
            print(nodeInfo)
print("}")

