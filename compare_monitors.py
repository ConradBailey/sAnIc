#!/usr/bin/env python3.6

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import argparse

from analyze_monitor import make_stats


def get_colors(n):
  return iter(plt.cm.rainbow(np.linspace(0,1,n)))


def make_histogram(output_dir, title, labels, dfs):
  colors = get_colors(len(labels))
  ax = None
  for df in dfs:
    ax = df.hist(column='r',range=(0,10000), color=next(colors), grid=True, alpha=.5, ax=ax)[0]
  ax.set_xlabel('Episodic Reward')
  ax.set_xticks(range(0,11000,1000))
  ax.set_title('{}: Rewards Histogram'.format(title))
  ax.legend(labels=labels, loc='upper right', bbox_to_anchor=(1.37,1))
  return ax


def make_mean_rewards(output_dir, title, labels, dfs):
  colors = get_colors(len(labels))
  ax = None
  for df in dfs:
    ax = df.plot.line(x='Timesteps', y='Mean Reward', c=next(colors), ax=ax, legend=False)
  ax.set_title('{}: Mean Reward vs Timesteps'.format(title))
  ax.set_ylabel('Mean Reward')
  ax.legend(labels=labels, loc='upper right', bbox_to_anchor=(1.37,1))
  return ax


def make_webpage(title, list_of_stats):
  categories = ['Reward','Timesteps']
  stats = ['Total', 'Max', 'Min', 'Mean', 'Median', 'Std Dev', 'Variance']

  page = '<h1>{}</h1>\n\n'.format(title)

  # Stats
  page += '<div id=stats>\n'
  page += '  <h2>Stats</h2>\n'
  page += '  <table border="1">\n'

  ## Experiment Names
  page += '    <tr><td></td>'
  for observed_stats in list_of_stats:
    page += '<td colspan="2"><b>{}</b></td>'.format(observed_stats['Title'])
  page += '</tr>\n'

  ## Number of Episodes
  page += '    <tr><td><b>Number of</br>Episodes</b></td>'
  for observed_stats in list_of_stats:
    page += '<td colspan="2">{}</td>'.format(observed_stats['Number of Episodes'])
  page += '</tr>\n'

  ## Descriptive Stats
  ### Headers
  page += '    <tr><td></td>'
  for observed_stats in list_of_stats:
    for category in categories:
      page += '<td><b>{}</b></td>'.format(category)
  page += '</tr>\n'
  ### Values
  for stat in stats:
    page += '    <tr><td><b>{}</b></td>'.format(stat)
    for observed_stats in list_of_stats:
      for category in categories:
        page += '<td>%.2f</td>' % observed_stats[category][stat]
    page += '</tr>\n'

  page += '  </table>\n'
  page += '</div>\n\n'

  # Graphs
  page += '<div id=graphs>\n'
  page += '  <h2>Graphs</h2>\n'
  for graph in ['rewards.svg','histogram.svg']:
    page += '<img src="{}">'.format(graph)

  return page


def compare(output_dir, comparison_name, experiments):
  dfs = [pd.read_csv(path) for name, path in experiments]
  labels = [name for name, path in experiments]

  for df in dfs:
    df['Mean Reward'] = df['r'].expanding().mean()
    df['Timesteps'] = df['l'].expanding().sum()

  ax = make_mean_rewards(output_dir, comparison_name, labels, dfs)
  ax.get_figure().savefig(os.path.join(output_dir,'rewards.svg'), bbox_inches='tight')

  ax = make_histogram(output_dir, comparison_name, labels, dfs)
  ax.get_figure().savefig(os.path.join(output_dir,'histogram.svg'), bbox_inches='tight')

  list_of_stats = [make_stats(label, df) for label, df in zip(labels, dfs)]
  page = make_webpage(comparison_name, list_of_stats)
  open(os.path.join(output_dir, 'analysis.html'), 'w').write(page)


def init_parser():
  parser = argparse.ArgumentParser(description="Statistically and graphically compare monitor.csv files produced by local_eval.py")
  parser.add_argument('output_dir', type=str, help='Directory where output files will be created')
  parser.add_argument('comparison_name', type=str, help='A title describing this comparison')
  parser.add_argument('experiments', type=str, nargs='+', help='Alternating list of experiment names and their associated monitor.csv path, e.g. "exp name 1" path1 "exp name 2" path2 ... ')
  return parser


def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)

  if (len(args.experiments) % 2) != 0:
    raise ValueError("Odd number of experiment args detected. Every experiment name requires a monitor.csv path")

  sys.exit(compare(args.output_dir, args.comparison_name,
                   list(zip(args.experiments[::2],args.experiments[1::2]))))


if __name__ == "__main__":
  main()
