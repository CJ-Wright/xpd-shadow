from xpdacq.utils import import_sample_info, _import_sample_info
from xpdacq.beamtime import ScanPlan, tseries, Tramp, Tlist
from xpdan.pipelines.main import conf_main_pipeline
from shed.event_streams import istar
from bluesky.callbacks.core import CallbackBase
from pprint import pprint
import yaml
import os


class DBCheckCallback(CallbackBase):
    def __init__(self, db):
        self.db = db
        self.docs = []

    def __call__(self, name, doc):
        self.docs.append(doc)
        return getattr(self, name)(doc)

    def stop(self, doc):
        db_docs = [y for x, y in self.db[-1].documents()]
        assert len(db_docs) == len(self.docs)
        for a, b in zip(db_docs, self.docs):
            pprint(a)
            pprint(b)
            for k in set(a.keys()) | set(b.keys()):
                assert a[k] == b[k]


def test_acq_basic(fresh_xrun, bt, db):
    xrun = fresh_xrun
    # import import
    # if beamline run this, else run underscore
    # import_sample_info()
    _import_sample_info(saf_num=300000, bt=bt)
    xrun.beamtime = bt
    xrun.subscribe(print)
    # xrun.subscribe(DBCheckCallback(db))
    for sp in [0,
               ScanPlan(bt, tseries, 2, 1, 5),
               ScanPlan(bt, Tramp, 2, 295, 305, 2),
               ScanPlan(bt, Tlist, 2, [305, 300, 295])
               ]:
        xrun(0, sp)
    img = next(db[-1].data('pe1_image', fill=True))
    print(img.shape)
    AAA


def test_acq_basic_pipeline(fresh_xrun, bt, db, glbl):
    xrun = fresh_xrun
    s = conf_main_pipeline(db, glbl['tiff_base'],
                           calibration_md_folder=glbl['config_base'],
                           write_to_disk=True,
                           vis=False,
                           verbose=True)
    # import import
    _import_sample_info(saf_num=300000, bt=bt)
    xrun.beamtime = bt
    xrun.subscribe(istar(s.emit))
    xrun.subscribe(istar(pprint))
    tiff_files = set()
    for sp, ntiff in zip([0,
                          ScanPlan(bt, tseries, 2, 1, 5),
                          ScanPlan(bt, Tramp, 2, 295, 305, 2),
                          ScanPlan(bt, Tlist, 2, [305, 300, 295])
                          ], [1, 5, 6, 3]):
        xrun(0, sp)
        new_tiffs = []
        for root, dir, files in os.walk(glbl['tiff_base']):
            new_tiffs.extend([f for f in files if f.endswith('.tiff')])
        new_tiffs = set(new_tiffs)
        assert len(new_tiffs - tiff_files) == ntiff
        for e in new_tiffs:
            tiff_files.add(e)


def test_acq_basic_pipeline_cal(fresh_xrun, bt, db, glbl, cal_yaml):
    with open(os.path.join(glbl['config_base'], glbl['calib_config_name']),
              'w') as f:
        yaml.dump(cal_yaml, f)
    xrun = fresh_xrun
    s = conf_main_pipeline(db, glbl['tiff_base'],
                           calibration_md_folder=glbl['config_base'],
                           write_to_disk=True,
                           vis=False,
                           verbose=True)
    # import import
    _import_sample_info(saf_num=300000, bt=bt)
    xrun.beamtime = bt
    xrun.subscribe(istar(s.emit))
    xrun.subscribe(istar(pprint))
    tiff_files = set()
    for sp, ntiff in zip([0,
                          ScanPlan(bt, tseries, 2, 1, 5),
                          ScanPlan(bt, Tramp, 2, 295, 305, 2),
                          ScanPlan(bt, Tlist, 2, [305, 300, 295])
                          ], [1, 5, 6, 3]):
        xrun(0, sp)
        new_tiffs = []
        for root, dir, files in os.walk(glbl['tiff_base']):
            new_tiffs.extend([f for f in files if f.endswith('.tiff')])
        new_tiffs = set(new_tiffs)
        assert len(new_tiffs - tiff_files) == ntiff
        for e in new_tiffs:
            tiff_files.add(e)
