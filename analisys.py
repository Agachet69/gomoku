import pstats

stats = pstats.Stats("main.prof")
stats.strip_dirs().sort_stats('cumtime').print_stats(100)