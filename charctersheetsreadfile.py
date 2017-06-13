def readfile(file):
    infile = open(file, 'r')
    info = []
    for line in infile:
        info.append(line.rstrip().split('\t'))
    infile.close()
    return info

def writefile(characterList):
    outfile = open('CharacterSheetCode', 'w')
    for item in characterList:
        outfile.write('''cur.execute("""INSERT INTO character (cid, name, desriptionURL, imageURL, gtid) VALUES ((SELECT floor(random()*(2034343003-43434+1))+10), '%s', '%s', '%s', ((SELECT gtid from gametype where title = '2002 French Presidential Election'));""")\n'''%(str(item[0]), str(item[1]), str(item[2])))
    outfile.close()
        
characterList = readfile('charactersheets.txt')
writefile(characterList)