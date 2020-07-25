from renko import loadSequence
from stats import KnowledgeBook

if __name__ == '__main__':
    labelWinSize = 1
    predWinSize = int(input())
    renko = loadSequence('eurgbp',50)
    book = KnowledgeBook()
    
    for i in range(len(renko)):
        if i >= len(renko) - labelWinSize - predWinSize : break

        featureHead = i
        featureTail = featureHead + predWinSize
        featurePattern = renko[featureHead:featureTail]

        labelHead = featureTail
        labelTail = labelHead + labelWinSize
        labelingPattern = renko[labelHead:labelTail]
        
        book.includeSample(featurePattern, labelingPattern)

    book.showAllInfo()
