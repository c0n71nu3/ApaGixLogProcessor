# python utility to get certain patterns from Nginx & Apache log files

from collections import Counter
from datetime import datetime
import argparse
import os
import subprocess as sub
import re

# defining custom exceptions
class CommandLineErrors(Exception):    
    errorCodeToMessageMap = {
        1: "Supplied logfile not found", 
        2: "Supplied logfile is not a text file",
        3: "Supplied logfile is empty",
        4: '''Supplied file does not look like a supported apache/nginx log format\nThe supported logs contain lines like:\n83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"''',
        5: "Limit can be only positive integer",
        6: "Invalid date format. Start & end date needed as %%d/%%b/%%Y:%%H:%%M:%%S e.g. 17/May/2015:09:05:00",
        7: "Start date should be less than the end date"        
    }                  

    errorMessage = None

    def __init__(self, errorCode):
        self.errorMessage = self.errorCodeToMessageMap.get(errorCode)
        self.errorCode = errorCode        

    def __str__(self):
        return self.errorMessage

# actual logic class
class ApaGixLogProcessor():    
    allLines = []
    allIps = []      
    listOfIpsAndCorrespondingApisWithCount = []    

    def __init__(self, allLines, start=None, end=None):
        try:
            listOfIpsAndCorrespondingApis = []                                                                
            if start and end:                    
                startDateTime = datetime.strptime(start, "%d/%b/%Y:%H:%M:%S")
                endDateTime = datetime.strptime(end, "%d/%b/%Y:%H:%M:%S")

                self.allLines = [line for line in allLines if datetime.strptime(line.split("- - [")[1].split("]")[0].split(" +")[0].strip(), "%d/%b/%Y:%H:%M:%S") > startDateTime and datetime.strptime(line.split("- - [")[1].split("]")[0].split(" +")[0].strip(), "%d/%b/%Y:%H:%M:%S") < endDateTime]

            else:
                self.allLines = allLines
            
            self.allIps = [line.split('-')[0].strip() for line in self.allLines]                
            # for each ip get a list of APIs it has hit along with the frequency. Keep this as a pre calculated (for direct lookup) list of dict                
            listOfIpsAndCorrespondingApis = [line.split('-')[0].strip() + ' - ' + line.split("\"")[1].split()[1].strip() for line in self.allLines if line]
            self.listOfIpsAndCorrespondingApisWithCount = Counter(listOfIpsAndCorrespondingApis).items()
        
        except Exception as error:
            raise error


    ''' 
    List Unique IP addresses with frequency of their occurrences
    Returns: List of tuples, where first item is IP addresses & second item is the frequency of that IP address
    '''
    def getUniqueIpsWithFrequency(self):
        try:
            result = []
            rawResult = None        
            rawResult = Counter(self.allIps).items()            
            
            return rawResult
        
        except Exception as error:
            print error    

    ''' 
    List of top 10 APIs
    Takes 2 optional parameters: 
        ip => if the result needs to be filtered by a certain IP (defaults to None, in which case top 10 results are returned. See below for definition of 'top')
        limit => the total number of results to be returned (defaults to 10)
    Returns 2 items: 
    1. List of tuples => indicates top APIs being hit. 'Top' as per number of hits on a certain API grouped by IP
        Tuple[0] => <IP address> - <api or HTTP end point>
        Tuple[1] => total count of the above combination
    2. List of tuples => indicates top APIs being hit. 'Top' as per the top 10 entries in the log file ordered by latest first
        Tuple[0] => <IP address> - <api or HTTP end point>
        Tuple[1] => Timestamp in the format 'dd/Mon/YYYY:hh:mm:ss'
    '''
    def getTopTenApis(self, ip=None, limit=10):                                
        try:
            resultSetForQueriedIp = []        
            rawResultByFrequencyOfHit = None
            rawResultByTime = None
            limit = int(limit)
            
            if ip:
                resultSetForQueriedIp = [item for item in self.listOfIpsAndCorrespondingApisWithCount if item[0].split('-')[0].strip() == ip]
                listOfInterestingLines = [line for line in self.allLines if line.split('-')[0].strip() == ip]
            else:
                resultSetForQueriedIp = self.listOfIpsAndCorrespondingApisWithCount
                listOfInterestingLines = self.allLines

            # top 10 APIs by frequency of hit
            resultSetForQueriedIp.sort(key = lambda item: item[1], reverse=True)
            if resultSetForQueriedIp:
                rawResultByFrequencyOfHit = resultSetForQueriedIp[:limit]
            
            # top 10 by timestamp        
            listOfIpsAndCorrespondingApisWithTime = [(line.split('-')[0].strip() + ' - ' + line.split("\"")[1].split()[1].strip(), line.split("- - [")[1].split("]")[0].split(" +")[0].strip()) for line in listOfInterestingLines if line]    
            listOfIpsAndCorrespondingApisWithTime.sort(key=lambda x: datetime.strptime(x[1], "%d/%b/%Y:%H:%M:%S"), reverse=True)
            if listOfIpsAndCorrespondingApisWithTime:
                rawResultByTime = listOfIpsAndCorrespondingApisWithTime[:limit]

            return rawResultByFrequencyOfHit, rawResultByTime
        
        except Exception as e:
            print e            


    def displayResults(self, resultList, outputFormat=None, outputFrom=None):
        finalResult = []                
        jsonFormattedResult = []

        if resultList and outputFormat == 'json' and outputFrom == 'ipWithFreq':
            dictOfIpsWithCount = {'ip':None, 'frequency':None}
            for item in resultList:
                dictOfIpsWithCount.update({'ip':item[0], 'frequency':item[1]})
                jsonFormattedResult.append(dictOfIpsWithCount.copy())

            finalResult = jsonFormattedResult
            
        elif resultList and outputFormat == 'json' and outputFrom in ['topTenH', 'topTenT']:
            if outputFrom == 'topTenH':
                key = 'frequency'
            else:
                key = 'time'
            #('46.105.14.53 - /blog/tags/puppet?flav=rss20', 364)            
            #('66.249.73.135 - /blog/tags/wine', '20/May/2015:21:05:59')
            dictOfIpsWithCount = {'ip':None, 'url':None, key:None}
            for item in resultList:
                dictOfIpsWithCount.update({'ip':item[0].split(' - ')[0].strip(), 'url':item[0].split(' - ')[1].strip(), key:item[1]})
                jsonFormattedResult.append(dictOfIpsWithCount.copy())
            
            finalResult = jsonFormattedResult

        else:
            if not resultList or outputFrom not in ['ipWithFreq', 'topTenH', 'topTenT']:
                print "No results found"
                return 
            
            finalResult = resultList            
        
        for item in finalResult:
            print item                 

# do some basic sanity checks before proceeding with the actual processing    
def allSanityChecksPass(cmdLineArgs):
    try:
        #print cmdLineArgs        
        stringToDateConversionExceptionExpected = None
        errorCode = None
        lineNumber = 0
        allLinesRead = None
        regex = '([(\d\.)]+) - (.*) \[(.*?)\] "(.*?)" (\d+) (.*) (.*) (.*)'
                
        # check if file exists
        if not os.path.exists(cmdLineArgs.logFile):    
            errorCode = 1
            raise CommandLineErrors(errorCode)
            
        # check for log file type
        fileType = sub.check_output(['file', 'apache_logs.txt'])    
        if 'ASCII' not in fileType:
            errorCode = 2
            raise CommandLineErrors(errorCode)

        # check for empty file
        if not os.stat(cmdLineArgs.logFile).st_size:
            errorCode = 3
            raise CommandLineErrors(errorCode)

        # check if file somewhat looks like apache or nginx logs
        with open(cmdLineArgs.logFile, 'r') as fileHandle:
            allLinesRead = fileHandle.readlines()

            for line in allLinesRead:
                if not re.match(regex, line):
                    errorCode = 4
                    break
                lineNumber += 1

            if errorCode:
                print "Faulty line {0}".format(lineNumber)
                print allLinesRead[lineNumber]
                raise CommandLineErrors(errorCode)    

        # check if limit has been supplied and if it is integer
        if cmdLineArgs.limit and not cmdLineArgs.limit.isdigit():
            errorCode = 5
            raise CommandLineErrors(errorCode)                            

        # check if time period exists and if arguments are proper date time formats
        if cmdLineArgs.timePeriod:            
            arg1 = cmdLineArgs.timePeriod[0]
            arg2 = cmdLineArgs.timePeriod[1]
            stringToDateConversionExceptionExpected = True
            startDate = datetime.strptime(arg1, '%d/%b/%Y:%H:%M:%S')
            endDate = datetime.strptime(arg2, '%d/%b/%Y:%H:%M:%S')
            stringToDateConversionExceptionExpected = False
            if startDate >= endDate:
                errorCode = 7
                raise CommandLineErrors(errorCode)

        return allLinesRead

    except Exception as e:
        if stringToDateConversionExceptionExpected:
            errorCode = 6
            raise CommandLineErrors(errorCode)
        #allLinesRead = None
        raise
      
    # define output format - in file, or json, or on screen


if __name__ == '__main__':    
    try:
        message = ''        
        parser = argparse.ArgumentParser(description='A python utility to get certain patterns from Nginx & Apache log files')    
        parser.add_argument('logFile', help='Apache or Nginx log file to process. Full path if in another location or just the file name if it is in the same location from where the script is being executed')

        notTogether = parser.add_mutually_exclusive_group()
        notTogether.add_argument('-fq', '--ipWithFreq', help='get a list of all ips with frequency', action="store_true")
        notTogether.add_argument('-tt','--topTen', metavar='filter_by_ip', help='list the top 10 API / URL endpoints hit by the provided IP address', nargs='?', const='')
        
        parser.add_argument('-tp','--timePeriod', metavar=('start_date', 'end_date'), help='list the top n API / URL endpoints between the 2 time stamps. 1st arg = start date & 2nd arg = end date. Format for both should be %%d/%%b/%%Y:%%H:%%M:%%S e.g. 17/May/2015:09:05:00 . n = 10 by default. n can be specified by the -l or --limit switch', nargs=2)    
        parser.add_argument('-l', '--limit', metavar='limit_by_value', help='limit results of top hits. It should be a positive integer only. Default is 10')        
        parser.add_argument('-o', '--output', metavar='output_format', help='output format. Can be json. Defaults to raw on screen results', choices=['json'])        
        args = parser.parse_args()                
                        
        if args.timePeriod:
            naviObj = ApaGixLogProcessor(allSanityChecksPass(args), args.timePeriod[0], args.timePeriod[1])
        
        else:
            naviObj = ApaGixLogProcessor(allSanityChecksPass(args))
        
        if args.ipWithFreq:
            print "\n[+] Ips with frequency of hit"
            resultToPrint = naviObj.getUniqueIpsWithFrequency()            
            naviObj.displayResults(resultToPrint, outputFormat=args.output, outputFrom='ipWithFreq')                           

        else:
            resultMessage = ''
            if args.topTen:            
                if args.limit:
                    resultMessage = "\n[+] APIs filtered by IP =>  Top {0} {1}"
                    resultToPrintTopTenByFrequencyOfHit, resultToPrintTopTenByTime = naviObj.getTopTenApis(ip=args.topTen, limit=args.limit)                     
                    
                    print resultMessage.format(args.limit, "as per frequency of hit")                                        
                    naviObj.displayResults(resultToPrintTopTenByFrequencyOfHit, outputFormat=args.output, outputFrom='topTenH')
                    
                    print resultMessage.format(args.limit, "as per time")
                    naviObj.displayResults(resultToPrintTopTenByTime, outputFormat=args.output, outputFrom='topTenT')

                else:                    
                    resultMessage = "\n[+] APIs filtered by IP =>  Top 10 {0}"                    
                    resultToPrintTopTenByFrequencyOfHit, resultToPrintTopTenByTime = naviObj.getTopTenApis(ip=args.topTen)                     
                    
                    print resultMessage.format("as per frequency of hit")                    
                    naviObj.displayResults(resultToPrintTopTenByFrequencyOfHit, outputFormat=args.output, outputFrom='topTenH')
                    
                    print resultMessage.format("as per time")                    
                    naviObj.displayResults(resultToPrintTopTenByTime, outputFormat=args.output, outputFrom='topTenT')
            
            else:
                if args.limit:
                    resultMessage = "\n[+] APIs unfiltered =>  Top {0} {1}"                    
                    resultToPrintTopTenByFrequencyOfHit, resultToPrintTopTenByTime = naviObj.getTopTenApis(limit=args.limit) 

                    print resultMessage.format(args.limit, "as per frequency of hit")                    
                    naviObj.displayResults(resultToPrintTopTenByFrequencyOfHit, outputFormat=args.output, outputFrom='topTenH')
                    
                    print resultMessage.format(args.limit, "as per time")                    
                    naviObj.displayResults(resultToPrintTopTenByTime, outputFormat=args.output, outputFrom='topTenT')                    

                else:
                    resultMessage = "\n[+] APIs unfiltered =>  Top 10 {0}"                    
                    resultToPrintTopTenByFrequencyOfHit, resultToPrintTopTenByTime = naviObj.getTopTenApis()                     

                    print resultMessage.format("as per frequency of hit")                    
                    naviObj.displayResults(resultToPrintTopTenByFrequencyOfHit, outputFormat=args.output, outputFrom='topTenH')
                    
                    print resultMessage.format("as per time")
                    naviObj.displayResults(resultToPrintTopTenByTime, outputFormat=args.output, outputFrom='topTenT')
        
        print "\n"                    

    except CommandLineErrors as e:
        allLinesRead = None
        message = "Command line error => "
        errorCode = e.errorCode
        message += e.errorMessage
        print message    

    except Exception as e:
        message = "Inside system generated exception => "
        errorCode = -1        
        message += str(e)    
        print message    