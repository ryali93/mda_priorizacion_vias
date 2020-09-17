from settings2 import *

class gpo_limitedistrital(object):
    """
    FEATURE CLASS DE ANP
    """
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.iddpto = "IDDPTO"
        self.idprov = "IDPROV"
        self.prov     = "PROV"
        self.iddist = "IDDIST"
        self.dist = "DIST"

    @property
    def dataset(self):
        return 'LIMITES'

    @property
    def name(self):
        return 'DIST'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpl_rv_departamental(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.iddpto   = "IDDPTO"
        self.dpto     = "DPTO"

    @property
    def dataset(self):
        return 'LIMITES'

    @property
    def name(self):
        return 'DPTO'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpl_rv_nacional(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.codruta = "CODRUTA"
        self.superficie_l = "SUPERFICIE_L"

    @property
    def dataset(self):
        return 'f01_RedVial'

    @property
    def name(self):
        return 'gpl_rv_nacional'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpl_rv_vecinal(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.codruta = "CODRUTA"
        self.superficie_l = "SUPERFICIE_L"

    @property
    def dataset(self):
        return 'f01_RedVial'

    @property
    def name(self):
        return 'gpl_rv_vecinal'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpl_rv_teu(object):
    def __init__(self):
        self.id         = "OBJECTID"
        self.shape      = "SHAPE"
        self.iddpto     = "IDDPTO"
        self.dpto       = "DPTO"
        self.idprov     = "IDPROV"
        self.prov       = "PROV"
        self.iddist     = "IDDIST"
        self.dist       = "DIST"
        self.codruta    = "CODRUTA"
        self.superfic_l = "SUPERFIC_L"
        self.fuente     = "FUENTE"
        self.l_tramo    = "L_TRAMO"

    @property
    def dataset(self):
        return 'RV'

    @property
    def name(self):
        return 'RED_VIAL_TEU'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_anp(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.ranp     = "RANP"
        self.anp_cod  = "CODANP"
        self.anp_nom  = "NOMANP"
        self.iddpto   = "IDDPTO"
        self.dpto     = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'ANP'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_cagri(object):
    def __init__(self):
        self.id        = "OBJECTID"
        self.shape     = "SHAPE"
        self.cagri_cat = "CATEGORIA"
        self.iddpto    = "IDDPTO"
        self.dpto      = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'CAGRI'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_rdef(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.prob = "PROB"
        self.bprob = "BPROB"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'RDEF'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_roam(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.prioridad = "PRIORIDAD"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'ROAM'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_zdegra(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'ZDEGRA'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_brturis(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.rt_nom = "NOMRT"
        self.rt_cat = "CATRT"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'BRTURIS'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpt_ccpp(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        # self.regionnat = "REGIONNAT"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"
        self.ccpp_cod = "CODCCPP"
        self.ccpp_nom = "NOMCCPP"
        self.ccpp_pob = "POBCCPP"
        self.ccpp_pobh = "POBHCCPP"
        self.ccpp_pobm = "POBMCCPP"
        self.ccpp_cat = "CATCCPP"
        self.viv_ccpp = "VIVCCPP"
        self.viv_ccppo = "VIVOCCPPP"
        self.viv_ccppd = "VIVDCCPP"


    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'CCPP'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_polos(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.pcultivos = "PCULTIVOS"
        self.pacu = "PACU"
        self.pespforest = "PESPFOREST"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'VARIABLES'

    @property
    def name(self):
        return 'POLOS'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)