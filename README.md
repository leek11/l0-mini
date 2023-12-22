# LayerZero AIO ``mini``

#### Установка зависимостей для Windows:

1. `cd путь\к\проекту`.
2. `python -m venv venv`.
3. `.\venv\Scripts\activate`.
4. `pip install -r requirements.txt`.

#### Установка зависимостей для MacOS / Linux:

Выполняем данные команды в терминале:

1. `cd путь/к/проекту`.
2. `python3 -m venv venv`.
3. MacOS/Linux `source venv/bin/activate`.
4. `pip install -r requirements.txt`.

#### Настройка:

Все настройки софта находятся в файле `config.py`:

- ``TG_TOKEN`` – токен Telegram бота для логов
- ``TG_IDS`` – список ID получателей логов 
- ``USE_MOBILE_PROXY`` – использование мобильных прокси (``True``/``False``)
- ``PROXY_CHANGE_IP_URL`` – ссылка на смену IP адреса при использовании мобильных прокси
- ``ZEROX_API_KEY`` – API ключ от 0x
- ``GAS_DELAY_RANGE`` – время задержки между проверкой текущего GWEI
- ``TX_DELAY_RANGE`` – время задержки после отправки любой транзакции
- ``AFTER_APPROVE_DELAY_RANGE`` – задержка после апрув транзакций
- ``WALLET_DELAY_RANGE`` – задержка между кошельками
- ``MAX_SLIPPAGE`` – максимальный slippage
- ``REQUEST_SLEEP_TIME_RANGE`` – задержка между HTTP запросами
- ``TOKEN_USE_PERCENTAGE`` – процент от баланса токена, который будет использован в транзакции CoreBridge
- ``USE_SWAP_BEFORE_BRIDGE`` – использование свапа перед бриджем через Stargate / CoreBridge
- ``ROUND_TO`` – количество знаков после запятой, в случае, если число округляется
- ``MERKLY_TX_COUNT`` – количество транзакций на Merkly
- ``STARGATE_TX_COUNT`` – количество транзакций на Stargate
- ``CORE_TX_COUNT`` – количество транзакций на CoreBridge
- ``OKX_API_KEY``, ``OKX_API_SECRET``, ``OKX_API_PASSWORD`` – данные от API ключа OKX
- ``USE_OKX_WITHDRAW`` – параметры для вывода с ОКХ в случае недостаточного баланса при бридже
- ``OKX_WITHDRAWAL_AMOUNT_RANGE`` – диапазон USDC для вывода с OKX
- ``MAINNET_RPC_URL`` и прочие RPC-ссылки


#### *Запуск:*

1. В `data/private_keys.txt` записываете приватные ключи EVM
2. В `data/proxies.txt` записываете прокси в формате `user:pass@ip:port`

Пишем в консоли `python main.py` на Windows или `python3 main.py` на MacOS / Linux
