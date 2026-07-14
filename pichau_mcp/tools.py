"""Tool definitions and handlers for the Pichau MCP server."""

import json

from mcp.types import TextContent, Tool

from pichau_mcp.client import PichauAPIError, fetch_products

PLATFORM_MAP = {"amd": "7", "intel": "8"}
SORT_OPTIONS = ["relevance", "price-asc", "price-desc", "name-asc", "name-desc"]

PROCESSOR_SOCKETS = {
    "Intel 775": "421",
    "Intel 1150": "6",
    "Intel 1151": "363",
    "Intel 1151 v2": "592",
    "Intel 1155": "5",
    "Intel 1200": "854",
    "Intel 1200 v2": "6365",
    "Intel 1700": "6526",
    "Intel 1700 V2": "7251",
    "Intel 1851": "7685",
    "Intel 2011": "3",
    "Intel 2066": "569",
    "AMD AM5": "6689",
    "AMD AM4": "539",
    "AMD AM4 G": "6539",
    "AMD Am3+ (95w)": "261",
    "TR4": "708",
    "sTR5": "7499",
    "sWRX8": "6473",
}
PROCESSOR_BRANDS = {"AMD": "116", "Intel": "117", "Multi": "74"}
PROCESSOR_INTEGRATED_GRAPHICS = {"Sim": "152", "Não": "153"}
PROCESSOR_OVERCLOCK = {"Sim": "134", "Não": "133"}

COOLER_BRANDS = {
    "1STPLAYER": "6403",
    "Acegeek": "7252",
    "Aerocool": "100",
    "AIGO": "824",
    "Akasa": "351",
    "Akko": "6684",
    "ALLTEK": "7414",
    "Alseye": "630",
    "AMD": "116",
    "Antec": "274",
    "Arctic": "7977",
    "Asus": "34",
    "AZZA": "721",
    "Barrow": "764",
    "Be Quiet!": "7630",
    "BlueCase": "494",
    "Cooler Master": "60",
    "Corsair": "59",
    "Cougar": "93",
    "Cryorig": "8026",
    "DeepCool": "394",
    "DT3": "430",
    "Duex": "6350",
    "Fortrek": "55",
    "Gamdias": "273",
    "Geometric Future": "7968",
    "Gigabyte": "36",
    "HAVIT": "606",
    "Hawin": "7663",
    "HYTE": "7629",
    "Iceberg Thermal": "7627",
    "Intel": "117",
    "K-MEX": "107",
    "KWG": "826",
    "Lian Li": "743",
    "Loving Cool": "7874",
    "Mancer": "536",
    "MSI": "121",
    "Multi": "74",
    "NZXT": "96",
    "OnePower": "511",
    "PCCooler": "8116",
    "PCYES!": "79",
    "Pichau": "210",
    "Redragon": "419",
    "Scythe": "753",
    "Snowman": "7875",
    "T-Dagger": "750",
    "Team Group": "596",
    "TGT": "749",
    "THERMALRIGHT": "7568",
    "Thermaltake": "52",
    "TRYX": "8123",
    "Valkyrie": "7635",
    "Zalman": "115",
}

MOTHERBOARD_BRANDS = {
    "3GREEN": "7611",
    "AFOX": "851",
    "AIGO": "824",
    "AsRock": "35",
    "Asus": "34",
    "Biostar": "624",
    "BlueCase": "494",
    "Brazil PC": "6287",
    "BRX": "6288",
    "Duex": "6350",
    "Esonic": "6681",
    "Gigabyte": "36",
    "Hayom": "6665",
    "JGINYUE": "7975",
    "Mancer": "536",
    "MAXSUN": "7830",
    "MSI": "121",
    "NTC Computadores": "6369",
    "NZXT": "96",
    "Onda": "7974",
    "PCWare": "730",
    "PCWinmax": "6691",
    "Pichau": "210",
    "TGT": "749",
    "VX Pro": "7724",
}
MOTHERBOARD_MEMORY_TYPES = {"DDR3": "423", "DDR4": "422", "DDR5": "6389"}
MOTHERBOARD_FORM_FACTORS = {
    "SSI CEB": "9",
    "SSI EEB": "10",
    "Micro ATX": "11",
    "ATX": "12",
    "E-ATX": "13",
    "Mini ITX": "14",
}
MOTHERBOARD_FEATURES = {
    "AMD Crossfire": "172",
    "AMD Crossfire X3": "161",
    "AMD Crossfire X4": "162",
    "Bluetooth": "155",
    "Botões Integrado": "164",
    "Cpu Integrada": "173",
    "DDR4 DIMMs": "369",
    "DDR5 DIMMs": "6695",
    "Debug Display": "163",
    "Dual LAN": "157",
    "GPU integrado": "166",
    "Intel XMP": "167",
    "M.2": "254",
    "mSATA": "159",
    "nVidia SLI": "169",
    "nVidia SLI 3-Way": "170",
    "nVidia SLI 4-Way": "171",
    "PCI Express v3.0": "168",
    "PCI Express v5.0": "6696",
    "RAID": "158",
    "Sata 6Gb/s": "160",
    "SATA Express": "253",
    "USB 3.0": "165",
    "USB 3.1 Type-C": "370",
    "WIFI integrado": "156",
}
_FEATURE_CODE_TO_NAME = {code: name for name, code in MOTHERBOARD_FEATURES.items()}

MEMORY_BRANDS = {
    "ADATA": "257",
    "Aitek": "8020",
    "Apacer": "112",
    "Best Memory": "6704",
    "BlueCase": "494",
    "Brazil PC": "6287",
    "Corsair": "59",
    "Crucial": "247",
    "Duex": "6350",
    "G.Skill": "75",
    "GET": "6520",
    "Gigabyte": "36",
    "Hayom": "6665",
    "HIKSEMI": "7470",
    "Indilinx": "7870",
    "Intel": "117",
    "KingDian": "8035",
    "Kingston": "68",
    "KingSpec": "7439",
    "KTROK": "8045",
    "Lexar": "723",
    "Macrovip": "8014",
    "Mancer": "536",
    "Multi": "74",
    "Netac": "8016",
    "OXYBR": "7567",
    "Patriot": "67",
    "PCYES!": "79",
    "Pichau": "210",
    "PNY": "71",
    "Redragon": "419",
    "Rise Mode": "490",
    "SYNEX": "8088",
    "Team Group": "596",
    "TGT": "749",
    "Wicgtyp": "7198",
    "ZADAK": "7502",
}
MEMORY_FREQUENCIES = {
    "1333Mhz": "26",
    "1600Mhz": "27",
    "1866Mhz": "28",
    "2133Mhz": "241",
    "2400Mhz": "240",
    "2600Mhz": "237",
    "2666Mhz": "239",
    "2800Mhz": "238",
    "2933Mhz": "236",
    "3000Mhz": "235",
    "3200Mhz": "482",
    "3333Mhz": "485",
    "3400Mhz": "506",
    "3466Mhz": "507",
    "3600Mhz": "484",
    "3733MHz": "6605",
    "3866MHz": "715",
    "4000Mhz": "481",
    "4133Mhz": "486",
    "4266MHz": "586",
    "4400MHz": "6606",
    "4500MHz": "756",
    "4600MHz": "6542",
    "4800MHz": "6390",
    "5066MHz": "6540",
    "5200MHz": "6574",
    "5333MHz": "6541",
    "5600MHz": "6602",
    "6000MHz": "6578",
    "6200MHz": "6575",
    "6400MHz": "6576",
    "6600MHz": "7570",
    "6800MHz": "7423",
    "7000MHz": "7569",
    "7200MHz": "7254",
    "7600MHz": "7636",
    "8000MHz": "7424",
    "8200MHz": "7422",
    "8400MHz": "7795",
    "8800MHz": "7786",
}
MEMORY_CAPACITIES = {
    "4 GB": "198",
    "8 GB": "199",
    "16 GB": "196",
    "24 GB": "7796",
    "32 GB": "195",
    "48 GB": "7420",
    "64 GB": "197",
    "96 GB": "7421",
    "128 GB": "6623",
    "256 GB": "6624",
}

GPU_BRANDS = {
    "Mancer": "536",
    "AFOX": "851",
    "AMD": "116",
    "AsRock": "35",
    "Asus": "34",
    "Duex": "6350",
    "EVGA": "92",
    "Galax": "275",
    "Gainward": "752",
    "Gigabyte": "36",
    "INNO3D": "7368",
    "Intel": "117",
    "MAXSUN": "7830",
    "MSI": "121",
    "PALIT": "7513",
    "PCYES!": "79",
    "PNY": "71",
    "PowerColor": "120",
    "Sapphire": "123",
    "Sparkle": "7822",
    "TGT": "749",
    "XFX": "85",
    "Zotac": "119",
}
GPU_VENDORS = {"AMD/ATI": "129", "NVIDIA": "130", "INTEL": "6708"}
GPU_MODELS = {
    "G210 1GB": "6394",
    "GT240 1GB": "6683",
    "NVS 810 4GB": "763",
    "GT 610 2GB": "6363",
    "GT 710 2GB": "338",
    "GT 730 2GB": "334",
    "GT 730 4GB": "6379",
    "GT 740 4GB": "331",
    "GT 1030 2GB": "560",
    "GT 1030 4GB": "7845",
    "GTX 1050 2Gb": "515",
    "GTX 1050 Ti 4Gb": "514",
    "GTX 1060 3GB": "496",
    "GTX 1060 6GB": "489",
    "GTX 1630 4GB": "6674",
    "GTX 1650 4GB": "717",
    "GTX 1650 Super": "766",
    "GTX 1660 6GB": "712",
    "GTX 1660 Super": "767",
    "GTX 1660 TI 6G": "700",
    "GTX 1070 8GB": "453",
    "GTX 1070 Ti 8GB": "604",
    "GTX 1080 8GB": "445",
    "GTX 1080 Ti 11GB": "550",
    "GTX 750 2GB": "296",
    "GTX 750 4GB": "7415",
    "GTX 750 Ti 2GB": "321",
    "GTX 750 Ti 4GB": "6380",
    "GTX 980 TI 6GB": "386",
    "RTX 2060 6GB": "690",
    "RTX 2060 12GB": "6584",
    "RTX 2060 SUPER 8GB": "748",
    "RTX 2070 8GB": "671",
    "RTX 2070 SUPER 8GB": "747",
    "RTX 2080 8GB": "652",
    "RTX 2080 SUPER 8GB": "751",
    "RTX 2080 Ti 11GB": "651",
    "RTX 3050 4GB": "6611",
    "RTX 3050 6GB": "7522",
    "RTX 3050 8GB": "6592",
    "RTX 3060 8GB": "7192",
    "RTX 3060 12GB": "6359",
    "RTX 3060 TI 8GB": "6343",
    "RTX 3070 8GB": "6304",
    "RTX 3070 Ti 8GB": "6383",
    "RTX 3080 10GB": "6305",
    "RTX 3080 12GB": "6609",
    "RTX 3080 TI 12GB": "6377",
    "RTX 3090 24GB": "6306",
    "RTX 3090 TI 24GB": "6653",
    "RTX 4060 8GB": "7401",
    "RTX 4060 TI 8GB": "7383",
    "RTX 4060 TI 16GB": "7426",
    "RTX 4070 12GB": "7369",
    "RTX 4070 SUPER 12GB": "7510",
    "RTX 4070 TI 12GB": "7208",
    "RTX 4070 TI SUPER 16GB": "7511",
    "RTX 4080 16GB": "7185",
    "RTX 4080 SUPER 16GB": "7512",
    "RTX 4090 24GB": "6703",
    "RTX 5050 8GB": "7895",
    "RTX 5060 8GB": "7827",
    "RTX 5060 TI 8GB": "7828",
    "RTX 5060 TI 16GB": "7826",
    "RTX 5070 12GB": "7725",
    "RTX 5070 TI 16GB": "7726",
    "RTX 5080 16GB": "7708",
    "RTX 5090 32GB": "7723",
    "Quadro T400 2GB": "6491",
    "Quadro T400 4GB": "6676",
    "Quadro T600 4GB": "6537",
    "Quadro P1000 4GB": "587",
    "Quadro P2000 5GB": "589",
    "Quadro P400 2GB": "610",
    "Quadro P620 2GB": "639",
    "Quadro P4000 8GB": "590",
    "Quadro RTX A400 4GB": "7649",
    "Quadro RTX A1000 8GB": "7650",
    "Quadro RTX 4000 8GB": "731",
    "Quadro RTX A2000 6GB": "6601",
    "Quadro RTX A2000 12GB": "6639",
    "Quadro RTX A4000 16GB": "6524",
    "Quadro RTX 4000 20GB": "7481",
    "Quadro RTX A4500 20GB": "6640",
    "Quadro RTX A5000 24GB": "6525",
    "Quadro RTX A5500 24GB": "7250",
    "Quadro T1000 4GB": "6641",
    "Quadro T1000 8GB": "6642",
    "R5 220 2GB": "6289",
    "R5 230 1GB": "744",
    "R5 230 2GB": "607",
    "R7 240": "656",
    "PRO W6400 4GB": "7479",
    "PRO W6600 8GB": "6598",
    "RX 460 2GB": "499",
    "RX 470 8GB": "503",
    "RX 550 2GB": "576",
    "RX 550 4GB": "575",
    "RX 560 2GB": "572",
    "RX 560 4GB": "573",
    "RX 560 8GB": "7701",
    "RX 570 4GB": "556",
    "RX 570 8GB": "686",
    "RX 580 4GB": "561",
    "RX 580 8GB": "611",
    "RX 590 8GB": "674",
    "RX 5500 4GB": "838",
    "RX 5500 XT 4GB": "842",
    "RX 5500 XT 8GB": "844",
    "RX 5600 XT 6GB": "841",
    "RX 5700 8GB": "741",
    "RX 5700 XT 8GB": "742",
    "RX 6400 4GB": "6630",
    "RX 6500 XT 4GB": "6588",
    "RX 6600 8GB": "6481",
    "RX 6600 XT 8GB": "6402",
    "RX 6650 XT 8GB": "6631",
    "RX 6700 XT 12GB": "6362",
    "RX 6750 XT 12GB": "6632",
    "RX 6800 16GB": "6336",
    "RX 6800 XT 16GB": "6337",
    "RX 6900 XT 16GB": "6347",
    "RX 6950 XT 16GB": "6658",
    "RX 7600 8GB": "7400",
    "RX 7600 XT 16GB": "7519",
    "RX 7700 XT 12GB": "7428",
    "RX 7800 XT 16GB": "7429",
    "RX 7900 GRE 16GB": "7631",
    "RX 7900 XT 20GB": "7201",
    "RX 7900 XTX 24GB": "7202",
    "RX 9060 XT 8GB": "7843",
    "RX 9060 XT 16GB": "7844",
    "RX 9070 16GB": "7709",
    "RX 9070 XT 16GB": "7722",
    "A380 6GB": "7190",
    "A750 8GB": "7191",
    "A770 8GB": "6707",
    "A770 16GB": "7431",
    "B570 10GB": "7704",
    "B580 12GB": "7703",
}

STORAGE_INTERFACES = {"NVME": "6617", "SATA": "6618"}
STORAGE_FORM_FACTORS = {"2.5\"": "6615", "M.2": "6616", "Placa PCIe": "6619"}
STORAGE_CAPACITIES = {
    "HD 1TB": "308",
    "HD 500GB": "307",
    "HD 2TB": "309",
    "HD 3TB": "310",
    "HD 4TB": "311",
    "HD 5TB": "7620",
    "HD 6TB": "6663",
    "HD 8TB": "6521",
    "HD 10TB": "6522",
    "HD 12TB": "6523",
    "HD 14TB": "6652",
    "HD 16TB": "6664",
    "HD 18TB": "7533",
    "HD 20TB": "7621",
    "HD 22TB": "7618",
    "HD 24TB": "8125",
    "HD 26TB": "8120",
    "SSD 120GB": "305",
    "SSD 128GB": "6494",
    "SSD 240GB": "361",
    "SSD 250GB": "6505",
    "SSD 256GB": "6495",
    "SSD 480GB": "761",
    "SSD 500GB": "6506",
    "SSD 512GB": "762",
    "SSD 960GB": "845",
    "SSD 1TB": "6492",
    "SSD 1920GB": "6620",
    "SSD 2TB": "6507",
    "SSD 4TB": "6508",
    "SSD 8TB": "6509",
    "SSD 15.3TB": "6621",
}

CASE_FORM_FACTORS = {
    "Micro ATX": "11",
    "ATX": "12",
    "E-ATX": "13",
    "Mini ITX": "14",
    "SSI CEB": "9",
    "SSI EEB": "10",
    "XL-ATX": "15",
}
CASE_TYPES = {"Full Tower": "6659", "Mid Tower": "6660", "Mini Tower": "6661"}
CASE_BRANDS = {
    "Pichau": "210",
    "Mancer": "536",
    "1STPLAYER": "6403",
    "A+ PLUS": "7589",
    "Acegeek": "7252",
    "Aerocool": "100",
    "AIGO": "824",
    "Alseye": "630",
    "Antec": "274",
    "Asus": "34",
    "AZZA": "721",
    "Be Quiet!": "7630",
    "Bitfenix": "99",
    "BlueCase": "494",
    "BRX": "6288",
    "C3Tech": "78",
    "Cooler Master": "60",
    "Corsair": "59",
    "Cougar": "93",
    "DeepCool": "394",
    "DT3": "430",
    "Duex": "6350",
    "ELG": "350",
    "EVGA": "92",
    "Fantech": "7648",
    "Force Line": "86",
    "Fortrek": "55",
    "G-Fire": "269",
    "Galax": "275",
    "Gamdias": "273",
    "Gamemax": "488",
    "Geometric Future": "7968",
    "Gigabyte": "36",
    "Hardline": "508",
    "Hayom": "6665",
    "HYTE": "7629",
    "Implastec": "535",
    "In Win": "510",
    "KWG": "826",
    "Lian Li": "743",
    "LikeTec": "7506",
    "Mloong": "7894",
    "MSI": "121",
    "Multi": "74",
    "Mymax": "53",
    "NZXT": "96",
    "OnePower": "511",
    "PCYES!": "79",
    "Pixxo": "106",
    "RAIDMAX": "90",
    "Redragon": "419",
    "Riotoro": "388",
    "Rise Mode": "490",
    "SAMA": "7409",
    "T-Dagger": "750",
    "Tecnomall": "8034",
    "TGT": "749",
    "THERMALRIGHT": "7568",
    "Thermaltake": "52",
    "thunderx3": "541",
    "Valkyrie": "7635",
    "Vinik": "213",
    "X-Trike": "215",
    "X2": "360",
    "Xigmatek": "270",
    "XPG": "7354",
    "YouCase": "564",
}

PSU_WATTAGE = {
    "Menos de 400W": "6482",
    "400W ~ 599W": "6483",
    "600W ~ 799W": "6484",
    "800W ~ 1199W": "6485",
    "1200W ~ 1499W": "6486",
    "Mais de 1500W": "6487",
}
PSU_MODULAR = {
    "Full Modular": "6488",
    "Semi Modular": "6489",
    "Não Modular": "6490",
}
PSU_EFFICIENCY = {
    "White": "7596",
    "Bronze": "7597",
    "Gold": "7599",
    "Platinum": "7600",
    "Titanium": "7601",
}
PSU_BRANDS = {
    "1STPLAYER": "6403",
    "Acegeek": "7252",
    "Acer": "449",
    "Aerocool": "100",
    "AIGO": "824",
    "AsRock": "35",
    "Asus": "34",
    "AZZA": "721",
    "Be Quiet!": "7630",
    "BlueCase": "494",
    "BR One": "6292",
    "Brazil PC": "6287",
    "BRX": "6288",
    "Cooler Master": "60",
    "Corsair": "59",
    "Cougar": "93",
    "DeepCool": "394",
    "Duex": "6350",
    "EVGA": "92",
    "Fortrek": "55",
    "Galax": "275",
    "Gamdias": "273",
    "Gigabyte": "36",
    "Lian Li": "743",
    "Mancer": "536",
    "MSI": "121",
    "Multi": "74",
    "NZXT": "96",
    "OnePower": "511",
    "PCCooler": "8116",
    "PCYES!": "79",
    "Pichau": "210",
    "Redragon": "419",
    "Seasonic": "271",
    "Super Flower": "821",
    "TGT": "749",
    "THERMALRIGHT": "7568",
    "Thermaltake": "52",
    "VX Pro": "7724",
    "XPG": "7354",
}

MONITOR_BRANDS = {
    "3GREEN": "7611",
    "Acer": "449",
    "AIGO": "824",
    "AOC": "110",
    "AsRock": "35",
    "Asus": "34",
    "Benq": "221",
    "BlueCase": "494",
    "Braview": "477",
    "Brazil PC": "6287",
    "BRX": "6288",
    "Cooler Master": "60",
    "Corsair": "59",
    "Dell": "645",
    "Duex": "6350",
    "Gigabyte": "36",
    "HOF LITE": "7622",
    "HP": "95",
    "Jingshu": "7700",
    "Level": "7582",
    "LG": "111",
    "Mancer": "536",
    "MITSUSHIBA": "566",
    "MSI": "121",
    "Multi": "74",
    "PCTop": "378",
    "PCYES!": "79",
    "Philips": "82",
    "Pichau": "210",
    "Redragon": "419",
    "Samsung": "72",
    "SZL": "7544",
    "TCL": "7592",
    "TGT": "749",
    "VST": "7612",
    "VX Pro": "7724",
    "Zinnia": "6625",
    "Zowie": "480",
}

KEYBOARD_MECHANICAL = {"Sim": "45", "Não": "44"}
KEYBOARD_INTERFACES = {
    "Bluetooth": "46",
    "PS2": "48",
    "Sem fio(Wireless)": "47",
    "Com fio": "7535",
    "USB": "49",
    "USB/3.5mm": "7487",
    "Tipo-C": "7488",
    "Bluetooth/Wireless": "7491",
    "Tri-mode": "8028",
}
KEYBOARD_BRANDS = {
    "1STPLAYER": "6403",
    "A+ PLUS": "7589",
    "AIGO": "824",
    "Ajazz": "7976",
    "Akko": "6684",
    "AOC": "110",
    "ATK GEAR": "8031",
    "ATTACKSHARK": "7940",
    "BRX": "6288",
    "Cherry Xtrfy": "8127",
    "Cooler Master": "60",
    "Corsair": "59",
    "Cougar": "93",
    "Dazz": "568",
    "DeepCool": "394",
    "Duex": "6350",
    "Durgod": "746",
    "ELG": "350",
    "Epomaker": "7647",
    "Fantech": "7648",
    "Fortrek": "55",
    "Force One": "6693",
    "FNATIC": "7507",
    "Gamdias": "273",
    "GET": "6520",
    "GEONAV": "6375",
    "HAVIT": "606",
    "HyperX": "6348",
    "HYTE": "7629",
    "Intelbras": "353",
    "Keychron": "7534",
    "Kingston": "68",
    "K-MEX": "107",
    "KROSS": "7469",
    "Logitech": "57",
    "Mancer": "536",
    "Marvo": "580",
    "Microsoft": "202",
    "Motospeed": "720",
    "MSI": "121",
    "Multi": "74",
    "Machenike": "8090",
    "NewLink": "389",
    "NZXT": "96",
    "Patriot": "67",
    "PCYES!": "79",
    "Philips": "82",
    "Pichau": "210",
    "R8": "7787",
    "Razer": "58",
    "Redragon": "419",
    "RAPOO": "7416",
    "ROYAL KLUDGE": "7509",
    "Scyrox": "7962",
    "Steelseries": "368",
    "Skyloong": "7640",
    "Solid Gear": "7973",
    "T-Dagger": "750",
    "TESORO": "425",
    "TGT": "749",
    "Thermaltake": "52",
    "Trust": "616",
    "THUNDEROBOT": "7508",
    "Vinik": "213",
    "Xanova": "825",
    "XPG": "7354",
}

CABLE_BRANDS = {
    "Ajazz": "7976",
    "Akko": "6684",
    "ALN": "7876",
    "ATTACKSHARK": "7940",
    "Baseus": "8030",
    "ChipSCE": "6303",
    "Cooler Master": "60",
    "Corsair": "59",
    "DeepCool": "394",
    "DEX": "545",
    "Elgato": "725",
    "ELG": "350",
    "Empire": "500",
    "Exbom": "602",
    "F3": "760",
    "Fortrek": "55",
    "GEONAV": "6375",
    "Händz": "6519",
    "Hayom": "6665",
    "HP": "95",
    "HyperX": "6348",
    "Intelbras": "353",
    "Kingston": "68",
    "Lian Li": "743",
    "Lexar": "723",
    "Marvo": "580",
    "MD9": "513",
    "Megatron": "6627",
    "motorola": "548",
    "Multi": "74",
    "Mymax": "53",
    "PCYES!": "79",
    "Pichau": "210",
    "Pix": "558",
    "PlusCable": "455",
    "Point of View": "258",
    "QCY": "745",
    "Redragon": "419",
    "ROYAL KLUDGE": "7509",
    "Seccon": "7453",
    "Senye": "7829",
    "Thermaltake": "52",
    "Thermal Grizzly": "6361",
    "Trust": "616",
    "Ubiquiti": "6310",
    "UGREEN": "8021",
    "Vinik": "213",
    "Xiaomi": "6401",
    "X-CELL": "6360",
}

MOUSE_INTERFACES = {
    "Bluetooth": "46",
    "Sem fio(Wireless)": "47",
    "Com fio": "7535",
    "USB": "49",
    "USB/3.5mm": "7487",
    "Tipo-C": "7488",
    "Bluetooth/Wireless": "7491",
    "Tri-mode": "8028",
}
MOUSE_BRANDS = {
    "1STPLAYER": "6403",
    "A+ PLUS": "7589",
    "Acer": "449",
    "ADATA": "257",
    "AIGO": "824",
    "Ajazz": "7976",
    "Akko": "6684",
    "AOC": "110",
    "Asus": "34",
    "ATK GEAR": "8031",
    "ATTACKSHARK": "7940",
    "Benq": "221",
    "BlueCase": "494",
    "BRX": "6288",
    "Cherry Xtrfy": "8127",
    "Cooler Master": "60",
    "Corsair": "59",
    "Cougar": "93",
    "Darmoshark": "7639",
    "Dazz": "568",
    "DeepCool": "394",
    "DEEPSKY": "7571",
    "Duex": "6350",
    "ELG": "350",
    "Fantech": "7648",
    "Fortrek": "55",
    "Force One": "6693",
    "FOXXRAY": "7935",
    "GEONAV": "6375",
    "Glorious": "828",
    "HAVIT": "606",
    "HP": "95",
    "HyperX": "6348",
    "Intelbras": "353",
    "Keychron": "7534",
    "Kingston": "68",
    "K-MEX": "107",
    "KROSS": "7469",
    "KWG": "826",
    "Lamzu": "7964",
    "Logitech": "57",
    "Mad Catz": "836",
    "Mancer": "536",
    "Marvo": "580",
    "MAXPRINT": "88",
    "Microdigi": "420",
    "Microsoft": "202",
    "MONSGEEK": "7565",
    "Motospeed": "720",
    "MSI": "121",
    "Multi": "74",
    "NZXT": "96",
    "PCYES!": "79",
    "Philips": "82",
    "Pichau": "210",
    "R8": "7787",
    "Razer": "58",
    "Redragon": "419",
    "RAPOO": "7416",
    "ROYAL KLUDGE": "7509",
    "Scyrox": "7962",
    "Solid Gear": "7973",
    "T-Dagger": "750",
    "TGT": "749",
    "Thermaltake": "52",
    "Trust": "616",
    "THUNDEROBOT": "7508",
    "Vinik": "213",
    "XPG": "7354",
    "Xtrfy": "6308",
    "Zalman": "115",
    "Zowie": "480",
}

SPEAKER_BRANDS = {
    "Audio Technica": "6294",
    "C3Tech": "78",
    "Creative": "6299",
    "Duex": "6350",
    "Divoom": "7223",
    "Edifier": "64",
    "ELG": "350",
    "Empire": "500",
    "Fifine": "7641",
    "Fortrek": "55",
    "Force One": "6693",
    "FOXXRAY": "7935",
    "GEONAV": "6375",
    "Harman": "724",
    "HAVIT": "606",
    "HP": "95",
    "JBL": "532",
    "Kisonli": "7689",
    "K-MEX": "107",
    "LG": "111",
    "Logitech": "57",
    "Mancer": "536",
    "Marvo": "580",
    "Microlab": "719",
    "Multi": "74",
    "NewLink": "389",
    "Philips": "82",
    "Pichau": "210",
    "Pulse": "431",
    "QCY": "745",
    "R8": "7787",
    "Razer": "58",
    "Redragon": "419",
    "ROYAL KLUDGE": "7509",
    "T-Dagger": "750",
    "TGT": "749",
    "Trust": "616",
    "Vinik": "213",
    "WaveOne": "7690",
    "Xiaomi": "6401",
}

WEBCAM_BRANDS = {
    "BlueCase": "494",
    "Brazil PC": "6287",
    "Cougar": "93",
    "Creative": "6299",
    "Elgato": "725",
    "Fortrek": "55",
    "Genius": "54",
    "GET": "6520",
    "HAVIT": "606",
    "HyperX": "6348",
    "Intelbras": "353",
    "Kisonli": "7689",
    "Logitech": "57",
    "Mancer": "536",
    "Microsoft": "202",
    "Multi": "74",
    "PCYES!": "79",
    "Pichau": "210",
    "Razer": "58",
    "Redragon": "419",
    "RAPOO": "7416",
    "STREAMPLIFY": "7365",
    "T-Dagger": "750",
    "TGT": "749",
    "Trust": "616",
    "Zinnia": "6625",
}

SEARCH_PROCESSORS_TOOL = Tool(
    name="search_processors",
    description=(
        "Search for CPUs/processors for sale on Pichau (Brazilian computer hardware "
        "store). Use this when the user asks to find, compare, or check prices for "
        "processors, e.g. 'Ryzen 7', 'Intel Core Ultra', 'processador mais barato AMD'."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'ryzen 7' or 'core ultra 5'",
            },
            "platform": {
                "type": "string",
                "enum": ["AMD", "Intel"],
                "description": "Filter by CPU platform/manufacturer",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(PROCESSOR_BRANDS)},
                "description": (
                    "Optional filter by manufacturer brand -- a finer-grained "
                    "alternative to `platform` that also includes 'Multi'-brand "
                    "listings"
                ),
            },
            "socket": {
                "type": "array",
                "items": {"type": "string", "enum": list(PROCESSOR_SOCKETS)},
                "description": "Optional filter by one or more CPU sockets",
            },
            "integrated_graphics": {
                "type": "array",
                "items": {"type": "string", "enum": list(PROCESSOR_INTEGRATED_GRAPHICS)},
                "description": "Optional filter by presence of integrated graphics",
            },
            "overclockable": {
                "type": "array",
                "items": {"type": "string", "enum": list(PROCESSOR_OVERCLOCK)},
                "description": "Optional filter by whether the CPU supports overclocking",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_COOLERS_TOOL = Tool(
    name="search_coolers",
    description=(
        "Search for CPU coolers (air or liquid/water coolers) on Pichau compatible "
        "with a given socket. The `socket` value must come from the `socket` field "
        "(not `sockettext`) of a processor previously returned by search_processors "
        "-- coolers are only useful paired with a processor's socket."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "socket": {
                "type": "string",
                "description": (
                    "Socket code taken from a processor's `socket` field, "
                    "e.g. '7685' for an Intel LGA1851 CPU"
                ),
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(COOLER_BRANDS)},
                "description": "Optional filter by one or more cooler brands",
            },
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'water cooler 360mm'",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
        "required": ["socket"],
    },
)

SEARCH_MOTHERBOARDS_TOOL = Tool(
    name="search_motherboards",
    description=(
        "Search for motherboards on Pichau compatible with a given CPU socket. "
        "The `socket` value must come from the `socket` field (not `sockettext`) "
        "of a processor previously returned by search_processors."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "socket": {
                "type": "string",
                "description": (
                    "Socket code taken from a processor's `socket` field, "
                    "e.g. '7685' for an Intel LGA1851 CPU"
                ),
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOTHERBOARD_BRANDS)},
                "description": "Optional filter by one or more motherboard brands",
            },
            "memory_type": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOTHERBOARD_MEMORY_TYPES)},
                "description": "Optional filter by supported RAM type",
            },
            "form_factor": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOTHERBOARD_FORM_FACTORS)},
                "description": "Optional filter by board form factor",
            },
            "features": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOTHERBOARD_FEATURES)},
                "description": "Optional filter by one or more board features",
            },
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'b850 wifi'",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
        "required": ["socket"],
    },
)

SEARCH_MEMORY_TOOL = Tool(
    name="search_memory",
    description=(
        "Search for RAM memory modules on Pichau. `memory_type` must match the "
        "memory type of the target motherboard -- use the `memory_type` field of "
        "a motherboard previously returned by search_motherboards (DDR4 or DDR5)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "memory_type": {
                "type": "string",
                "enum": list(MOTHERBOARD_MEMORY_TYPES),
                "description": "RAM type, must match the target motherboard",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(MEMORY_BRANDS)},
                "description": "Optional filter by one or more memory brands",
            },
            "frequency": {
                "type": "array",
                "items": {"type": "string", "enum": list(MEMORY_FREQUENCIES)},
                "description": "Optional filter by one or more clock speeds",
            },
            "capacity": {
                "type": "array",
                "items": {"type": "string", "enum": list(MEMORY_CAPACITIES)},
                "description": "Optional filter by one or more kit capacities",
            },
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'vengeance rgb'",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
        "required": ["memory_type"],
    },
)

SEARCH_GPUS_TOOL = Tool(
    name="search_gpus",
    description=(
        "Search for graphics cards / GPUs (placas de vídeo) for sale on Pichau. "
        "Unlike processors, coolers, motherboards and memory, this search has no "
        "socket dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(GPU_BRANDS)},
                "description": "Optional filter by one or more GPU board brands",
            },
            "vendor": {
                "type": "array",
                "items": {"type": "string", "enum": list(GPU_VENDORS)},
                "description": "Optional filter by GPU chip vendor",
            },
            "model": {
                "type": "array",
                "items": {"type": "string", "enum": list(GPU_MODELS)},
                "description": (
                    "Optional filter by one or more specific GPU models, "
                    "e.g. 'RTX 4070 12GB' or 'RX 7800 XT 16GB'"
                ),
            },
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'rtx 4070 gigabyte'",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_STORAGE_TOOL = Tool(
    name="search_storage",
    description=(
        "Search for storage drives (HDDs and SSDs) for sale on Pichau -- both "
        "hard disk drives and solid-state drives are covered by the same catalog. "
        "No socket dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'nvme 1tb'",
            },
            "interface": {
                "type": "array",
                "items": {"type": "string", "enum": list(STORAGE_INTERFACES)},
                "description": "Optional filter by connection interface",
            },
            "form_factor": {
                "type": "array",
                "items": {"type": "string", "enum": list(STORAGE_FORM_FACTORS)},
                "description": "Optional filter by physical form factor",
            },
            "capacity": {
                "type": "array",
                "items": {"type": "string", "enum": list(STORAGE_CAPACITIES)},
                "description": "Optional filter by one or more capacities",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_CASES_TOOL = Tool(
    name="search_cases",
    description=(
        "Search for PC cases (gabinetes) on Pichau compatible with a given "
        "motherboard form factor."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "form_factor": {
                "type": "string",
                "enum": list(CASE_FORM_FACTORS) + list(CASE_FORM_FACTORS.values()),
                "description": (
                    "Motherboard form factor to filter compatible cases by. Accepts "
                    "either a human name (e.g. 'ATX') or the raw code from a "
                    "motherboard's `formato_placa` field (e.g. '11') returned by "
                    "search_motherboards -- both work."
                ),
            },
            "case_type": {
                "type": "array",
                "items": {"type": "string", "enum": list(CASE_TYPES)},
                "description": "Optional filter by case size/type",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(CASE_BRANDS)},
                "description": "Optional filter by one or more case brands",
            },
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'lateral de vidro'",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
        "required": ["form_factor"],
    },
)

SEARCH_POWER_SUPPLIES_TOOL = Tool(
    name="search_power_supplies",
    description=(
        "Search for power supplies (fontes) for sale on Pichau. No socket "
        "dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'corsair 850w'",
            },
            "wattage": {
                "type": "array",
                "items": {"type": "string", "enum": list(PSU_WATTAGE)},
                "description": "Optional filter by one or more wattage ranges",
            },
            "modular": {
                "type": "array",
                "items": {"type": "string", "enum": list(PSU_MODULAR)},
                "description": "Optional filter by cable modularity",
            },
            "efficiency": {
                "type": "array",
                "items": {"type": "string", "enum": list(PSU_EFFICIENCY)},
                "description": "Optional filter by 80 Plus efficiency rating",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(PSU_BRANDS)},
                "description": "Optional filter by one or more PSU brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_MONITORS_TOOL = Tool(
    name="search_monitors",
    description=(
        "Search for monitors for sale on Pichau. Only text search (`query`) and "
        "`brands` are reliably applied server-side -- Pichau's backend does not "
        "honor refresh rate, resolution, panel type, screen size, response time "
        "or connector filters for this category (verified by testing), so those "
        "were intentionally left out. Check those specs in each result's `name` "
        "field instead, e.g. 'Monitor Gamer LG UltraGear, 27 Pol, IPS, QHD, 1ms, "
        "165Hz, HDMI/DP'."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. '27 polegadas 165hz'",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(MONITOR_BRANDS)},
                "description": "Optional filter by one or more monitor brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_KEYBOARDS_TOOL = Tool(
    name="search_keyboards",
    description=(
        "Search for keyboards for sale on Pichau. Only `query`, `mechanical`, "
        "`interface` and `brands` are reliably applied server-side -- Pichau's "
        "backend does not honor layout, backlighting or macro-key filters for "
        "this category (verified by testing), so those were intentionally left "
        "out. Check those specs in each result's `name` field instead."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'teclado mecanico switch red'",
            },
            "mechanical": {
                "type": "array",
                "items": {"type": "string", "enum": list(KEYBOARD_MECHANICAL)},
                "description": "Optional filter by whether the keyboard is mechanical",
            },
            "interface": {
                "type": "array",
                "items": {"type": "string", "enum": list(KEYBOARD_INTERFACES)},
                "description": "Optional filter by one or more connection interfaces",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(KEYBOARD_BRANDS)},
                "description": "Optional filter by one or more keyboard brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_CABLES_TOOL = Tool(
    name="search_cables",
    description=(
        "Search for cables, adapters, hubs, and switches (cabos e adaptadores) "
        "for sale on Pichau, e.g. HDMI cables, USB hubs, KVM/HDMI switches, "
        "docking stations. Only `query` and `brands` are reliably applied "
        "server-side -- Pichau's backend does not honor color filters for this "
        "category (verified by testing), so that was intentionally left out. "
        "No socket dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'hub usb 3.0' or 'cabo hdmi 2.1'",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(CABLE_BRANDS)},
                "description": "Optional filter by one or more brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_MICE_TOOL = Tool(
    name="search_mice",
    description=(
        "Search for computer mice for sale on Pichau. Only `query`, "
        "`interface` and `brands` are reliably applied server-side -- "
        "Pichau's backend does not honor color or backlighting filters for "
        "this category (verified by testing), so those were intentionally "
        "left out. No socket dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'mouse sem fio 26000dpi'",
            },
            "interface": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOUSE_INTERFACES)},
                "description": "Optional filter by one or more connection interfaces",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(MOUSE_BRANDS)},
                "description": "Optional filter by one or more mouse brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_SPEAKERS_TOOL = Tool(
    name="search_speakers",
    description=(
        "Search for computer speakers (caixas de som) for sale on Pichau. "
        "Only `query` and `brands` are reliably applied server-side -- "
        "Pichau's backend does not honor color, backlighting, or "
        "connectivity filters for this category (verified by testing), so "
        "those were intentionally left out. No socket dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'caixa de som bluetooth'",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(SPEAKER_BRANDS)},
                "description": "Optional filter by one or more speaker brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)

SEARCH_WEBCAMS_TOOL = Tool(
    name="search_webcams",
    description=(
        "Search for webcams for sale on Pichau. Only `query` and `brands` "
        "are reliably applied server-side (verified by testing). No socket "
        "dependency."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text search terms, e.g. 'webcam 1080p com microfone'",
            },
            "brands": {
                "type": "array",
                "items": {"type": "string", "enum": list(WEBCAM_BRANDS)},
                "description": "Optional filter by one or more webcam brands",
            },
            "sort": {
                "type": "string",
                "enum": SORT_OPTIONS,
                "default": "relevance",
                "description": "Result ordering",
            },
            "page": {
                "type": "integer",
                "default": 1,
                "description": "Page number of results",
            },
            "max_results": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
    },
)


def _product_url(item: dict) -> str:
    return f"https://www.pichau.com.br/{item['url_key']}"


def _price_fields(item: dict) -> dict:
    prices = item.get("pichau_prices") or {}
    return {
        "price_pix": prices.get("avista"),
        "price_card_full": prices.get("final_price"),
        "installments": (
            f"{prices['max_installments']}x de R$ {prices['min_installment_price']}"
            if prices.get("max_installments")
            else None
        ),
    }


def _require_socket(arguments: dict) -> tuple[str | None, str | None]:
    """Validate the required `socket` argument. Returns (socket, error_message)."""
    socket = arguments.get("socket")
    if not socket:
        return None, (
            "O parâmetro 'socket' é obrigatório. Use o campo 'socket' "
            "(não 'sockettext'/'compatible_sockets') de um processador "
            "retornado por search_processors."
        )
    return socket, None


def _resolve_case_form_factor(arguments: dict) -> tuple[str | None, str | None]:
    """Resolve the required `form_factor` argument to a raw Pichau code.

    Accepts either a human-readable name (e.g. 'ATX') or the raw numeric
    code from a motherboard's `formato_placa` field (e.g. '11'), so the
    tool works standalone as well as chained from search_motherboards.
    """
    value = arguments.get("form_factor")
    if not value:
        return None, (
            f"O parâmetro 'form_factor' é obrigatório. Use um nome como "
            f"{', '.join(CASE_FORM_FACTORS)}, ou o código bruto do campo "
            f"'form_factor' de uma placa-mãe retornada por search_motherboards."
        )
    value = str(value).strip()
    if value in CASE_FORM_FACTORS.values():
        return value, None
    code = {name.lower(): code for name, code in CASE_FORM_FACTORS.items()}.get(value.lower())
    if code is not None:
        return code, None
    return None, (
        f"Valor inválido para 'form_factor': {value!r}. Use um nome como "
        f"{', '.join(CASE_FORM_FACTORS)}, ou um código bruto reconhecido "
        f"({', '.join(CASE_FORM_FACTORS.values())})."
    )


def _resolve_codes(
    values: list[str] | None, catalog: dict[str, str], label: str
) -> tuple[list[str], str | None]:
    """Map a list of human-readable names to their Pichau filter codes.

    Returns (codes, error_message); error_message is set on the first
    unrecognized name.
    """
    lookup = {name.lower(): code for name, code in catalog.items()}
    codes = []
    for value in values or []:
        code = lookup.get(str(value).strip().lower())
        if code is None:
            return [], f"Valor inválido para '{label}': {value!r}. Válidos: {', '.join(catalog)}."
        codes.append(code)
    return codes, None


def _resolve_code(
    value: str | None, catalog: dict[str, str], label: str
) -> tuple[str | None, str | None]:
    """Map a single required human-readable name to its Pichau filter code."""
    if not value:
        return None, f"O parâmetro '{label}' é obrigatório. Válidos: {', '.join(catalog)}."
    lookup = {name.lower(): code for name, code in catalog.items()}
    code = lookup.get(str(value).strip().lower())
    if code is None:
        return None, f"Valor inválido para '{label}': {value!r}. Válidos: {', '.join(catalog)}."
    return code, None


def _decode_features(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    codes = [c.strip() for c in raw.split(",") if c.strip()]
    return [_FEATURE_CODE_TO_NAME.get(c, c) for c in codes]


def _format_processor(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "platform": item.get("plataformatext"),
        "socket": item.get("socket"),
        "socket_name": item.get("sockettext"),
        "integrated_graphics": item.get("vgaintegradotext"),
        "tdp_w": item.get("potencia"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_cooler(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "compatible_sockets": item.get("sockettext"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_motherboard(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "socket": item.get("socket"),
        "socket_name": item.get("sockettext"),
        "form_factor": item.get("formato_placa"),
        "form_factor_name": item.get("formato_placatext"),
        "memory_type": item.get("tipo_de_memoriatext"),
        "memory_slots": item.get("slots_memoria"),
        "sata_ports": item.get("portas_sata"),
        "features": _decode_features(item.get("caracteristicas")),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_memory(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "memory_type": item.get("tipo_de_memoriatext"),
        "capacity": item.get("capacidadememoriatext"),
        "frequency": item.get("frequenciatext"),
        "modules": item.get("quantidade_pacote"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_gpu(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "model": item.get("rgputext"),
        "vendor": item.get("plataformavideotext"),
        "power_w": item.get("potencia"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_storage(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "capacity": item.get("rarmazenamento_text"),
        "form_factor": item.get("formato_ssd_text"),
        "interface": item.get("barramento_ssd_text"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_case(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "case_type": item.get("tipo_gabinetetext"),
        "supported_form_factors": item.get("formato_placatext"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_psu(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "power_w": item.get("potencia"),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_monitor(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_keyboard(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_cable(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_mouse(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_speaker(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


def _format_webcam(item: dict) -> dict:
    return {
        "name": item.get("name"),
        "sku": item.get("sku"),
        "url": _product_url(item),
        "stock_status": item.get("stock_status"),
        **_price_fields(item),
    }


async def handle_search_processors(arguments: dict) -> list[TextContent]:
    platform = arguments.get("platform")
    plataforma_code = None
    if platform:
        plataforma_code = PLATFORM_MAP.get(platform.strip().lower())
        if plataforma_code is None:
            return [
                TextContent(
                    type="text",
                    text=f"Plataforma inválida: {platform!r}. Use 'AMD' ou 'Intel'.",
                )
            ]

    brand_codes, error = _resolve_codes(arguments.get("brands"), PROCESSOR_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    socket_codes, error = _resolve_codes(arguments.get("socket"), PROCESSOR_SOCKETS, "Socket")
    if error:
        return [TextContent(type="text", text=error)]

    igpu_codes, error = _resolve_codes(
        arguments.get("integrated_graphics"), PROCESSOR_INTEGRATED_GRAPHICS, "Vídeo integrado"
    )
    if error:
        return [TextContent(type="text", text=error)]

    overclock_codes, error = _resolve_codes(
        arguments.get("overclockable"), PROCESSOR_OVERCLOCK, "Overclock"
    )
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "sort": None if sort == "relevance" else sort,
        "plataforma": plataforma_code,
        "marcas": ",".join(brand_codes) if brand_codes else None,
        "socket": ",".join(socket_codes) if socket_codes else None,
        "vgaintegrado": ",".join(igpu_codes) if igpu_codes else None,
        "overclock": ",".join(overclock_codes) if overclock_codes else None,
        "q": query,
    }

    try:
        data = await fetch_products("monte-processador", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar processadores: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_processor(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_coolers(arguments: dict) -> list[TextContent]:
    socket, error = _require_socket(arguments)
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), COOLER_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "socket": socket,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-processador-cooler", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar coolers: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_cooler(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_motherboards(arguments: dict) -> list[TextContent]:
    socket, error = _require_socket(arguments)
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(
        arguments.get("brands"), MOTHERBOARD_BRANDS, "Marca"
    )
    if error:
        return [TextContent(type="text", text=error)]

    memory_codes, error = _resolve_codes(
        arguments.get("memory_type"), MOTHERBOARD_MEMORY_TYPES, "Tipo de memória"
    )
    if error:
        return [TextContent(type="text", text=error)]

    form_factor_codes, error = _resolve_codes(
        arguments.get("form_factor"), MOTHERBOARD_FORM_FACTORS, "Formato de placa"
    )
    if error:
        return [TextContent(type="text", text=error)]

    feature_codes, error = _resolve_codes(
        arguments.get("features"), MOTHERBOARD_FEATURES, "Característica"
    )
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "socket": socket,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "tipo_de_memoria": ",".join(memory_codes) if memory_codes else None,
        "formato_placa": ",".join(form_factor_codes) if form_factor_codes else None,
        "caracteristicas": ",".join(feature_codes) if feature_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-placa-mae", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar placas-mãe: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_motherboard(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_memory(arguments: dict) -> list[TextContent]:
    memory_type_code, error = _resolve_code(
        arguments.get("memory_type"), MOTHERBOARD_MEMORY_TYPES, "memory_type"
    )
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), MEMORY_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    frequency_codes, error = _resolve_codes(
        arguments.get("frequency"), MEMORY_FREQUENCIES, "Frequência"
    )
    if error:
        return [TextContent(type="text", text=error)]

    capacity_codes, error = _resolve_codes(
        arguments.get("capacity"), MEMORY_CAPACITIES, "Capacidade"
    )
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "tipo_de_memoria": memory_type_code,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "frequencia": ",".join(frequency_codes) if frequency_codes else None,
        "capacidadememoria": ",".join(capacity_codes) if capacity_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-memoria", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar memórias: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_memory(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_gpus(arguments: dict) -> list[TextContent]:
    marcas_codes, error = _resolve_codes(arguments.get("brands"), GPU_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    vendor_codes, error = _resolve_codes(
        arguments.get("vendor"), GPU_VENDORS, "Fabricante do chip"
    )
    if error:
        return [TextContent(type="text", text=error)]

    model_codes, error = _resolve_codes(arguments.get("model"), GPU_MODELS, "Modelo")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "placadevideo": ",".join(vendor_codes) if vendor_codes else None,
        "rgpu": ",".join(model_codes) if model_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-placa-de-video", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar placas de vídeo: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_gpu(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_storage(arguments: dict) -> list[TextContent]:
    interface_codes, error = _resolve_codes(
        arguments.get("interface"), STORAGE_INTERFACES, "Interface"
    )
    if error:
        return [TextContent(type="text", text=error)]

    form_factor_codes, error = _resolve_codes(
        arguments.get("form_factor"), STORAGE_FORM_FACTORS, "Formato"
    )
    if error:
        return [TextContent(type="text", text=error)]

    capacity_codes, error = _resolve_codes(
        arguments.get("capacity"), STORAGE_CAPACITIES, "Capacidade"
    )
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "barramento_ssd": ",".join(interface_codes) if interface_codes else None,
        "formato_ssd": ",".join(form_factor_codes) if form_factor_codes else None,
        "rarmazenamento": ",".join(capacity_codes) if capacity_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-ssd", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar HDs/SSDs: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_storage(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_cases(arguments: dict) -> list[TextContent]:
    form_factor, error = _resolve_case_form_factor(arguments)
    if error:
        return [TextContent(type="text", text=error)]

    case_type_codes, error = _resolve_codes(
        arguments.get("case_type"), CASE_TYPES, "Tipo de gabinete"
    )
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), CASE_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "formato_placa": form_factor,
        "tipo_gabinete": ",".join(case_type_codes) if case_type_codes else None,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-gabinete", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar gabinetes: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_case(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_power_supplies(arguments: dict) -> list[TextContent]:
    wattage_codes, error = _resolve_codes(arguments.get("wattage"), PSU_WATTAGE, "Potência")
    if error:
        return [TextContent(type="text", text=error)]

    modular_codes, error = _resolve_codes(
        arguments.get("modular"), PSU_MODULAR, "Modularidade"
    )
    if error:
        return [TextContent(type="text", text=error)]

    efficiency_codes, error = _resolve_codes(
        arguments.get("efficiency"), PSU_EFFICIENCY, "Eficiência"
    )
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), PSU_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "potencia_fonte": ",".join(wattage_codes) if wattage_codes else None,
        "modular_fonte": ",".join(modular_codes) if modular_codes else None,
        "eficiencia_fonte": ",".join(efficiency_codes) if efficiency_codes else None,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-fonte", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar fontes: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_psu(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_monitors(arguments: dict) -> list[TextContent]:
    marcas_codes, error = _resolve_codes(arguments.get("brands"), MONITOR_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-monitor", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar monitores: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_monitor(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_keyboards(arguments: dict) -> list[TextContent]:
    mechanical_codes, error = _resolve_codes(
        arguments.get("mechanical"), KEYBOARD_MECHANICAL, "Mecânico"
    )
    if error:
        return [TextContent(type="text", text=error)]

    interface_codes, error = _resolve_codes(
        arguments.get("interface"), KEYBOARD_INTERFACES, "Interface"
    )
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), KEYBOARD_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "mecanico": ",".join(mechanical_codes) if mechanical_codes else None,
        "interface": ",".join(interface_codes) if interface_codes else None,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-keyboard", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar teclados: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_keyboard(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_cables(arguments: dict) -> list[TextContent]:
    marcas_codes, error = _resolve_codes(arguments.get("brands"), CABLE_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-cabos", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar cabos/adaptadores: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_cable(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_mice(arguments: dict) -> list[TextContent]:
    interface_codes, error = _resolve_codes(
        arguments.get("interface"), MOUSE_INTERFACES, "Interface"
    )
    if error:
        return [TextContent(type="text", text=error)]

    marcas_codes, error = _resolve_codes(arguments.get("brands"), MOUSE_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "interface": ",".join(interface_codes) if interface_codes else None,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-mouse", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar mouses: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_mouse(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_speakers(arguments: dict) -> list[TextContent]:
    marcas_codes, error = _resolve_codes(arguments.get("brands"), SPEAKER_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-sound", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar caixas de som: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_speaker(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def handle_search_webcams(arguments: dict) -> list[TextContent]:
    marcas_codes, error = _resolve_codes(arguments.get("brands"), WEBCAM_BRANDS, "Marca")
    if error:
        return [TextContent(type="text", text=error)]

    query = arguments.get("query")
    sort = arguments.get("sort", "relevance")
    page = arguments.get("page", 1)
    max_results = arguments.get("max_results", 10)

    params = {
        "page": page,
        "marcas": ",".join(marcas_codes) if marcas_codes else None,
        "q": query,
        "sort": None if sort == "relevance" else sort,
    }

    try:
        data = await fetch_products("monte-webcam", params)
    except PichauAPIError as exc:
        return [TextContent(type="text", text=f"Erro ao buscar webcams: {exc}")]

    products = data.get("products", {})
    items = products.get("items", [])[:max_results]
    page_info = products.get("page_info", {})

    result = {
        "page": page_info.get("current_page", page),
        "total_pages": page_info.get("total_pages"),
        "results": [_format_webcam(item) for item in items],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


TOOLS: list[Tool] = [
    SEARCH_PROCESSORS_TOOL,
    SEARCH_COOLERS_TOOL,
    SEARCH_MOTHERBOARDS_TOOL,
    SEARCH_MEMORY_TOOL,
    SEARCH_GPUS_TOOL,
    SEARCH_STORAGE_TOOL,
    SEARCH_CASES_TOOL,
    SEARCH_POWER_SUPPLIES_TOOL,
    SEARCH_MONITORS_TOOL,
    SEARCH_KEYBOARDS_TOOL,
    SEARCH_CABLES_TOOL,
    SEARCH_MICE_TOOL,
    SEARCH_SPEAKERS_TOOL,
    SEARCH_WEBCAMS_TOOL,
]

HANDLERS = {
    "search_processors": handle_search_processors,
    "search_coolers": handle_search_coolers,
    "search_motherboards": handle_search_motherboards,
    "search_memory": handle_search_memory,
    "search_gpus": handle_search_gpus,
    "search_storage": handle_search_storage,
    "search_cases": handle_search_cases,
    "search_power_supplies": handle_search_power_supplies,
    "search_monitors": handle_search_monitors,
    "search_keyboards": handle_search_keyboards,
    "search_cables": handle_search_cables,
    "search_mice": handle_search_mice,
    "search_speakers": handle_search_speakers,
    "search_webcams": handle_search_webcams,
}
