#!/usr/bin/env python
'Process the output logfile from ioping.py'
import logging
import os
import sys

import numpy

def main(args):
  readings = []
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  try:
    with open(args[0], 'r') as logfile:
      for line in logfile:
        time, reading = line.split(': ')
        readings.append([int(time), float(reading)])
  except IOError:
    logging.error('Unable to open file: args=%r', args)

  readings_array = numpy.array(readings)

  (bins, edges) = numpy.histogram(readings_array[:,1])

  scale = 50.0 / max(bins)

  for i in range(len(bins)):
    print '[%10.3f] [%10d] %s' % (edges[i], bins[i], '*' * int(bins[i]*scale))

if __name__ == '__main__':
  main(sys.argv[1:])
