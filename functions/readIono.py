def readIonosphericParamters(file_rinex):

    with open(file_rinex,'r') as file:
        for line in file:
            line=line.replace('D', 'e')
            line=line.replace('E', 'e')
            if line.startswith('GPSA'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                alpha0 = float(wordList[1])
                alpha1 = float(wordList[2])
                alpha2 = float(wordList[3])
                alpha3 = float(wordList[4])
                
            elif line.startswith('GPSB'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                beta0 = float(wordList[1])
                beta1 = float(wordList[2])
                beta2 = float(wordList[3])
                beta3 = float(wordList[4])
                
        
    return alpha0, alpha1, alpha2, alpha3, beta0, beta1, beta2, beta3


def readTimeCorrParamters(file_rinex):

    timeCorrParam = []
    
    with open(file_rinex,'r') as file:
        for line in file:
            line=line.replace('D', 'e')
            line=line.replace('E', 'e')
            if line.startswith('GPUT'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                # a0, a1 coefficients of linear polynomial
                alpha = wordList[1].split('-')
                alpha0 = float('-' + alpha[1] + '-' + alpha[2])
                alpha1 = float('-' + alpha[3] + '-' + alpha[4])
                
                # Reference time for polynomial
                referenceTime = float(wordList[2])
                
                # Reference week number
                weekNUmber = float(wordList[3])
                
    return alpha0, alpha1, referenceTime, weekNUmber


x = readIonosphericParamters('Data/ANK.rnx')
