def acq_basic_test():
    # import import
    import_sample_info()
    # test ct
    xrun(0, 0)
    # tsereis, 2s expo, 1s delay, 5 repeats
    xrun(0, ScanPlan(bt, tseries, 2, 1, 5))
    # Tramp, 2s expo, from 295k to 305k with 2k step
    xrun(0, ScanPlan(bt, Tramp, 2, 295, 305, 2))
    # Tlist 2s expo, 305k, 300k, 295k
    xrun(0, ScanPlan(bt, Tlist, 2, [305, 300, 295]))

