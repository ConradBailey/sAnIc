#!/usr/bin/env python3.6

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import argparse
import json

def make_rewards(exp_name, df, out_dir):
  ax = df.plot.line(x='Timesteps', y='Mean Reward', color='blue', legend=False)
  ax = df.plot.scatter(x='Timesteps', y='r', ax=ax, color='green', legend=False)
  ax.set_title('{}: Rewards vs Timesteps'.format(exp_name))
  ax.set_ylabel('Rewards')
  ax.legend(labels=['mean','data'], loc='upper center', bbox_to_anchor=(.8,-.1), ncol=2)

  ax.get_figure().savefig(os.path.join(out_dir,'rewards.svg'), bbox_inches='tight')
  return ax


def make_hists(exp_name, df, out_dir):
  ax = df['r'].to_frame().plot.hist(range=(0,10000), grid=True, ax=None, legend=False)
  ax.set_xlabel('Episodic Reward')
  ax.set_xticks(range(0,11000,1000))
  ax.set_title('{}: Rewards Histogram'.format(exp_name))

  ax.get_figure().savefig(os.path.join(out_dir,'histogram.svg'))
  return ax


def make_stats(exp_name, df, out_dir):
  stats = {
    'Title': exp_name,
    'Number of Episodes': len(df['r']),
    'Reward': {
      'Total': float(df['r'].sum()),
      'Max': float(df['r'].max()),
      'Min': float(df['r'].min()),
      'Mean': float(df['r'].mean()),
      'Median': float(df['r'].median()),
      'Std Dev': float(df['r'].std()),
      'Variance': float(df['r'].var())
    },
    'Timesteps': {
      'Total': float(df['l'].sum()),
      'Max': float(df['l'].max()),
      'Min': float(df['l'].min()),
      'Mean': float(df['l'].mean()),
      'Median': float(df['l'].median()),
      'Std Dev': float(df['l'].std()),
      'Variance': float(df['l'].var())
    }
  }
  json.dump(stats, open(os.path.join(out_dir, 'stats.json'), 'w'))

  return stats



def make_webpage(exp_name, out_dir, observed_stats):
  categories = ['Reward','Timesteps']
  stats = ['Total', 'Max', 'Min', 'Mean', 'Median', 'Std Dev', 'Variance']

  page = '<h1>{}</h1>\n\n'.format(exp_name)

  # Stats
  page += '<div id=stats>\n'
  page += '  <h2>Stats</h2>\n'
  page += '  <table border="1">\n'
  page += '    <tr><td><b>Number of</br>Episodes</b></td><td colspan="2">{}</td></tr>'.format(observed_stats['Number of Episodes'])
  page += '    <tr><td></td>'
  for category in categories:
    page += '<td><b>{}</b></td>'.format(category)
  page += '</tr>\n'
  for stat in stats:
    page += '    <tr><td><b>{}</b></td>'.format(stat)
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

  open(os.path.join(out_dir, 'analysis.html'), 'w').write(page)
  return page


def analyze(args):
  monitor_path = args.monitor_path
  out_dir, _ = os.path.split(monitor_path)

  exp_name = args.experiment_name

  df = pd.read_csv(monitor_path)
  df['Mean Reward'] = df['r'].expanding().mean()
  df['Timesteps'] = df['l'].expanding().sum()

  make_rewards(exp_name, df, out_dir)
  make_hists(exp_name, df, out_dir)
  stats = make_stats(exp_name, df, out_dir)
  make_webpage(exp_name, out_dir, stats)

def init_parser():
  parser = argparse.ArgumentParser(description="Statistically analyze a monitor.csv produced by local_eval.py")
  parser.add_argument('monitor_path', type=str, help='Location of monitor.csv file to analyze')
  parser.add_argument('experiment_name', type=str, help='Name of the experiment that produced the results')
  return parser


def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)
  sys.exit(analyze(args))


if __name__ == "__main__":
  main()
