from settings2 import *

class gpo_limitedistrital(object):
    """
    FEATURE CLASS DE ANP
    """
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.anp_cate = "anp_cate"
        self.anp_nomb = "anp_nomb"
        self.tipo     = "anp_tipo"

    @property
    def dataset(self):
        return 'f00_Base'

    @property
    def name(self):
        return 'gpo_anp'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpl_rv_departamental(object):
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
        return 'gpl_rv_departamental'

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
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.codruta = "CODRUTA"
        self.superficie_l = "SUPERFICIE_L"
        self.fuente = "FUENTE"
        self.l_tramo = "L_TRAMO"
        self.l_tramo_dist = "L_TRAMO_DIST"
        self.id_ev = "ID_EV"
        self.iddpto = "IDDPTO"
        self.idprov = "IDPROV"
        self.iddist = "IDDIST"
        self.dpto = "DPTO"
        self.prov = "PROV"
        self.dist = "DIST"
        self.ubigeo = "UBIGEO"

    @property
    def dataset(self):
        return 'f01_RedVial'

    @property
    def name(self):
        return 'gpl_rv_teu'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_anp(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.ranp = "RANP"
        self.anp_cod = "ANP_COD"
        self.anp_nom = "ANP_NOM"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_anp'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_cagri(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.cagri_cat = "CAGRI_CAT"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_cagri'

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
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_rdef'

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
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_roam'

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
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_zdegra'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_brturis(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.rt_nom = "RT_NOM"
        self.rt_cat = "RT_CAT"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_brturis'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpt_ccpp(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.regionnat = "REGIONNAT"
        self.ccpp_cat = "CCPP_CAT"
        self.ccpp_cod = "CCPP_COD"
        self.ccpp_nom = "CCPP_NOM"
        self.ccpp_pob = "CCPP_POB"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpt_ccpp'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)

class gpo_polos(object):
    def __init__(self):
        self.id       = "OBJECTID"
        self.shape    = "SHAPE"
        self.ranp = "RANP"
        self.anp_cod = "ANP_COD"
        self.anp_nom = "ANP_NOM"
        self.iddpto = "IDDPTO"
        self.dpto = "DPTO"

    @property
    def dataset(self):
        return 'f02_Variables'

    @property
    def name(self):
        return 'gpo_anp'

    @property
    def path(self):
        return os.path.join(PATH_GDB, self.dataset, self.name)