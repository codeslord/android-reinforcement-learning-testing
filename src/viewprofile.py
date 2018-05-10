import pstats
p = pstats.Stats('profile.tmp')
p.sort_stats('cumulative').print_stats(100)