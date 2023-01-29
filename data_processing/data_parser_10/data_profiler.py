import pstats
import cProfile
from data_parser_10 import main

cProfile.run("main()", "data_parser_10.stats")
stats = pstats.Stats("data_parser_10.stats")
stat = stats.sort_stats("time").print_stats(100)
open("profile.txt", "w").write(str(stat))
