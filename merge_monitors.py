#!/usr/bin/env python3.6

import pandas as pd
import numpy as np
from statistics import mean
import sys
import argparse


def get_dfs(monitors):
  dfs = [pd.read_csv(monitor) for monitor in monitors]
  for df in dfs:
    df['Timesteps'] = df['l'].expanding().sum()
  return dfs


def merge_monitor_dfs(dfs):
  def picker(l,r):
    if np.isnan(l):
      return r
    elif np.isnan(r):
      return l
    else:
      return mean([l,r])

  merged = pd.DataFrame(dfs[0][['r','l','Timesteps']]).set_index('Timesteps')
  for df in dfs[1:]:
    other = pd.DataFrame(df[['r','l','Timesteps']]).set_index('Timesteps')
    merged = pd.merge(merged, other, left_index=True, right_index=True, how='outer')
    tmp = pd.DataFrame()
    tmp['r'] = merged['r_x'].combine(merged['r_y'], picker)
    tmp['l'] = merged['l_x'].combine(merged['l_y'], picker)
    merged = tmp
  merged.reset_index(inplace=True)
  return merged


def merge_monitors(output_name, monitor_paths):
  dfs = get_dfs(monitor_paths)
  merged = merge_monitor_dfs(dfs)
  csv = merged.to_csv(columns=['r','l','Timesteps'], index=False)
  if output_name:
    open(output_name, 'w').write(csv)
  else:
    print(csv)


def init_parser():
  parser = argparse.ArgumentParser(description="Merge multiple monitor.csv files into a single monitor.csv. If two or more rewards are recorded on the same timestep, then their mean reward and length is reported.")
  parser.add_argument('monitors', type=str, nargs='+', help='List of monitor.csv files to merge')
  parser.add_argument('-o', type=str, default=None, help='Place output here. Default is stdout')
  return parser


def main(argv=sys.argv[1:]):
  parser = init_parser()
  args = parser.parse_args(argv)
  sys.exit(merge_monitors(args.o, args.monitors))


if __name__ == "__main__":
  main()
