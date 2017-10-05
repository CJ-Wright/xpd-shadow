##############################################################################
#
# xpdan            by Billinge Group
#                   Simon J. L. Billinge sb2896@columbia.edu
#                   (c) 2016 trustees of Columbia University in the City of
#                        New York.
#                   All rights reserved
#
# File coded by:    Timothy Liu, Christopher J. Wright
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
import os
import sys
import shutil
import asyncio
import numpy as np
import yaml

import pytest

from xpdacq.xpdacq_conf import (glbl_dict,
                                configure_device,
                                xpd_configuration)

from xpdacq.xpdacq import CustomizedRunEngine
from xpdacq.beamtimeSetup import _start_beamtime
from xpdacq.utils import import_sample_info, ExceltoYaml
from xpdsim import cs700, xpd_pe1c, simple_pe1c, shctl1

from pkg_resources import resource_filename as rs_fn


@pytest.fixture(scope='module')
def db():
    from xpdsim import db
    yield db


@pytest.fixture(scope='module')
def bt(home_dir, db):
    # start a beamtime
    PI_name = 'Billinge '
    saf_num = 300000
    wavelength = 0.1812
    experimenters = [('van der Banerjee', 'S0ham', 1),
                     ('Terban ', ' Max', 2)]
    bt = _start_beamtime(PI_name, saf_num,
                         experimenters,
                         wavelength=wavelength)
    # spreadsheet
    pytest_dir = rs_fn('xpdacq', 'tests/')
    xlf = '300000_sample.xlsx'
    src = os.path.join(pytest_dir, xlf)
    shutil.copyfile(src, os.path.join(glbl_dict['import_dir'], xlf))
    import_sample_info(saf_num, bt)

    # set simulation objects
    # alias
    #pe1c = xpd_pe1c 
    pe1c = simple_pe1c
    configure_device(db=db, shutter=shctl1,
                     area_det=pe1c, temp_controller=cs700)
    yield bt


@pytest.fixture(scope='module')
def glbl(bt):
    from xpdacq.glbl import glbl
    yield glbl


@pytest.fixture(scope='module')
def fresh_xrun(bt):
    # create xrun
    xrun = CustomizedRunEngine(None)
    xrun.md['beamline_id'] = glbl_dict['beamline_id']
    xrun.md['group'] = glbl_dict['group']
    xrun.md['facility'] = glbl_dict['facility']
    xrun.ignore_callback_exceptions = False
    # link mds
    xrun.subscribe(xpd_configuration['db'].insert, 'all')
    yield xrun


@pytest.fixture(scope='function')
def exp_hash_uid(bt, fresh_xrun, glbl):
    fresh_xrun.beamtime = bt
    exp_hash_uid = glbl['exp_hash_uid']
    yield exp_hash_uid


@pytest.fixture(scope='module')
def home_dir():
    stem = glbl_dict['home']
    config_dir = glbl_dict['xpdconfig']
    archive_dir = glbl_dict['archive_dir']
    os.makedirs(stem, exist_ok=True)
    yield glbl_dict
    for el in [stem, config_dir, archive_dir]:
        if os.path.isdir(el):
            print("flush {}".format(el))
            shutil.rmtree(el)


@pytest.fixture(scope='function')
def zmq_proxy(fresh_xrun):
    # COMPONENT 1
    # Run a 0MQ proxy on a separate process.
    def start_proxy():
        Proxy(5567, 5568).start()

    proxy_proc = multiprocessing.Process(target=start_proxy, daemon=True)
    proxy_proc.start()
    time.sleep(5)  # Give this plenty of time to start up.

    # COMPONENT 2
    # Run a Publisher and a RunEngine in this main process.

    p = Publisher('127.0.0.1:5567', RE=fresh_xrun)  # noqa

    # COMPONENT 3
    # Run a RemoteDispatcher on another separate process. Pass the documents
    # it receives over a Queue to this process, so we can count them for our
    # test.

    d = RemoteDispatcher('127.0.0.1:5568')
    dispatcher_proc = multiprocessing.Process(target=make_and_start_dispatcher,
                                              daemon=True, args=(queue,))
    dispatcher_proc.start()
    time.sleep(5)  # As above, give this plenty of time to start.
    yield fresh_xrun, d, proxy_proc, dispatcher_proc
    p.close()
    proxy_proc.terminate()
    dispatcher_proc.terminate()
    proxy_proc.join()
    dispatcher_proc.join()
    assert remote_accumulator == local_accumulator


@pytest.fixture(scope='module')
def cal_yaml():
    yml = '''is_pytest: True
calibrant_name: Ni24
centerX: !!python/object/apply:numpy.core.multiarray.scalar
- &id001 !!python/object/apply:numpy.dtype
  args: [f8, 0, 1]
  state: !!python/tuple [3, <, null, null, null, -1, -1, 0]
- !!binary |
  u1dLU14uj0A=
centerY: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  XIRrFZNrj0A=
dSpacing:
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    8rtCHNNGAEA=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    G9gqweIw/D8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    5EYPEEzv8z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    zH5+PRsA8T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    8rtCHNNG8D8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    /tR46SYx7D8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    0xsrs+ne6T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    yXmujDc36T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    8S6gqccE5z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    136uJcSz5T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    5EYPEEzv4z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    VNvKdK8P4z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    RIJQRm/L4j8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    3+/dF4fU4T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    Vpn742sy4T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    +6F+PRsA4T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    Id9CHNNG4D8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    sSJWztOU3z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    0z02FbZG3z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    3L1JxHUj3j8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    BoRIyr5c3T8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    /tR46SYx3D8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    IvutPbmN2z8=
- !!python/object/apply:numpy.core.multiarray.scalar
  - *id001
  - !!binary |
    uflzd6pZ2z8=
detector: Perkin detector
directDist: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  PkhCH0Zaa0A=
dist: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  WBS6ty0CzD8=
poni_file_name: /home/timothy/xpdUser/config_base/20170822-190241_pyFAI_calib_Ni24.poni
pixel1: 0.0002
pixel2: 0.0002
pixelX: 200.0
pixelY: 200.0
poni1: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  v2bqxnzJyT8=
poni2: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  wuhgu+O3yT8=
rot1: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  TMD+Y8aNeT8=
rot2: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  29GPLz/bW78=
rot3: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  +AmRb2WqXT4=
splineFile: null
tilt: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  XeT7mBa21z8=
tiltPlanRotation: !!python/object/apply:numpy.core.multiarray.scalar
- *id001
- !!binary |
  GR/FlSyYZMA=
time: 20170822-190241
wavelength: 1.832e-11
'''
    return yaml.load(yml)