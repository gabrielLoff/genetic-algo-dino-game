SESSION_STATE_CONFIG = "config"
SESSION_STATE_EVOLVING = "evolving"
SESSION_STATE_PAUSED = "paused"
SESSION_STATE_FINISHED = "finished"


class Session:
    def __init__(self, config):
        self.state = SESSION_STATE_CONFIG
        self._config = config
        self._to_run = 0
        self._should_pause_next = False

    def start_evolution(self):
        if self.state == SESSION_STATE_CONFIG:
            self.state = SESSION_STATE_EVOLVING

    def pause(self):
        if self.state == SESSION_STATE_EVOLVING:
            self.state = SESSION_STATE_PAUSED

    def resume(self):
        if self.state == SESSION_STATE_PAUSED:
            self.state = SESSION_STATE_EVOLVING

    def finish(self):
        if self.state == SESSION_STATE_EVOLVING:
            self.state = SESSION_STATE_FINISHED

    def run_next_generation(self):
        if self.state == SESSION_STATE_PAUSED:
            self._to_run = 1
            self.state = SESSION_STATE_EVOLVING

    def run_n_generations(self, n):
        if self.state == SESSION_STATE_PAUSED:
            self._to_run = n
            self.state = SESSION_STATE_EVOLVING

    def _decrement_to_run(self):
        if self._to_run > 0:
            self._to_run -= 1
            if self._to_run == 0:
                self._should_pause_next = True

    def _check_pause(self):
        if self._should_pause_next and self.state == SESSION_STATE_EVOLVING:
            self._should_pause_next = False
            self.state = SESSION_STATE_PAUSED
