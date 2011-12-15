import patternatom
import util
import collections
import logging

max_trials = 8 # algorithm is exponential in this number! Can be tweaked up and down, distinguishes best of the correct choices but not overall correctness
        
def best(patterns,extended):
    # Enumberate daytimes
    dts = collections.defaultdict(set)
    all = []
    for p in patterns:
        all.extend(p[0].each())
    for p in all:
        for dt in p.getDayTimesRaw():
            dts[dt.data()].add(p)
    # For each daytime, iterate patterns to find termweeks
    dt_tw = {}
    dt_tw_sz = {}
    for (dt,ps) in dts.iteritems():
        tws = collections.defaultdict(set)
        for p in ps:
            for (term,week) in p.getTermWeeks().each():
                tws[term].add(week)
        dt_tw[dt] = tws
        dt_tw_sz[dt] = reduce(lambda tot,item: tot+len(item),tws.itervalues(),0)
    # restrict to at most max_trials (longest)
    dt_use = set()
    dt_candidates = dt_tw.keys()
    for i in range(0,max_trials):
        if len(dt_candidates) == 0:
            break
        use = max(dt_candidates,key = lambda k: dt_tw_sz[k])
        dt_candidates.remove(use)
        dt_use.add(use)
    # find longest range of each, using 1-8,9-16,17-24 type ranges to allow term overlap
    dt_longest = {}
    for dt in dt_use:
        # build termy week numbers (1-24)
        week_nums = set()
        for (term,weeks) in dt_tw[dt].iteritems():
            for week in filter(lambda x: x>0 and x<9,weeks):
                week_nums.add(term*8+week)
        ranges = sorted(util.ranges(week_nums),key = lambda x: x[1],reverse = True)
        if len(ranges) == 0:
            dt_longest[dt] = set()
        else:
            dt_longest[dt] = set(range(ranges[0][0],ranges[0][0]+ranges[0][1]))
    # permute through including and excluding date ranges to see which gives best coverage (EXPONENTIAL!)
    best_score = None
    best = None
    for dts in util.powerset(dt_use):
        if len(dts) == 0:
            continue
        all = set(range(1,25))
        for dt in dts:
            all &= dt_longest[dt]
        score = len(all) * len(dts)
        if best_score == None or score > best_score:
            best_score = score
            best = dts
    # Generate pattern
    if best is None:
        logger.error("No common in %s" % all)
        return None
    p = patternatom.PatternAtom(False)
    for b in best:
        p.addDayTimeRange(b[0],b[1][0],b[1][1],b[2][0],b[2][1])
    p.setAllYear()
    # Extend to include out-of-term dates, where required
    if extended:
        for q in patterns:
            for qa in q[0].blast():
                p.expand_back_to(qa)
                p.expand_forward_to(qa)
    return p
