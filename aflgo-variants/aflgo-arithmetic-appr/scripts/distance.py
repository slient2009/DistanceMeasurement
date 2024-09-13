#!/usr/bin/env python3

import argparse
import collections
import functools
import networkx as nx


class memoize:
  # From https://github.com/S2E/s2e-env/blob/master/s2e_env/utils/memoize.py

  def __init__(self, func):
    self._func = func
    self._cache = {}

  def __call__(self, *args):
    if not isinstance(args, collections.abc.Hashable):
      return self._func(args)

    if args in self._cache:
      return self._cache[args]

    value = self._func(*args)
    self._cache[args] = value
    return value

  def __repr__(self):
    # Return the function's docstring
    return self._func.__doc__

  def __get__(self, obj, objtype):
    # Support instance methods
    return functools.partial(self.__call__, obj)


#################################
# Get graph node name
#################################
def node_name (name):
  if is_cg:
    return "\"{%s}\"" % name
  else:
    return "\"{%s:" % name

#################################
# Find the graph node for a name
#################################
@memoize
def find_nodes (name):
  n_name = node_name (name)
  return [n for n, d in G.nodes(data=True) if n_name in d.get('label', '')]

##################################
# Calculate Distance
##################################
def distance (name):
  # print("calc the distance of BB/Func %s" % (name))
  # print("initial bb_distance: ", bb_distance)
  if not is_cg and name in bb_distance.keys(): # 这里都要把function distance和basic block distance合在一起吗？是的，问就是代码复用，但是也不是高度代码复用啊....
    out.write(name)
    out.write(",")
    out.write(str(10 * bb_distance[name])) # woc，记忆化搜索？# 已经在bb_distance中的就直接输出了
    out.write("\n")
    return
  distance = -1
  # print("find_nodes (name): ", find_nodes (name))
  for n in find_nodes (name): # 根据name从networkx格式数据库中检索出对应的Node对象， 因为aflgo目前没有处理基本块重名问题，所以这里的find_nodes似乎会查出那些同名的基本块
    # 为什么这里的返回值可能是列表，会查出来多个Node对象吗？ 当查的是基本块，使用的name是前缀，可能返回一个列表，包含前缀名相同的若干基本块
    # print("n in find_nodes (name):", n)
    d = 0.0
    i = 0

    if is_cg:
      for t in targets: # 枚举计算当前函数n到多个targets的多条最短路长度
        try:
          shortest = nx.dijkstra_path_length (G, n, t)
          # print("shortest(%s, %s) found with %d" % (n, t, shortest))
          # d += 1.0 / (1.0 + shortest) # 距离数值从1开始，避免除零操作。
          d += (1.0 + shortest) # 这里尝试使用算数平均值，距离数值从1开始，避免除零操作。
          i += 1
        except nx.NetworkXNoPath:
          pass
    else:
      for t_name, bb_d in bb_distance.items(): # 经过主函数过程中的初始化，bb_distance中已经包含了所有的可以到达target的基本块
        di = 0.0
        ii = 0
        # print("enumerate t_name=", t_name)
        for t in find_nodes(t_name): # 对于当前CFG中的每一个BB，枚举可达target的基本块，相当于是尝试枚举出口函数。
          try:
            if(n==t):
              shortest=0
            else:
              shortest = nx.dijkstra_path_length(G, n, t)
            # di += 1.0 / (1.0 + 10 * bb_d + shortest) 
            di += 1.0 + 10 * bb_d + shortest # 尝试使用算术平均值
            ii += 1
            # print("%s -> %s -> targets : %f" % (n, t, shortest))
          except nx.NetworkXNoPath:
            pass
        if ii != 0:
          d += di / ii
          i += 1

    if d != 0 and (distance == -1 or distance > d / i) : # 会在所有同名基本块中选出一个最小值，理论上这是不对滴。
      # distance = i / d # 这里似乎能够解释为什么样例的distance值是按照调和平均值算出来的整数倍，按照标准的调和平均值应该有i=1
      distance = d / i # 尝试使用算术平均值

  if distance != -1:
    out.write (name)
    out.write (",")
    out.write (str (distance))
    out.write ("\n")

##################################
# Main function
##################################
if __name__ == '__main__':
  parser = argparse.ArgumentParser ()
  parser.add_argument ('-d', '--dot', type=str, required=True, help="Path to dot-file representing the graph.") # 目标CFG对应的cfg.*.dot文件  /  callgraph.dot
  parser.add_argument ('-t', '--targets', type=str, required=True, help="Path to file specifying Target nodes.") # BBtargets.txt  /  Ftargets.txt
  parser.add_argument ('-o', '--out', type=str, required=True, help="Path to output file containing distance for each node.") # 目标CFG中基本块距离数据的输出文件  /  callgraph.distance.txt
  parser.add_argument ('-n', '--names', type=str, required=True, help="Path to file containing name for each node.") # BBnames.txt  /  Fnames.txt
  parser.add_argument ('-c', '--cg_distance', type=str, help="Path to file containing call graph distance.") # callgraph.distance.txt  /  None
  parser.add_argument ('-s', '--cg_callsites', type=str, help="Path to file containing mapping between basic blocks and called functions.") # BBcalls.txt  /  None

  args = parser.parse_args ()

  print ("\nParsing %s .." % args.dot)
  G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(args.dot))
  print (nx.info(G))

  is_cg = "Call graph" in nx.info(G)
  print ("\nWorking in %s mode.." % ("CG" if is_cg else "CFG"))

  # Process as ControlFlowGraph
  caller = ""
  cg_distance = {}
  bb_distance = {}
  if not is_cg :

    if args.cg_distance is None:
      print ("Specify file containing CG-level distance (-c).")
      exit(1)

    elif args.cg_callsites is None:
      print ("Specify file containing mapping between basic blocks and called functions (-s).")
      exit(1)

    else:

      caller = args.dot.split(".")
      caller = caller[len(caller)-2]
      print ("Loading cg_distance for function '%s'.." % caller) # caller是当前的工作目标函数

      with open(args.cg_distance, 'r') as f: # 加载callgraph distance文件
        for l in f.readlines():
          s = l.strip().split(",")
          cg_distance[s[0]] = float(s[1])

      if not cg_distance:
        print ("Call graph distance file is empty.") # 程序怎么都得有个函数吧，有函数就有距离
        exit(0)
      
      print("cg_distance: ", cg_distance)

      # 枚举callsites，也就是出口函数。
      with open(args.cg_callsites, 'r') as f:
        for l in f.readlines():
          s = l.strip().split(",") # 每一行的形式是 xyz.c:123,xxfunc
          if find_nodes(s[0]):
            if s[1] in cg_distance: # 当前基本块call了一个func，也许func在CG中，可以作为一个出口函数
              if s[0] in bb_distance: 
                if bb_distance[s[0]] > cg_distance[s[1]]: # 也许会call多个func，所以要不断更新记录一个最优的出口函数
                  bb_distance[s[0]] = cg_distance[s[1]]
              else:
                bb_distance[s[0]] = cg_distance[s[1]] # 如果当前基本块还没有距离值，就用call的func的CG距离值来初始化

      print("initial bb_distance: ", bb_distance)
      print ("Adding target BBs (if any)..")
      with open(args.targets, "r") as f:
        for l in f.readlines ():
          s = l.strip().split("/")
          line = s[len(s) - 1]
          if find_nodes(line):
            bb_distance[line] = 0
            print ("Added target BB %s!" % line)
          # print("bb_distance: ", bb_distance)

  # Process as CallGraph
  else:

    print ("Loading targets..")
    with open(args.targets, "r") as f:
      targets = []
      for line in f.readlines ():
        line = line.strip ()
        for target in find_nodes(line):
          targets.append (target)
          print("Ftarget %s is found in G" % (target))

    if (not targets and is_cg):
      print ("No targets available")
      exit(0)

  print ("Calculating distance..")
  with open(args.out, "w") as out, open(args.names, "r") as f:
    for line in f.readlines():
      distance (line.strip()) # 枚举所有 函数名/基本块名，计算到 目标函数/目标基本块 的距离 
