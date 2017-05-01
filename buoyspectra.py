import math
import tools
from units import Units, degree_to_direction
from swell import Swell


class BuoySpectra:

    def __init__(self):
        self.frequency= []
        self.energy = []
        self.angle = []
        self.seperation_frequency = float('nan')

    def average_period(self):
        zero_moment = 0.0
        second_moment = 0.0

        if len(self.frequency) < 1 or len(self.energy) < 1:
            return float('nan')

        for i in range(0, len(self.frequency)):
            bandwidth = 0.01
            if i > 0:
                bandwidth = math.abs(self.frequency[i] - self.frequency[i-1])
            else:
                bandwidth = math.abs(self.frequency[i+1] - self.frequency[i])

            zero_moment += tools.zero_spectral_moment(self.energy[i], bandwidth)
            second_moment += tools.second_spectral_moment(self.energy[i], bandwidth, self.frequency[i])

        return math.sqrt(zero_moment/second_moment)

    def wave_summary(self):
        if len(self.frequency) < 1 or len(self.energy) < 1:
            return None

        # Calculate the Significant wave height over the entire spectra
        # And find the dominant frequency index
        max_energy_index = -1
        max_energy = -1.0
        zero_moment = 0.0

        for i in range(0, len(self.frequency)):
            bandwidth = 0.01
            if i > 0:
                bandwidth = math.abs(self.frequency[i] - self.frequency[i-1])
            else:
                bandwidth = math.abs(self.frequency[i+1] - self.frequency[i])

            zero_moment += tools.zero_spectral_moment(self.energy[i], bandwidth)

            if self.energy[i] > max_energy:
                max_energy = self.energy[i]
                max_energy_index = i

        primary_swell = Swell(Units.metric)
        primary_swell.wave_height = 4.0 * math.sqrt(zero_moment)
        primary_swell.period = 1.0 / self.frequency[max_energy_index]
        primary_swell.direction = self.angle[max_energy_index]
        primary_swell.compass_direction = degree_to_direction(primary_swell.direction)
        return primary_swell

    def swell_components(self):
        if len(self.frequency) < 1 or len(self.energy) < 1:
            return []

        min_indexes, min_energies, max_indexes, max_energies = tools.peakdetect(self.energy, 0.01)

        components = []
        prev_index = 0
        for i in range(0, max_energies):
            min_index = prev_index
            if i >= len(min_indexes):
                min_index = len(self.energy)
            else:
                min_index = min_indexes[i]

            zero_moment = 0.0
            for i in range(prev_index, min_index):
                bandwidth = 0.01
                if i > 0:
                    bandwidth = math.abs(self.frequency[i] - self.frequency[i-1])
                else:
                    bandwidth = math.abs(self.frequency[i+1] - self.frequency[i])

                zero_moment += tools.zero_spectral_moment(self.energy[i], bandwidth)

            component = Swell(Units.metric)
            component.wave_height = 4.0 * math.sqrt(zero_moment)
            component.period = 1.0 / self.frequency[max_indexes[i]]
            component.direction = self.angle[max_indexes[i]]
            component.compass_direction = degree_to_direction(component.direction)
            component._max_energy = max_energies[i]
            component._frequency_index = max_indexes[i]
            components.append(component)

        components.sort(key=lambda x: x._max_energy, reverse=True)
        return components