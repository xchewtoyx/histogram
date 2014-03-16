#!/usr/bin/env python
'Process the output logfile from ioping.py'
from argparse import ArgumentTypeError
import re

from cement.core import controller, foundation, handler
from numpy.core.multiarray import array
from numpy.lib.function_base import histogram, percentile

def zoom_type(zoom_string):
  # Allow an empty string to disable zoom
  if not zoom_string:
    zoom_string = '0:100'
  try:
    if ':' not in zoom_string:
      raise ValueError
    zoom_intervals = []
    for interval_string in zoom_string.split(':'):
      interval = int(interval_string)
      if interval < 0:
        raise ValueError
      zoom_intervals.append(interval)
    if sum(zoom_intervals) != 100:
      raise ValueError
  except (AssertionError, ValueError):
    raise ArgumentTypeError(
      'Zoom must be a colon separated list of positive integers and must '
      'total to 100.')
  return zoom_intervals

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
      (['--zoom'], {
        'help': (
          'Zoom in on certain percentile bands.  This is a colon separated '
          'list of positive integers that must sum to 100.  For example '
          'the default of 80:20 will display a distribution of the 80th '
          'centile and then a distribution of the remainder. 10:80:10 '
          'would display three distributions, distribution of values in '
          'the 10th centile, the 11-90th centile and the 91-100th centile. '
          'To disable zoom provide an empty string to this argument, or a '
          'valid distribution starting with 0: (e.g. 0:100).'
        ),
        'action': 'store',
        'default': [80, 20],
        'type': zoom_type,
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

  def _print_zoom_histograms(self):
    if self.app.pargs.zoom[0] == 0:
      return

    interval_start = 0
    # set the initial minimum to less than the input minimum
    # makes the condition match easier (min < x <= max)
    min_value = self.readings_array.min() - 1
    for interval_width in self.app.pargs.zoom:
      interval_end = interval_start + interval_width
      title = 'Distribution of values in percentile range %d - %d' % (
        interval_start, interval_end)

      def value_in_interval(value):
        if interval_start < value <= interval_end:
          return value

      self._print_histogram(title, condition=value_in_interval)
      interval_start = interval_end

  @controller.expose(hide=True, aliases=['run'])
  def default(self):
    'Base controller for application.'
    readings = self._read_logfile()
    self.readings_array = array(readings)[:, 0]

    self._print_distribution_stats()
    self._print_histogram('Full distribution histogram')
    self._print_zoom_histograms()


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
