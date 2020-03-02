# ApaGixLogProcessor
A simple python command line utility to parse Apache & Nginx logs. Gives top hits by IP

    python logProcessor.py -h
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

                        
### Output
- Currently ouputs to stdout
- Example: using the sample apache_logs.txt included in the repo
> python logProcessor.py apache_logs.txt -tt 120.202.255.147 -l30 -tp
> 17/May/2015:09:05:00 27/May/2015:09:05:00

    [+] APIs filtered by IP =>  Top 30 as per frequency of hit
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', 10)
    
    [+] APIs filtered by IP =>  Top 30 as per time
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '20/May/2015:17:05:26')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '20/May/2015:08:05:41')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '19/May/2015:22:05:55')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '19/May/2015:12:05:19')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '19/May/2015:02:05:37')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '18/May/2015:19:05:27')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '18/May/2015:13:05:55')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '18/May/2015:06:05:33')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '18/May/2015:00:05:57')
    ('120.202.255.147 - /files/logstash/logstash-1.1.0-monolithic.jar', '17/May/2015:16:05:39')

### Requirements
Uses only standard libraries. No external pip installs needed. Simply clone the repo & run as shown in the example

### Few things to remember
- ipWithFreq & topTen are 2 mutually exclusive params, as they provide two completely different functionalities
- tt/topTen also accepts an optional ip address as argument based on which results can be filtered
- for time period parameter, date format is of type : 17/May/2015:09:05:00
- for time period parameter, start date must be less than end date
- all of these are also mentioned in the readme that can be pulled up using -h 
