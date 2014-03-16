#!/usr/bin/env python
'Process the output logfile from ioping.py'
import re

from cement.core import controller, foundation, handler
from numpy.core.multiarray import array
from numpy.lib.function_base import histogram, percentile

class HistogramBaseController(controller.CementBaseController):
  'Controller for histogram app.'
  class Meta:
    # pylint doesn't like the way that cement Meta classes work...
    # pylint: disable=C1001, W0232, C0111, R0903
    label = 'base'
    arguments = [
      (['-i', '--input_file'], {
        'help': 'Input file to read data from',
        'action': 'store',
        'required': True,
      }),
      (['-p', '--pattern'], {
        'help': ('Regular expression containing a match group identifying '
                 'the value to plot the histogram for.'),
        'action': 'store',
        'required': True,
      }),
      (['-b', '--bins'], {
        'help': 'Number of bins to display in histogram',
        'action': 'store',
        'default': 10,
        'type': int,
      }),
    ]

  def __init__(self):
    super(HistogramBaseController, self).__init__()
    self.readings_array = array([])

  def _read_logfile(self):
    'Read in the input_file and match lines against pattern'
    readings = []
    reading_pattern = re.compile(self.app.pargs.pattern)
    try:
      with open(self.app.pargs.input_file, 'r') as logfile:
        for line in logfile:
          match = reading_pattern.match(line)
          readings.append([float(m) for m in match.groups()])
    except IOError:
      self.app.log.error('Unable to open file: args=%r' %
                         self.app.pargs.input_file)
      raise
    return readings

  def _print_title(self, title):
    'helper funtion, print title underlined with a row of = characters.'
    print title
    print '=' * len(title)

  def _print_histogram(self, title, condition=lambda x: True):
    'Display a histogram for readings matching condition.'
    self._print_title(title)
    readings = [
      reading for reading in self.readings_array if condition(reading)
    ]
    (bins, edges) = histogram(readings, bins=self.app.pargs.bins)
    scale = 50.0 / max(bins)
    for bin_edge, bin_value in zip(edges, bins):
      print '[%10.3f] [%10d] %s' % (bin_edge, bin_value,
                                    '*' * int(bin_value*scale))
    print

  def _print_distribution_stats(self):
    'Print a summary table of distribution stats.'
    self._print_title('Distribution stats')
    print 'Minimum: %0.3f' % self.readings_array.min()
    print 'Maximum: %0.3f' % self.readings_array.max()
    print 'Mean: %0.3f' % self.readings_array.mean()
    print 'Deviation: %0.3f' % self.readings_array.std()
    print 'Median: %0.3f' % percentile(self.readings_array, 50)
    print '80th Percentile: %0.3f' % percentile(self.readings_array, 80)
    print

  @controller.expose(hide=True, aliases=['run'])
  def default(self):
    'Base controller for application.'
    readings = self._read_logfile()
    self.readings_array = array(readings)[:, 0]

    self._print_distribution_stats()
    self._print_histogram('Full distribution histogram')

    eighty_twenty = percentile(self.readings_array, 80)

    self._print_histogram('Distribution of 80th percentile',
                          condition=lambda x: x <= eighty_twenty)

    self._print_histogram('Distribution of remainder',
                          condition=lambda x: x > eighty_twenty)


def main():
  'Initialise and execute the cement app.'
  histogram_app = foundation.CementApp('histogram')
  handler.register(HistogramBaseController)

  try:
    histogram_app.setup()
    histogram_app.run()
  finally:
    histogram_app.close()

if __name__ == '__main__':
  main()
