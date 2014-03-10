#!/usr/bin/env python
'Process the output logfile from ioping.py'
import logging
import os
import sys

import numpy

def read_logfile(filename):
  readings = []
  try:
    with open(filename, 'r') as logfile:
      for line in logfile:
        time, reading = line.split(': ')
        readings.append([int(time), float(reading)])
  except IOError:
    logging.error('Unable to open file: args=%r', args)
    raise
  return readings

def print_title(title):
  print title
  print '=' * len(title)

def print_distribution_stats(readings_array):
  print 'Minimum: %0.3f' % readings_array.min()
  print 'Maximum: %0.3f' % readings_array.max()
  print 'Mean: %0.3f' % readings_array.mean()
  print 'Deviation: %0.3f' % readings_array.std()
  print 'Median: %0.3f' % numpy.percentile(readings_array, 50)
  print '80th Percentile: %0.3f' % numpy.percentile(readings_array, 80)
  print

def print_histogram(readings_array):
  (bins, edges) = numpy.histogram(readings_array, bins=10)
  scale = 50.0 / max(bins)
  for i in range(len(bins)):
    print '[%10.3f] [%10d] %s' % (edges[i], bins[i], '*' * int(bins[i]*scale))
  print

def main(args):
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  readings = read_logfile(args[0])
  readings_array = numpy.array(readings)[:,1]

  print_title('Distribution details')
  print_distribution_stats(readings_array)

  print_title('Full distribution histogram')
  print_histogram(readings_array)

  eighty_twenty = numpy.percentile(readings_array, 80)

  print_title('Distribution of 80th percentile')
  print_histogram(
    [value for value in readings_array if value <= eighty_twenty])

  print_title('Distribution of remainder')
  print_histogram(
    [value for value in readings_array if value > eighty_twenty])

if __name__ == '__main__':
  main(sys.argv[1:])
