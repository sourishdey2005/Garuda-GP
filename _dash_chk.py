"""Quick smoke-test: dashboard team-accumulation chart for every year."""
import sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

from data_model import get_seasons_data, get_championship_standings, get_races

for yr in [2000, 2003, 2007, 2010, 2014, 2019, 2024, 2025]:
    data = get_seasons_data()
    standings = get_championship_standings(yr)
    races = get_races(yr)

    _all_teams = sorted(set(r['team']
        for race in races
        for r in data[yr]['seasons'].get(race, [])))

    running = {t: 0 for t in _all_teams}
    per_team = {t: [] for t in _all_teams}
    for ri, race_nm in enumerate(races, 1):
        for r in data[yr]['seasons'].get(race_nm, []):
            running[r['team']] = running.get(r['team'], 0) + r['points']
        for t in _all_teams:
            per_team[t].append((ri, running.get(t, 0)))

    traces = 0
    for t in _all_teams:
        ys = [v[1] for v in per_team[t]]
        if max(ys) >= 1:
            traces += 1

    top3 = sorted(per_team.items(), key=lambda x: max(v[1] for v in x[1]), reverse=True)[:3]
    top3_s = ', '.join(f'{t}:{max(v[1] for v in pts)}' for t, pts in top3)
    print(f'{yr}: {len(races)}races {traces}traces teams={_all_teams[:5]}... top={top3_s}')

print('all-clear')
