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

def print_histogram(title, readings_array):
  print title
  print '=' * len(title)
  (bins, edges) = numpy.histogram(readings_array, bins=10)
  scale = 50.0 / max(bins)
  for i in range(len(bins)):
    print '[%10.3f] [%10d] %s' % (edges[i], bins[i], '*' * int(bins[i]*scale))
  print

def main(args):
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  readings = read_logfile(args[0])
  readings_array = numpy.array(readings)

  print_histogram('Full distribution', readings_array[:,1])

  eighty_twenty = numpy.percentile(readings_array[:,1], 80)

  print_histogram(
    'Distribution of 80th percentile',
    [value for value in readings_array[:,1] if value <= eighty_twenty])

  print_histogram(
    'Distribution of remainder',
    [value for value in readings_array[:,1] if value > eighty_twenty])

if __name__ == '__main__':
  main(sys.argv[1:])
