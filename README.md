A simple python command line utility to parse Apache & Nginx logs. Gives top hits by IP

logProcessor.py -h
usage: logProcessor.py [-h] [-fq | -tt [filter_by_ip]]
                       [-tp start_date end_date] [-l limit_by_value]
                       logFile

A python utility to get certain patterns from Nginx & Apache log files

positional arguments:
  logFile               Apache or Nginx log file to process. Full path if in
                        another location or just the file name if it is in the
                        same location from where the script is being executed

optional arguments:
  -h, --help            show this help message and exit
  -fq, --ipWithFreq     get a list of all ips with frequency
  -tt [filter_by_ip], --topTen [filter_by_ip]
                        list the top 10 API / URL endpoints hit by the
                        provided IP address
  -tp start_date end_date, --timePeriod start_date end_date
                        list the top n API / URL endpoints between the 2 time
                        stamps. 1st arg = start date & 2nd arg = end date.
                        Format for both should be %d/%b/%Y:%H:%M:%S e.g.
                        17/May/2015:09:05:00 . n = 10 by default. n can be
                        specified by the -l or --limit switch
  -l limit_by_value, --limit limit_by_value
                        limit results of top hits. It should be a positive
                        integer only. Default is 10
