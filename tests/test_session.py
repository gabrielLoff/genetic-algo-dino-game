from game.session import Session, SESSION_STATE_CONFIG, SESSION_STATE_EVOLVING, SESSION_STATE_PAUSED, SESSION_STATE_FINISHED


class TestSessionStateMachine:
    def test_session_starts_in_config_state(self):
        s = Session(None)
        assert s.state == SESSION_STATE_CONFIG

    def test_session_transitions_to_evolving(self):
        s = Session(None)
        s.start_evolution()
        assert s.state == SESSION_STATE_EVOLVING

    def test_session_pauses(self):
        s = Session(None)
        s.start_evolution()
        s.pause()
        assert s.state == SESSION_STATE_PAUSED

    def test_session_resumes(self):
        s = Session(None)
        s.start_evolution()
        s.pause()
        s.resume()
        assert s.state == SESSION_STATE_EVOLVING

    def test_session_completes(self):
        s = Session(None)
        s.start_evolution()
        s.finish()
        assert s.state == SESSION_STATE_FINISHED

    def test_pause_only_possible_while_evolving(self):
        s = Session(None)
        s.pause()
        assert s.state == SESSION_STATE_CONFIG

    def test_resume_only_possible_while_paused(self):
        s = Session(None)
        s.resume()
        assert s.state == SESSION_STATE_CONFIG


class TestSessionControlFlow:
    def test_run_next_generation_sets_remaining_to_run(self):
        s = Session(None)
        s._config = type("C", (), {"max_generations": 10})()
        s.state = SESSION_STATE_PAUSED
        s.run_next_generation()
        assert s._remaining_to_run == 1
        assert s.state == SESSION_STATE_EVOLVING

    def test_run_n_generations_sets_remaining_to_run(self):
        s = Session(None)
        s._config = type("C", (), {"max_generations": 10})()
        s.state = SESSION_STATE_PAUSED
        s.run_n_generations(5)
        assert s._remaining_to_run == 5
        assert s.state == SESSION_STATE_EVOLVING

    def test_decrement_to_run(self):
        s = Session(None)
        s._remaining_to_run = 3
        s._decrement_to_run()
        assert s._remaining_to_run == 2
        s._decrement_to_run()
        s._decrement_to_run()
        assert s._remaining_to_run == 0

    def test_should_pause_after_decrement(self):
        s = Session(None)
        s._remaining_to_run = 1
        s._decrement_to_run()
        assert s._should_pause_next is True
