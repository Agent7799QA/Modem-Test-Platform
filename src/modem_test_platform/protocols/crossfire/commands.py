class Commands:
    """Константы команд модема."""

    # Существующие
    PRINT = "print"
    STAT = "stat"
    TTLSTAT = "ttlstat"
    HELP = "help"

    # Новые команды
    LED = "led"
    REBOOT = "reboot"
    FREQ = "freq"
    MODE = "mode"
    CODE = "code"
    ATTENUATION = "attenuation"
    ADDRESS = "address"  # НЕ ИСПОЛЬЗОВАТЬ
    PAN = "pan"
    RATE = "rate"
    BIND = "bind"
    FHSS = "fhss"
    DSSS = "dsss"
    TIMESLOT = "timeslot"
    EW_TESTS = "ewtests"
    PROTOCOL = "protocol"
    TTL = "ttl"  # Только для TX (ретрансляции)
    ACK = "ack"  # Только для TX (подтверждения)
    CWAVE = "cwave"  # НЕ ТРОГАТЬ
    TRIM = "trim"  # НЕ ТРОГАТЬ