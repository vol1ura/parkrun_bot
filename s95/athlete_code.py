class AthleteCode:
    PARKZHRUN_BORDER = 690_000_000
    SAT_5AM_9KM_BORDER = 770_000_000
    FIVE_VERST_BORDER = 790_000_000
    RUN_PARK_BORDER = 7_000_000_000

    def __init__(self, code) -> None:
        self.__code = code

    @property
    def is_valid(self) -> bool:
        return (isinstance(self.__code, int) or self.__code.isdigit()) and self._int_val > 0

    @property
    def value(self) -> int:
        if self.key == 'id':
            return self._int_val - self.SAT_5AM_9KM_BORDER
        return self._int_val

    @property
    def key(self) -> str:
        if self._is_parkrun_code:
            return 'parkrun_code'
        if self._is_runpark_code:
            return 'fiveverst_code'
        if self._is_fiveverst_code:
            return 'fiveverst_code'
        if self._is_parkzhrun_code:
            return 'parkzhrun_code'
        return 'id'

    @property
    def url(self) -> str:
        if self._is_parkrun_code:
            return f'https://www.parkrun.com.au/results/athleteresultshistory/?athleteNumber={self._int_val}'
        if self._is_runpark_code:
            return 'https://runpark.ru'
        if self._is_fiveverst_code:
            return f'https://5verst.ru/userstats/{self._int_val}/'
        return f'https://s95.ru/athletes/{self._int_val}'

    @property
    def _int_val(self) -> int:
        return int(self.__code)

    @property
    def _is_parkrun_code(self) -> bool:
        """1. ParkRun condition"""
        return self._int_val < self.PARKZHRUN_BORDER

    @property
    def _is_parkzhrun_code(self) -> bool:
        """2. Parkzhrun condition"""
        return self.PARKZHRUN_BORDER < self._int_val < self.SAT_5AM_9KM_BORDER

    @property
    def _is_runpark_code(self) -> bool:
        """3. RunPark condition"""
        return self._int_val > self.RUN_PARK_BORDER

    @property
    def _is_fiveverst_code(self) -> bool:
        """4. 5 verst condition"""
        return self._int_val > self.FIVE_VERST_BORDER
