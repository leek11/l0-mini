# токен Telegram бота для отправки сообщений
TG_TOKEN = ""

# ID получателей
TG_IDS = []

# использование мобильных прокси (True - если да, иначе False)
USE_MOBILE_PROXY = False

# ссылка для смены IP адреса
PROXY_CHANGE_IP_URL = ""

# api ключ 1INCH (используется в модуле 3)
INCH_API_KEY = ""

# api ключ 0x (используется в модуле 2)
ZEROX_API_KEY = ""

# максимальный GWEI, при котором будут отправлятся транзакции (только в модуле 3)
GAS_THRESHOLD = 15

# время задержки между проверкой текущего GWEI
GAS_DELAY_RANGE = [3, 5]

# время задержки после отправки любой транзакции, кроме апрувов
TX_DELAY_RANGE = [30, 50]

# задержка после апрув транзакций
AFTER_APPROVE_DELAY_RANGE = [2, 4]

# задержка между кошельками (только для модуля 3)
WALLET_DELAY_RANGE = [120, 240]

# максимальный slippage в процентах (1 = 1%)
MAX_SLIPPAGE = 2

# задержка между HTTP запросами (только для модуля 3)
REQUEST_SLEEP_TIME_RANGE = 2

# процент от баланса токена, который будет использован (только для модуля 2)
# в случае, если USE_SWAP_BEFORE_BRIDGE = True, при бридже через Stargate / CoreBridge
# будет браться баланс токена STG / USDT и умножаться на этот коэффициент
TOKEN_USE_PERCENTAGE = 0.003

# использование свапа перед бриджем через Stargate / CoreBridge (True, если использовать)
# если баланс STG / USDT равен нулю, то свап будет проведен вне зависимости от значения этого параметра
USE_SWAP_BEFORE_BRIDGE = True

# количество знаков после запятой, в случае, если число округляется
ROUND_TO = 5

# количество транзакций на Merkly
MERKLY_TX_COUNT = {
    "BSC": {                # Сеть-источник (BSC)
        "Gnosis": [0, 0],   # Сеть-получатель №1 (Gnosis) [от, до]
        "Celo": [0, 0],
        "Kava": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Scroll": [0, 0],
        "DFK": [0, 0],
        "Harmony": [0, 0]
    },
    "Polygon": {
        "Gnosis": [0, 0],
        "Celo": [0, 0],
        "BSC": [0, 0],
        "Kava": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Zora": [0, 0],
        "Scroll": [0, 0],
        "DFK": [0, 0],
        "Harmony": [0, 0]
    },
    "Celo": {
        "Gnosis": [1, 1],
        "Linea": [0, 0],
        "BSC": [0, 0]
    },
    "Gnosis": {
        "Celo": [0, 0],
        "BSC": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Scroll": [0, 0]
    },
    "Arbitrum": {
        "Gnosis": [0, 0],
        "Celo": [0, 0],
        "BSC": [0, 0],
        "Kava": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Zora": [0, 0],
        "Scroll": [0, 0],
        "DFK": [0, 0],
        "Harmony": [0, 0]
    },
    "Moonbeam": {
        "Gnosis": [0, 0],
        "Celo": [0, 0],
        "BSC": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Scroll": [0, 0],
        "DFK": [0, 0],
        "Harmony": [0, 0]
    },
    "Moonriver": {
        "BSC": [0, 0],
        "Kava": [0, 0],
        "Linea": [0, 0],
        "Base": [0, 0],
        "Scroll": [0, 0],
    },
    "Conflux": {
        "Celo": [0, 0]
    }
}

# количество транзакций на Stargate (перед этим идет свап MATIC -> STG через 0x)
STARGATE_TX_COUNT = {
    "Polygon-Kava": [0, 0]
}

# количество транзакций на CoreBridge (перед этим идет свап BNB -> USDT через 0x)
CORE_TX_COUNT = {
    "BSC-Core": [0, 0]
}

# кол-во транзакций на прогон одного аккаунта (в модуле 3)
# считаются только:
# bridge CELO -> GNOSIS
# bridge GNOSIS -> CELO
# остальные транзакции в этот счет не входят
ANGLE_TX_COUNT = [0, 0]

# OKX
OKX_API_KEY = ""
OKX_API_SECRET = ""
OKX_API_PASSWORD = ""

# использование вывода с OKX при бриджах (только в модуле 2)
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
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    },
    "Conflux": {
        "use": False,
        "amount": [0, 0],
        "min-balance": 0.0001
    }
}

# диапазон USDC для вывода с OKX (только для модуля 3)
OKX_WITHDRAWAL_AMOUNT_RANGE = [7, 20]

# ОБЯЗАТЕЛЬНО ЗАПОЛНИТЕ ЭТУ RPC
MAINNET_RPC_URL = "https://rpc.ankr.com/eth"

# rpc (все, что планируются к использованию как сеть-источник должны быть заполнены)
ARBITRUM_RPC_URL = ""
OPTIMISM_RPC_URL = ""
POLYGON_RPC_URL = "https://1rpc.io/matic"
BSC_RPC_URL = "https://rpc.ankr.com/bsc"
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
