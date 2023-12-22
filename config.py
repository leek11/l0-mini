##########################################################################
############################# Telegram logs ##############################
##########################################################################

# Токен от телеграм бота.
TG_TOKEN = ""

# ID от аккаунтов телеграм, которым нужно отсылать телеграм логи.
TG_IDS = []

# Eсли хотите получать логи в телеграм: True, а если нет: False.
USE_TG_BOT = False

##########################################################################
################################## Proxy #################################
##########################################################################

# Eсли используете мобильные прокси: True и USE_PROXY = True, а если нет: False.
USE_MOBILE_PROXY = False

# Ссылка на смену ip адреса мобильных прокси.
PROXY_CHANGE_IP_URL = ""

##########################################################################
########################### Основные настройки ###########################
##########################################################################

# API ключ 0x.
ZEROX_API_KEY = ""

# Максимальный slippage в процентах (1 = 1%).
MAX_SLIPPAGE = 2

# Время задержки после отправки любой транзакции, кроме апрувов.
TX_DELAY_RANGE = [30, 100]

# Задержка после апрув транзакций.
AFTER_APPROVE_DELAY_RANGE = [5, 10]

# Процент от баланса токена, который будет использован
# в случае, если USE_SWAP_BEFORE_BRIDGE = False, при бридже через Stargate / CoreBridge
# будет браться баланс токена STG / USDT и умножаться на этот коэффициент.
TOKEN_USE_PERCENTAGE = 0.003

# Использование свапа перед бриджем через Stargate / CoreBridge (True, если использовать)
# если баланс STG / USDT равен нулю, то свап будет проведен вне зависимости от значения этого параметра.
USE_SWAP_BEFORE_BRIDGE = True

# Количество знаков после запятой, в случае, если число округляется.
ROUND_TO = 5

##########################################################################
################################### OKX ##################################
##########################################################################

# API ключ от OKX.
OKX_API_KEY = ""

# Секрет от API ключа от OKX.
OKX_API_SECRET = ""

# Пароль от API ключа от OKX.
OKX_API_PASSWORD = ""

# Использование вывода с OKX при бриджах.
USE_OKX_WITHDRAW = {
    "BSC": {                        # сеть-получатель вывода (источник бриджа)
        "use": False,               # использовать ли вывод, если в данной сети недостаточный баланс (True/False)
        "amount": [0, 0],           # количество для вывода [от, до]
        "min-balance": 0.0001       # минимальный баланс, при котором надо совершать вывод (если "use": True)
    },
    "Polygon": {
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    },
    "Celo": {
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    },
    "Moonbeam": {
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    },
    "Moonriver": {
        "use": True,
        "amount": [0.01, 0.05],
        "min-balance": 0.0001
    },
    "Conflux": {
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    }
}

##########################################################################
##################### RPC (заполнить для всех сетей) #####################
##########################################################################

MAINNET_RPC_URL = "https://rpc.ankr.com/eth"
ARBITRUM_RPC_URL = ""
OPTIMISM_RPC_URL = ""
POLYGON_RPC_URL = "https://1rpc.io/matic"
BSC_RPC_URL = "https://rpc.ankr.com/bsc"  # обязательно поставить приватный анкор
MOONBEAM_RPC_URL = "https://1rpc.io/glmr"
DFK_RPC_URL = "https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc"
HARMONY_RPC_URL = "https://api.harmony.one/"
CELO_RPC_URL = "https://forno.celo.org"
MOONRIVER_RPC_URL = "https://rpc.api.moonriver.moonbeam.network"
KAVA_RPC_URL = "https://evm2.kava.io"
GNOSIS_RPC_URL = ""
CORE_RPC_URL = "https://1rpc.io/core"
LINEA_RPC_URL = "https://1rpc.io/linea"
SCROLL_RPC_URL = ""
BASE_RPC_URL = ""
CONFLUX_RPC_URL = "https://evm.confluxrpc.com"
ZORA_RPC_URL = ""

##########################################################################
########################## Количество транзакций #########################
##########################################################################

# Количество транзакций на Merkly.
MERKLY_TX_COUNT = {
    "BSC": {                            # Сеть-источник (BSC)
        "Gnosis": {                     # сеть-получатель (Gnosis)
            "tx-range": [0, 0],         # диапазон количества транзакций
            "amount-range": [0, 0]      # диапазон получаемых токенов в сети-получателе
        },                              # если amount-range будет 0.5, то в Gnosis придет 0.5 xdai
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Kava": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "DFK": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Harmony": {
            "tx-range": [0, 0],
            "amount-range": [0.01, 0.02]
        }
    },
    "Polygon": {
        "Gnosis": {
            "tx-range": [0, 0],
            "amount-range": [0.01, 0.02]
        },
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Kava": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Zora": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "DFK": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Harmony": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        }
    },
    "Celo": {
        "Gnosis": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        }
    },
    "Gnosis": {
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        }
    },
    "Arbitrum": {
        "Gnosis": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Kava": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Zora": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "DFK": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Harmony": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        }
    },
    "Moonbeam": {
        "Gnosis": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "DFK": {
            "tx-range": [0, 0],
            "amount-range": [0.0001, 0.001]
        },
        "Harmony": {
            "tx-range": [0, 0],
            "amount-range": [0.001, 0.001]
        }
    },
    "Moonriver": {
        "BSC": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Kava": {
            "tx-range": [0, 0],
            "amount-range": [0.0001, 0.001]
        },
        "Linea": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Base": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
        "Scroll": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        },
    },
    "Conflux": {
        "Celo": {
            "tx-range": [0, 0],
            "amount-range": [0, 0]
        }
    }
}

# Количество транзакций на Stargate (перед этим идет свап MATIC -> STG через 0x).
STARGATE_TX_COUNT = {
    "Polygon-Kava": {
        "tx-range": [0, 0],
        "amount-range": [0.01, 0.05]
    }
}

# Количество транзакций на CoreBridge (перед этим идет свап BNB -> USDT через 0x).
CORE_TX_COUNT = {
    "BSC-Core": {
        "tx-range": [0, 0],
        "amount-range": [0, 0]
    }
}
