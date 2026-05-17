"""
data_model.py
Comprehensive F1 data model spanning 26 years (2000–2025).
Every page draws its info from here so year selection flows seamlessly.
"""

import numpy as np
import hashlib

SEED_BASE = 42  # fixed seed so data is deterministic per year/circuit/driver

# ─────────────────────────────────────────────
#  Circuit registry  (name, country, length_km, laps_2025)
# ─────────────────────────────────────────────
CIRCUITS = {
    2000: [
        'Australian GP','Malaysian GP','Brazilian GP','San Marino GP','European GP',
        'Spanish GP','European GP','Monaco GP','Canadian GP','French GP',
        'British GP','German GP','Hungarian GP','Belgian GP','Italian GP',
        'United States GP','Japanese GP','Malaysian GP'
    ],
    2001: [
        'Australian GP','Malaysian GP','Brazilian GP','San Marino GP','Spanish GP',
        'Austrian GP','Monaco GP','Canadian GP','European GP','French GP',
        'British GP','German GP','Hungarian GP','Belgian GP','Italian GP',
        'United States GP','Japanese GP'
    ],
    2002: [
        'Australian GP','Malaysian GP','Brazilian GP','San Marino GP','Spanish GP',
        'Austrian GP','Monaco GP','Canadian GP','European GP','British GP',
        'French GP','German GP','Hungarian GP','Belgian GP','Italian GP',
        'United States GP','Japanese GP'
    ],
    2003: [
        'Australian GP','Malaysian GP','Brazilian GP','San Marino GP','Spanish GP',
        'Austrian GP','Monaco GP','Canadian GP','European GP','French GP',
        'British GP','German GP','Hungarian GP','Italian GP','United States GP',
        'Japanese GP'
    ],
    2004: [
        'Australian GP','Malaysian GP','Bahrain GP','San Marino GP','Spanish GP',
        'Monaco GP','European GP','Canadian GP','United States GP','French GP',
        'British GP','German GP','Hungarian GP','Belgian GP','Italian GP',
        'Chinese GP','Japanese GP','Brazilian GP'
    ],
    2005: [
        'Australian GP','Malaysian GP','Bahrain GP','San Marino GP','Spanish GP',
        'Monaco GP','European GP','Canadian GP','United States GP','French GP',
        'British GP','German GP','Hungarian GP','Turkish GP','Italian GP',
        'Belgian GP','Brazilian GP','Japanese GP','Chinese GP'
    ],
    2006: [
        'Bahrain GP','Malaysian GP','Australian GP','San Marino GP','European GP',
        'Spanish GP','Monaco GP','British GP','Canadian GP','United States GP',
        'French GP','German GP','Hungarian GP','Turkish GP','Italian GP',
        'Chinese GP','Japanese GP','Brazilian GP'
    ],
    2007: [
        'Australian GP','Malaysian GP','Bahrain GP','Spanish GP','Monaco GP',
        'Canadian GP','United States GP','French GP','British GP','European GP',
        'German GP','Hungarian GP','Turkish GP','Italian GP','Belgian GP',
        'Japanese GP','Chinese GP','Brazilian GP'
    ],
    2008: [
        'Australian GP','Malaysian GP','Bahrain GP','Spanish GP','Turkey GP',
        'Monaco GP','Canadian GP','France GP','British GP','German GP',
        'Hungarian GP','European GP','Belgian GP','Italian GP','Singapore GP',
        'Japanese GP','Chinese GP','Brazilian GP'
    ],
    2009: [
        'Australian GP','Malaysian GP','Chinese GP','Bahrain GP','Spanish GP',
        'Monaco GP','Turkish GP','British GP','German GP','Hungarian GP',
        'European GP','Belgian GP','Italian GP','Singapore GP','Japanese GP',
        'Brazilian GP','Abu Dhabi GP'
    ],
    2010: [
        'Bahrain GP','Australian GP','Malaysian GP','Chinese GP','Spanish GP',
        'Monaco GP','Turkish GP','Canadian GP','European GP','British GP',
        'German GP','Hungarian GP','Belgian GP','Italian GP','Singapore GP',
        'Japanese GP','Korean GP','Brazilian GP','Abu Dhabi GP'
    ],
    2011: [
        'Australian GP','Malaysian GP','Chinese GP','Turkish GP','Spanish GP',
        'Monaco GP','Canadian GP','European GP','British GP','German GP',
        'Hungarian GP','Belgian GP','Italian GP','Singapore GP','Japanese GP',
        'Korean GP','Indian GP','Abu Dhabi GP','Brazilian GP'
    ],
    2012: [
        'Australian GP','Malaysian GP','Chinese GP','Bahrain GP','Spanish GP',
        'Monaco GP','Canadian GP','European GP','British GP','German GP',
        'Hungarian GP','Belgian GP','Italian GP','Singapore GP','Japanese GP',
        'Korean GP','Indian GP','Abu Dhabi GP','United States GP','Brazilian GP'
    ],
    2013: [
        'Australian GP','Malaysian GP','Chinese GP','Bahrain GP','Spanish GP',
        'Monaco GP','Canadian GP','British GP','German GP','Hungarian GP',
        'Belgian GP','Italian GP','Singapore GP','Korean GP','Japanese GP',
        'Indian GP','Abu Dhabi GP','United States GP','Brazilian GP'
    ],
    2014: [
        'Australian GP','Malaysian GP','Bahrain GP','Chinese GP','Spanish GP',
        'Monaco GP','Canadian GP','Austrian GP','British GP','German GP',
        'Hungarian GP','Belgian GP','Italian GP','Singapore GP','Japanese GP',
        'Russian GP','United States GP','Mexican GP','Brazilian GP','Abu Dhabi GP'
    ],
    2015: [
        'Australian GP','Malaysian GP','Chinese GP','Bahrain GP','Spanish GP',
        'Monaco GP','Canadian GP','Austrian GP','British GP','Hungarian GP',
        'Belgian GP','Italian GP','Singapore GP','Japanese GP','Russian GP',
        'United States GP','Mexican GP','Brazilian GP','Abu Dhabi GP'
    ],
    2016: [
        'Australian GP','Bahrain GP','Chinese GP','Russian GP','Spanish GP',
        'Monaco GP','Canadian GP','European GP','Austrian GP','British GP',
        'Hungarian GP','German GP','Belgian GP','Italian GP','Singapore GP',
        'Malaysian GP','Japanese GP','United States GP','Mexican GP','Brazilian GP',
        'Abu Dhabi GP'
    ],
    2017: [
        'Australian GP','Chinese GP','Bahrain GP','Russian GP','Spanish GP',
        'Monaco GP','Canadian GP','Azerbaijan GP','Austrian GP','British GP',
        'Hungarian GP','Belgian GP','Italian GP','Singapore GP','Malaysian GP',
        'Japanese GP','United States GP','Mexican GP','Brazilian GP','Abu Dhabi GP'
    ],
    2018: [
        'Australian GP','Bahrain GP','Chinese GP','Azerbaijan GP','Spanish GP',
        'Monaco GP','Canadian GP','French GP','Austrian GP','British GP',
        'German GP','Hungarian GP','Belgian GP','Italian GP','Singapore GP',
        'Russian GP','Japanese GP','United States GP','Mexican GP','Brazilian GP',
        'Abu Dhabi GP'
    ],
    2019: [
        'Australian GP','Bahrain GP','Chinese GP','Azerbaijan GP','Spanish GP',
        'Monaco GP','Canadian GP','French GP','Austrian GP','British GP',
        'German GP','Hungarian GP','Belgian GP','Italian GP','Singapore GP',
        'Russian GP','Japanese GP','Mexican GP','United States GP','Brazilian GP',
        'Abu Dhabi GP'
    ],
    2020: [
        'Austrian GP','Styrian GP','Hungarian GP','British GP','70th Anniversary GP',
        'Spanish GP','Belgian GP','Italian GP','Tuscan GP','Russian GP',
        'Eifel GP','Portuguese GP','Emilia Romagna GP','Turkish GP','Bahrain GP',
        'Sakhir GP','Abu Dhabi GP'
    ],
    2021: [
        'Bahrain GP','Emilia Romagna GP','Portuguese GP','Spanish GP','Monaco GP',
        'Azerbaijan GP','French GP','Styrian GP','Austrian GP','British GP',
        'Hungarian GP','Belgian GP','Dutch GP','Italian GP','Russian GP',
        'Turkish GP','United States GP','Mexico City GP','Sao Paulo GP','Qatar GP',
        'Saudi Arabian GP','Abu Dhabi GP'
    ],
    2022: [
        'Bahrain GP','Saudi Arabian GP','Australian GP','Emilia Romagna GP',
        'Miami GP','Spanish GP','Monaco GP','Azerbaijan GP','Canadian GP',
        'British GP','Austrian GP','French GP','Hungarian GP','Belgian GP',
        'Dutch GP','Italian GP','Singapore GP','Japanese GP','United States GP',
        'Mexico City GP','Sao Paulo GP','Abu Dhabi GP'
    ],
    2023: [
        'Bahrain GP','Saudi Arabian GP','Australian GP','Azerbaijan GP',
        'Miami GP','Monaco GP','Spanish GP','Canadian GP','Austrian GP',
        'British GP','Hungarian GP','Belgian GP','Dutch GP','Italian GP',
        'Singapore GP','Japanese GP','Qatar GP','United States GP','Mexico City GP',
        'Sao Paulo GP','Las Vegas GP','Abu Dhabi GP'
    ],
    2024: [
        'Bahrain GP','Saudi Arabian GP','Australian GP','Japanese GP','Chinese GP',
        'Miami GP','Emilia Romagna GP','Monaco GP','Canadian GP','Spanish GP',
        'Austrian GP','British GP','Hungarian GP','Belgian GP','Dutch GP',
        'Italian GP','Azerbaijan GP','Singapore GP','United States GP',
        'Mexico City GP','Sao Paulo GP','Las Vegas GP','Qatar GP','Abu Dhabi GP'
    ],
    2025: [
        'Bahrain GP','Saudi Arabian GP','Australian GP','Chinese GP','Japanese GP',
        'Spanish GP','Monaco GP','Canadian GP','French GP','Austrian GP',
        'British GP','Hungarian GP','Belgian GP','Dutch GP','Italian GP',
        'Singapore GP','United States GP','Mexico City GP','Sao Paulo GP',
        'Las Vegas GP','Qatar GP','Abu Dhabi GP'
    ],
    2026: [
        'Bahrain GP','Saudi Arabian GP','Australian GP','Japanese GP','Chinese GP',
        'Spanish GP','Monaco GP','Canadian GP','Spanish GP','Austrian GP',
        'British GP','Hungarian GP','Belgian GP','Dutch GP','Italian GP',
        'Singapore GP','United States GP','Mexico City GP','Sao Paulo GP',
        'Las Vegas GP','Qatar GP','Abu Dhabi GP'
    ],
}

YEARS = list(range(2000, 2027))

# ─────────────────────────────────────────────
#  Full grid of seasons  (year → dict)
# ─────────────────────────────────────────────
_SEASONS: dict = {}

def _build_all():
    rng = np.random
    for yr in YEARS:
        races = CIRCUITS.get(yr, CIRCUITS[2025])
        n = len(races)
        s = _seeded(yr)
        # ── drivers present this season ──
        drivers = DRIVERS[yr]
        nd = len(drivers)
        # ── base driver skill 0-100 (deterministic per year+driver) ──
        skill = {d: float(s.integers(72, 99)) for d in drivers}
        # ── per-race results ──
        seasons: dict = {}
        for ri, race in enumerate(races):
            sr = _seeded(yr * 1000 + ri)
            # race pace offset ±3
            race_offsets = {d: float(sr.normal(0, 1.5)) for d in drivers}
            race_skill = {d: np.clip(skill[d] + race_offsets[d], 60, 100) for d in drivers}
            sorted_drivers = sorted(drivers, key=lambda d: -race_skill[d])
            results = []
            for pos_i, drv in enumerate(sorted_drivers):
                laps = n_race_laps(yr, ri)
                best = 88 + sr.normal(0, 1.0)
                wet = False
                pit_stops = sr.choice([1, 1, 1, 2, 2], p=[0.25, 0.25, 0.10, 0.30, 0.10])
                results.append({
                    'position': pos_i + 1,
                    'driver': drv,
                    'team': DRIVER_TO_TEAM.get(drv, 'Unknown'),
                    'points': _points_table(pos_i + 1, yr),
                    'best_lap': round(float(best), 3),
                    'laps': laps,
                    'pit_stops': int(pit_stops),
                    'wet': wet,
                })
            seasons[race] = results
        _SEASONS[yr] = {
            'races': races,
            'seasons': seasons,
            'driver_skill': skill,
        }
    return _SEASONS

def _seeded(val):
    return np.random.default_rng(int(abs(val)) % (2**31))

def _points_table(pos: int, yr: int) -> int:
    """Classic + sprint points."""
    base = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    if pos <= 10:
        return base[pos - 1]
    if yr >= 2021 and pos == 11:
        return 1  # sprint 11th in some seasons
    return 0

# ─────────────────────────────────────────────
#  Drivers per year
# ─────────────────────────────────────────────
DRIVER_TO_TEAM = {
    'Max Verstappen': 'Red Bull', 'Sergio Perez': 'Red Bull',
    'Lewis Hamilton': 'Mercedes', 'George Russell': 'Mercedes',
    'Charles Leclerc': 'Ferrari', 'Carlos Sainz': 'Ferrari',
    'Lando Norris': 'McLaren', 'Oscar Piastri': 'McLaren',
    'Fernando Alonso': 'Aston Martin', 'Lance Stroll': 'Aston Martin',
    'Pierre Gasly': 'Alpine', 'Esteban Ocon': 'Alpine',
    'Alexander Albon': 'Williams', 'Logan Sargeant': 'Williams',
    'Yuki Tsunoda': 'RB', 'Daniel Ricciardo': 'RB',
    'Kevin Magnussen': 'Haas', 'Nico Hulkenberg': 'Haas',
    'Valtteri Bottas': 'Sauber', 'Guanyu Zhou': 'Sauber',
}

# Historical fill-in (2000-2023 drivers absent from the above)
_MISSING_TEAM = {
    'Michael Schumacher':'Ferrari','Mika Hakkinen':'McLaren',
    'David Coulthard':'McLaren','Ralf Schumacher':'Williams',
    'Giancarlo Fisichella':'Jordan','Jenson Button':'Benetton',
    'Kimi Raikkonen':'Sauber','Eddie Irvine':'Jaguar',
    'Mika Salo':'Ferrari','Heinz-Harald Frentzen':'Jordan',
    'Johnny Herbert':'Stewart','Ricardo Zonta':'BAR',
    'Pedro de la Rosa':'Arrows','Marc Gene':'Minardi',
    'Jarno Trulli':'Jordan','Nick Heidfeld':'Prost',
    'Gastón Mazzacane':'Minardi','Tarso Marques':'Minardi',
    'Alex Yoong':'Minardi','Juan Pablo Montoya':'Williams',
    'Jacques Villeneuve':'BAR','Olivier Panis':'Toyota',
    'Alain Prost':'Prost','Enrique Bernoldi':'Arrows',
    'Jos Verstappen':'Arrows','Luciano Burti':'Prost',
    'Allan McNish':'Jaguar','Anthony Davidson':'Minardi',
    'Takuma Sato':'Jordan','Cristiano da Matta':'Toyota',
    'Justin Wilson':'Minardi','Ralph Firman':'Jordan',
    'Giorgio Pantano':'Jordan','Gianmaria Bruni':'Minardi',
    'Zsolt Baumgartner':'Minardi','Tiago Monteiro':'Jordan',
    'Christijan Albers':'Minardi','Patrick Friesacher':'Minardi',
    'Vitantonio Liuzzi':'Red Bull','Narain Karthikeyan':'Jordan',
    'Yuji Ide':'Super Aguri','Franck Montagny':'Super Aguri',
    'Robert Doornbos':'Red Bull','Heikki Kovalainen':'Renault',
    'Adrian Sutil':'Spyker','Sakon Yamamoto':'Super Aguri',
    'Alexander Wurz':'Williams','Timo Glock':'BMW',
    'Nelson Piquet Jr.':'Renault','Kazuki Nakajima':'Williams',
    'Sébastien Bourdais':'Toro Rosso','Jean Alesi':'Prost',
    'Robbie Kerr':'Minardi','Scott Speed':'Toro Rosso',
    'Vitaly Petrov':'Renault','Kamui Kobayashi':'BMW',
    'Nico Hulkenberg':'Williams','Jaime Alguersuari':'Toro Rosso',
    'Sébastien Buemi':'Toro Rosso','Lucas di Grassi':'Virgin',
    'Bruno Senna':'HRT','Paul di Resta':'Force India',
    'Esteban Gutierrez':'Sauber','Pastor Maldonado':'Williams',
    'Jules Bianchi':'Marussia','Jean-Eric Vergne':'Toro Rosso',
    'Max Chilton':'Marussia','Giedo van der Garde':'Caterham',
    'Daniil Kvyat':'Toro Rosso','Marcus Ericsson':'Caterham',
    'Felipe Nasr':'Sauber','Romain Grosjean':'Lotus',
    'Will Stevens':'Marussia','Roberto Merhi':'Marussia',
    'Jolyon Palmer':'Lotus','Pascal Wehrlein':'Manor',
    'Rio Haryanto':'Manor','Stoffel Vandoorne':'McLaren',
    'Antonio Giovinazzi':'Haas','Brendon Hartley':'Toro Rosso',
    'Sergey Sirotkin':'Williams','George Russell':'Williams',
    'Robert Kubica':'Williams','Nicholas Latifi':'Williams',
    'Mick Schumacher':'Haas','Nikita Mazepin':'Haas',
    'Nyck De Vries':'Williams',
}

# Merge, current drivers take priority over any shadow overlap
DRIVER_TO_TEAM = {**_MISSING_TEAM, **DRIVER_TO_TEAM}

TEAM_COLORS = {
    'Red Bull':    '#3671C6',
    'Mercedes':    '#27F4D2',
    'Ferrari':     '#FF2800',
    'McLaren':     '#F58020',
    'Aston Martin':'#358C75',
    'Alpine':      '#2293D1',
    'Williams':    '#37BEDD',
    'RB':          '#6676FF',
    'Haas':        '#B6BABD',
    'Sauber':      '#52E252',
}

DRIVER_COLORS = {
    'Max Verstappen':  '#3671C6',
    'Lewis Hamilton':  '#27F4D2',
    'Charles Leclerc': '#FF2800',
    'Lando Norris':    '#F58020',
    'Carlos Sainz':    '#FF2800',
    'George Russell':  '#27F4D2',
    'Fernando Alonso': '#358C75',
    'Sergio Perez':    '#3671C6',
    'Lance Stroll':    '#358C75',
    'Oscar Piastri':   '#F58020',
    'Pierre Gasly':    '#2293D1',
    'Esteban Ocon':    '#2293D1',
    'Alexander Albon': '#37BEDD',
    'Logan Sargeant':  '#37BEDD',
    'Yuki Tsunoda':    '#6676FF',
    'Daniel Ricciardo':'#6676FF',
    'Kevin Magnussen': '#B6BABD',
    'Nico Hulkenberg': '#B6BABD',
    'Valtteri Bottas': '#52E252',
    'Guanyu Zhou':     '#52E252',
}

# Rotating drivers across 26 seasons
YEAR_DRIVERS = {
    2000: ['Michael Schumacher','Mika Hakkinen','David Coulthard','Rubens Barrichello',
           'Ralf Schumacher','Giancarlo Fisichella','Jenson Button','Kimi Raikkonen',
           'Eddie Irvine','Mika Salo','Heinz-Harald Frentzen','Johnny Herbert',
           'Ricardo Zonta','Pedro de la Rosa','Marc Gene','Jarno Trulli',
           'Nick Heidfeld','Gastón Mazzacane','Tarso Marques','Alex Yoong'],
    2001: ['Michael Schumacher','Rubens Barrichello','David Coulthard','Mika Hakkinen',
           'Ralf Schumacher','Juan Pablo Montoya','Kimi Raikkonen','Jenson Button',
           'Eddie Irvine','Giancarlo Fisichella','Heinz-Harald Frentzen','Jarno Trulli',
           'Olivier Panis','Pedro de la Rosa','Jean Alesi','Nick Heidfeld',
           'Enrique Bernoldi','Jos Verstappen','Tarso Marques','Luciano Burti'],
    2002: ['Michael Schumacher','Rubens Barrichello','Juan Pablo Montoya','Kimi Raikkonen',
           'Ralf Schumacher','David Coulthard','Jenson Button','Jarno Trulli',
           'Eddie Irvine','Giancarlo Fisichella','Heinz-Harald Frentzen','Pedro de la Rosa',
           'Nick Heidfeld','Olivier Panis','Allan McNish','Mark Webber',
           'Alex Yoong','Anthony Davidson','Takuma Sato','Felipe Massa'],
    2003: ['Michael Schumacher','Rubens Barrichello','Kimi Raikkonen','Juan Pablo Montoya',
           'Ralf Schumacher','Jenson Button','David Coulthard','Jarno Trulli',
           'Giancarlo Fisichella','Heinz-Harald Frentzen','Nick Heidfeld','Olivier Panis',
           'Mark Webber','Felipe Massa','Jacques Villeneuve','Pedro de la Rosa',
           'Cristiano da Matta','Justin Wilson','Ralph Firman','Jos Verstappen','Heinz-Harald Frentzen'],
    2004: ['Michael Schumacher','Rubens Barrichello','Jenson Button','Jarno Trulli',
           'Fernando Alonso','Kimi Raikkonen','Juan Pablo Montoya','Giancarlo Fisichella',
           'David Coulthard','Nick Heidfeld','Mark Webber','Felipe Massa',
           'Heinz-Harald Frentzen','Olivier Panis','Pedro de la Rosa','Jacques Villeneuve',
           'Cristiano da Matta','Giorgio Pantano','Gianmaria Bruni','Zsolt Baumgartner'],
    2005: ['Fernando Alonso','Kimi Raikkonen','Michael Schumacher','Giancarlo Fisichella',
           'Juan Pablo Montoya','Jarno Trulli','Ralf Schumacher','David Coulthard',
           'Jenson Button','Nick Heidfeld','Mark Webber','Felipe Massa',
           'Rubens Barrichello','Jacques Villeneuve','Tiago Monteiro','Christijan Albers',
           'Patrick Friesacher','Vitantonio Liuzzi','Narain Karthikeyan','Juan Pablo Montoya'],
    2006: ['Fernando Alonso','Michael Schumacher','Felipe Massa','Kimi Raikkonen',
           'Giancarlo Fisichella','Jenson Button','Rubens Barrichello','Jarno Trulli',
           'Nick Heidfeld','David Coulthard','Mark Webber','Jacques Villeneuve',
           'Robert Kubica','Pedro de la Rosa','Scott Speed','Tiago Monteiro',
           'Yuji Ide','Christijan Albers','Franck Montagny','Robert Doornbos'],
    2007: ['Lewis Hamilton','Fernando Alonso','Kimi Raikkonen','Felipe Massa',
           'Nick Heidfeld','Heikki Kovalainen','Robert Kubica','Heinz-Harald Frentzen',
           'Giancarlo Fisichella','Jenson Button','Ralf Schumacher','David Coulthard',
           'Mark Webber','Vitantonio Liuzzi','Robbie Kerr','Adrian Sutil',
           'Scott Speed','Takuma Sato','Sakon Yamamoto','Anthony Davidson'],
    2008: ['Lewis Hamilton','Felipe Massa','Kimi Raikkonen','Fernando Alonso',
           'Robert Kubica','Nick Heidfeld','Heikki Kovalainen','Jarno Trulli',
           'Timo Glock','Sebastian Vettel','Nico Rosberg','David Coulthard',
           'Jenson Button','Mark Webber','Rubens Barrichello','Nelson Piquet Jr.',
           'Giancarlo Fisichella','Kazuki Nakajima','Adrian Sutil','Takuma Sato'],
    2009: ['Jenson Button','Sebastian Vettel','Rubens Barrichello','Mark Webber',
           'Fernando Alonso','Kimi Raikkonen','Lewis Hamilton','Heikki Kovalainen',
           'Nico Rosberg','Felipe Massa','Robert Kubica','Jarno Trulli',
           'Nick Heidfeld','Timo Glock','Giancarlo Fisichella','Sébastien Bourdais',
           'Adrian Sutil','Pedro de la Rosa','Kamui Kobayashi','Sakon Yamamoto'],
    2010: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Jenson Button','Nico Rosberg','Robert Kubica','Felipe Massa',
           'Rubens Barrichello','Michael Schumacher','Vitaly Petrov','Kamui Kobayashi',
           'Nico Hulkenberg','Pedro de la Rosa','Jaime Alguersuari','Sébastien Buemi',
           'Lucas di Grassi','Heikki Kovalainen','Jarno Trulli','Timo Glock','Bruno Senna'],
    2011: ['Sebastian Vettel','Jenson Button','Fernando Alonso','Mark Webber',
           'Lewis Hamilton',' Felipe Massa','Michael Schumacher','Nico Rosberg',
           'Nico Hulkenberg','Robert Kubica','Vitaly Petrov','Kamui Kobayashi',
           'Rubens Barrichello','Jarno Trulli','Adrian Sutil','Sébastien Buemi',
           'Pastor Maldonado','Heikki Kovalainen','Jérôme d\'Ambrosio','Timo Glock'],
    2012: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Jenson Button','Felipe Massa','Kimi Raikkonen','Nico Rosberg',
           'Michael Schumacher','Sergio Perez','Nico Hulkenberg','Kamui Kobayashi',
           'Pastor Maldonado','Bruno Senna','Romain Grosjean','Heikki Kovalainen',
           'Pedro de la Rosa','Charles Pic','Timo Glock','Narain Karthikeyan','Vitaly Petrov'],
    2013: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Kimi Raikkonen','Felipe Massa','Romain Grosjean','Nico Rosberg',
           'Jenson Button','Paul di Resta','Sergio Perez','Nico Hulkenberg',
           'Esteban Gutierrez','Valtteri Bottas','Pastor Maldonado','Jules Bianchi',
           'Adrian Sutil','Jean-Eric Vergne','Charles Pic','Max Chilton','Giedo van der Garde'],
    2014: ['Lewis Hamilton','Nico Rosberg','Daniel Ricciardo','Fernando Alonso',
           'Valtteri Bottas','Sebastian Vettel','Felipe Massa','Jenson Button',
           'Nico Hulkenberg','Sergio Perez','Kevin Magnussen','Daniil Kvyat',
           'Jules Bianchi','Max Chilton','Esteban Gutierrez','Marcus Ericsson',
           'Pastor Maldonado','Kamui Kobayashi','Adrian Sutil','Jean-Eric Vergne'],
    2015: ['Lewis Hamilton','Nico Rosberg','Sebastian Vettel','Kimi Raikkonen',
           'Valtteri Bottas','Felipe Massa','Daniil Kvyat','Daniel Ricciardo',
           'Sergio Perez','Nico Hulkenberg','Max Verstappen','Carlos Sainz',
           'Marcus Ericsson','Felipe Nasr','Romain Grosjean','Pastor Maldonado',
           'Will Stevens','Roberto Merhi','Jolyon Palmer','Fernando Alonso'],
    2016: ['Nico Rosberg','Lewis Hamilton','Daniel Ricciardo','Max Verstappen',
           'Sebastian Vettel','Kimi Raikkonen','Valtteri Bottas','Nico Hulkenberg',
           'Daniil Kvyat','Sergio Perez','Fernando Alonso','Felipe Massa',
           'Jenson Button','Carlos Sainz','Kevin Magnussen','Jolyon Palmer',
           'Esteban Gutierrez','Pascal Wehrlein','Rio Haryanto','Marcus Ericsson'],
    2017: ['Lewis Hamilton','Sebastian Vettel','Valtteri Bottas','Kimi Raikkonen',
           'Daniel Ricciardo','Max Verstappen','Sergio Perez','Esteban Ocon',
           'Carlos Sainz','Nico Hulkenberg','Felipe Massa','Lance Stroll',
           'Daniil Kvyat','Jenson Button','Romain Grosjean','Jolyon Palmer',
           'Pascal Wehrlein','Stoffel Vandoorne','Fernando Alonso','Kevin Magnussen','Marcus Ericsson'],
    2018: ['Lewis Hamilton','Sebastian Vettel','Kimi Raikkonen','Valtteri Bottas',
           'Max Verstappen','Daniel Ricciardo','Nico Hulkenberg','Sergio Perez',
           'Kevin Magnussen','Carlos Sainz','Fernando Alonso','Esteban Ocon',
           'Charles Leclerc','Stoffel Vandoorne','Lance Stroll','Marcus Ericsson',
           'Pierre Gasly','Brendon Hartley','Sergey Sirotkin','Romain Grosjean'],
    2019: ['Lewis Hamilton','Valtteri Bottas','Charles Leclerc','Max Verstappen',
           'Sebastian Vettel','Carlos Sainz','Daniel Ricciardo','Kimi Raikkonen',
           'Nico Hulkenberg','Alexander Albon','Sergio Perez','Lance Stroll',
           'Pierre Gasly','Kevin Magnussen','Romain Grosjean','Nico Hulkenberg',
           'George Russell','Robert Kubica','Antonio Giovinazzi','Daniil Kvyat'],
    2020: ['Lewis Hamilton','Valtteri Bottas','Max Verstappen','Sergio Perez',
           'Daniel Ricciardo','Carlos Sainz','Lando Norris','Charles Leclerc',
           'Alexander Albon','Pierre Gasly','Esteban Ocon','Lance Stroll',
           'Daniil Kvyat','Nico Hulkenberg','George Russell','Kevin Magnussen',
           'Kimi Raikkonen','Antonio Giovinazzi','Romain Grosjean','Nicholas Latifi'],
    2021: ['Max Verstappen','Lewis Hamilton','Valtteri Bottas','Sergio Perez',
           'Charles Leclerc','Carlos Sainz','Daniel Ricciardo','Pierre Gasly',
           'Lando Norris','Esteban Ocon','Sebastian Vettel','Yuki Tsunoda',
           'George Russell','Kimi Raikkonen','Mick Schumacher','Fernando Alonso',
           'Lance Stroll','Nicholas Latifi','Nikita Mazepin','Robert Kubica'],
    2022: ['Max Verstappen','Sergio Perez','Charles Leclerc','George Russell',
           'Lewis Hamilton','Carlos Sainz','Lando Norris','Fernando Alonso',
           'Esteban Ocon','Pierre Gasly','Lewis Hamilton','Kevin Magnussen',
           'Daniel Ricciardo','Sebastian Vettel','Valtteri Bottas','Lance Stroll',
           'Alexander Albon','Yuki Tsunoda','Zhou Guanyu','Mick Schumacher','Nicholas Latifi'],
    2023: ['Max Verstappen','Sergio Perez','Charles Leclerc','Lewis Hamilton',
           'Carlos Sainz','Lando Norris','Fernando Alonso','George Russell',
           'Esteban Ocon','Pierre Gasly','Lance Stroll','Yuki Tsunoda',
           'Daniel Ricciardo','Oscar Piastri','Nico Hulkenberg','Kevin Magnussen',
           'Alexander Albon','Logan Sargeant','Valtteri Bottas','Zhou Guanyu','Nyck De Vries'],
    2024: ['Max Verstappen','Charles Leclerc','Lewis Hamilton','Carlos Sainz',
           'Lando Norris','George Russell','Oscar Piastri','Sergio Perez',
           'Fernando Alonso','Lance Stroll','Nico Hulkenberg','Pierre Gasly',
           'Alexander Albon','Esteban Ocon','Yuki Tsunoda','Daniel Ricciardo',
           'Kevin Magnussen','Zhou Guanyu','Valtteri Bottas','Logan Sargeant'],
2025: ['Max Verstappen','Charles Leclerc','Lewis Hamilton','Carlos Sainz',
            'Lando Norris','George Russell','Oscar Piastri','Sergio Perez',
            'Fernando Alonso','Lance Stroll','Nico Hulkenberg','Pierre Gasly',
            'Alexander Albon','Esteban Ocon','Yuki Tsunoda','Daniel Ricciardo',
            'Kevin Magnussen','Zhou Guanyu','Valtteri Bottas','Logan Sargeant'],
    2026: ['Max Verstappen','Charles Leclerc','Lewis Hamilton','Carlos Sainz',
            'Lando Norris','George Russell','Oscar Piastri','Sergio Perez',
            'Fernando Alonso','Lance Stroll','Nico Hulkenberg','Pierre Gasly',
            'Alexander Albon','Esteban Ocon','Yuki Tsunoda','Daniel Ricciardo',
            'Kevin Magnussen','Zhou Guanyu','Valtteri Bottas','Oliver Bearman'],
}

DRIVERS = YEAR_DRIVERS  # alias

def n_race_laps(yr: int, race_idx: int) -> int:
    s = _seeded(yr * 100 + race_idx)
    return int(s.integers(44, 78))

# ─────────────────────────────────────────────
#  Championship standings  (year → list[-20] sorted)
# ─────────────────────────────────────────────
_SEASONS_DATA = _build_all()

def get_seasons_data():
    return _SEASONS_DATA


def get_races(year: int) -> list:
    return _SEASONS_DATA[year]['races']


def get_race_results(year: int, race: str) -> list:
    return _SEASONS_DATA[year]['seasons'].get(race, [])


def get_driver_skill(year: int, driver: str) -> float:
    return _SEASONS_DATA[year]['driver_skill'].get(driver, 75)


def get_championship_standings(year: int) -> list:
    pts = {}
    for race in _SEASONS_DATA[year]['races']:
        for r in _SEASONS_DATA[year]['seasons'].get(race, []):
            pts[r['driver']] = pts.get(r['driver'], 0) + r['points']
    drivers = _SEASONS_DATA[year]['races'][0].split() and list({
        d for race in _SEASONS_DATA[year]['races']
        for r in _SEASONS_DATA[year]['seasons'].get(race, [])
        for d in [r['driver']]
    })
    # Rebuild fully
    from collections import defaultdict
    pts2 = defaultdict(int)
    races = _SEASONS_DATA[year]['races']
    for race in races:
        for r in _SEASONS_DATA[year]['seasons'].get(race, []):
            pts2[r['driver']] += r['points']
    sorted_d = sorted(pts2.keys(), key=lambda d: (-pts2[d], d))
    return [{'driver': d, 'points': pts2[d],
             'team': DRIVER_TO_TEAM.get(d, 'Unknown')} for d in sorted_d]


def get_team_cumulative(year: int) -> dict:
    team_pts = {}
    races = _SEASONS_DATA[year]['races']
    cumul = {}
    for race in races:
        results = _SEASONS_DATA[year]['seasons'].get(race, [])
        for r in results:
            t = r['team']
            team_pts[t] = team_pts.get(t, 0) + r['points']
        cumul[race] = dict(sorted(team_pts.items(), key=lambda x: -x[1]))
    return cumul


def get_driver_lap_data(year: int, driver: str, race: str = None) -> dict:
    """Return synthetic lap times for a driver. If race is None, use mid-season race."""
    if race is None:
        race = _SEASONS_DATA[year]['races'][len(_SEASONS_DATA[year]['races'])//2]
    results = _SEASONS_DATA[year]['seasons'].get(race, [])
    best = next((r['best_lap'] for r in results if r['driver'] == driver), 92.0)
    laps = np.linspace(1, 56, 56)
    base = best + 0.5
    trend = 0.015 * (laps - 28)
    noise = _seeded(hash(driver + str(year) + race).__hash__()).normal(0, 0.35, 56)
    lap_times = base + trend + noise
    return {
        'laps': laps.astype(float).tolist(),
        'lap_times': lap_times.tolist(),
        'best_lap': float(best),
        'avg_lap': float(np.mean(lap_times)),
    }
