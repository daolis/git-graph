#!/usr/bin/python3
__author__ = 'Stephan Bechter <stephan@apogeum.at>'
import subprocess
import re
import hashlib
import sys
import logging
import os

class GitGraph():
    # colors
    COLOR_NODE = "cornsilk"
    COLOR_NODE_MERGE = "cornsilk2"
    COLOR_NODE_FIRST = "cornflowerblue"
    COLOR_NODE_CHERRY_PICK = "burlywood1"
    COLOR_NODE_REVERT = "azure4"
    COLOR_HEAD = "darkgreen"
    COLOR_TAG = "yellow2"
    COLOR_BRANCH = "orange"
    COLOR_STASH = "red"

    def __init__(self, showMessages=False):
        """
        """
        self.pattern = re.compile(r'^\[(\d+)\|\|(.*)\|\|(.*)\|\|\s?(.*)\]\s([0-9a-f]*)\s?([0-9a-f]*)\s?([0-9a-f]*)$')
        self.revertMessagePattern = re.compile(r'Revert "(.*)"')

    @staticmethod
    def getLog(revRange=None):
        """
        :param revRange: git commit range to deal with
        """
        if revRange is not None:
            logging.info("Range: " + revRange)
        else:
            revRange = ""
        
        gitLogCommand = 'git log --pretty=format:"[%ct||%cn||%s||%d] %h %p" --all ' + revRange
        logging.info('Git log command: ' + gitLogCommand)
        output = subprocess.Popen(gitLogCommand, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        (out, err) = output.communicate()
        return out.split("\n")

    @staticmethod
    def getCommitDiff(hash):
        # get only the changed lines (starting with + or -), no line numbers, hashes, ...
        command = 'git diff ' + hash + '^ ' + hash + ' | grep "^[-+]"'
        logging.debug("Hash Command: " + command)
        diffOutput = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        (diff, err) = diffOutput.communicate()
        return diff
    
    def getCommitDiffHash(self, hash):
        diff = self.getCommitDiff(hash)
        sha = hashlib.sha1(diff.encode('utf-8'))
        return sha.hexdigest()

    def getDot(self, showMessages=False, revRange=None):
        """
        :param showMessages (optional): Show commit messages in node
        :param revRange: git commit range to deal with
        """
        lines = self.getLog(revRange)
        
        dates = {}
        messages = {}
        predefinedNodeColor = {}
        
        digraph = "digraph G {"
        #first extract messages
        for line in lines:
            match = re.match(self.pattern, line)
            if match:
                date = match.group(1)
                message = match.group(3)
                commitHash = match.group(5)
                if message in messages:
                    existing = messages[message]
                    #print(dates[existing]+" - "+date)
                    if dates[existing] > date:
                        #print("setting message ["+message+"] with ["+hash+"]")
                        messages[message] = commitHash
                else:
                    messages[message] = commitHash
                dates[commitHash] = date
        
        for line in lines:
            #print(line)
            match = re.match(self.pattern, line)
            if match:
                date = match.group(1)
                user = match.group(2)
                message = match.group(3)
                ref = match.group(4)
                commitHash = match.group(5)
                parentHash1 = match.group(6)
                parentHash2 = match.group(7)
        
                link = ""
                link2 = ""
                labelExt = ""
                nodeMessage = ""
                if args.messages:
                    nodeMessage = "\n" + message.replace("\"", "'");
                if commitHash in predefinedNodeColor:
                    labelExt = "\\nSTASH INDEX"
                    nodeColor = predefinedNodeColor[commitHash]
        
                else:
                    nodeColor=self.COLOR_NODE
                if parentHash1:
                    link = " \"" + parentHash1 + "\"->\"" + commitHash + "\";"
                else:
                    #initial commit
                    nodeColor = self.COLOR_NODE_FIRST
                if parentHash2:
                    link2 = " \"" + parentHash2 + "\"->\"" + commitHash + "\";"
                if parentHash1 and parentHash2:
                    nodeColor = self.COLOR_NODE_MERGE
                if message in messages:
                    # message exists in history - possible cherry-pick -> compare diff hashes
                    existingHash = messages[message]
                    if commitHash is not existingHash and date > dates[existingHash]:
                        diffHashOld = self.getCommitDiffHash(existingHash)
                        diffHashActual = self.getCommitDiffHash(commitHash)
                        logging.debug("M [" + message + "]")
                        logging.debug("1 [" + diffHashOld + "]")
                        logging.debug("2 [" + diffHashActual + "]")
                        if diffHashOld == diffHashActual:
                            logging.debug("equal")
                            digraph += '    "' + str(existingHash) + '"->"' + commitHash + '"[label="Cherry\\nPick",style=dotted,fontcolor="red",color="red"]'
                            nodeColor = self.COLOR_NODE_CHERRY_PICK
                            #labelExt = "\\nCherry Pick"
                        logging.debug("")
                logging.debug("Message: [" + message + "]")
                if message.startswith("Revert"):
                    # check for revert
                    logging.debug("Revert commit")
                    match = re.match(self.revertMessagePattern, message)
                    if match:
                        originalMessage = match.group(1)
                        logging.debug("Revert match [" + originalMessage + "]")
                        if originalMessage in messages:
                            origRevertHash = messages[originalMessage]
                            digraph += '    "' + commitHash + '"->"' + str(origRevertHash) + '"[label="Revert",style=dotted,fontcolor="azure4",color="azure4"]'
                        else:
                            logging.warning('Not able to find the original revert commit for commit ' + commitHash)
                            digraph += '    "revert_' + commitHash + '"[label="", shape=none, height=.0, width=.0]; "' + commitHash + '"->"revert_' + commitHash + '"[label="Revert ??",style=dotted,fontcolor="azure4",color="azure4"];'
                    nodeColor = self.COLOR_NODE_REVERT
        
                nodeInfo = ""
                if ref:
                    refEntries = ref.replace("(", "").replace(")", "").split(",")
                    for refEntry in refEntries:
                        style = "shape=oval,fillcolor=" + self.COLOR_BRANCH
                        if "HEAD" in refEntry:
                            style = "shape=diamond,fillcolor=" + self.COLOR_HEAD
                        elif "tag" in refEntry:
                            refEntry = refEntry.replace("tag: ", "")
                            style = "shape=oval,fillcolor=" + self.COLOR_TAG
                        elif "stash" in refEntry:
                            style = "shape=box,fillcolor=" + self.COLOR_STASH
                            nodeColor = self.COLOR_STASH
                            labelExt = "\\nSTASH"
                            if self.getCommitDiff(parentHash1) == "":
                                logging.debug('>>> "' + parentHash1 + '"[color=red]')
                                predefinedNodeColor[parentHash1] = self.COLOR_STASH
                            elif self.getCommitDiff(parentHash2) == "":
                                logging.debug('>>> "' + parentHash2 + '"[color=red]')
                                predefinedNodeColor[parentHash2] = self.COLOR_STASH
                            continue
                        #else:
                            #if "origin" in refEntry:
                            #    continue
                        nodeInfo += '    "' + refEntry + '"[style=filled,' + style + ']; "' + refEntry + '" -> "' + commitHash + '"\n'
                digraph += "    \"" + commitHash + "\"[label=\"" + commitHash + nodeMessage + labelExt + "\\n(" + user + ")\",shape=box,style=filled,fillcolor=" + nodeColor + "];" + link + link2
                if nodeInfo:
                    digraph += nodeInfo
        digraph += "}"
        return digraph

    def getImage(self, filename, showMessages=False, revRange=None):
        """
        Write an image
        :param showMessages (optional): Show commit messages in node
        :param revRange: git commit range to deal with
        :param filename: name of the image file to produce
                         The extension is used to determine the image format,
                         it must be one of the accepted agrument accepted on the
                         command line of the dot utility
                         See: https://www.graphviz.org/docs/outputs/
        """
        fmt = os.path.splitext(filename)[1][1:]
        dotCommand = ['dot', '-T' + fmt, '-o', filename]
        logging.info('Dot command: ' + ' '.join(dotCommand))
        subprocess.run(dotCommand, input=self.getDot(showMessages, revRange).encode('utf8'), check=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="Show info messages on stderr or debug messages if -v option is set twice")
    parser.add_argument("-m", "--messages", dest="messages", action="store_true", help="Show commit messages in node" )
    parser.add_argument("-r", "--range", dest="range", default=None, help="git commit range" )
    parser.add_argument("-o", "--output", dest='output', default=None,
                        help="Image filename to produce, if not provided the DOT file will be outputed on STDOUT." + \
                             "The extension is used to determine the image format, it must be one of the accepted agrument accepted on the" + \
                             "command line of the dot utility (See: https://www.graphviz.org/docs/outputs/)")
    
    args = parser.parse_args()
    if args.verbose > 0:
        level = 'INFO' if args.verbose == 1 else 'DEBUG'
        logging.basicConfig(level=getattr(logging, level, None))

    if args.output is None:
        print(GitGraph().getDot(showMessages=args.messages, revRange=args.range))
    else:
        GitGraph().getImage(args.output, showMessages=args.messages, revRange=args.range)

