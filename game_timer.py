# game_timer.py
class GameTimer:
    def __init__(self):
        self.timer = 0
        self.phase = 'chase'  # Початкова фаза
        self.phase_durations = {
            'chase': 20 * 60,      # 20 секунд переслідування
            'scatter': 7 * 60      # 7 секунд розсіювання
        }

    def update(self):
        self.timer += 1
        current_duration = self.phase_durations[self.phase]
        if self.timer >= current_duration:
            self.timer = 0
            self.switch_phase()

    def switch_phase(self):
        if self.phase == 'chase':
            self.phase = 'scatter'
        else:
            self.phase = 'chase'
        print(f"Фаза змінилася на {self.phase}")
