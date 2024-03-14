import pandas as pd

# ========= metadata ========== # 

metadata_otoriver = pd.DataFrame([
    {'varname': 'B', 'fullname': "bioclicks", 'source': 'otoriver', 'unit': "nb/sec"},
    {'varname': 'Bs40k', 'fullname': "bioclicks_series_40k", 'source': 'otoriver', 'unit': "pct"},
    {'varname': 'B40k', 'fullname': "bioclicks_40k", 'source': 'otoriver', 'unit': "nb/sec"},
    {'varname': 'Bs2k30k', 'fullname': "bioclicks_series_2k30k", 'source': 'otoriver', 'unit': "pct"},
    {'varname': 'B2k30K', 'fullname': "bioclicks_2k30k", 'source': 'otoriver', 'unit': "nb/sec"},
    {'varname': 'BUS', 'fullname': "bioclicks_US", 'source': 'otoriver', 'unit': "nb/sec"},
    {'varname': 'PW', 'fullname': "phoque_wedell", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'PB', 'fullname': "phoque_bardu", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'DS', 'fullname': "dophins_sifflements", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'BC', 'fullname': "baleines chant", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'BM', 'fullname': "bioclicks_mammiferes", 'source': 'otoriver', 'unit': "pct"},
    {'varname': 'P20h400h', 'fullname': "poisson_20h400h", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'SPLP20h400h', 'fullname': "spl_poisson_20h400h", 'source': 'otoriver', 'unit': "db"},
    {'varname': 'P400h2000h', 'fullname': "poisson_400h2000h", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'SPLP 400h2000h','fullname': "spl_poisson_400h2000h",'source': 'otoriver','unit': "db"},
    {'varname': 'BT', 'fullname': "bateaux_totaux", 'source': 'otoriver', 'unit': "nb"},
    {'varname': 'SELBI', 'fullname': "sel_bateaux_indiv", 'source': 'otoriver', 'unit': "db"},
    {'varname': 'SELBT', 'fullname': "sel_bateaux_totaux", 'source': 'otoriver', 'unit': "db"},
    {'varname': 'NS10h10kh', 'fullname': "ns_10h10kh", 'source': 'otoriver', 'unit': "db"},
    {'varname': 'NS63h', 'fullname': "ns_63h", 'source': 'otoriver', 'unit': "db"},
    {'varname': 'NS125h', 'fullname': "ns_125h", 'source': 'otoriver', 'unit': "db"}
    ])

metadata_sensea = pd.DataFrame([
    {'varname': '0', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '1', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '2', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '3', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '4', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '5', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '6', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '7', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '8', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '9', 'fullname': None, 'source': 'sensea', 'unit': None},
    {'varname': '10', 'fullname': None, 'source': 'sensea', 'unit': None}])