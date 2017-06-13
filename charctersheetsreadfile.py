def readfile(file):
    infile = open(file, 'r')
    info = []
    for line in infile:
        info.append(line.rstrip().split('\t'))
    infile.close()
    return info

def writefile(characterList):
    outfile = open('CharacterSheets', 'w')
    for item in characterList:
        outfile.write(str('\t'.join(item))+'\n')
    outfile.close()
        
characterList = readfile('charactersheets.txt')
writefile(characterList)